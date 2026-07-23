# Skill Cookbook

!!! abstract "In a nutshell"
    The rest of this manual documents individual building blocks — settings, scheduling, playback, a GUI — one at a time. This page instead shows them **combined**, the way a real skill uses them: a complete, working file for each common job a skill needs to do. If you already know what `schedule_event` or `@ocp_search` does and just want to see it used correctly next to everything else it needs, start here.

Each recipe below is a **complete skill module** (or a clearly-marked excerpt of one), followed by notes on the moving parts and links to the reference page that documents each API in full. None of these recipes invent new methods: every class, method signature, and bus event name was checked against the installed `ovos-workshop`, `ovos-bus-client`, and `ovos-utils` packages.

!!! note "Scaffolding not shown"
    To keep each recipe focused, `requirements.txt`, `manifest.yml`, `setup.py`/`pyproject.toml`, and the `__init__.py` boilerplate needed to actually publish a skill are omitted here — see [Skill Anatomy](skill-design-guidelines.md) and [Skill Structure](core.md) for those. Intent files (`.intent`, `.voc`) referenced below live under `locale/<lang>/`.

---

## 1. A reminder skill: scheduled events with restart persistence

**When you'd want this:** the user says "remind me in 10 minutes to check the oven", and the reminder must still fire even if the device rebooted in the meantime.

The scheduler (`self.schedule_event`) lives entirely in memory — if the skill process restarts, every pending timer is gone. The only thing that survives a restart is the skill's [settings](skill-settings.md) file, so a reminder skill must write down *when* each reminder is due and re-schedule anything still in the future the moment the skill reloads.

```python
import datetime
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler


class ReminderSkill(OVOSSkill):
    def initialize(self):
        # on every load (including after a restart), re-arm anything
        # that was still pending when we last shut down
        for name, when_iso in self.settings.get("pending_reminders", {}).items():
            when = datetime.datetime.fromisoformat(when_iso)
            if when > datetime.datetime.now():
                self.schedule_event(self.handle_reminder_due, when, name=name)
            else:
                # missed it while we were down, fire immediately
                self.schedule_event(self.handle_reminder_due, 1, name=name)

    @intent_handler("set_reminder.intent")
    def handle_set_reminder(self, message):
        minutes = message.data.get("minutes", 5)
        text = message.data.get("utterance", "your reminder")
        when = datetime.datetime.now() + datetime.timedelta(minutes=float(minutes))
        name = f"reminder_{when.timestamp():.0f}"

        self.schedule_event(self.handle_reminder_due, when,
                             data={"text": text, "name": name}, name=name)

        pending = self.settings.get("pending_reminders", {})
        pending[name] = when.isoformat()
        self.settings["pending_reminders"] = pending
        self.settings.store()

        self.speak_dialog("reminder_set", {"minutes": minutes})

    def handle_reminder_due(self, message):
        self.speak_dialog("reminder_due", {"text": message.data["text"]})
        pending = self.settings.get("pending_reminders", {})
        pending.pop(message.data["name"], None)
        self.settings["pending_reminders"] = pending
        self.settings.store()

    @intent_handler("cancel_reminder.intent")
    def handle_cancel_reminder(self, message):
        pending = self.settings.get("pending_reminders", {})
        # cancel every reminder we know about; a real skill would
        # let the user pick one by name/time instead
        for name in list(pending):
            self.cancel_scheduled_event(name)
            pending.pop(name)
        self.settings["pending_reminders"] = pending
        self.settings.store()
        self.speak_dialog("reminders_cleared")
```

`locale/en-us/dialog/reminder_set.dialog`:

```
I'll remind you in {minutes} minutes
```

`locale/en-us/dialog/reminder_due.dialog`:

```
Reminder: {text}
```

### Moving parts

- `self.schedule_event(handler, when, data=None, name=None)` — `when` accepts a
  `datetime.datetime` (absolute) or an `int`/`float` (seconds from now). `name` is
  the handle you cancel or update by later. Full signature and semantics: [Decorators & Scheduling](decorators.md).
- `self.cancel_scheduled_event(name)` / `self.update_scheduled_event(name, data)` — manage an existing timer by name.
- For a recurring alarm (not a one-shot reminder) use `self.schedule_repeating_event(handler, when, frequency, name=...)` instead — same page.
- `self.settings` is a `JsonStorage` (dict-like) backed by `settings.json`; `self.settings.store()` writes it to disk immediately. See [Skill Settings](skill-settings.md) for the storage location and lifecycle.
- The pattern of "write intended future state to settings, replay it in `initialize()`" is the standard way any OVOS skill survives a restart — there is no separate scheduler persistence API.

!!! tip "Full production example"
    [`ovos-skill-alarm`](https://github.com/OpenVoiceOS/ovos-skill-alarm) implements exactly this pattern for real alarms and timers, including recurring (weekday) alarms via `schedule_repeating_event`.

---

## 2. User-configurable behavior: settings + settingsmeta + live reload

**When you'd want this:** a skill has a behavior the user should be able to tune — a unit system, a greeting name, an API key — and it should react immediately when that value changes, whether the change came from a config file edit or a remote settings backend.

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler


class GreeterSkill(OVOSSkill):
    def initialize(self):
        self.settings_change_callback = self.on_settings_changed
        self._apply_settings()

    def _apply_settings(self):
        self.greeting_name = self.settings.get("name", "friend")
        self.use_title_case = self.settings.get("shout", False)

    def on_settings_changed(self):
        # called whenever settings.json changes on disk, or a remote
        # settings backend pushes an update for this skill
        self._apply_settings()
        self.log.info(f"settings updated, now greeting as {self.greeting_name}")

    @intent_handler("greet.intent")
    def handle_greet(self, message):
        name = self.greeting_name.upper() if self.use_title_case else self.greeting_name
        self.speak_dialog("greeting", {"name": name})
```

`settingsmeta.yaml` (the optional form shown by web/companion-app settings UIs):

```yaml
skillMetadata:
  sections:
    - name: "Greeter"
      fields:
        - name: "name"
          type: "text"
          label: "What should I call you?"
          value: "friend"
        - name: "shout"
          type: "checkbox"
          label: "SHOUT the greeting"
          value: false
```

### Moving parts

- `self.settings_change_callback` is a plain attribute you assign a callable to (there is no decorator for it) — the base class checks `if self.settings_change_callback is not None` both on a local file-watcher change and on a remote `mycroft.skills.settings.changed` push, and calls it with no arguments either way. See [Skill Settings](skill-settings.md) for the two trigger paths.
- Read settings defensively with `.get(key, default)` — a fresh install has an empty `settings.json` until `settingsmeta.yaml` defaults are applied by a settings UI, or you seed `self.settings` yourself in `initialize()`.
- `settingsmeta.yaml`/`.json` is descriptive only: it drives a *UI* for editing settings, it does not itself create or validate keys — [Skill Settings Meta](skill-settings-meta.md) covers the full field-type table and where the file must live.

---

## 3. Calling an external API safely: timeouts, `runtime_requirements`, spoken errors, and a cache

**When you'd want this:** a skill answers "what's the exchange rate" or similar by hitting a remote HTTP API, and needs to (a) never hang the skill process on a slow/dead endpoint, (b) not even try to load fully when there's no network, and (c) fail with a spoken sentence instead of a traceback.

```python
import json
import time

import requests
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler

API_URL = "https://api.example.com/rate"
CACHE_TTL = 3600  # seconds


class ExchangeRateSkill(OVOSSkill):

    @property
    def runtime_requirements(self):
        # this skill is useless without a live network connection,
        # so don't even finish loading it until one is available
        return RuntimeRequirements(
            network_before_load=True,
            internet_before_load=True,
            requires_internet=True,
            requires_network=True,
            no_internet_fallback=False,
            no_network_fallback=False,
        )

    def _cache_path(self):
        return self.file_system.path + "/rate_cache.json"

    def _read_cache(self):
        try:
            with open(self._cache_path()) as f:
                data = json.load(f)
            if time.time() - data["fetched_at"] < CACHE_TTL:
                return data["rate"]
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass
        return None

    def _write_cache(self, rate):
        with open(self._cache_path(), "w") as f:
            json.dump({"rate": rate, "fetched_at": time.time()}, f)

    def _fetch_rate(self):
        cached = self._read_cache()
        if cached is not None:
            return cached
        try:
            resp = requests.get(API_URL, timeout=5)
            resp.raise_for_status()
            rate = resp.json()["rate"]
        except requests.exceptions.Timeout:
            self.speak_dialog("api_timeout")
            return None
        except requests.exceptions.RequestException as e:
            self.log.warning(f"exchange rate API call failed: {e}")
            self.speak_dialog("api_error")
            return None
        self._write_cache(rate)
        return rate

    @intent_handler("exchange_rate.intent")
    def handle_exchange_rate(self, message):
        rate = self._fetch_rate()
        if rate is not None:
            self.speak_dialog("exchange_rate", {"rate": rate})
```

### Moving parts

- `runtime_requirements` (a `@property` you override, returning `RuntimeRequirements(...)`) tells the skill loader whether to gate loading/running this skill on network and internet availability — this is the mechanism, `requires_internet=True` alone does not skip loading, `*_before_load` flags do. See [Decorators & Runtime Requirements](decorators.md) for every flag and its default.
- Always pass `timeout=` to `requests.get`/`.post` — an OVOS skill runs on the shared bus-handling thread pool and a hung HTTP call can stall other skill callbacks.
- `self.file_system` (a `FileSystemAccess`, exposing `.path`) is a writable, skill-private directory distinct from `settings.json` — the right place for a response cache, downloaded assets, or anything larger than a few settings keys.
- Wrap the network call narrowly (`requests.exceptions.Timeout` / `.RequestException`) so a real bug elsewhere in the handler still raises normally instead of being swallowed by a broad `except Exception`.

---

## 4. Continuous conversation: multi-turn dialog with `converse` and `get_response`

**When you'd want this:** the interaction needs more than one exchange — booking a table means asking for a time, a party size, and a name in sequence, or reacting to whatever the user says next without them repeating the skill's name.

There are two complementary tools for this:

- `self.get_response(...)` — call it *from inside an intent handler* to ask one question and block until an answer (or timeout) comes back. Best for a short, linear form.
- `ConversationalSkill.converse(message)` — override this to intercept **every** utterance while your skill is "active" (recently used), before intent matching even runs. Best for an open-ended back-and-forth.

```python
from ovos_workshop.skills.converse import ConversationalSkill
from ovos_workshop.decorators import intent_handler


class TableBookingSkill(ConversationalSkill):
    def initialize(self):
        self._pending_booking = None

    @intent_handler("book_table.intent")
    def handle_book_table(self, message):
        party_size = self.get_response("ask_party_size")
        if party_size is None:
            self.speak_dialog("booking_cancelled")
            return
        time_str = self.get_response("ask_time")
        if time_str is None:
            self.speak_dialog("booking_cancelled")
            return

        self._pending_booking = {"size": party_size, "time": time_str}
        # stay "active" so the next thing the user says, even without
        # re-invoking this skill, is routed to converse() below
        self.activate()
        self.speak_dialog("confirm_booking", self._pending_booking)

    def converse(self, message):
        if self._pending_booking is None:
            return False  # not our turn, let normal intent matching happen

        utterance = message.data.get("utterances", [""])[0]
        if self.voc_match(utterance, "yes"):
            self.speak_dialog("booking_confirmed", self._pending_booking)
            self._pending_booking = None
            return True
        if self.voc_match(utterance, "no"):
            self.speak_dialog("booking_cancelled")
            self._pending_booking = None
            return True
        return False  # didn't understand, let something else try
```

### Moving parts

- `get_response(dialog="", data=None, validator=None, on_fail=None, num_retries=-1)` speaks `dialog` (rendered with `data`), then waits for a reply; it returns the utterance string, or `None` if the user didn't answer / said "cancel". `validator` can reject and re-ask (e.g. requiring a number).
- `converse()` only runs while the skill is **active** — recently handled an intent, or explicitly kept alive with `self.activate(duration_minutes=...)` as shown above. It must subclass `ConversationalSkill` (not plain `OVOSSkill`) to be dispatched; returning `True` claims the utterance, `False` lets normal pipeline processing continue. See [Converse](converse.md) and the [Converse Pipeline](converse-pipeline.md) for how a skill enters and leaves the active list.
- `self.voc_match(utterance, "yes")` checks against `locale/en-us/vocab/yes.voc` — see [Skill Design Guidelines](skill-design-guidelines.md) for vocab file conventions.
- [Context](context.md) (`self.set_context()`) is the lighter-weight alternative when you only need to bias which of *your own* intents can match next, rather than intercepting raw utterances.

---

## 5. A small local media playlist: an OCP skill

**When you'd want this:** "play the office playlist" should hand back a short, fixed list of local audio files without any external search or streaming service.

```python
from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_search
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill

PLAYLIST = [
    {
        "title": "Morning Briefing",
        "uri": "file:///opt/office-media/morning-briefing.mp3",
        "length": 180,
    },
    {
        "title": "Lobby Loop",
        "uri": "file:///opt/office-media/lobby-loop.mp3",
        "length": 600,
    },
]


class OfficePlaylistSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, supported_media=[MediaType.MUSIC], **kwargs)
        self.skill_icon = ""  # optional path/URI to an icon shown in OCP's UI

    @ocp_search()
    def search_office_playlist(self, phrase, media_type=MediaType.GENERIC):
        # self.voc_match() lets a skill claim narrow phrases confidently;
        # everything else gets a low, generic confidence
        confident = self.voc_match(phrase, "office_playlist")
        for track in PLAYLIST:
            if confident or track["title"].lower() in phrase.lower():
                yield {
                    "title": track["title"],
                    "uri": track["uri"],
                    "media_type": MediaType.MUSIC,
                    "playback": PlaybackType.AUDIO,
                    "match_confidence": 90 if confident else 40,
                    "length": track["length"],
                }
```

`locale/en-us/vocab/office_playlist.voc`:

```
office playlist
lobby music
```

### Moving parts

- `MediaType` and `PlaybackType` are enums imported from `ovos_utils.ocp`; results are plain dicts, not a dedicated result class — mandatory keys are `uri`, `title`, `media_type`, `playback`, `match_confidence` (0-100), with `artist`, `album`, `image`, `length` (seconds) optional. Full field table: [OCP Skills](ocp-skills.md).
- `@ocp_search()` (imported from `ovos_workshop.decorators.ocp`) marks a method as a search provider; OCP calls every registered provider's search method in parallel and keeps the best-confidence result across all installed OCP skills. A search method may `return` a list or `yield` results incrementally.
- `supported_media` (passed to `super().__init__()`) tells OCP which `MediaType`s this skill should even be asked about.
- `self.voc_match(phrase, "office_playlist")` reuses the same vocabulary mechanism as intents to give a confident match a high score, while still falling back to a loose substring check.
- [OCP Skills](ocp-skills.md) also documents `self.extend_timeout()` (ask OCP to wait longer for a slow search) and notes that new integrations not needing the full skill lifecycle may prefer a `MediaProvider` plugin instead — see that page's opening warning.

---

## 6. GUI + voice together: show a page while speaking, update it live

**When you'd want this:** a skill on a screen-equipped device (a Mark 2, say) should show a result — a weather card, a list, a picture — at the same moment it speaks about it, and keep the screen in sync as things change (e.g. counting down a timer).

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler


class WeatherCardSkill(OVOSSkill):
    @intent_handler("weather.intent")
    def handle_weather(self, message):
        temperature = self._get_temperature()  # however this skill fetches it

        self.gui["temperature"] = temperature
        self.gui["condition"] = "Sunny"
        self.gui.show_page("weather.qml", override_idle=30)

        self.speak_dialog("weather", {"temp": temperature})

    def handle_temperature_update(self, message):
        # e.g. called from a scheduled event every few minutes while the
        # weather page is showing, to refresh the number without re-speaking
        self.gui["temperature"] = message.data["temperature"]
```

`gui/qt5/weather.qml` renders `temperature`/`condition` as GUI session data; see [Skill GUI](skill-gui.md) for the full page/session-data lifecycle and `gui/qt6`/other render-backend layout conventions.

### Moving parts

- `self.gui` is a `SkillGUI` instance (a subclass of `GUIInterface`), set up automatically once a skill initializes — no separate import or manual construction needed.
- `self.gui["key"] = value` sets session data the page template reads; `self.gui.show_page(name, override_idle=...)` requests that page be displayed (`override_idle` keeps it up for N seconds even if something would otherwise return to the idle screen).
- Updating `self.gui[...]` again while the page is already showing (as in `handle_temperature_update`) pushes fresh data to an already-visible page without calling `show_page` again.
- !!! danger "This is the legacy GUI stack"
    Everything in this recipe targets the current, **deprecated** `.qml`-based GUI stack, which [Skill GUI](skill-gui.md) documents as effectively unusable outside Mark 2 maintenance today. The forward-looking replacement is the **Upcoming** [GUI rework](gui-adapters.md) (spec OVOS-GUI-1), which instead has a skill declare intent via a closed `SYSTEM_*` template vocabulary rather than shipping custom `.qml`; that page is the one to design new screen support against.

---

## 7. Fallback + LLM: delegating unmatched utterances to a solver plugin

**When you'd want this:** every intent-matching skill has had its turn and none of them understood the utterance — instead of a flat "sorry, I don't understand", hand it to a language-model-backed plugin and speak whatever it comes back with.

```python
from ovos_plugin_manager.templates.solvers import QuestionSolver
from ovos_workshop.skills.fallback import FallbackSkill


class LLMFallbackSkill(FallbackSkill):
    def initialize(self):
        # a specific solver plugin id, e.g. "ovos-solver-openai-persona-plugin";
        # load_solver_plugin looks it up via the opm.solver entry point group
        from ovos_plugin_manager.solvers import find_question_solver_plugins
        plugin_id = self.settings.get("solver_plugin", "ovos-solver-openai-persona-plugin")
        plugins = find_question_solver_plugins()
        if plugin_id not in plugins:
            self.log.warning(f"solver plugin '{plugin_id}' not installed, "
                              "falling back to a plain 'I don't understand'")
            self.solver = None
        else:
            self.solver: QuestionSolver = plugins[plugin_id]()

        # broad catch-all: let every more specific fallback/skill go first
        self.register_fallback(self.handle_fallback, 90)

    def handle_fallback(self, message):
        utterance = message.data["utterance"]
        if self.solver is None:
            return False
        answer = self.solver.get_spoken_answer(utterance, lang=self.lang)
        if answer:
            self.speak(answer)
            return True
        return False
```

### Moving parts

- A `FallbackSkill` subclass calls `self.register_fallback(handler, priority)` in `initialize()`; `handler` must return `True` if it produced an answer (stopping the chain) or `False` to let the next-priority fallback try. Priority `90` is deliberately high (tried late) since an LLM should be the *last* resort, not the first — see [Fallback Skill](fallbacks.md) for the recommended priority tiers.
- `QuestionSolver.get_spoken_answer(query, lang=None, units=None)` is the common template every question-answering solver plugin implements — a plugin is just a Python entry point (`opm.solver`) you load by id, the same plugin-discovery pattern used everywhere else in OVOS.
- !!! warning "Upcoming — solver templates are being replaced"
      `ovos_plugin_manager.templates.solvers` (including `QuestionSolver`, used above because it is what ships and runs today) is deprecated in favor of `ovos_plugin_manager.templates.agents.AbstractAgentEngine` and the `opm.agents.*` entry point groups. New solver plugins should target the newer API; see [Specialized Agent Engine Types](advanced-solvers.md) for the full migration table and what each new agent type replaces.
- `self.speak(text)` (a raw string) is used here instead of `self.speak_dialog(...)` because the LLM's answer is not a template — it's already the exact sentence to say.

---

## 8. Ambient behavior from bus events: react to listening state and time of day

**When you'd want this:** a skill needs to do something not triggered by an utterance at all — dim a light while the device is actively listening, or change its greeting depending on whether it's morning or night, driven purely by bus events other services already emit.

```python
import datetime

from ovos_bus_client.message import Message
from ovos_workshop.skills import OVOSSkill


class AmbientMoodSkill(OVOSSkill):
    def initialize(self):
        # the listener (ovos-dinkum-listener) emits these around each
        # recording, independent of any skill or intent
        self.add_event("recognizer_loop:record_begin", self.handle_listening_start)
        self.add_event("recognizer_loop:record_end", self.handle_listening_end)
        self.add_event("recognizer_loop:audio_output_start", self.handle_speaking_start)
        self.add_event("recognizer_loop:audio_output_end", self.handle_speaking_end)

        # check the time of day once now, and again every 15 minutes
        self._update_time_of_day()
        self.schedule_repeating_event(self._update_time_of_day, None, 15 * 60,
                                       name="mood_time_check")

    def handle_listening_start(self, message):
        self._set_mood("listening")

    def handle_listening_end(self, message):
        self._set_mood("idle")

    def handle_speaking_start(self, message):
        self._set_mood("speaking")

    def handle_speaking_end(self, message):
        self._set_mood("idle")

    def _update_time_of_day(self, message=None):
        hour = datetime.datetime.now().hour
        self.is_daytime = 7 <= hour < 20

    def _set_mood(self, mood):
        self.bus.emit(Message("ovos.ambient_mood.changed",
                               {"mood": mood, "daytime": self.is_daytime}))
```

### Moving parts

- `recognizer_loop:record_begin` / `recognizer_loop:record_end` bracket an active recording (wake word already triggered); `recognizer_loop:audio_output_start` / `_end` bracket the device speaking — both pairs are emitted by the listener service regardless of which skill (if any) is involved. There is also `recognizer_loop:wakeword`, emitted the instant the wake word itself is detected, slightly before recording begins.
- `self.add_event(msg_type, handler)` subscribes for the lifetime of the skill (auto-removed on shutdown) — the general-purpose alternative to a decorator-based intent handler, for any bus event that isn't an utterance.
- `schedule_repeating_event(handler, when, frequency, name=...)` with `when=None` starts the first run after one `frequency` interval; pass a `datetime` for `when` instead if the first run needs to happen at a specific moment.
- This skill emits its own `ovos.ambient_mood.changed` event rather than reaching into a light/hardware plugin directly, keeping it decoupled from whatever actually consumes the mood (a PHAL plugin, another skill, a GUI). See [Bus Service](bus-service.md) for the emit/on API and [PIPELINE-1 correlation](converse-pipeline.md) for how bus events relate to a given utterance's session.

---

## Recipe index

| # | Recipe | Base class | Key APIs |
|---|--------|-----------|----------|
| 1 | Reminder with restart persistence | `OVOSSkill` | `schedule_event`, `settings` |
| 2 | Configurable + reactive settings | `OVOSSkill` | `settings_change_callback`, `settingsmeta.yaml` |
| 3 | Safe external API call | `OVOSSkill` | `runtime_requirements`, `file_system` |
| 4 | Multi-turn conversation | `ConversationalSkill` | `get_response`, `converse`, `activate` |
| 5 | Local media playlist | `OVOSCommonPlaybackSkill` | `@ocp_search`, `MediaType`/`PlaybackType` |
| 6 | GUI + voice together | `OVOSSkill` | `self.gui`, `show_page` |
| 7 | Fallback to an LLM solver | `FallbackSkill` | `register_fallback`, `QuestionSolver` |
| 8 | Ambient bus-event behavior | `OVOSSkill` | `add_event`, `recognizer_loop:*` |

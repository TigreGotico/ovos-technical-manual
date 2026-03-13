# Skill Classes

`ovos-workshop` provides all base classes needed to write skills for OpenVoiceOS. Every skill ultimately inherits from `OVOSSkill`.

**Package:** `ovos-workshop` | **Entry point group:** `opm.skills`

---

## Class Hierarchy

```
OVOSSkill                             ovos_workshop/skills/ovos.py
├── ConversationalSkill               ovos_workshop/skills/converse.py
│   └── ActiveSkill                   ovos_workshop/skills/active.py
├── FallbackSkill                     ovos_workshop/skills/fallback.py
├── CommonQuerySkill                  ovos_workshop/skills/common_query_skill.py
├── OVOSCommonPlaybackSkill           ovos_workshop/skills/common_play.py
│   └── OVOSGameSkill                 ovos_workshop/skills/game_skill.py
│       └── ConversationalGameSkill   ovos_workshop/skills/game_skill.py
├── UniversalSkill                    ovos_workshop/skills/auto_translatable.py
│   ├── UniversalFallback             ovos_workshop/skills/auto_translatable.py
│   └── UniversalCommonQuerySkill     ovos_workshop/skills/auto_translatable.py (deprecated)
└── OVOSAbstractApplication           ovos_workshop/app.py

```

---

## OVOSSkill

**Module:** `ovos_workshop.skills.ovos.OVOSSkill`

The universal base class. Every skill and application ultimately inherits from `OVOSSkill`. Handles intent registration, resource files, settings, GUI interface, [MessageBus](bus-service.md) events, and the full skill lifecycle.

```python
from ovos_workshop.skills.ovos import OVOSSkill
from ovos_workshop.decorators import intent_handler

class HelloWorldSkill(OVOSSkill):
    """A minimal OVOS skill."""

    @intent_handler("hello.intent")
    def handle_hello(self, message):
        """Respond to a greeting."""
        self.speak_dialog("hello.response")


def create_skill():
    return HelloWorldSkill()

```

`pyproject.toml` entry point:

```toml
[project.entry-points."opm.skills"]
hello-world-skill = "hello_world_skill:HelloWorldSkill"

```

### Constructor

```python
OVOSSkill(
    name: str = None,          # DEPRECATED, use skill_id
    bus: MessageBusClient = None,
    resources_dir: str = None,
    settings: dict = None,     # initial default settings
    gui: GUIInterface = None,
    skill_id: str = "",        # set by SkillLoader
)

```

Modern skills should always accept `**kwargs` and pass them to `super().__init__`.

### Lifecycle Methods

Override these in your skill class:

| Method | When called | Notes |
|---|---|---|
| `initialize()` | After full startup | Legacy. Prefer `__init__`. |
| `get_intro_message()` | First run only | Return a dialog name or string to speak on first install |
| `stop()` | User/system stop | Return `True` if the skill handled the stop |
| `stop_session(session)` | Per-session stop | Called before `stop()`; return `True` to prevent global `stop()` |
| `can_stop(message)` | Before stop | Must be implemented if `stop()` or `stop_session()` is defined |
| `shutdown()` | Skill unload | Final cleanup after all other shutdown steps |

### Startup Sequence

1. Set `skill_id`


2. Init settings (`_init_settings`)


3. Bind bus (`bind`)


4. Init GUI


5. Load resource files (`load_data_files`)


6. Register decorated intents (`_register_decorated`)


7. Register homescreen app if `@homescreen_app` used


8. Register resting screen if `@resting_screen_handler` used


9. Call `initialize()`


10. Check first run


11. Set status to `ready`

### Key Properties

**[Session](session.md)-aware (read from current Session):**

| Property | Type | Description |
|---|---|---|
| `lang` | `str` | BCP-47 language of the current request |
| `core_lang` | `str` | Default configured language |
| `secondary_langs` | `list` | Configured secondary languages |
| `location` | `dict` | Location preferences |
| `location_timezone` | `str` | Timezone code |
| `system_unit` | `str` | `"metric"` or `"imperial"` |

**Infrastructure:**

| Property | Type | Description |
|---|---|---|
| `settings` | `JsonStorage` | Persistent skill settings |
| `bus` | `MessageBusClient` | MessageBus connection |
| `gui` | `SkillGUI` | GUI interface |
| `file_system` | `FileSystemAccess` | Managed local file access |
| `resources` | `SkillResources` | Resource files for `self.lang` |
| `event_scheduler` | `EventSchedulerInterface` | Schedule future bus events |
| `audio_service` | `OCPInterface` | Control audio/[OCP](ocp-pipeline.md) playback |
| `is_fully_initialized` | `bool` | True after `_startup` completes |

### Speaking

```python
self.speak("Hello world")
self.speak_dialog("my.dialog.file")            # uses locale/<lang>/dialog/my.dialog.file
self.speak_dialog("my.dialog", data={"name": "Alice"})  # Mustache templating

```

### Getting User Input

```python
response = self.get_response("What is your name?")

# Yes/No question
answer = self.ask_yesno("Do you want to continue?")   # returns "yes" / "no" / None

# Selection from list
choice = self.ask_selection(["A", "B", "C"], "Pick one")

```

`get_response` suspends the converse channel for this skill until the user responds or a timeout is hit.

### RuntimeRequirements

Override the class property to declare connectivity needs:

```python
from ovos_utils.process_utils import RuntimeRequirements

@classproperty
def runtime_requirements(cls):
    return RuntimeRequirements(
        internet_before_load=False,
        network_before_load=False,
        requires_internet=False,
        requires_network=False,
    )

```

Used by `SkillManager` to defer loading until requirements are met.

---

## ConversationalSkill

**Module:** `ovos_workshop.skills.converse.ConversationalSkill`

Extends `OVOSSkill` with explicit converse support — `activate()`, `deactivate()`, and `@conversational_intent` decorated handlers. The skill registers itself in the active-skills list after handling an intent.

```python
from ovos_workshop.skills.converse import ConversationalSkill

class MySkill(ConversationalSkill):
    def converse(self, message):
        utterance = message.data["utterances"][0]
        if "help" in utterance:
            self.speak("Here to help!")
            return True   # consumed
        return False      # pass to next handler

```

Additional bus events registered:

- `{skill_id}.converse.ping` — capability advertisement


- `{skill_id}.converse.request` — converse request from pipeline


- `{skill_id}.activate` / `{skill_id}.deactivate`

---

## ActiveSkill

**Module:** `ovos_workshop.skills.active.ActiveSkill`

Extends `ConversationalSkill`. Always present in the converse active-skills list — the skill never deactivates unless explicitly told to. Useful for always-on assistants or global command handlers.

```python
from ovos_workshop.skills.active import ActiveSkill

class AlwaysListeningSkill(ActiveSkill):
    def converse(self, message):
        utterance = message.data["utterances"][0]
        # handle every utterance
        return False  # let other skills also process

```

---

## FallbackSkill

**Module:** `ovos_workshop.skills.fallback.FallbackSkill`

Handles utterances that matched no intent. Must implement `can_answer()` and provide at least one `@fallback_handler`.

```python
from ovos_workshop.skills.fallback import FallbackSkill
from ovos_workshop.decorators import fallback_handler

class MyFallback(FallbackSkill):
    def can_answer(self, utterances, lang) -> bool:
        return True   # always willing to try

    @fallback_handler(priority=50)
    def handle_fallback(self, message):
        self.speak("I don't know, but I tried.")
        return True   # consumed — stop checking other fallbacks

```

Priority determines stage:

| Range | Stage |
|---|---|
| 0–4 | `fallback_high` |
| 5–89 | `fallback_medium` |
| 90–100 | `fallback_low` |

Priority can be overridden in config:

```json
{"skills": {"fallbacks": {"fallback_priorities": {"my-skill-id": 10}}}}

```

---

## CommonQuerySkill

**Module:** `ovos_workshop.skills.common_query_skill.CommonQuerySkill`

Participates in the `question:query` / `common_qa` pipeline. The skill attempts to answer a natural language question and returns a confidence score. The pipeline collects responses from all skills and speaks the highest-confidence answer.

```python
from ovos_workshop.skills.common_query_skill import CommonQuerySkill
from ovos_workshop.decorators import common_query

class MyQuerySkill(CommonQuerySkill):
    @common_query()
    def handle_query(self, phrase, lang):
        if "capital of france" in phrase.lower():
            return "Paris", 0.9   # (answer, confidence)
        return None, 0

```

---

## OVOSCommonPlaybackSkill

**Module:** `ovos_workshop.skills.common_play.OVOSCommonPlaybackSkill`

Integrates with OCP (OpenVoiceOS [Common Play](ocp-pipeline.md)) for media playback. Uses `@ocp_search`, `@ocp_play`, and related decorators to respond to play requests and appear in the OCP media browser.

```python
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_utils.ocp import MediaType, PlaybackType, MediaEntry, Playlist

class MyMusicSkill(OVOSCommonPlaybackSkill):
    @ocp_search()
    def search_music(self, phrase: str, media_type: MediaType):
        if media_type == MediaType.MUSIC:
            yield MediaEntry(
                title="My Song",
                uri="https://example.com/song.mp3",
                playback=PlaybackType.AUDIO,
                media_type=MediaType.MUSIC,
                match_confidence=80,
            )

    @ocp_featured_media()
    def featured(self) -> Playlist:
        pl = Playlist(title="My Playlist", playback=PlaybackType.AUDIO,
                      media_type=MediaType.MUSIC, match_confidence=90)
        pl.add_entry(MediaEntry(uri="https://example.com/song.mp3",
                                title="My Song",
                                playback=PlaybackType.AUDIO,
                                media_type=MediaType.MUSIC,
                                match_confidence=90))
        return pl

```

---

## OVOSGameSkill

**Module:** `ovos_workshop.skills.game_skill.OVOSGameSkill`
**Source:** `ovos_workshop/skills/game_skill.py:14`

Extends `OVOSCommonPlaybackSkill`. Structured base for OCP-integrated voice games. Subclasses must implement all six abstract methods: `on_play_game`, `on_pause_game`, `on_resume_game`, `on_stop_game`, `on_save_game`, `on_load_game`.

```python
from ovos_workshop.skills.game_skill import OVOSGameSkill

class TriviaGameSkill(OVOSGameSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(skill_voc_filename="trivia_game", *args, **kwargs)

    def on_play_game(self):
        self.speak("Starting trivia!")

    def on_pause_game(self):
        self._paused.set()

    def on_resume_game(self):
        self._paused.clear()

    def on_stop_game(self):
        self.speak("Game over.")

    def on_save_game(self):
        self.speak("Save is not supported.")

    def on_load_game(self):
        self.speak("Load is not supported.")

```

---

## ConversationalGameSkill

**Module:** `ovos_workshop.skills.game_skill.ConversationalGameSkill`
**Source:** `ovos_workshop/skills/game_skill.py:151`

Extends `OVOSGameSkill`. Adds a **converse loop**: every utterance that does not match a registered intent is piped to `on_game_command()` while the game is playing. Also adds auto-save support, default pause/resume dialogs, and `on_abandon_game()`.

Remaining abstract methods: `on_play_game`, `on_stop_game`, `on_game_command`.

```python
from ovos_workshop.skills.game_skill import ConversationalGameSkill

class AdventureSkill(ConversationalGameSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(skill_voc_filename="adventure_game", *args, **kwargs)

    def on_play_game(self):
        self.speak("You enter a dark room. What do you do?")

    def on_stop_game(self):
        self.speak("Adventure ends.")

    def on_game_command(self, utterance: str, lang: str):
        if "north" in utterance:
            self.speak("You walk north.")
        else:
            self.speak("I don't understand that command.")

```

---

## UniversalSkill

**Module:** `ovos_workshop.skills.auto_translatable.UniversalSkill`
**Source:** `ovos_workshop/skills/auto_translatable.py:14`

Extends `OVOSSkill`. Automatically translates incoming utterances to `self.internal_language` before the intent handler runs, and translates `self.speak()` output back to the user's language. Requires a translator plugin to be configured.

```python
from ovos_workshop.skills.auto_translatable import UniversalSkill
from ovos_workshop.decorators import intent_handler

class MySkill(UniversalSkill):
    def __init__(self, *args, **kwargs):
        # All handlers receive utterances in English regardless of user's language.
        super().__init__(internal_language="en-US", *args, **kwargs)

    @intent_handler("ask_weather.intent")
    def handle_weather(self, message):
        # Utterance is already in en-US here.
        self.speak("The weather is sunny.")  # auto-translated back to user's lang

```

---

## UniversalFallback

**Module:** `ovos_workshop.skills.auto_translatable.UniversalFallback`
**Source:** `ovos_workshop/skills/auto_translatable.py:314`

Combines `UniversalSkill` and `FallbackSkill`. [Fallback](fallback-pipeline.md) handlers receive utterances in `self.internal_language`. `self.speak()` translates output back to the user's language.

```python
from ovos_workshop.skills.auto_translatable import UniversalFallback
from ovos_workshop.decorators import fallback_handler

class MyUniversalFallback(UniversalFallback):
    def __init__(self, *args, **kwargs):
        super().__init__(internal_language="en-US", *args, **kwargs)

    @fallback_handler(priority=75)
    def handle_unknown(self, message) -> bool:
        utterance = message.data["utterances"][0]
        self.speak(f"I heard: {utterance}")
        return True

```

---

## OVOSAbstractApplication

**Module:** `ovos_workshop.app.OVOSAbstractApplication`
**Source:** `ovos_workshop/app.py:12`

Like `OVOSSkill` but designed to run **without** an intent service. Suitable for standalone GUI apps, [HiveMind](hivemind-agents.md)-attached services, or any program that needs [TTS](tts-plugins.md)/MessageBus/settings but does not register intents with `ovos-core`. Creates its own bus connection if none is provided. Settings stored under `apps/<id>/` instead of `skills/<id>/`.

```python
from ovos_workshop.app import OVOSAbstractApplication

class MyApp(OVOSAbstractApplication):
    def __init__(self, **kwargs):
        super().__init__(skill_id="my-app.author", **kwargs)

    def initialize(self):
        self.speak("App is ready.")

app = MyApp()  # Creates its own bus connection automatically.

```

---

## Skill Launcher

**Module:** `ovos_workshop.skill_launcher.PluginSkillLoader`

`PluginSkillLoader` is used by `SkillManager` to load plugin-based skills:

```python
from ovos_workshop.skill_launcher import PluginSkillLoader

loader = PluginSkillLoader(bus, skill_id)
loader.load(MySkillClass)   # instantiates and calls _startup

```

Skills can also be run as standalone processes:

```bash
ovos-skill-launcher my_skill_package_name

```

This is the recommended approach for running skills in Docker containers.

---

## Decorators Quick Reference

All decorators are importable from `ovos_workshop.decorators`:

| Decorator | Description |
|---|---|
| `@intent_handler("file.intent")` | Register [Padatious](padatious-pipeline.md) or [Adapt](adapt-pipeline.md) intent handler |
| `@conversational_intent("file.intent")` | Register converse-only Padatious handler |
| `@fallback_handler(priority=50)` | Register fallback handler with priority |
| `@common_query()` | Register CommonQuery handler (return answer, confidence) |
| `@converse_handler` | Alias method as the skill's `converse` handler |
| `@adds_context("Context")` | Add context entity after method runs |
| `@removes_context("Context")` | Remove context entity after method runs |
| `@skill_api_method` | Expose method over the bus for inter-skill calls |
| `@killable_intent()` | Intent that can be interrupted mid-execution |
| `@homescreen_app(icon, name)` | Register as homescreen app launcher |
| `@ocp_search()` | Search for playable content |
| `@ocp_featured_media()` | Provide featured media for OCP GUI |
| `@layer_intent(intent, layer_name)` | Intent belonging to a named layer |
| `@enables_layer("layer")` | Activate a named intent layer after method |
| `@disables_layer("layer")` | Deactivate a named intent layer after method |

---

## Related Pages

- [ovos-core](core.md) — `SkillManager`, `IntentService`, skill loading


- [Converse Pipeline](converse-pipeline.md) — `ConversationalSkill` in action


- [Fallback Pipeline](fallback-pipeline.md) — `FallbackSkill` in action


- [Skill Settings](skill-settings.md) — `self.settings` persistence


- [Skill Filesystem](skill-filesystem.md) — `self.file_system`


- [Skill API](ovos-skill.md) — `@skill_api_method`, inter-skill calls


- [Bus Session](session.md) — session state available to skills

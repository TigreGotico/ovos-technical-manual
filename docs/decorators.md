# Decorators

!!! abstract "In a nutshell"
    A "decorator" is a small label you place on a line just above one of your skill's functions (it starts with an `@`). The label tells OVOS what that function is for — for example, "run this when the user asks about the weather" or "run this only if nothing else understood the request." It's like sticking a labelled note on a drawer so the system knows what's inside without opening it. This page lists the available labels and what each one does. New to skills? See [Skill Classes](skill-classes.md) or the [Glossary](glossary.md).

All decorators are importable from `ovos_workshop.decorators`.

```python
from ovos_workshop.decorators import (
    intent_handler,
    fallback_handler,
    converse_handler,
    conversational_intent,
    common_query,
    skill_api_method,
    adds_context,
    removes_context,
    homescreen_app,
    killable_intent,
    killable_event,
)
from ovos_workshop.decorators.layers import (
    layer_intent,
    enables_layer,
    disables_layer,
    replaces_layer,
    removes_layer,
    resets_layers,
)
from ovos_workshop.decorators.ocp import (
    ocp_search,
    ocp_play,
    ocp_pause,
    ocp_resume,
    ocp_next,
    ocp_previous,
    ocp_featured_media,
)

```

---

## Intent Decorators

### `@intent_handler`

`intent_handler` — `ovos_workshop/decorators/__init__.py:57`

Register a method as a [Padatious](padatious-pipeline.md) (`.intent` file) or [Adapt](adapt-pipeline.md) (`IntentBuilder`) intent handler.

```python
from ovos_workshop.decorators import intent_handler
from ovos_workshop.intents import IntentBuilder

# Padatious intent file
@intent_handler("my.intent")
def handle_my(self, message): ...

# Adapt intent
@intent_handler(IntentBuilder("GreetIntent").require("Hello"))
def handle_greet(self, message): ...

# With voc blacklist — suppress adapt keywords in this handler
@intent_handler("my.intent", voc_blacklist=["StopKeyword"])
def handle_my_no_stop(self, message): ...

```

A method can have multiple `@intent_handler` decorators to handle multiple intents with the same function.

---

### `@conversational_intent`

`conversational_intent` — `ovos_workshop/decorators/__init__.py:134`

Register a Padatious `.intent` file as a converse-only matcher. Only active when the skill is in converse mode. Requires the skill to extend `ConversationalSkill`.

> **Note:** Only Padatious intents are supported, not Adapt.

```python
from ovos_workshop.decorators import conversational_intent

@conversational_intent("help.intent")
def handle_help_in_converse(self, message): ...

```

---

### `@fallback_handler`

`fallback_handler` — `ovos_workshop/decorators/__init__.py:150`

Register a method as a fallback handler with a given priority (0–100, lower = higher priority).

```python
from ovos_workshop.decorators import fallback_handler

@fallback_handler(priority=50)
def handle_unknown(self, message):
    self.speak("I don't know.")
    return True  # consumed — stop checking other fallbacks

```

---

### `@common_query`

`common_query` — `ovos_workshop/decorators/__init__.py:111`

Register a method as a CommonQuery handler. The method must return `(answer, confidence)` or `None`.

```python
from ovos_workshop.decorators import common_query

@common_query(callback=None)
def handle_query(self, phrase, lang):
    if "meaning of life" in phrase:
        return "42", 0.99
    return None, 0

```

`callback` is optional. If provided it is called with `(phrase, answer, lang)` after the answer is spoken.

---

## Converse Decorators

### `@converse_handler`

`converse_handler` — `ovos_workshop/decorators/__init__.py:125`

Alias a method as the skill's `converse` handler instead of overriding `converse()` directly.

```python
from ovos_workshop.decorators import converse_handler

@converse_handler
def my_converse(self, message):
    return False  # not consumed

```

---

## Context Decorators

`adds_context` — `ovos_workshop/decorators/__init__.py:16`
`removes_context` — `ovos_workshop/decorators/__init__.py:37`

These run **after** the decorated method completes.

### `@adds_context`

```python
from ovos_workshop.decorators import adds_context

@adds_context("OrderContext", "ordering")
def handle_order(self, message):
    self.speak("What would you like to order?")

```

### `@removes_context`

```python
from ovos_workshop.decorators import removes_context

@removes_context("OrderContext")
def handle_cancel(self, message):
    self.speak("Order cancelled.")

```

---

## Killable / Abortable Decorators

### Exception Classes

`AbortEvent` — `ovos_workshop/decorators/killable.py:12`
`AbortIntent` — `ovos_workshop/decorators/killable.py:16`
`AbortQuestion` — `ovos_workshop/decorators/killable.py:20`

```python
class AbortEvent(StopIteration):
    """Base class — abort any bus event handler."""

class AbortIntent(AbortEvent):
    """Abort intent parsing; raised by @killable_intent."""

class AbortQuestion(AbortEvent):
    """Gracefully abort get_response queries."""

```

These exceptions are **raised inside the handler thread** when the kill message is received. They propagate through the call stack; wrap long-running loops to catch and clean up:

```python
from ovos_workshop.decorators.killable import killable_intent, AbortIntent

@killable_intent()
def handle_long_task(self, message):
    for step in range(1000):
        try:
            self.speak(f"Step {step}")
        except AbortIntent:
            self.speak("Task was cancelled.")
            return

```

---

### `@killable_intent`

`killable_intent` — `ovos_workshop/decorators/killable.py:24`

Mark an intent handler that can be interrupted mid-execution. Spawns the handler in a daemon thread. When the kill message arrives:

1. Optionally emits `mycroft.audio.speech.stop` (if `stop_tts=True`).


2. Optionally calls `skill.stop()` (if `call_stop=True`).


3. Raises `AbortIntent` in the handler thread.


4. Calls `callback` if one was provided.

```python
from ovos_workshop.decorators import killable_intent

@killable_intent(
    msg="mycroft.skills.abort_execution",  # bus message that triggers abort
    callback=None,                          # optional cleanup callable
    react_to_stop=True,                     # also react to stop messages
    call_stop=True,                         # call skill.stop() on abort
    stop_tts=True,                          # stop TTS playback on abort
)
def handle_long_task(self, message):
    import time
    for i in range(60):
        self.speak(f"Counting {i}")
        time.sleep(1)

```

Default parameters:

| Parameter | Default |
|---|---|
| `msg` | `"mycroft.skills.abort_execution"` |
| `callback` | `None` |
| `react_to_stop` | `True` |
| `call_stop` | `True` |
| `stop_tts` | `True` |

**Abort flow:**

```
Bus receives "mycroft.skills.abort_execution"
  └─► abort() called in main thread
      ├─► emit "mycroft.audio.speech.stop"  (if stop_tts=True)
      ├─► skill.stop()                       (if call_stop=True)
      ├─► t.raise_exc(AbortIntent)           ← raised inside handler thread
      └─► callback()                         (if provided)

```

---

### `@killable_event`

`killable_event` — `ovos_workshop/decorators/killable.py:40`

Like `@killable_intent` but for any bus event handler. Does **not** react to stop messages or call `skill.stop()` by default.

```python
from ovos_workshop.decorators.killable import killable_event, AbortEvent

@killable_event(
    msg="my.abort.signal",
    exc=AbortEvent,          # exception to raise (default AbortEvent)
    callback=None,
    react_to_stop=False,     # default False for events
    call_stop=False,         # default False for events
    stop_tts=False,
    check_skill_id=False,    # require skill_id match in message.data
)
def handle_background_task(self, message):
    # long-running work here
    pass

```

The `check_skill_id=True` option prevents accidental termination when another skill's abort message is received.

---

## Intent Layer Decorators

Intent layers let you enable or disable groups of intents at runtime, implementing modal/state-based flows.

### `@layer_intent`

`layer_intent` — `ovos_workshop/decorators/layers.py:159`

Register an intent handler that belongs to a named layer. The intent is disabled until the layer is activated.

```python
from ovos_workshop.decorators.layers import layer_intent
from ovos_workshop.intents import IntentBuilder

@layer_intent(IntentBuilder("MoveIntent").require("Move"), layer_name="game_active")
def handle_move(self, message): ...

```

---

### `@enables_layer` / `@disables_layer`

`enables_layer` — `ovos_workshop/decorators/layers.py:66`
`disables_layer` — `ovos_workshop/decorators/layers.py:85`

Activate or deactivate a named intent layer **after** the decorated method runs.

```python
from ovos_workshop.decorators.layers import enables_layer, disables_layer

@enables_layer("game_active")
def start_game(self, message):
    self.speak("Game started!")

@disables_layer("game_active")
def stop_game_intent(self, message):
    self.speak("Game stopped!")

```

---

### `@replaces_layer`

`replaces_layer` — `ovos_workshop/decorators/layers.py:104`

Replace the intent list of a named layer after the method runs.

```python
from ovos_workshop.decorators.layers import replaces_layer

@replaces_layer("my_layer", intent_list=["NewIntent1", "NewIntent2"])
def transition(self, message): ...

```

---

### `@removes_layer`

`removes_layer` — `ovos_workshop/decorators/layers.py:123`

Remove a named layer entirely (and disable its intents) after the method runs.

```python
from ovos_workshop.decorators.layers import removes_layer

@removes_layer("temporary_layer")
def finish_flow(self, message): ...

```

---

### `@resets_layers`

`resets_layers` — `ovos_workshop/decorators/layers.py:142`

Disable **all** intent layers after the method runs.

```python
from ovos_workshop.decorators.layers import resets_layers

@resets_layers()
def reset_everything(self, message):
    self.speak("All modes cleared.")

```

---

## GUI / Homescreen Decorators

### `@homescreen_app`

`homescreen_app` — `ovos_workshop/decorators/__init__.py:166`

Register a method as a homescreen app launcher. The icon file must be inside the `gui/` subfolder of the skill.

```python
from ovos_workshop.decorators import homescreen_app

@homescreen_app(icon="my_app.png", name="My App")
def launch_app(self, message):
    self.gui.show_page("main.qml")

```

---

## API Decorator

### `@skill_api_method`

`skill_api_method` — `ovos_workshop/decorators/__init__.py:94`

Expose a method over the bus so other skills or applications can call it via `SkillApi`. See [skill-api.md](ovos-skill.md) for the full RPC documentation.

```python
from ovos_workshop.decorators import skill_api_method

@skill_api_method
def get_data(self, key: str) -> dict:
    """Return data for key."""
    return {"key": key, "value": self.settings.get(key)}

```

The method is registered as `{skill_id}.get_data` on the bus.

---

## OCP Decorators

OCP (OpenVoiceOS [Common Play](ocp-pipeline.md)) decorators are used with `OVOSCommonPlaybackSkill` and `OVOSGameSkill`.

**Source:** `ovos_workshop/decorators/ocp.py`

| Decorator | Attribute set | Description | Source line |
|---|---|---|---|
| `@ocp_search()` | `is_ocp_search_handler` | Search for playable content; yield/return `MediaEntry` results. | `ocp.py:5` |
| `@ocp_play()` | `is_ocp_playback_handler` | Handle a play request (start playback). | `ocp.py:34` |
| `@ocp_pause()` | `is_ocp_pause_handler` | Handle a pause request. | `ocp.py:82` |
| `@ocp_resume()` | `is_ocp_resume_handler` | Handle a resume request. | `ocp.py:98` |
| `@ocp_next()` | `is_ocp_next_handler` | Handle skip-forward. | `ocp.py:66` |
| `@ocp_previous()` | `is_ocp_prev_handler` | Handle skip-backward. | `ocp.py:50` |
| `@ocp_featured_media()` | `is_ocp_featured_handler` | Provide featured/recommended media for the OCP GUI. | `ocp.py:114` |

```python
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_utils.ocp import MediaType, PlaybackType, MediaEntry, Playlist


class MyMusicSkill(OVOSCommonPlaybackSkill):

    @ocp_search()
    def search_music(self, phrase: str, media_type: MediaType):
        if media_type == MediaType.MUSIC:
            yield MediaEntry(
                uri="https://example.com/song.mp3",
                title="My Song",
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

## Combining Decorators

Python applies stacked decorators **bottom-up** (innermost first). Whether
order matters depends on what each decorator does to the function:

- `@intent_handler`, `@fallback_handler`, `@common_query`, `@conversational_intent`,
  `@homescreen_app`, and `@skill_api_method` are pure **tags** — they set an
  attribute on the function object and return it unchanged, without wrapping
  it. Because of this, stacking one of these with a wrapping decorator (like
  `@killable_intent` or `@adds_context`) works in **either order**: the tag
  ends up on whatever object is on top by the time it runs, and
  `functools.wraps` propagates it if another wrapper is added afterwards.

```python
# Both of these register the intent correctly — order does not matter here,
# because @intent_handler never wraps the function.
@killable_intent(react_to_stop=True)
@intent_handler("long_task.intent")
def handle_long_task(self, message):
    ...

@intent_handler("long_task.intent")
@killable_intent(react_to_stop=True)
def handle_long_task(self, message):
    ...
```

- `@adds_context`, `@removes_context`, `@killable_intent`, `@killable_event`,
  and the intent-layer decorators (`@enables_layer`, `@disables_layer`, etc.)
  **do** wrap the function — they run code before and/or after calling it.
  When you stack two *wrapping* decorators together, the order changes what
  actually executes and when, so make sure the one that should run
  last (e.g. `@adds_context`, which fires after the handler body returns) is
  the outermost:

```python
@adds_context("ConfirmContext")   # runs after handle_confirm() returns
@intent_handler("confirm_order.intent")
def handle_confirm(self, message):
    self.speak("Order confirmed.")
```

---

*Source code: [OpenVoiceOS/ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop).*

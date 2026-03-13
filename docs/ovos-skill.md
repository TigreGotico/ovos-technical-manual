# OVOSSkill

**Module:** `ovos_workshop.skills.ovos.OVOSSkill`

`OVOSSkill` is the base class that all OVOS skills inherit from. It handles startup, intent registration, resource loading, settings, event management, GUI, and shutdown.

## Constructor

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

Modern skills should always accept `**kwargs` and pass them to `super().__init__`:

```python
class MySkill(OVOSSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

```

## Lifecycle Methods

Override these in your skill class:

| Method | When called | Notes |
|---|---|---|
| `initialize()` | After full startup | Legacy. Prefer `__init__`. |
| `get_intro_message()` | First run only | Return a dialog name or string to speak on first install |
| `stop()` | User/system stop | Return `True` if the skill handled the stop |
| `stop_session(session)` | Per-session stop | Called before `stop()`; return `True` to prevent global `stop()` |
| `can_stop(message)` | Before stop | Must be implemented if `stop()` or `stop_session()` is defined |
| `shutdown()` | [Skill](skill-design-guidelines.md) unload | Final cleanup after all other shutdown steps |

### Startup Sequence (`_startup`)

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

### Shutdown Sequence (`default_shutdown`)

1. `stop()`


2. Store settings


3. Shutdown GUI


4. Shutdown event scheduler, clear events


5. Call `shutdown()`


6. Emit `detach_skill`

## Key Properties

### Session-aware (read from current Session)

| Property | Type | Description |
|---|---|---|
| `lang` | `str` | BCP-47 language of the current request |
| `core_lang` | `str` | Default configured language |
| `secondary_langs` | `list` | Configured secondary languages |
| `native_langs` | `list` | `core_lang` + `secondary_langs` |
| `location` | `dict` | Location preferences |
| `location_pretty` | `str` | City name |
| `location_timezone` | `str` | Timezone code |
| `system_unit` | `str` | `"metric"` or `"imperial"` |
| `date_format` | `str` | `"DMY"`, `"MDY"`, or `"YMD"` |
| `time_format` | `str` | `"half"` or `"full"` |

### Infrastructure

| Property | Type | Description |
|---|---|---|
| `settings` | `JsonStorage` | Persistent skill settings |
| `bus` | `MessageBusClient` | [MessageBus](bus-service.md) connection |
| `gui` | `SkillGUI` | GUI interface |
| `enclosure` | `EnclosureAPI` | Hardware interface |
| `file_system` | `FileSystemAccess` | Managed local file access |
| `resources` | `SkillResources` | Resource files for `self.lang` |
| `dialog_renderer` | `MustacheDialogRenderer` | Render dialog templates |
| `event_scheduler` | `EventSchedulerInterface` | Schedule future bus events |
| `intent_service` | `IntentServiceInterface` | Register/manage intents |
| `intent_layers` | `IntentLayers` | Manage intent layer sets |
| `audio_service` | `OCPInterface` | Control audio/[OCP](ocp-pipeline.md) playback |
| `translator` | `OVOSLangTranslation` | Language translation (lazy init) |
| `lang_detector` | `OVOSLangDetection` | Language detection (lazy init) |
| `is_fully_initialized` | `bool` | True after `_startup` completes |
| `reload_skill` | `bool` | Set to `False` to prevent hot-reload |

## Speaking

```python
self.speak("Hello world")
self.speak_dialog("my.dialog.file")            # uses locale/lang/dialog/my.dialog.file
self.speak_dialog("my.dialog", data={"name": "Alice"})  # Mustache templating

```

## Getting User Input

```python
response = self.get_response("What is your name?")

# Yes/No question
answer = self.ask_yesno("Do you want to continue?")   # returns "yes" / "no" / None

# Selection from list
choice = self.ask_selection(["A", "B", "C"], "Pick one")

```

`get_response` suspends the converse channel for this skill until the user responds or a timeout is hit. Raise `AbortQuestion` to cancel gracefully.

## Intent Registration

```python

# Padatious (intent file)
self.register_intent_file("my.intent", self.handler)

# Adapt (vocab-based)
from ovos_workshop.intents import IntentBuilder
intent = IntentBuilder("MyIntent").require("Keyword").build()
self.register_intent(intent, self.handler)

# Vocabulary keywords
self.register_vocabulary("hello", "HelloKeyword")
self.register_entity_file("food.entity")

```

## Context Management

```python
self.set_context("MyContext", "value")
self.remove_context("MyContext")

```

## Public Skill API

Decorate a method with `@skill_api_method` to expose it over the bus. Other skills or tools can call it via `SkillApi`.

## RuntimeRequirements

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

This is used by `SkillManager` to defer loading until the required connectivity is available.

## System Bus Events Handled (per skill)

| Event | Description |
|---|---|
| `mycroft.stop` | Trigger stop flow |
| `{skill_id}.stop` | Skill-specific stop |
| `{skill_id}.stop.ping` | Check if skill can stop |
| `{skill_id}.converse.get_response` | Feed user response to `get_response` |
| `mycroft.skill.enable_intent` | Enable a disabled intent |
| `mycroft.skill.disable_intent` | Disable an active intent |
| `mycroft.skill.set_cross_context` | Set cross-skill context |
| `mycroft.skill.remove_cross_context` | Remove cross-skill context |
| `mycroft.skills.settings.changed` | Remote settings update |
| `ovos.skills.settings_changed` | Local settings file changed |
| `question:query` | Common query pipeline request |
| `ovos.common_query.ping` | Common query service discovery |
| `question:action.{skill_id}` | Common query callback |
| `homescreen.metadata.get` | Homescreen requesting metadata |
| `{skill_id}.public_api` | Skill API introspection |

# Skill API — Inter-Skill RPC

`SkillApi` provides a [MessageBus](bus-service.md)-based remote procedure call (RPC) mechanism. Methods decorated with `@skill_api_method` are exposed on the bus; any other skill (or application) can call them by fetching a `SkillApi` proxy object.

**Source:** `ovos_workshop/skills/api.py`

---

## Overview

The bus message protocol for `SkillApi` has two phases:

1. **Discovery** — the caller sends `<skill_id>.public_api` on the bus. The target skill responds with a dict mapping method names to their bus message type and docstring.


2. **Call** — the caller sends a `Message` of the method's registered type with `{"args": [...], "kwargs": {...}}`. The target skill responds with `{"result": <return value>}`.

Return values must be JSON-serializable. Standard Python builtins (`str`, `int`, `list`, `dict`, `None`, `bool`) work. Custom classes are not supported.

---

## `@skill_api_method` Decorator

`skill_api_method` — `ovos_workshop/decorators/__init__.py:77`

Tag a skill method as part of the public API. The decorator sets `func.api_method = True`. During skill initialization `OVOSSkill` discovers all methods with this attribute and registers a bus listener for each one at `<skill_id>.<method_name>`.

```python
from ovos_workshop.decorators import skill_api_method

class MySkill(OVOSSkill):

    @skill_api_method
    def get_temperature(self, city: str) -> float:
        """Return the current temperature for the given city."""
        return self._fetch_temperature(city)

```

---

## `SkillApi` Class

`SkillApi` — `ovos_workshop/skills/api.py:20`

### Setup

Before calling `SkillApi.get()`, register the bus client once during skill initialization:

```python
from ovos_workshop.skills.api import SkillApi

SkillApi.connect_bus(self.bus)

```

### `SkillApi.get(skill, api_timeout=3)`

Fetches the public API for the given skill and returns a proxy object.

| Parameter | Description |
|---|---|
| `skill` | The `skill_id` of the target skill |
| `api_timeout` | Seconds to wait for each remote method call (default `3`) |

Returns `None` if the skill is not running or exposes no API methods. Raises `RuntimeError` if `SkillApi.bus` has not been set.

The proxy object has one attribute per exposed method. Calling `proxy.method_name(*args, **kwargs)` sends the corresponding bus message and returns the `result` field of the response. Returns `None` on timeout.

---

## Bus Message Protocol

### Discovery

**Request:** `<skill_id>.public_api` (no data)

**Response:** `<skill_id>.public_api` with data:

```json
{
  "get_temperature": {
    "help": "Return the current temperature for the given city.",
    "type": "my-weather-skill.get_temperature"
  }
}

```

### Method Call

**Request:** `my-weather-skill.get_temperature` with data:

```json
{"args": ["London"], "kwargs": {}}

```

**Response:** same message type with data:

```json
{"result": 18.5}

```

---

## Full Example

### Exposing methods (server skill)

```python
from ovos_workshop.skills.ovos import OVOSSkill
from ovos_workshop.decorators import skill_api_method


class WeatherSkill(OVOSSkill):

    @skill_api_method
    def get_temperature(self, city: str) -> float:
        """Return the current temperature in Celsius for the given city."""
        # … real implementation …
        return 18.5

    @skill_api_method
    def get_forecast(self, city: str, days: int = 3) -> list:
        """Return a weather forecast list for the given city."""
        return [{"day": i, "condition": "sunny"} for i in range(days)]

```

### Calling methods (client skill)

```python
from ovos_workshop.skills.ovos import OVOSSkill
from ovos_workshop.skills.api import SkillApi


class MyClientSkill(OVOSSkill):

    def initialize(self):
        SkillApi.connect_bus(self.bus)

    def handle_ask_weather(self, message):
        weather_api = SkillApi.get("my-weather-skill.author")
        if weather_api is None:
            self.speak("Weather skill is not available.")
            return

        temp = weather_api.get_temperature("London")
        if temp is None:
            self.speak("No response from weather skill.")
            return

        self.speak(f"It is {temp} degrees in London.")

```

---

## Limitations

- Return values must be JSON-serializable.


- The target skill must be running when `SkillApi.get()` is called — it sends a live bus message.


- Method calls time out after `api_timeout` seconds (default `3`). The caller receives `None` on timeout.


- `SkillApi.get()` returns `None` (not an exception) if the target skill is absent or unresponsive.

---

## Related Pages

- [Skill Classes](skill-classes.md) — `OVOSSkill` base class


- [Decorators](skill-classes.md#decorators-quick-reference) — `@skill_api_method` and other decorators


- [Bus Client](bus-client-overview.md) — `MessageBusClient` used internally by `SkillApi`

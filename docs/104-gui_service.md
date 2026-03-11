# GUI Service (ovos-gui)

`ovos-gui` is the GUI orchestration daemon for OpenVoiceOS. It tracks display state,
routes template and page events to all loaded adapter plugins, and manages the namespace
stack that determines what is currently visible on screen. `ovos-gui` does **not** render
anything itself — rendering is delegated to independently installable GUI adapter plugins.

---

## Architecture

The GUI system has two orthogonal abstractions:

1. **Template-based `GUIInterface`** (`ovos-gui-api-client`) — skills call typed methods
   (`show_weather()`, `show_text()`, …) instead of naming framework-specific files.
   Each call emits `gui.value.set` + `gui.page.show` on the OVOS MessageBus with a
   `SYSTEM_*` identifier from the `PageTemplates` enum.

2. **GUI adapter plugin system** (`opm.gui_adapter` entry point) — any number of adapters
   may be installed simultaneously. All loaded adapters receive every template event
   concurrently, enabling multi-modal output (Qt window + terminal + web at once).

```
┌──────────────────────────────────────────────────────────┐
│  Skill (OVOSSkill)                                       │
│                                                          │
│  self.gui.show_weather(22, 18, 26, "Sunny", ...)         │
└────────────────────┬─────────────────────────────────────┘
                     │  gui.value.set  +  gui.page.show
                     │  (MessageBus)
                     ▼
┌──────────────────────────────────────────────────────────┐
│  ovos-gui  —  NamespaceManager                           │
│                                                          │
│  Detects SYSTEM_* in page_names                          │
│  → calls adapter.dispatch_template() on all adapters     │
│  Detects non-SYSTEM_* → legacy path (unchanged)          │
└──────┬───────────────────────────┬───────────────────────┘
       │                           │
       ▼                           ▼
┌─────────────────┐   ┌────────────────────────────────────┐
│ LegacyMycoft    │   │  Any other opm.gui_adapter plugin  │
│ GuiPlugin       │   │  (pyhtmx, TUI, e-ink, …)           │
│                 │   │                                    │
│ Tornado WS      │   │  Implements handle_show_weather()  │
│ server          │   │  however it sees fit               │
│ port 18181      │   └────────────────────────────────────┘
│                 │
│ mycroft.session │
│ .set / list.*   │
│ / gui.list.*    │
│                 │
└────────┬────────┘
         │  WebSocket
         ▼
   Qt5 / Qt6 GUI client
   (mycroft-gui)
   renders bundled QML
```

### Package responsibilities

| Package | Role |
|---|---|
| `ovos-gui-api-client` | `GUIInterface` with 21 typed `show_*()` methods; `PageTemplates` enum; `FillMode`, `ListItem`, `GridItem`, `SelectItem` data types |
| `ovos-workshop` | `OVOSSkill.gui` returns a `GUIInterface` sourced from `ovos-gui-api-client` |
| `ovos-plugin-manager` | `AbstractGUIPlugin` base class; `PluginTypes.GUI_ADAPTER`; `OVOSGUIAdapterFactory` |
| `ovos-gui` | `NamespaceManager` routes SYSTEM_* template events to all loaded adapters; starts adapters at service startup |
| `ovos-legacy-mycroft-gui-plugin` | Adapter that translates templates to the mycroft-gui Qt WebSocket protocol; bundles all 21 QML pages |

---

## Namespaces

GUI state is organized into **namespaces**, each corresponding to a `skill_id`. Each namespace
holds session data (key/value pairs) and a list of pages.

- `NamespaceManager` maintains an ordered **active stack**. The namespace at position 0
  is the one currently displayed.
- Skills may have multiple pages; users can swipe between them within a namespace.
- When a skill clears its namespace (`gui.clear()` / `ovos.gui.screen.close`), the
  namespace is removed from the active stack and the next namespace becomes visible.
- When the stack is empty, the GUI adapter shows an idle/homescreen view.

Example lifecycle:

```
OVOS idle          → homescreen namespace active
"play music"       → music player namespace at position 0
"what time is it"  → clock namespace at position 0; music player at 1
clock times out    → music player namespace at position 0
music ends         → stack empty → homescreen shown
```

> **Note:** GUI does not yet track namespaces per Session. In a future release, remote
> HiveMind satellites will each have their own independent GUI state.

---

## Data Flow for a `show_weather()` Call

```
skill.gui.show_weather(22, 18, 26, "Sunny")
│
├─ gui["current_temp"] = 22   ─┐
├─ gui["min_temp"]     = 18    │  GUIInterface.__setitem__
├─ gui["max_temp"]     = 26    │  (queued, no bus emit yet)
├─ gui["condition"]    = "Sunny" ┘
│
├─ GUIInterface._show_pages(["SYSTEM_weather"])
│    ├─ bus.emit("gui.value.set", {current_temp, min_temp, ...})
│    └─ bus.emit("gui.page.show", {page_names: ["SYSTEM_weather"], ...})
│
└─ NamespaceManager.handle_show_page()
     ├─ page_names[0].startswith("SYSTEM_")  →  True
     ├─ read namespace.data  (updated by handle_set_value just before)
     └─ for adapter in self.adapters:
          adapter.dispatch_template("SYSTEM_weather", skill_id, data)
            └─ adapter.handle_show_weather(skill_id, data)
```

---

## GUI Adapter Plugins

Adapters register under the `opm.gui_adapter` entry point group:

```toml
# pyproject.toml
[project.entry-points."opm.gui_adapter"]
my-adapter = "my_package:MyGUIPlugin"
```

**Base class:** `ovos_plugin_manager.templates.gui.AbstractGUIPlugin`

```python
from ovos_plugin_manager.templates.gui import AbstractGUIPlugin

class MyGUIPlugin(AbstractGUIPlugin):
    def __init__(self, config: dict, bus=None):
        super().__init__(config, bus)
        # start any servers, load resources, etc.
```

### Template handlers

Override any of the 21 methods to render the corresponding template.
All default to **no-ops**:

```python
def handle_show_idle(self, skill_id: str, data: dict) -> None: ...
def handle_show_loading(self, skill_id: str, data: dict) -> None: ...
def handle_show_status(self, skill_id: str, data: dict) -> None: ...
def handle_show_error(self, skill_id: str, data: dict) -> None: ...
def handle_show_text(self, skill_id: str, data: dict) -> None: ...
def handle_show_image(self, skill_id: str, data: dict) -> None: ...
def handle_show_animated_image(self, skill_id: str, data: dict) -> None: ...
def handle_show_list(self, skill_id: str, data: dict) -> None: ...
def handle_show_grid(self, skill_id: str, data: dict) -> None: ...
def handle_show_table(self, skill_id: str, data: dict) -> None: ...
def handle_show_html(self, skill_id: str, data: dict) -> None: ...
def handle_show_url(self, skill_id: str, data: dict) -> None: ...
def handle_show_audio_player(self, skill_id: str, data: dict) -> None: ...
def handle_show_video_player(self, skill_id: str, data: dict) -> None: ...
def handle_show_clock(self, skill_id: str, data: dict) -> None: ...
def handle_show_timer(self, skill_id: str, data: dict) -> None: ...
def handle_show_weather(self, skill_id: str, data: dict) -> None: ...
def handle_show_map(self, skill_id: str, data: dict) -> None: ...
def handle_show_confirm(self, skill_id: str, data: dict) -> None: ...
def handle_show_select(self, skill_id: str, data: dict) -> None: ...
def handle_show_face(self, skill_id: str, data: dict) -> None: ...
```

### Lifecycle hooks

```python
def on_namespace_activated(self, skill_id: str) -> None: ...
```
Called when a skill's namespace moves to the top of the active stack.

```python
def on_namespace_deactivated(self, skill_id: str) -> None: ...
```
Called when a skill clears its namespace or when it is removed by the idle timer.

```python
def on_idle(self) -> None: ...
```
Called when the GUI returns to the idle/resting state with no active skill.

### Session data hook

```python
def on_session_update(self, skill_id: str, data: dict) -> None: ...
```
Called on every `gui.value.set` message — i.e. whenever a skill sets a GUI variable.
Reserved keys (`__from`, `__idle`, `__animations`) are stripped before delivery.
Adapters that maintain live data bindings (e.g. SSE push) can use this for incremental updates.

### Status event hook

```python
def on_status_event(self, event_name: str, data: dict) -> None: ...
```

`NamespaceManager` forwards these core bus events to all adapters:

| `event_name` | Meaning |
|---|---|
| `recognizer_loop:wakeword` | Wake word detected |
| `recognizer_loop:record_begin` | Microphone opened |
| `recognizer_loop:record_end` | Microphone closed |
| `recognizer_loop:utterance` | Utterance recognised |
| `recognizer_loop:recognition_unknown` | STT gave no result |
| `speak` | TTS about to speak |
| `recognizer_loop:audio_output_start` | Audio playback started |
| `recognizer_loop:audio_output_end` | Audio playback ended |
| `recognizer_loop:sleep` | Device going to sleep |
| `recognizer_loop:wake_up` | Device waking up |
| `mycroft.awoken` | Wake-up acknowledged |
| `ovos.utterance.handled` | Intent matched and handled |
| `ovos.utterance.cancelled` | Utterance cancelled |

### Factory

```python
from ovos_plugin_manager.gui_adapter import OVOSGUIAdapterFactory

# Load all installed adapters (used by ovos-gui at startup)
adapters = OVOSGUIAdapterFactory.create_all(config={...}, bus=my_bus)

# Load a single adapter by name
adapter = OVOSGUIAdapterFactory.create("my-adapter", config={}, bus=my_bus)

# Discover installed adapters (without instantiating)
from ovos_plugin_manager.gui_adapter import find_gui_adapter_plugins
plugins = find_gui_adapter_plugins()   # {name: class, ...}
```

---

## Page Templates

Skills display content through 21 pre-defined `PageTemplates` (from `ovos-gui-api-client`).
Custom per-skill QML or HTML is not supported through the template interface.

```python
from ovos_gui_api_client import PageTemplates, GUIInterface, FillMode, ListItem, GridItem, SelectItem
```

### Template Reference

| Template identifier | `GUIInterface` method | Key session data keys |
|---|---|---|
| `SYSTEM_idle` | Reserved — not called by skills | — |
| `SYSTEM_loading` | `gui.show_loading(text="")` | `label` |
| `SYSTEM_status` | `gui.show_status(text, success)` | `label`, `success` |
| `SYSTEM_error` | `gui.show_error(text, detail=None)` | `label`, `detail` |
| `SYSTEM_text` | `gui.show_text(text, title=None)` | `text`, `title` |
| `SYSTEM_image` | `gui.show_image(url, caption, title, fill, background_color)` | `image`, `title`, `caption`, `fill`, `background_color` |
| `SYSTEM_animated_image` | `gui.show_animated_image(...)` or `show_image(..., animated=True)` | same as IMAGE |
| `SYSTEM_list` | `gui.show_list(items, title=None)` | `title`, `items` |
| `SYSTEM_grid` | `gui.show_grid(items, title=None)` | `title`, `items` |
| `SYSTEM_table` | `gui.show_table(columns, rows, title=None)` | `title`, `columns`, `rows` |
| `SYSTEM_html` | `gui.show_html(html, resource_url=None)` | `html`, `resource_url` |
| `SYSTEM_url` | `gui.show_url(url)` | `url` |
| `SYSTEM_audio_player` | `gui.show_audio_player(title, artist, album, image, position, duration, playing)` | `title`, `artist`, `album`, `image`, `position`, `duration`, `playing` |
| `SYSTEM_video_player` | `gui.show_video_player(uri, title, playing)` | `uri`, `title`, `playing` |
| `SYSTEM_clock` | `gui.show_clock()` | — |
| `SYSTEM_timer` | `gui.show_timer(end_time, label, count_up)` | `end_time`, `label`, `count_up` |
| `SYSTEM_weather` | `gui.show_weather(current_temp, min_temp, max_temp, condition, icon, location)` | `current_temp`, `min_temp`, `max_temp`, `condition`, `icon`, `location` |
| `SYSTEM_map` | `gui.show_map(latitude, longitude, zoom, label)` | `latitude`, `longitude`, `zoom`, `label` |
| `SYSTEM_confirm` | `gui.show_confirm(question)` | `question` |
| `SYSTEM_select` | `gui.show_select(items, prompt)` | `prompt`, `items` |
| `SYSTEM_face` | `gui.show_face(awake=True)` | `sleeping` |

### `FillMode` (used by `show_image()`)

```python
class FillMode(str, enum.Enum):
    FIT     = "fit"      # preserve aspect ratio, letterbox
    CROP    = "crop"     # fill area, crop overflow
    STRETCH = "stretch"  # fill area exactly, ignore aspect ratio
```

### `ListItem` / `GridItem` / `SelectItem`

```python
@dataclass
class ListItem:
    title: str
    subtitle: Optional[str] = None
    image: Optional[str] = None   # URL or path

@dataclass
class GridItem:
    image: str            # URL or path (required)
    title: Optional[str] = None

@dataclass
class SelectItem:
    label: str   # text shown to the user
    value: Any   # machine value returned on selection
```

### Confirm and Select interaction

`SYSTEM_confirm` and `SYSTEM_select` are **visual accompaniments** to voice prompts.
Touch shortcuts (if the adapter supports them) fire:

```
<skill_id>.confirm.response  →  {"confirmed": bool}
<skill_id>.select.response   →  {"value": <selected value>}
```

Skills must register handlers for these events **and** handle the spoken reply.

---

## Legacy Qt Adapter (`ovos-legacy-mycroft-gui-plugin`)

**Entry point:** `opm.gui_adapter = ovos_legacy_mycroft_gui:LegacyMycoftGuiPlugin`

This adapter translates the `SYSTEM_*` template API into the mycroft-gui Qt WebSocket
protocol so existing Qt5/Qt6 GUI clients work without any skill-provided QML files.
Rendering is done by 21 system-template QML pages bundled in `mycroft-gui-qt5` and
installed to `$prefix/share/mycroft-gui/system-templates/`.

**Startup actions:**

1. Starts the **Tornado WebSocket server** (default port `18181`) via `create_gui_service(self)`.
2. Registers `mycroft.gui.connected` on the OVOS core bus so Qt clients receive the WebSocket port.
3. Starts **`HomescreenManager`** — replaces `ovos-skill-homescreen` (deprecated). Subscribes
   to datetime, weather, wallpaper, notification, app, widget, and connectivity events and
   re-emits them as `homescreen.data.*` / `homescreen.widget.*` bus messages.

### Template → QML mapping

| Template identifier | Bundled QML file |
|---|---|
| `SYSTEM_idle` | `Idle.qml` |
| `SYSTEM_loading` | `Loading.qml` |
| `SYSTEM_status` | `Status.qml` |
| `SYSTEM_error` | `Error.qml` |
| `SYSTEM_text` | `Text.qml` |
| `SYSTEM_image` | `Image.qml` |
| `SYSTEM_animated_image` | `AnimatedImage.qml` |
| `SYSTEM_list` | `List.qml` |
| `SYSTEM_grid` | `Grid.qml` |
| `SYSTEM_table` | `Table.qml` |
| `SYSTEM_html` | `Html.qml` |
| `SYSTEM_url` | `Url.qml` |
| `SYSTEM_audio_player` | `AudioPlayer.qml` |
| `SYSTEM_video_player` | `VideoPlayer.qml` |
| `SYSTEM_clock` | `Clock.qml` |
| `SYSTEM_timer` | `Timer.qml` |
| `SYSTEM_weather` | `Weather.qml` |
| `SYSTEM_map` | `Map.qml` |
| `SYSTEM_confirm` | `Confirm.qml` |
| `SYSTEM_select` | `Select.qml` |
| `SYSTEM_face` | `Face.qml` |

QML pages are sent as `SYSTEM:<Name>.qml` URIs; the Qt client resolves them via the
`OVOS_SYSTEM_TEMPLATES` env var or the compiled-in default
(`/usr/share/mycroft-gui/system-templates/`).

### HomescreenManager events

| Event emitted | Payload keys |
|---|---|
| `homescreen.data.time` | `time_string`, `date_string`, `weekday_string`, `day_string`, `month_string`, `year_string` |
| `homescreen.data.weather` | `weather_api_enabled`, `weather_code`, `weather_temp` |
| `homescreen.data.wallpaper` | `wallpaper_path`, `selected_wallpaper` |
| `homescreen.data.notifications` | `notification_counter`, `notification_model` |
| `homescreen.data.apps` | `applications_model` |
| `homescreen.data.examples` | `skill_examples`, `skill_info_enabled`, `skill_info_prefix` |
| `homescreen.data.connectivity` | `system_connectivity` |
| `homescreen.widget.timer` | `count`, widget fields |
| `homescreen.widget.alarm` | `count`, widget fields |
| `homescreen.widget.media` | `enabled`, `widget`, `state` |

---

## Configuration

```json
{
  "gui": {
    "adapters": {
      "ovos-legacy-mycroft-gui": {
        "base_port": 18181,
        "default_qt_version": 5
      },
      "my-custom-adapter": {
        "port": 9090
      }
    }
  }
}
```

| Key | Description |
|---|---|
| `gui.adapters.<name>` | Per-adapter configuration dict passed as `config` to `AbstractGUIPlugin.__init__` |
| `base_port` | TCP port the legacy adapter's Tornado WebSocket server listens on (default: `18181`) |
| `default_qt_version` | Qt version assumed when a client does not declare its framework (default: `5`) |

---

## Backward Compatibility

- Non-`SYSTEM_*` page names in `gui.page.show` go through the unchanged legacy namespace
  management path inside `NamespaceManager` — existing Qt skills with custom QML files
  continue working without modification.
- The `LegacyMycoftGuiPlugin` intercepts all template events and translates them to Qt
  WebSocket messages, so existing Qt deployments work without modifying skills.
- Headless deployments with no adapter installed — all `GUIInterface` calls are silently
  no-ops because `NamespaceManager.adapters` is empty.

---

## Minimal Adapter Example

```python
# my_adapter/__init__.py
from ovos_plugin_manager.templates.gui import AbstractGUIPlugin

class MyGUIPlugin(AbstractGUIPlugin):

    def handle_show_text(self, skill_id: str, data: dict) -> None:
        title = data.get("title", "")
        text = data.get("text", "")
        print(f"[{skill_id}] {title}\n{text}")

    def handle_show_weather(self, skill_id: str, data: dict) -> None:
        print(
            f"[{skill_id}] {data['current_temp']}° "
            f"{data['condition']} @ {data.get('location', '')}"
        )

    def on_namespace_deactivated(self, skill_id: str) -> None:
        print(f"[{skill_id}] screen cleared")
```

```toml
# pyproject.toml
[project.entry-points."opm.gui_adapter"]
my-adapter = "my_adapter:MyGUIPlugin"
```

Install, restart `ovos-gui`, and the adapter is discovered and loaded automatically
alongside any other installed adapters.

---

See [GUI Protocol](701-gui_protocol.md) for the full Qt WebSocket wire protocol used by
`LegacyMycoftGuiPlugin`. See [OVOS Shell](702-ovos-shell.md) for the production Qt5/Kirigami
shell application.

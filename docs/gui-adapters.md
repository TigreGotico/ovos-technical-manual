# GUI Adapter Plugins

GUI adapter plugins are the rendering backends for `ovos-gui`.  Each adapter
receives template events from `NamespaceManager` and translates them into
whatever protocol or framework it needs (Qt WebSocket, HTTP+SSE, curses, etc.).

Multiple adapters can be installed simultaneously — every template event is
dispatched to **all** loaded adapters concurrently, enabling multi-modal rendering.


## Entry point

Adapters are discovered via the `opm.gui_adapter` entry point group:

```toml
[project.entry-points."opm.gui_adapter"]
"my-adapter" = "my_package:MyGUIPlugin"

```

The class must extend `AbstractGUIPlugin` from `ovos-plugin-manager`.


## `AbstractGUIPlugin`

```python
from ovos_plugin_manager.templates.gui import AbstractGUIPlugin

class MyGUIPlugin(AbstractGUIPlugin):
    def __init__(self, config: dict, bus=None):
        super().__init__(config, bus)
        # start your server / rendering pipeline here

```

### 21 template handlers

Override any of the following methods to render a template.
Each receives `skill_id: str` (the namespace) and `data: dict` (current session data).

| Method | Template | Key data keys |
|---|---|---|
| `handle_show_idle` | `SYSTEM_idle` | — |
| `handle_show_loading` | `SYSTEM_loading` | `label` |
| `handle_show_status` | `SYSTEM_status` | `label`, `success` |
| `handle_show_error` | `SYSTEM_error` | `label`, `detail` |
| `handle_show_text` | `SYSTEM_text` | `text`, `title` |
| `handle_show_image` | `SYSTEM_image` | `image`, `title`, `caption`, `fill` |
| `handle_show_animated_image` | `SYSTEM_animated_image` | same as image |
| `handle_show_html` | `SYSTEM_html` | `html` |
| `handle_show_url` | `SYSTEM_url` | `url` |
| `handle_show_list` | `SYSTEM_list` | `title`, `items` |
| `handle_show_grid` | `SYSTEM_grid` | `title`, `items` |
| `handle_show_table` | `SYSTEM_table` | `title`, `columns`, `rows` |
| `handle_show_audio_player` | `SYSTEM_audio_player` | `title`, `artist`, `album`, `image`, `playing`, `position`, `duration` |
| `handle_show_video_player` | `SYSTEM_video_player` | `uri`, `title`, `playing` |
| `handle_show_clock` | `SYSTEM_clock` | — |
| `handle_show_timer` | `SYSTEM_timer` | `end_time`, `label`, `count_up` |
| `handle_show_weather` | `SYSTEM_weather` | `current_temp`, `min_temp`, `max_temp`, `condition`, `icon`, `location` |
| `handle_show_map` | `SYSTEM_map` | `latitude`, `longitude`, `zoom`, `label` |
| `handle_show_confirm` | `SYSTEM_confirm` | `question` |
| `handle_show_select` | `SYSTEM_select` | `prompt`, `items` |
| `handle_show_face` | `SYSTEM_face` | `sleeping` |

### Lifecycle hooks

```python
def on_namespace_activated(self, skill_id: str) -> None:
    """Called when a namespace moves to the top of the display stack."""

def on_namespace_deactivated(self, skill_id: str) -> None:
    """Called when a namespace is removed from the display stack."""

def on_session_update(self, skill_id: str, data: dict) -> None:
    """Called whenever skill session data changes (e.g. gui['key'] = value)."""

def on_status_event(self, event_name: str, data: dict) -> None:
    """Called for system status events (wakeword, utterance handled, etc.)."""

```

### Connection status

Implement `any_client_connected() -> bool` to participate in
`gui.status.request` responses:

```python
def any_client_connected(self) -> bool:
    return len(self._my_connected_clients) > 0

```


## Built-in adapters

| Package | Entry point name | Description |
|---|---|---|
| `ovos-legacy-mycroft-gui-plugin` | `ovos-legacy-mycroft-gui` | Tornado WebSocket → Qt / mycroft-gui clients |
| `ovos-gui-plugin-pyhtmx` | `ovos-gui-plugin-pyhtmx` | FastAPI / SSE → browser (HTMX) |


## Writing a custom adapter

```python
from ovos_plugin_manager.templates.gui import AbstractGUIPlugin

class TerminalGUIPlugin(AbstractGUIPlugin):
    """Render OVOS GUI templates in the terminal using curses."""

    def __init__(self, config, bus=None):
        super().__init__(config, bus)
        self._start_curses()

    def handle_show_text(self, skill_id, data):
        self._render(data.get("title", ""), data.get("text", ""))

    def handle_show_weather(self, skill_id, data):
        self._render(
            data.get("location", ""),
            f"{data['current_temp']}° — {data['condition']}",
        )

    # ... implement other templates as needed ...

```

Register in `pyproject.toml`:

```toml
[project.entry-points."opm.gui_adapter"]
"my-terminal-gui" = "my_package:TerminalGUIPlugin"

```


## Configuration

Adapter configuration lives under `gui.adapters.<entry-point-name>` in
`mycroft.conf`:

```json
{
  "gui": {
    "adapters": {
      "ovos-gui-plugin-pyhtmx": {
        "host": "0.0.0.0",
        "port": 8080
      }
    }
  }
}

```


## Multi-modal rendering

When two adapters are installed (e.g. legacy Qt and PyHTMX), every template
event is dispatched to both:

```
Skill.show_weather(…)
       ↓
NamespaceManager._dispatch_template_to_adapters("SYSTEM_weather", skill_id, data)
       ├──→ LegacyMycoftGuiPlugin.handle_show_weather(…)   → Qt client
       └──→ PyHTMXGUIPlugin.handle_show_weather(…)          → browser

```

Both displays update simultaneously and independently.

# GUI Adapter Plugins

!!! warning "Upcoming — unreleased GUI rework"
    This whole page describes the **GUI-rendering rework**, which is **not yet released**.
    Nothing here is available on a stable install. It is implemented across these
    branches:

    - `ovos-plugin-manager` @ `gui` — `AbstractGUIPlugin`, `opm.gui_adapter` plugin type
    - `ovos-gui` @ `feat/gui-rework-landing` — the router that dispatches to adapters
    - `ovos-gui-api-client` @ `dev` (PyPI `0.0.2a1`, pre-release) — `PageTemplates` + the
      template-based `GUIInterface`
    - `ovos-legacy-mycroft-gui-plugin` @ `feat/session-id-contract` — the Qt adapter
    - `pyhtmx-gui-client` @ `feat/gui-adapter` — the browser/HTMX adapter

    The per-call routing argument is still in flux: the `ovos-plugin-manager` base class
    currently names it `site_id`, while the `ovos-gui` router and the latest legacy-plugin
    branch pass `session_id`. Treat the signatures below as approximate until the rework
    lands on `dev`.

In the rework, `ovos-gui` no longer renders or talks to Qt clients directly. It becomes a
router that dispatches each display event to every installed **GUI adapter plugin**. Each
adapter translates template events into whatever protocol it needs (Qt WebSocket,
HTTP+SSE, curses, …). Multiple adapters can run at once, enabling multi-modal output.

## Entry point

Adapters are discovered via the `opm.gui_adapter` entry-point group:

```toml
[project.entry-points."opm.gui_adapter"]
"my-adapter" = "my_package:MyGUIPlugin"
```

The class extends `AbstractGUIPlugin` from `ovos_plugin_manager.templates.gui`.

## `AbstractGUIPlugin`

```python
from ovos_plugin_manager.templates.gui import AbstractGUIPlugin

class MyGUIPlugin(AbstractGUIPlugin):
    def __init__(self, config: dict, bus=None):
        super().__init__(config, bus)
        # start your server / rendering pipeline here
```

### Template handlers

Override any of the following methods to render a template. Each receives `skill_id: str`
(the namespace), `data: dict` (current session data), and a routing id
(`session_id`/`site_id`, default `"default"`). All default to no-ops, so partial
implementations are valid.

| Method | Template | Key data keys |
|---|---|---|
| `handle_show_idle` | `SYSTEM_idle` | — |
| `handle_show_loading` | `SYSTEM_loading` | `label` |
| `handle_show_status` | `SYSTEM_status` | `label`, `success` |
| `handle_show_error` | `SYSTEM_error` | `label`, `detail` |
| `handle_show_text` | `SYSTEM_text` | `text`, `title` |
| `handle_show_image` | `SYSTEM_image` | `image`, `title`, `caption`, `fill` |
| `handle_show_animated_image` | `SYSTEM_animated_image` | same as image |
| `handle_show_list` | `SYSTEM_list` | `title`, `items` |
| `handle_show_grid` | `SYSTEM_grid` | `title`, `items` |
| `handle_show_table` | `SYSTEM_table` | `title`, `columns`, `rows` |
| `handle_show_html` | `SYSTEM_html` | `html` |
| `handle_show_url` | `SYSTEM_url` | `url` |
| `handle_show_audio_player` | `SYSTEM_audio_player` | `title`, `artist`, `album`, `image`, `playing`, `position`, `duration` |
| `handle_show_video_player` | `SYSTEM_video_player` | `uri`, `title`, `playing` |
| `handle_show_media_player` | `SYSTEM_media_player` | media fields |
| `handle_show_clock` | `SYSTEM_clock` | — |
| `handle_show_timer` | `SYSTEM_timer` | `end_time`, `label`, `count_up` |
| `handle_show_weather` | `SYSTEM_weather` | `current_temp`, `min_temp`, `max_temp`, `condition`, `icon`, `location` |
| `handle_show_map` | `SYSTEM_map` | `latitude`, `longitude`, `zoom`, `label` |
| `handle_show_confirm` | `SYSTEM_confirm` | `question` |
| `handle_show_select` | `SYSTEM_select` | `prompt`, `items` |
| `handle_show_face` | `SYSTEM_face` | `sleeping` |

### Lifecycle hooks

```python
def on_namespace_activated(self, skill_id: str, site_id: str = "default") -> None:
    """Called when a namespace moves to the top of the display stack."""

def on_namespace_deactivated(self, skill_id: str, site_id: str = "default") -> None:
    """Called when a namespace is removed from the display stack."""

def on_idle(self) -> None:
    """Called when the display returns to the idle/resting state."""

def on_session_update(self, skill_id: str, data: dict, ...) -> None:
    """Called whenever skill session data changes (e.g. gui['key'] = value)."""

def on_status_event(self, event_name: str, data: dict) -> None:
    """Called for system status events (wakeword, utterance handled, etc.)."""
```

### Dispatch

The router calls `adapter.dispatch_template(template, skill_id, data, ...)`, which maps the
`SYSTEM_*` template to the matching `handle_show_*` method. Adapters normally override the
individual `handle_show_*` methods rather than `dispatch_template` itself.

### Connection status

Implement `any_client_connected() -> bool` to participate in `gui.status.request`
responses:

```python
def any_client_connected(self) -> bool:
    return len(self._my_connected_clients) > 0
```

## Built-in adapters

| Package | Entry-point name | Class | Description |
|---|---|---|---|
| `ovos-legacy-mycroft-gui-plugin` | `ovos-legacy-mycroft-gui` | `LegacyMycoftGuiPlugin` | Tornado WebSocket → Qt / mycroft-gui clients; also runs `HomescreenManager` |
| `pyhtmx-gui-client` | `ovos-gui-plugin-pyhtmx` | HTMX adapter | FastAPI / SSE → browser (HTMX) |

## Writing a custom adapter

```python
from ovos_plugin_manager.templates.gui import AbstractGUIPlugin

class TerminalGUIPlugin(AbstractGUIPlugin):
    """Render OVOS GUI templates in the terminal."""

    def __init__(self, config, bus=None):
        super().__init__(config, bus)

    def handle_show_text(self, skill_id, data, session_id="default"):
        print(data.get("title", ""))
        print(data.get("text", ""))

    def handle_show_weather(self, skill_id, data, session_id="default"):
        print(data.get("location", ""),
              f"{data['current_temp']}° — {data['condition']}")
```

Register in `pyproject.toml`:

```toml
[project.entry-points."opm.gui_adapter"]
"my-terminal-gui" = "my_package:TerminalGUIPlugin"
```

## Configuration

Adapter configuration lives under `gui.adapters.<entry-point-name>` in `mycroft.conf` and
is passed as the `config` dict to the adapter's `__init__`:

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

With two adapters installed (e.g. legacy Qt and pyhtmx), every display event is dispatched
to both:

```
self.gui.show_weather(…)
       ↓
NamespaceManager._dispatch_template_to_adapters("SYSTEM_weather", skill_id, data, session_id)
       ├──→ LegacyMycoftGuiPlugin.handle_show_weather(…)   → Qt client
       └──→ pyhtmx adapter.handle_show_weather(…)           → browser
```

Both displays update simultaneously and independently.

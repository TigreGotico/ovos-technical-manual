# GUI Adapter Plugins

!!! abstract "In a nutshell"
    This page is for developers and describes the **new, not-yet-finished** way OVOS will draw things on a screen — the planned replacement for the old, deprecated GUI. The idea: instead of OVOS talking to one kind of screen directly, it sends a generic "show this weather card" message and small plug-ins called **adapters** translate that into whatever the actual display is (a touchscreen, a web browser, even a terminal). Several adapters can run at once, so the same content shows on multiple screens. This is upcoming work, not the everyday path today — see the [GUI Protocol](gui-protocol.md) for the current legacy screen and the [Glossary](glossary.md) for terms.

!!! info "This is the GUI replacement, still in progress"
    This page documents the **in-progress replacement** for the deprecated
    [legacy GUI](gui-service.md). It is **not yet usable**. Until it ships, there is no
    generally usable OVOS GUI; **Mark 2** devices keep a screen via the legacy stack that the
    [`ovos-installer`](ovos-installer.md) sets up.

!!! warning "Upcoming — unreleased"
    This whole page describes the **GUI-rendering rework**, which is **not yet released**.
    Nothing here is available on a stable install, and the pieces are at different stages.
    Tracked in [ovos-plugin-manager#377](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/377) (`AbstractGUIPlugin`),
    [ovos-gui#112](https://github.com/OpenVoiceOS/ovos-gui/pull/112) (adapter/template rework landing),
    [ovos-gui#117](https://github.com/OpenVoiceOS/ovos-gui/pull/117) (OVOS-GUI-1 service conformance),
    [ovos-bus-client#238](https://github.com/OpenVoiceOS/ovos-bus-client/pull/238) (GUI-1-conformant wire shapes), and
    [ovos-legacy-mycroft-gui-plugin#3](https://github.com/OpenVoiceOS/ovos-legacy-mycroft-gui-plugin/pull/3) (adapter conforms to the session_id-only contract):

    - `ovos-gui-api-client` — a template-based `GUIInterface` already exists and works today.
    - `ovos-legacy-mycroft-gui-plugin` and `ovos-gui-plugin-pyhtmx` (repo `pyhtmx-gui-client`)
      already implement the adapter-side contract described below (an `AbstractGUIPlugin`
      subclass registered under `opm.gui_adapter`) — but that base class does not exist yet in
      any released `ovos-plugin-manager`, and `ovos-gui` does not yet contain the router that
      would dispatch events to these adapters. These plugins are therefore built ahead of their
      own dependency.
    - The formal contract is specified by
      [OVOS-GUI-1](https://github.com/OpenVoiceOS/architecture/blob/dev/gui-1.md), an
      [architecture spec](architecture-specs.md). The spec deliberately leaves the exact
      entry-point group name and method signatures **non-normative** — it gives them only as an
      illustrative example. The names below (`AbstractGUIPlugin`, `handle_show_*`,
      `opm.gui_adapter`) are what the real adapter plugins linked above have already
      standardized on, which is why this page uses them.

    Per OVOS-GUI-1, the sole per-event routing key for the adapter contract is **`session_id`**
    — there is no separate site/room/location dimension; a shared/multi-room screen is expressed
    by its clients sharing one `session_id`.

    !!! note "Client-side `site_id` still exists (in flux)"
        The Qt6 client rework branch (`mycroft-gui-qt6`) still ships a separate **`site_id`**
        dimension (`--site-id` flag, `MYCROFT_SITE_ID` env var) for multi-site setups. So at the
        *client* layer site_id is not yet gone, even though the OVOS-GUI-1 *adapter contract*
        collapses routing to `session_id`. The two layers may still be reconciled.

In the rework, `ovos-gui` no longer renders or talks to Qt clients directly. It becomes a
router that dispatches each display event to every installed **GUI adapter plugin**. Each
adapter translates template events into whatever protocol it needs (Qt WebSocket,
HTTP+SSE, curses, …). Multiple adapters can run at once, enabling multi-modal output.

!!! info "Adapters can add their own extra functionality (optional)"
    Beyond rendering the standard display templates, a GUI adapter plugin **may define its own
    extra bus event listeners**, exposing additional, **optional** capabilities that skills can
    choose to use. Examples include **Mark 1 events / faceplate control** (the
    [Mark 1](mark1.md) faceplate becomes such an adapter), **home screens**, and **custom QML**.
    These are opt-in: a skill works without them, but can adopt the extra functionality offered
    by whichever adapter(s) are installed.

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
(the namespace), `data: dict` (current session data), and `session_id: str` (the routing
id, default `"default"`). All default to no-ops, so partial implementations are valid.

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
| `handle_show_ocp_now_playing` | `SYSTEM_ocp_now_playing` | media fields |
| `handle_show_ocp_search` | `SYSTEM_ocp_search` | search-result fields |
| `handle_show_ocp_playlist` | `SYSTEM_ocp_playlist` | playlist fields |

### Lifecycle hooks

```python
def on_namespace_activated(self, skill_id: str, session_id: str = "default") -> None:
    """Called when a namespace moves to the top of the display stack."""

def on_namespace_deactivated(self, skill_id: str, session_id: str = "default") -> None:
    """Called when a namespace is removed from the display stack."""

def on_idle(self) -> None:
    """Called when the display returns to the idle/resting state."""

def on_session_update(self, skill_id: str, data: dict, session_id: str = "default") -> None:
    """Called whenever skill session data changes (e.g. gui['key'] = value)."""

def on_status_event(self, event_name: str, data: dict, session_id: str = "default") -> None:
    """Called for system status events (wakeword, utterance handled, etc.)."""
```

### Dispatch

The (not-yet-built) router is expected to map each `SYSTEM_*` template name to the matching
`handle_show_*` method — the naming convention `handle_show_<template suffix>` is already fixed
by the adapter plugins that implement this contract today. An adapter overrides only the
individual `handle_show_*` methods it cares about; unimplemented ones default to no-ops.

### Connection status

The legacy [`gui.status.request`](gui-protocol.md) bus message already exists today and answers
whether any display is connected. An adapter is expected to optionally provide an
`any_client_connected() -> bool` method so a future router can fold it into that response; since
the base class and router are not yet built, treat the exact hook-up (duck-typing or otherwise)
as illustrative:

```python
def any_client_connected(self) -> bool:
    return len(self._my_connected_clients) > 0
```

## Built-in adapters

| Repo | PyPI package | Entry-point name | Class | Description |
|---|---|---|---|---|
| `ovos-legacy-mycroft-gui-plugin` | `ovos-legacy-mycroft-gui-plugin` | `ovos-legacy-mycroft-gui` | `LegacyMycoftGuiPlugin` | Tornado WebSocket → Qt / mycroft-gui clients; also runs `HomescreenManager` |
| `pyhtmx-gui-client` | `ovos-gui-plugin-pyhtmx` | `ovos-gui-plugin-pyhtmx` | `PyHTMXGUIPlugin` | Browser adapter (HTMX) |

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

Adapter configuration is expected to live under a `gui.adapters.<entry-point-name>` key in
[`mycroft.conf`](config.md), following the existing `get_plugin_config()` convention used by
other OPM plugin types, and to be passed as the `config` dict to the adapter's `__init__`. This
exact key path is not yet fixed by any released code — treat it as illustrative:

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
ovos-gui router, fanned out to every installed opm.gui_adapter plugin
       ├──→ LegacyMycoftGuiPlugin.handle_show_weather(…)   → Qt client
       └──→ PyHTMXGUIPlugin.handle_show_weather(…)          → browser
```

Both displays update simultaneously and independently.

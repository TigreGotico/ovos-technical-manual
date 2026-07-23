# GUI Service (ovos-gui)

!!! danger "The OVOS GUI is deprecated — assume it is not usable today"
    The current **"legacy" OVOS GUI** stack is **deprecated** and should be treated as
    **broken**: **there is no generally usable OVOS GUI right now**. A ground-up replacement
    (the [GUI rework](gui-adapters.md), spec **OVOS-GUI-1**) is actively being built but is
    **not yet ready**.

    On **Mark 2** devices the [`ovos-installer`](ovos-installer.md) still sets up this legacy
    GUI, so those devices keep a screen until the replacement lands. Everything below
    documents the legacy stack — kept for Mark 2 maintenance and reference, **not recommended
    for new work**.

!!! abstract "In a nutshell"
    `ovos-gui` is the part of OpenVoiceOS that decides what shows up on a screen — text, images, a music player, or an idle home screen. Skills never draw to the display themselves; they send a request to this service, which keeps track of what each skill wants shown and passes it on to whatever screen is connected. Think of it as a stage manager that decides which scene is in front of the audience at any moment. To learn more, see the [Home Screen](homescreen.md) and the [Glossary](glossary.md).

??? info "📐 Formal specification"
    The **forward** model for the display layer is
    **[OVOS-GUI-1 — GUI Display Subsystem](https://github.com/OpenVoiceOS/architecture/blob/dev/gui-1.md)**.
    It reframes the GUI as a *voice-OS peripheral*: an application declares
    **what** to show using a **closed `SYSTEM_*` template vocabulary**, and any
    number of interchangeable **render backends** decide **how** to draw it
    (pixels, a character grid, a synthesized face…), each routed solely by the
    message's `session_id`. The `ovos-gui` daemon described on this page is the
    current ("legacy") implementation; read GUI-1 for the target contract this
    subsystem is converging on. For the full set see the
    **[spec index](architecture-specs.md)**.

`ovos-gui` is the GUI orchestration daemon for OpenVoiceOS. It tracks display state and
manages the **namespace stack** that determines what is currently visible on screen.

## How a skill draws on screen (beginner view)

A skill never talks to the display directly. It calls methods on `self.gui` (a
`GUIInterface`), which emit messages on the OVOS [messagebus](bus-service.md). `ovos-gui`
receives those messages, keeps track of what each skill wants shown, and forwards the
result to whatever GUI client is connected (typically [ovos-shell](ovos-shell.md) running
the Qt/[Kirigami](qt5-gui.md) UI).

A minimal example — display some text:

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler

class HelloSkill(OVOSSkill):
    @intent_handler("hello.intent")
    def handle_hello(self, message):
        self.speak("Here is your message")
        self.gui.show_text("Hello from OVOS", title="Greeting")
```

`show_text()` writes the text into the skill's namespace and tells the GUI client to load
the built-in text page. When the skill is done, the namespace is removed and the screen
returns to the previous view or the idle/homescreen.

---

## Architecture (current)

`self.gui` is a `SkillGUI` (subclass of `GUIInterface` from
`ovos_bus_client.apis.gui`). It emits these bus messages:

| Bus message | Emitted by | Purpose |
|---|---|---|
| `gui.value.set` | `GUIInterface.__setitem__` / `_sync_data()` | Write session variables into the skill's namespace |
| `gui.page.show` | `GUIInterface.show_page()` / `show_pages()` | Request one or more QML pages be shown |
| `gui.page.delete` / `gui.page.delete.all` | `remove_page()` / `remove_all_pages()` | Remove pages from the namespace |
| `gui.event.send` | `send_event()` | Send a custom event into the namespace |
| `gui.clear.namespace` | `clear()` | Remove the skill's namespace from the active stack |

`ovos-gui` itself **is** the GUI WebSocket server. `ovos_gui/bus.py` runs a
[Tornado](https://www.tornadoweb.org/) WebSocket endpoint (default port `18181`) that Qt
clients connect to. `NamespaceManager` (`ovos_gui/namespace.py`) translates the bus
messages above into the Qt wire protocol (`mycroft.session.*`, `mycroft.gui.list.*`) and
pushes them to every connected client. See [GUI Protocol](gui-protocol.md) for the wire
format.

```text
┌──────────────────────────────────────────────────────────┐
│  Skill (OVOSSkill)                                        │
│  self.gui.show_text("Hello", title="Greeting")           │
└────────────────────┬─────────────────────────────────────┘
                     │  gui.value.set  +  gui.page.show
                     │  (OVOS MessageBus)
                     ▼
┌──────────────────────────────────────────────────────────┐
│  ovos-gui  —  NamespaceManager (namespace.py)            │
│              GUIWebsocketHandler (bus.py, Tornado)        │
│  Maintains the active namespace stack and per-namespace  │
│  session data + page list; mirrors it to every client    │
│  as mycroft.session.* / mycroft.gui.list.* messages      │
└────────────────────┬─────────────────────────────────────┘
                     │  WebSocket (port 18181)
                     ▼
            Qt5 / Qt6 GUI client (mycroft-gui / ovos-shell)
            resolves and renders the requested QML pages
```

### `GUIInterface` display methods

`self.gui` exposes these display methods (from `ovos_bus_client.apis.gui.GUIInterface`):

| Method | QML page shown |
|---|---|
| `show_page(name, ...)` / `show_pages(names, ...)` | arbitrary page resource(s) |
| `show_text(text, title=None, ...)` | `SYSTEM_TextFrame` |
| `show_image(url, caption=None, title=None, fill=None, ...)` | `SYSTEM_ImageFrame` |
| `show_animated_image(url, ...)` | `SYSTEM_AnimatedImageFrame` |
| `show_html(html, resource_url=None, ...)` | `SYSTEM_HtmlFrame` |
| `show_url(url, ...)` | `SYSTEM_UrlFrame` |
| `show_input_box(title=None, ...)` | `SYSTEM_InputBox` |
| `show_face(awake=True, ...)` | `SYSTEM_Face` |
| `show_loading_animation(text, ...)` | `SYSTEM_Loading` |
| `show_status_animation(text, success, ...)` | `SYSTEM_Status` |
| `show_notification(content, ...)` / `show_controlled_notification(content, ...)` | notification overlay |

Skills may also ship their own `.qml` pages and call `show_page("my_page.qml")`. Page
resources are resolved by the Qt client (see [GUI Protocol](gui-protocol.md)).

---

## Namespaces

GUI state is organized into **namespaces**, each corresponding to a `skill_id`. Each
namespace holds session data (key/value pairs) and an ordered list of displayed pages.

- `NamespaceManager` maintains an ordered **active stack** (mirrored to clients as the
  reserved `mycroft.system.active_skills` namespace). The namespace at position 0 is the
  one currently displayed.

- Skills display pages via `gui.show_*()`. Users interact with the rendered page.

- When a skill clears its namespace (`gui.clear()` → `gui.clear.namespace`), the namespace
  is removed from the active stack and the next namespace becomes visible.

- When the stack is empty, the GUI client shows its idle/homescreen view.

Example lifecycle:

```text
OVOS idle          → homescreen / idle view
"play music"       → music player namespace at position 0
"what time is it"  → clock skill namespace at position 0; music player at 1
clock times out    → music player namespace at position 0
music ends         → stack empty → idle view shown
```

> **Note:** GUI does not yet track namespaces per [Session](session.md). Today all clients
> share one global display stack.

---

## Configuration

The GUI WebSocket server is configured under `gui_websocket` in `mycroft.conf`:

```json
{
  "gui_websocket": {
    "host": "0.0.0.0",
    "base_port": 18181,
    "route": "/gui"
  }
}
```

| Key | Description |
|---|---|
| `host` | Interface the Tornado WebSocket server binds to |
| `base_port` | TCP port Qt clients connect to (default: `18181`) |
| `route` | WebSocket route path (default: `/gui`) |

---

!!! warning "Upcoming — unreleased"
    The following describes a **plugin-based rendering rework** that is **not yet
    released** and not present on any published package. It is specified by the
    [OVOS-GUI-1](https://github.com/OpenVoiceOS/architecture/blob/dev/gui-1.md) spec
    and implemented in `ovos-gui`, with adapters in
    `ovos-legacy-mycroft-gui-plugin` and `pyhtmx-gui-client`.
    Do not rely on any of this on a stable install. Tracked in
    [ovos-plugin-manager#377](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/377),
    [ovos-gui#112](https://github.com/OpenVoiceOS/ovos-gui/pull/112),
    [ovos-gui#117](https://github.com/OpenVoiceOS/ovos-gui/pull/117), and
    [ovos-legacy-mycroft-gui-plugin#3](https://github.com/OpenVoiceOS/ovos-legacy-mycroft-gui-plugin/pull/3).

    **What changes.** Per OVOS-GUI-1, `ovos-gui` becomes a **pure state-and-dispatch hub**:
    it runs **no WebSocket server** and renders nothing. It loads every installed
    **GUI adapter plugin** (`opm.gui_adapter` entry-point group) via
    `OVOSGUIAdapterFactory.create_all(bus, config)` and fans each display event out to all
    of them concurrently, enabling multi-modal output (Qt + browser + terminal at once). A
    headless device with zero adapters degrades to a no-op dispatch — it never crashes. The
    Qt WebSocket server moves into the `ovos-legacy-mycroft-gui-plugin` adapter.

    **Templates instead of QML page names.** Skills display one of a **closed vocabulary of
    22 `SYSTEM_*` templates** (`SYSTEM_weather`, `SYSTEM_text`, `SYSTEM_list`, …) defined by
    the spec. Custom QML page names are no longer accepted by the router. The template-based
    `GUIInterface` moves into the standalone `ovos-gui-api-client` package (separate from the
    current `ovos_bus_client.apis.gui.GUIInterface`).

    **Addressing is `session_id`-only.** The spec drops any separate site/room/location
    dimension: a GUI message is routed solely by its `session_id`, and a shared/multi-room
    screen is expressed by clients sharing one `session_id`. This is the intended target
    design, not a regression.

    See [GUI Adapter Plugins](gui-adapters.md) for the adapter API and the full template
    list, and the Upcoming section of [GUI Protocol](gui-protocol.md) for the routing
    messages.

---

See [GUI Protocol](gui-protocol.md) for the full Qt WebSocket wire protocol. See
[OVOS Shell](ovos-shell.md) for the production Qt5/[Kirigami](qt5-gui.md) shell
application, and [Home Screen](homescreen.md) for idle-screen skills.

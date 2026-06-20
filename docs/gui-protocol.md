# GUI Protocol

The `ovos-gui` service exposes two communication channels:

1. **OVOS [MessageBus](bus-service.md)** — used by skills and core components to set GUI state.


2. **Qt WebSocket** (default port 18181, served by `ovos-gui` itself) — used by Qt5/Qt6
   GUI clients (`mycroft-gui-qt5`, `ovos-shell`) to receive display commands and send
   back user interaction events.

The Qt WebSocket server runs inside `ovos-gui` (`ovos_gui/bus.py`, Tornado). The
client-side transport is implemented in the
[mycroft-gui-qt5](https://github.com/OpenVoiceOS/mycroft-gui-qt5) library.

![imagem](https://github.com/OpenVoiceOS/ovos-technical-manual/assets/33701864/92e73af7-f7d2-4aa3-a294-77f87aa22390)

---

## OVOS MessageBus Messages

### Messages emitted by skills (via `GUIInterface`)

#### `gui.value.set`

Sent by `GUIInterface.__setitem__` / `_sync_data()` to write session variables into
the skill's namespace.

```json
{
  "type": "gui.value.set",
  "data": {
    "current_temp": 22,
    "condition": "Sunny",
    "__from": "ovos-skill-weather",
    "__idle": null
  }
}

```

| Field | Description |
|---|---|
| `__from` | [Skill](skill-design-guidelines.md) ID (namespace owner) |
| `__idle` | Idle timeout in seconds, or `null` |
| All other keys | Skill-defined session variables |

`NamespaceManager` stores all keys in `namespace.data`. The reserved keys
(`RESERVED_KEYS = ['__from', '__idle']`) are stripped before the values are mirrored to
clients as `mycroft.session.set`.

---

#### `gui.page.show`

Sent by `GUIInterface.show_page()` / `show_pages()` to request one or more pages be shown.

```json
{
  "type": "gui.page.show",
  "data": {
    "page_names": ["SYSTEM_TextFrame"],
    "index": 0,
    "__from": "ovos-skill-weather",
    "__idle": null
  }
}

```

`page_names` are page resource identifiers. The built-in pages use `SYSTEM_*` names (e.g.
`SYSTEM_TextFrame`, `SYSTEM_ImageFrame`, `SYSTEM_Face`); skills may also ship their own
`.qml` pages and reference them by name. `NamespaceManager` records the page list against
the namespace and mirrors it to clients as `mycroft.gui.list.insert` with the resolved
page URIs.

---

#### `gui.page.delete`

Removes a specific page from a skill's namespace page list.

```json
{
  "type": "gui.page.delete",
  "data": {
    "page_names": ["Weather.qml"],
    "__from": "ovos-skill-weather"
  }
}

```

---

#### `gui.page.delete.all`

Clears all pages from a skill's namespace.

```json
{
  "type": "gui.page.delete.all",
  "data": {
    "__from": "ovos-skill-weather"
  }
}

```

---

#### `gui.event.send`

Sends an arbitrary event into a skill's namespace. `NamespaceManager` forwards it to
clients as `mycroft.events.triggered` with `namespace = __from`.

```json
{
  "type": "gui.event.send",
  "data": {
    "__from": "ovos-skill-weather",
    "event_name": "my.gui.event",
    "params": {"item": 3}
  }
}

```

---

### Messages consumed by `NamespaceManager` (from skills / core)

#### `gui.clear.namespace`

Removes a skill's namespace from the active display stack and discards its
[Session](session.md) data.

```json
{
  "type": "gui.clear.namespace",
  "data": {
    "__from": "ovos-skill-weather"
  }
}

```

---

#### `mycroft.gui.screen.close`

A global "back" request. `NamespaceManager.handle_namespace_global_back()` removes the
namespace currently at the top of the active stack. It carries no payload.

```json
{
  "type": "mycroft.gui.screen.close",
  "data": {}
}

```

---

### Messages emitted by `ovos-gui` service

#### `gui.namespace.removed`

Emitted by `NamespaceManager` after a namespace has been deactivated and cleared.

```json
{
  "type": "gui.namespace.removed",
  "data": {
    "skill_id": "ovos-skill-weather"
  }
}

```

#### `gui.namespace.displayed`

Emitted when a namespace moves to the top of the active display stack.

```json
{
  "type": "gui.namespace.displayed",
  "data": {
    "skill_id": "ovos-skill-weather"
  }
}

```

---

### Status events forwarded to GUI clients

`NamespaceManager` subscribes to the following core bus messages and re-emits each to
connected Qt clients (via `forward_to_gui` → `mycroft.events.triggered` in the `system`
namespace), so the UI can react to listening/speaking state:

| Bus message type | Meaning |
|---|---|
| `recognizer_loop:wakeword` | Wake word detected |
| `recognizer_loop:record_begin` | Microphone opened |
| `recognizer_loop:record_end` | Microphone closed |
| `recognizer_loop:utterance` | [Utterance](life-of-an-utterance.md) recognised |
| `recognizer_loop:recognition_unknown` | [STT](stt-plugins.md) gave no result |
| `speak` | [TTS](tts-plugins.md) about to speak |
| `recognizer_loop:audio_output_start` | Audio playback started |
| `recognizer_loop:audio_output_end` | Audio playback ended |
| `recognizer_loop:sleep` | Device going to sleep |
| `recognizer_loop:wake_up` | Device waking up |
| `mycroft.awoken` | Wake-up acknowledged |
| `mycroft.skill.handler.start` | A skill handler started |
| `mycroft.skill.handler.complete` | A skill handler completed |
| `ovos.utterance.handled` | Intent matched and handled |
| `ovos.utterance.cancelled` | Utterance cancelled |

---

## Qt WebSocket Protocol (Legacy Adapter)

> This section applies only when `ovos-legacy-mycroft-gui-plugin` is installed.

All messages are JSON objects sent over the WebSocket connection at `ws://localhost:18181`.

### Connection handshake

**Qt client → `ovos-gui` (OVOS MessageBus):**

```json
{
  "type": "mycroft.gui.connected",
  "data": {
    "gui_id": "unique_identifier_provided_by_client",
    "framework": "qt5"
  }
}

```

**`ovos-gui` → Qt client (OVOS MessageBus reply):**

```json
{
  "type": "mycroft.gui.port",
  "data": {
    "port": 18181,
    "gui_id": "qt-client-1",
    "framework": "qt5"
  }
}

```

The Qt client then opens a WebSocket connection to `ws://localhost:18181`.

When a client connects, `GUIWebsocketHandler.synchronize()` replays the full current state:

1. Re-sends `mycroft.session.list.insert` for every namespace in the active stack (in order).


2. For each namespace, re-sends `mycroft.gui.list.insert` with its current [QML](qt5-gui.md) page.


3. Re-sends all `mycroft.session.set` messages for every key in `namespace.data`.

---

### Namespace stack management (`mycroft.system.active_skills`)

The reserved namespace `mycroft.system.active_skills` defines the display priority.
The first item is always the namespace currently shown.

**Insert namespace** (skill becomes visible):

```json
{
  "type": "mycroft.session.list.insert",
  "namespace": "mycroft.system.active_skills",
  "position": 0,
  "data": [{"skill_id": "ovos-skill-weather"}]
}

```

**Move namespace** (existing skill re-activated):

```json
{
  "type": "mycroft.session.list.move",
  "namespace": "mycroft.system.active_skills",
  "from": 2,
  "to": 0,
  "items_number": 1
}

```

**Remove namespace** (skill cleared / idle):

```json
{
  "type": "mycroft.session.list.remove",
  "namespace": "mycroft.system.active_skills",
  "position": 0,
  "items_number": 1
}

```

---

### Session data sync (`mycroft.session.*`)

Session data is a key/value dictionary kept synchronized between `ovos-gui` and each
Qt client. Values may be strings, numbers, booleans, or lists.

**Set / update a key:**

```json
{
  "type": "mycroft.session.set",
  "namespace": "ovos-skill-weather",
  "data": {
    "current_temp": 22,
    "condition": "Sunny"
  }
}

```

**Delete a key:**

```json
{
  "type": "mycroft.session.delete",
  "namespace": "ovos-skill-weather",
  "property": "current_temp"
}

```

**List operations** (for list-typed session values):

```json
{
  "type": "mycroft.session.list.insert",
  "namespace": "ovos-skill-weather",
  "property": "forecast",
  "position": 0,
  "values": [{"date": "tomorrow", "temperature": 13}]
}

```

```json
{
  "type": "mycroft.session.list.update",
  "namespace": "ovos-skill-weather",
  "property": "forecast",
  "position": 0,
  "values": [{"date": "tomorrow", "temperature": 15}]
}

```

```json
{
  "type": "mycroft.session.list.move",
  "namespace": "ovos-skill-weather",
  "property": "forecast",
  "from": 2,
  "to": 0,
  "items_number": 1
}

```

```json
{
  "type": "mycroft.session.list.remove",
  "namespace": "ovos-skill-weather",
  "property": "forecast",
  "position": 0,
  "items_number": 1
}

```

---

### Page management (`mycroft.gui.list.*`)

Each active skill is associated with a list of page URIs.

**Insert new page at position:**

```json
{
  "type": "mycroft.gui.list.insert",
  "namespace": "ovos-skill-weather",
  "position": 0,
  "data": [{"url": "SYSTEM:TextFrame.qml", "page": "TextFrame.qml"}]
}

```

The `SYSTEM:` URI scheme is resolved by the Qt client to the matching system-template QML
file (see [OVOS Shell](ovos-shell.md) for the `OVOS_SYSTEM_TEMPLATES` override and
resolution order). Skill-provided `.qml` pages are sent as ordinary file URIs.

**Move pages:**

```json
{
  "type": "mycroft.gui.list.move",
  "namespace": "ovos-skill-weather",
  "from": 0,
  "to": 2,
  "items_number": 1
}

```

**Remove pages:**

```json
{
  "type": "mycroft.gui.list.remove",
  "namespace": "ovos-skill-weather",
  "position": 0,
  "items_number": 1
}

```

---

### Events (`mycroft.events.triggered`)

Events can be emitted by the GUI client (e.g. user tapped a button) or by the skill
(e.g. a voice command caused a state change).

```json
{
  "type": "mycroft.events.triggered",
  "namespace": "ovos-skill-weather",
  "event_name": "my.gui.event",
  "parameters": {"item": 3}
}

```

#### Page focus / interaction (client → core)

When the user swipes to a different page or interacts with one, the Qt client signals
core. `ovos-gui` listens for `gui.page_gained_focus` and `gui.page_interaction` on the
OVOS bus; both carry `skill_id` and a zero-based `page_number`. The interaction event also
resets the namespace's idle-removal timer.

```json
{
  "type": "gui.page_gained_focus",
  "data": {"skill_id": "ovos-skill-weather", "page_number": 0}
}

```

#### System status events

Core bus events forwarded to Qt clients:

```json
{
  "type": "mycroft.events.triggered",
  "namespace": "system",
  "event_name": "recognizer_loop:wakeword",
  "data": {}
}

```

---

### Qt client → OVOS core bus

Messages received from Qt clients over the WebSocket are forwarded to the OVOS core bus
unchanged. This allows Qt GUI interactions (button presses, text input) to reach skills
as normal bus events.

---

## Summary: message flow

```
Skill call:   self.gui.show_text("Hello", title="Greeting")
  → bus:      gui.value.set            (skill namespace data)
  → bus:      gui.page.show            (SYSTEM_TextFrame)
  → ovos-gui: NamespaceManager records page + data on the namespace
  → WS:       mycroft.session.list.insert (namespace into active stack)
  → WS:       mycroft.gui.list.insert     (SYSTEM:TextFrame.qml)
  → WS:       mycroft.session.set         (sync data to Qt)
  → Qt client renders the page

User swipes / taps on Qt:
  → WS → bus: gui.page_gained_focus / gui.page_interaction (skill_id, page_number)
  → ovos-gui updates focused page and reschedules namespace timeout
```

---

!!! warning "Upcoming — unreleased"
    On the GUI-rework branch ([OpenVoiceOS/ovos-gui#112](https://github.com/OpenVoiceOS/ovos-gui/pull/112),
    `feat/gui-rework-landing`), specified by the **OVOS-GUI-1** spec
    ([OpenVoiceOS/architecture#63](https://github.com/OpenVoiceOS/architecture/pull/63);
    see [GUI Service](gui-service.md)) the bus contract changes:

    - `gui.page.show` accepts **only** `SYSTEM_*` template names; if `page_names[0]` does
      not start with `SYSTEM_`, `handle_show_page()` logs an error and drops the request
      (custom QML is no longer supported).
    - Instead of mirroring to Qt clients directly, `NamespaceManager` calls
      `adapter.dispatch_template(template, skill_id, data, session_id)` on every loaded
      `opm.gui_adapter` plugin; the Qt WebSocket protocol moves into the
      `ovos-legacy-mycroft-gui-plugin` adapter.
    - Forwarded status events go to adapters via
      `adapter.on_status_event(event_name, data, session_id)` rather than straight to Qt clients.
    - `gui.namespace.removed` / `gui.namespace.displayed` are still emitted; the
      `gui.page.delete` / `gui.page.delete.all` handlers are removed.

    See [GUI Adapter Plugins](gui-adapters.md) for the adapter-side API.

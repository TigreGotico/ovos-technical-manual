# GUI Protocol

The `ovos-gui` service exposes two communication channels:

1. **OVOS [MessageBus](bus-service.md)** — used by skills and core components to set GUI state.


2. **Qt WebSocket** (port 18181, via `ovos-legacy-mycroft-gui-plugin`) — used by Qt5/Qt6
   GUI clients (`mycroft-gui-qt5`, `ovos-shell`) to receive display commands and send
   back user interaction events.

The transport protocol between `ovos-gui` and Qt clients is implemented in the
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
    "__idle": null,
    "__animations": false
  }
}

```

| Field | Description |
|---|---|
| `__from` | [Skill](skill-design-guidelines.md) ID (namespace owner) |
| `__idle` | Idle timeout in seconds, or `null` |
| `__animations` | Whether page transitions should animate |
| All other keys | Skill-defined session variables |

`NamespaceManager` stores all keys in `namespace.data` and forwards non-reserved keys
to adapters via `on_session_update()`.

---

#### `gui.page.show`

Sent by `GUIInterface._show_pages()` to request a template or page be shown.

**Template format (SYSTEM_*):**

```json
{
  "type": "gui.page.show",
  "data": {
    "page_names": ["SYSTEM_weather"],
    "index": 0,
    "persistence": true,
    "__from": "ovos-skill-weather",
    "__idle": null,
    "__animations": false
  }
}

```

When `page_names[0]` starts with `SYSTEM_`, `NamespaceManager` reads the namespace's
current `data` dict and dispatches to all loaded adapters via
`adapter.dispatch_template(template, skill_id, data)`.

**Legacy format (framework-specific pages):**

```json
{
  "type": "gui.page.show",
  "data": {
    "page_names": ["Weather.qml"],
    "index": 0,
    "__from": "ovos-skill-weather"
  }
}

```

Non-`SYSTEM_*` names are handled by the unchanged legacy path inside `NamespaceManager`
(forwarded to Qt clients via the legacy adapter).

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

Sends an arbitrary event into a skill's namespace (used for confirm/select responses
and custom interactions).

```json
{
  "type": "gui.event.send",
  "data": {
    "namespace": "ovos-skill-weather",
    "event_name": "skill.selection.confirmed",
    "params": {"confirmed": true}
  }
}

```

---

### Messages consumed by `NamespaceManager` (from skills / core)

#### `ovos.gui.screen.close`

Request to remove a skill's namespace from the active display stack and deactivate it.

```json
{
  "type": "ovos.gui.screen.close",
  "data": {
    "skill_id": "ovos-skill-weather"
  }
}

```

Triggers `adapter.on_namespace_deactivated(skill_id)` on all adapters.

---

#### `gui.clear.namespace`

Legacy equivalent of `ovos.gui.screen.close`. [Session](session.md) data is discarded.

```json
{
  "type": "gui.clear.namespace",
  "data": {
    "__from": "ovos-skill-weather"
  }
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

### Status events forwarded to adapters

`NamespaceManager` subscribes to the following core bus messages and forwards them to all
adapters via `adapter.on_status_event(event_name, data)`:

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
| `ovos.utterance.handled` | Intent matched and handled |
| `ovos.utterance.cancelled` | Utterance cancelled |

---

### Touch / Interaction responses (emitted back to the bus)

When a touch-capable adapter receives user input on confirm/select templates:

#### `<skill_id>.confirm.response`

```json
{
  "type": "ovos-skill-weather.confirm.response",
  "data": {
    "confirmed": true
  }
}

```

#### `<skill_id>.select.response`

```json
{
  "type": "ovos-skill-weather.select.response",
  "data": {
    "value": "Berlin"
  }
}

```

Skills must register handlers for these events if they use `show_confirm()` or `show_select()`.

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

When a client connects, `plugin.synchronize(client)` replays the full current state:

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
  "data": [{"url": "SYSTEM:Weather.qml", "page": "Weather.qml"}]
}

```

The `SYSTEM:` URI scheme is resolved by the Qt client: first checks `$OVOS_SYSTEM_TEMPLATES/Weather.qml`, then falls back to the compiled-in default at `/usr/share/mycroft-gui/system-templates/Weather.qml`.

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

#### Special event: `page_gained_focus`

Used when `ovos-gui` wants a specific page to become the active view. The Qt client
renders the requested page on receipt. Clients may also emit this event after a user
swipes to a new page.

```json
{
  "type": "mycroft.events.triggered",
  "namespace": "ovos-skill-weather",
  "event_name": "page_gained_focus",
  "data": {"number": 0}
}

```

The `number` field is the zero-based page position within the namespace's page list.

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

## Summary: message flows

```
Skill call:   gui.show_weather(22, "Sunny")
  → bus:      gui.value.set       (skill namespace data)
  → bus:      gui.page.show       (SYSTEM_weather)
  → adapter:  handle_show_weather (AbstractGUIPlugin)
  → WS:       mycroft.session.set (sync data to Qt)
  → WS:       mycroft.gui.list.insert (SYSTEM:Weather.qml)
  → WS:       mycroft.events.triggered / page_gained_focus

User taps confirm button on Qt:
  → WS:       mycroft.events.triggered / skill.confirm.confirmed
  → bus:      <skill_id>.confirm.response  {confirmed: true}
  → skill:    handler registered for that event

```

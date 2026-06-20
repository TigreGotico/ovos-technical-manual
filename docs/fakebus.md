# FakeBus

**Module:** `ovos_utils.fakebus`

In-process message bus and message implementation for testing, standalone usage, or environments where `ovos-bus-client` is not available. Behaves like the real `MessageBusClient` API without any WebSocket connection.

---

## `FakeBus`

```python
from ovos_utils.fakebus import FakeBus, FakeMessage

bus = FakeBus()

def on_utterance(message):
    print(message.data["utterances"])

bus.on("recognizer_loop:utterance", on_utterance)
bus.emit(FakeMessage("recognizer_loop:utterance", {"utterances": ["hello"]}))

```

### Internals

`FakeBus` uses a `pyee.EventEmitter` internally. When `emit()` is called:

1. Injects `session` into `message.context` if not present (replicates the real bus side effect)


2. Emits `"message"` with the serialized payload on the emitter


3. Emits `message.msg_type` directly on the emitter (for `bus.on()` handlers)


4. Calls `on_message()` with the serialized payload

### Session Handling

`FakeBus` replicates `SessionManager` side effects from `ovos-bus-client` if that package is installed:

- `emit()` serializes the current session into `message.context["session"]`


- `on_message()` calls `Session.from_message()` and `SessionManager.update()`


- `on_default_session_update()` updates the default session when `ovos.session.update_default` is received

### Key Methods

| Method | Description |
|---|---|
| `on(msg_type, handler)` | Register a handler for a message type |
| `once(msg_type, handler)` | Register a one-time handler |
| `emit(message)` | Dispatch a message locally |
| `remove(msg_type, handler)` | Unregister a handler |
| `remove_all_listeners(event_name)` | Remove all handlers for a message type |
| `wait_for_message(message_type, timeout)` | Block until a message of that type arrives |
| `wait_for_response(message, reply_type, timeout)` | Emit a message and wait for its response |
| `run_forever()` | No-op (sets `started_running = True`) |
| `run_in_thread()` | Calls `run_forever()` |
| `close()` | Calls `on_close()` |
| `create_client()` | Returns `self` |

---

## `AsyncFakeBus`

In-process stand-in for `AsyncMessageBusClient`, for asyncio-native code. It mirrors the same surface as `FakeBus`, but `connect()` / `close()` / `emit()` / `wait_for_message()` / `wait_for_response()` are **coroutines** (must be `await`ed), while `on()` / `once()` / `remove()` stay synchronous. The same session-injection side effects apply, so multi-turn flows behave identically.

```python
from ovos_utils.fakebus import AsyncFakeBus, FakeMessage

bus = AsyncFakeBus()
await bus.connect()
await bus.emit(FakeMessage("recognizer_loop:utterance", {"utterances": ["hello"]}))
reply = await bus.wait_for_response(FakeMessage("my.query"))

```

---

## `FakeMessage`

`FakeMessage` is a re-export of the canonical OVOS message envelope, `ovos_spec_tools.message.Message` (the reference implementation of the **OVOS-MSG-1** spec). It is **the same class** that `ovos_bus_client.Message` subclasses, so messages are interoperable across all three import paths — there is no proxying or runtime class-swapping involved.

```python
from ovos_utils.fakebus import FakeMessage

msg = FakeMessage("skill:action", {"key": "value"}, {"session_id": "abc"})

```

`ovos-spec-tools` is a hard dependency of `ovos-utils`, so `FakeMessage` is always the real envelope class — installing `ovos-bus-client` is not required.

| Attribute | Description |
|---|---|
| `msg_type` | Message type string |
| `data` | Payload dict |
| `context` | Context dict (includes session, source, destination) |

### Key Methods

OVOS-MSG-1 defines `forward` / `reply` / `response` as the three normative message derivations (§5).

| Method | Description |
|---|---|
| `serialize() → str` | JSON-encode the message |
| `FakeMessage.deserialize(value) → FakeMessage` | Construct from a JSON string |
| `as_dict() → dict` | Return the message as a plain dict |
| `forward(msg_type, data=None, context=None)` | Relay under a new topic, preserving context (no routing-key swap) |
| `reply(msg_type, data=None, context=None)` | §5.2 — reply addressed back to the source (swaps `source` ↔ `destination`) |
| `response(data=None, context=None)` | §5.3 — sugar for `reply(msg_type + ".response", ...)` |
| `publish(msg_type, data, context=None)` | **Deprecated** (see below) — relay under a new topic and drop `target` |

> **`publish` is deprecated.** It is not part of OVOS-MSG-1 and is slated for removal in the next major (`1.0.0`). It is attached to the `Message` class at import time for backwards compatibility (`ovos-utils` and `ovos-bus-client` both attach it idempotently). Use `forward()` when you want to relay without the routing-key swap, or `reply()` when you want the swap.

### `isinstance` Compatibility

`isinstance(msg, FakeMessage)` works across packages because `FakeMessage`, `ovos_spec_tools.Message`, and `ovos_bus_client.Message` form a single class hierarchy — `FakeMessage` *is* `ovos_spec_tools.Message`, and `ovos_bus_client.Message` is a subclass of it. (The historical `_MutableMessage` metaclass and dynamic `__new__` indirection have been removed; they are no longer needed now that spec-tools is a hard dependency.)

---

## `Message` (Deprecated)

`ovos_utils.fakebus.Message` is a deprecated alias for the OVOS-MSG-1 envelope; importing and instantiating it emits a `DeprecationWarning`. New code should import `ovos_spec_tools.Message` (or `ovos_bus_client.Message`) directly.

---

## `dig_for_message()`

Tries to import and call `ovos_bus_client.message.dig_for_message`. Returns `None` if `ovos-bus-client` is not installed.

# MessageBus Client

The [OVOS MessageBus Client](https://github.com/OpenVoiceOS/ovos-bus-client) (`ovos-bus-client`) provides the WebSocket client, `Message` objects, `Session` management, and high-level API interfaces for communicating with the OVOS MessageBus.

---

## Quick Start

```python
from ovos_bus_client import MessageBusClient
from ovos_bus_client.message import Message

bus = MessageBusClient()
bus.run_in_thread()
bus.connected_event.wait()

# Listen for an event
bus.on("recognizer_loop:utterance", lambda msg: print(msg.data))

# Send a message
bus.emit(Message("speak", {"utterance": "Hello world"}))

# Request/response
response = bus.wait_for_response(
    Message("intent.service.intent.get", {"utterance": "what time is it"}),
    reply_type="intent.service.intent.reply",
    timeout=5
)
```

> In skills and plugins, `self.bus` provides a `MessageBusClient` connection automatically — you do not need to initialize one yourself.

---

## Package Layout

```
ovos_bus_client/
├── message.py          # Message, CollectionMessage, GUIMessage, dig_for_message
├── session.py          # Session, SessionManager, IntentContextManager
├── client/
│   ├── client.py       # MessageBusClient, GUIWebsocketClient  (sync, thread-based)
│   ├── async_client.py # AsyncMessageBusClient (asyncio)
│   ├── collector.py    # MessageCollector (used by collect_responses)
│   └── waiter.py       # MessageWaiter (used by wait_for_response)
├── apis/
│   ├── events.py       # EventSchedulerInterface
│   ├── gui.py          # GUIInterface, PageTemplates
│   ├── ocp.py          # OCPInterface
│   └── enclosure.py    # EnclosureAPI (legacy)
├── util/
│   └── scheduler.py    # EventScheduler (server-side daemon thread)
└── conf.py             # load_message_bus_config, load_gui_message_bus_config
```

---

## MessageBusClient

**Module:** `ovos_bus_client.client.client.MessageBusClient`

### Connection

```python
# Default config from mycroft.conf (websocket section)
bus = MessageBusClient()

# Explicit connection
bus = MessageBusClient(host="127.0.0.1", port=8181, route="/core", ssl=False)

# Cache config (avoids re-reading .conf for each instantiation)
bus = MessageBusClient(cache=True)

# Run in a daemon thread (most common pattern)
bus.run_in_thread()
bus.connected_event.wait()   # block until connected

# Block the current thread
bus.run_forever()

# Close
bus.close()
```

On connection the client automatically emits `ovos.session.sync` to pull the current default session state from `ovos-core`. Auto-reconnection uses exponential back-off (5 s → 60 s max).

### Emitting Messages

```python
bus.emit(Message("speak", {"utterance": "Hello"}))
```

The session is automatically injected into `message.context["session"]` if not already present.

### Listening

```python
bus.on("my.event", handler)           # persistent listener
bus.once("my.event", handler)         # one-shot, auto-removed after first call
bus.remove("my.event", handler)       # remove a listener
bus.remove_all_listeners("my.event")  # remove all listeners for an event
```

Handlers receive a single `Message` argument.

### Waiting for a Response

```python
# Send and block until reply
response = bus.wait_for_response(
    Message("intent.service.intent.get", {"utterance": "what time is it"}),
    reply_type="intent.service.intent.reply",   # default: msg_type + ".response"
    timeout=3.0
)
if response:
    print(response.data)

# Wait without sending first
msg = bus.wait_for_message("mycroft.skills.initialized", timeout=30)
```

`reply_type` accepts `str` or `List[str]`.

### Collecting Responses from Multiple Handlers

Used when multiple services may respond to a single request (e.g. CommonQuery, OCP search):

```python
# Sender side
responses = bus.collect_responses(
    message=Message("question:query", {"phrase": "capital of France"}),
    min_timeout=0.2,
    max_timeout=3.0,
    direct_return_func=lambda msg: msg.data.get("conf", 0) > 0.9
)

# Handler side (registers with automatic acknowledgement)
def my_handler(msg: CollectionMessage):
    if answer:
        bus.emit(msg.success({"answer": "Paris", "conf": 0.9}))
    else:
        bus.emit(msg.failure())

bus.on_collect("question:query", my_handler, timeout=2)
```

The framework adds `__collect_id__` to `message.context` to correlate responses.

### GUIWebsocketClient

A subclass for the separate GUI WebSocket endpoint:

```python
from ovos_bus_client.client import GUIWebsocketClient

gui_bus = GUIWebsocketClient(host="127.0.0.1", port=18181, route="/")
```

Defaults to `gui` section of `mycroft.conf` (port 18181, route `/`). Emits `GUIMessage` objects.

### Configuration

```json
{
  "websocket": {
    "host": "127.0.0.1",
    "port": 8181,
    "route": "/core",
    "ssl": false,
    "secret_key": null,
    "allow_unencrypted": true
  }
}
```

See [Configuration](110-config.md) for the full config stack.

---

## Message

**Module:** `ovos_bus_client.message.Message`

Every event on the bus is a `Message`. Wire format:

```json
{"type": "speak", "data": {"utterance": "Hello"}, "context": {"skill_id": "my-skill"}}
```

```python
from ovos_bus_client.message import Message

msg = Message("speak", {"utterance": "Hi!"}, {"skill_id": "my-skill"})
json_str = msg.serialize()
msg2 = Message.deserialize(json_str)
```

### Routing Methods

| Method | Description |
|---|---|
| `forward(msg_type, data)` | Copy context verbatim; relay under a new type |
| `reply(msg_type, data, context)` | Copy context, swap `source`↔`destination` |
| `response(data, context)` | Shorthand for `reply(self.msg_type + ".response", ...)` |
| `publish(msg_type, data, context)` | Copy context without a `target` key; broadcast |

### `dig_for_message`

```python
from ovos_bus_client.message import dig_for_message

msg = dig_for_message(max_records=10)
```

Walks the call stack looking for a `Message` argument. Used internally by skills and APIs to recover the originating message without explicitly threading it through every call.

### Encryption

If `websocket.secret_key` is set in `mycroft.conf`, all messages are AES-encrypted on the wire. The `Message` class handles this transparently.

```json
{
  "websocket": {
    "secret_key": "my-secret",
    "allow_unencrypted": false
  }
}
```

### `CollectionMessage`

Extension of `Message` for use with `bus.collect_responses` / `bus.on_collect`:

```python
def my_handler(msg: CollectionMessage):
    if success:
        self.bus.emit(msg.success({"result": "data"}))
    else:
        self.bus.emit(msg.failure())
    # To extend the timeout while processing:
    self.bus.emit(msg.extend(timeout=5))
```

### Common `context` Keys

| Key | Set by | Meaning |
|---|---|---|
| `skill_id` | Skill | Which skill emitted this message |
| `session` | Core/client | Serialized `Session` object |
| `lang` | STT / transformer | Language of the utterance |
| `stt_lang` | STT | Language used to transcribe |
| `detected_lang` | Transformer | Language detected by classifier |
| `request_lang` | Source | Language volunteered by source |
| `source` | Bus routing | Origin of the message |
| `destination` | Bus routing | Target of the message |
| `cancel_word` | STT | The cancel word that was detected |
| `valid_langs` | Core | Languages enabled for this request |

---

## AsyncMessageBusClient

**Module:** `ovos_bus_client.client.async_client.AsyncMessageBusClient`

`AsyncMessageBusClient` is an asyncio-native client providing the same interface as `MessageBusClient` but with `async/await`. Requires the optional `websockets` dependency:

```bash
pip install "ovos-bus-client[async]"
```

```python
import asyncio
from ovos_bus_client import AsyncMessageBusClient
from ovos_bus_client.message import Message

async def main():
    bus = AsyncMessageBusClient()
    await bus.connect()

    bus.on("speak", lambda msg: print("OVOS said:", msg.data.get("utterance")))
    await bus.emit(Message("speak", {"utterance": "Hello world"}))

    response = await bus.wait_for_response(
        Message("intent.service.intent.get", {"utterance": "what time is it"}),
        reply_type="intent.service.intent.reply",
        timeout=5.0,
    )
    await bus.close()

asyncio.run(main())
```

### When to Use

| Situation | Recommended |
|---|---|
| Stand-alone script, daemon, OVOS plugin | `MessageBusClient` (sync, thread-based) |
| Inside an existing asyncio application | `AsyncMessageBusClient` |
| Emitting many messages concurrently | `AsyncMessageBusClient` |

The async client does not auto-reconnect on drop. Unlike the sync client, it has no `run_forever()` or `run_in_thread()` — the receive loop runs cooperatively inside your event loop.

### Key Differences vs `MessageBusClient`

| Feature | `MessageBusClient` | `AsyncMessageBusClient` |
|---|---|---|
| WebSocket library | `websocket-client` | `websockets` |
| I/O model | blocking threads | asyncio coroutines |
| `emit()` | sync | `async` |
| `wait_for_response()` | sync (blocks) | `async` |
| Auto-reconnect | yes (exponential back-off) | not built-in |
| Extra dependency | none | `websockets>=10` |

### Fan-out: Concurrent Emits

```python
import asyncio

messages = [Message(f"plugin.query.{i}", {"i": i}) for i in range(100)]
await asyncio.gather(*[bus.emit(m) for m in messages])
```

### Benchmarks (localhost, CPython 3.11, n=3000)

| Benchmark | Sync | Async |
|---|---|---|
| `emit()` mean latency | 0.022 ms | 0.025 ms |
| `wait_for_message()` mean | 0.020 ms | 0.006 ms (3.4× faster) |
| Concurrent emit ×200 (fan-out) | n/a | ~31,000 msg/s |

---

## High-Level APIs

### GUIInterface

**Module:** `ovos_bus_client.apis.gui.GUIInterface`

Interface to the `ovos-gui` display service. Used as `self.gui` inside skills.

```python
gui["temperature"] = 22        # synced to QML as sessionData.temperature
gui["city"] = "Paris"

gui.show_page(PageTemplates.TEXT)
gui.show_page(PageTemplates.IMAGE)

# Register a handler for events triggered by QML
gui.register_handler("button.pressed", self.on_button_pressed)
```

Available `PageTemplates`: `IDLE`, `LOADING`, `STATUS`, `TEXT`, `ERROR`, `IMAGE`, `ANIMATED_IMAGE`, `HTML`, `URL`, `WEATHER`, `CLOCK`, `FACE`.

### EventSchedulerInterface

**Module:** `ovos_bus_client.apis.events.EventSchedulerInterface`

Schedule future and repeating bus events. Used as `self.event_scheduler` inside skills.

```python
scheduler.schedule_event(handler=self.on_timer, when=10, name="my_timer")
scheduler.schedule_repeating_event(handler=self.on_tick, when=5, interval=60, name="my_tick")
scheduler.cancel_scheduled_event("my_timer")
scheduler.cancel_all_repeating_events()
```

Event names are scoped as `{skill_id}:{name}` to avoid collisions.

### OCPInterface

**Module:** `ovos_bus_client.apis.ocp.OCPInterface`

Interface to OCP (OpenVoiceOS Common Play) media playback. Used as `self.audio_service` inside skills.

```python
ocp.play(tracks=["https://example.com/song.mp3"])
ocp.queue(tracks=["https://example.com/song2.mp3"])
ocp.stop()
ocp.pause()
ocp.resume()
ocp.next()
ocp.prev()
```

Tracks can be a string URI or a `(uri, mime_type)` tuple.

---

## Related Pages

- [Bus Session](901-bus-session.md) — `Session`, `SessionManager`, `IntentContextManager`
- [Bus Service](100-bus_service.md) — `ovos-messagebus` WebSocket server
- [ovos-core](102-core.md) — Intent service, skill manager
- [Configuration](110-config.md) — `mycroft.conf` configuration

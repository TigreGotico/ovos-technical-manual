# MessageBusClient

**Module:** `ovos_bus_client.client.client.MessageBusClient`

`MessageBusClient` is a WebSocket client that connects to the OVOS `ovos-messagebus` service and provides an event-emitter interface over it.

## Connection

```python
from ovos_bus_client import MessageBusClient

# Default config from mycroft.conf (websocket section)
bus = MessageBusClient()

# Explicit connection
bus = MessageBusClient(host="127.0.0.1", port=8181, route="/core", ssl=False)

# Cache config (avoids re-reading .conf for each instantiation)
bus = MessageBusClient(cache=True)

```

### Running

```python

# Block the current thread
bus.run_forever()

# Run in a daemon thread (most common pattern)
bus.run_in_thread()
bus.connected_event.wait()   # block until connected

# Close
bus.close()

```

On connection the client automatically emits `ovos.session.sync` to pull the current default session state from `ovos-core`.

### Reconnection

On error the client waits `retry` seconds (starts at 5 s, doubles up to 60 s max) then reconnects automatically.

### Default Session

Each `MessageBusClient` instance is associated with a `Session`. On construction a default session is assigned. The client listens for `ovos.session.update_default` to keep the local session in sync with core.

---

## Emitting Messages

```python
from ovos_bus_client.message import Message

bus.emit(Message("speak", {"utterance": "Hello"}))

```

The session is automatically injected into `message.context["session"]` if not already present.

---

## Listening

```python

# Persistent listener
bus.on("my.event", handler)

# One-shot listener (auto-removed after first call)
bus.once("my.event", handler)

# Remove a listener
bus.remove("my.event", handler)

# Remove all listeners for an event
bus.remove_all_listeners("my.event")

```

Handlers receive a single `Message` argument.

---

## Waiting for a Response

### `wait_for_response`

Send a message and block until a matching reply arrives (or timeout).

```python
response = bus.wait_for_response(
    Message("intent.service.intent.get", {"utterance": "what time is it"}),
    reply_type="intent.service.intent.reply",   # default: msg_type + ".response"
    timeout=3.0
)
if response:
    print(response.data)

```

`reply_type` accepts a `str` or `List[str]`.

### `wait_for_message`

Wait for a message of a given type without sending anything first.

```python
msg = bus.wait_for_message("mycroft.skills.initialized", timeout=30)

```

---

## Collecting Responses from Multiple Handlers

Used when multiple services may respond to a single request (e.g. CommonQuery, OCP search).

### Sender side: `collect_responses`

```python
responses = bus.collect_responses(
    message=Message("question:query", {"phrase": "capital of France"}),
    min_timeout=0.2,   # wait at least this long
    max_timeout=3.0,   # give up after this long
    direct_return_func=lambda msg: msg.data.get("conf", 0) > 0.9
)

```

Returns a list of all `Message` responses received within the timeout window. `direct_return_func` enables early return when a sufficiently good result arrives.

The framework adds `__collect_id__` to `message.context` to correlate responses.

### Handler side: `on_collect`

```python
def my_handler(msg: CollectionMessage):
    # Acknowledge immediately
    # (the ack is sent automatically by the wrapper)
    answer = compute_answer(msg.data["phrase"])
    if answer:
        bus.emit(msg.success({"answer": answer, "conf": 0.9}))
    else:
        bus.emit(msg.failure())

bus.on_collect("question:query", my_handler, timeout=2)

```

`on_collect` wraps the handler: it sends an immediate `{event}.handling` acknowledgement, then calls the handler with a `CollectionMessage`.

---

## Event Emitter Events

These are synthetic events emitted locally (not over the bus) for connection lifecycle:

| Event | When |
|---|---|
| `open` | WebSocket connection established |
| `close` | WebSocket connection closed |
| `reconnecting` | About to attempt reconnection |
| `error` | WebSocket error occurred |
| `message` | Raw message string received |

```python
bus.on("open", lambda: print("connected"))
bus.on("close", lambda: print("disconnected"))

```

---

## `GUIWebsocketClient`

A subclass of `MessageBusClient` for the separate GUI WebSocket endpoint:

```python
from ovos_bus_client.client import GUIWebsocketClient

gui_bus = GUIWebsocketClient(host="127.0.0.1", port=18181, route="/")

```

Defaults to `gui` section of `mycroft.conf` (port 18181, route `/`). Emits `GUIMessage` objects.

---

## Configuration

Connection parameters are read from `mycroft.conf`:

```json
{
  "websocket": {
    "host": "127.0.0.1",
    "port": 8181,
    "route": "/core",
    "ssl": false,
    "secret_key": null,
    "allow_unencrypted": true
  },
  "gui": {
    "host": "127.0.0.1",
    "port": 18181,
    "route": "/"
  }
}

```

See [configuration.md](configuration-ref.md) for details.

---

## Async alternative

If your application already uses `asyncio`, use `AsyncMessageBusClient` instead.
It provides the same `emit`, `wait_for_response`, `wait_for_message`, and `collect_responses` interface as coroutines, with no threads required.

```python
from ovos_bus_client import AsyncMessageBusClient

bus = AsyncMessageBusClient()
await bus.connect()
await bus.emit(Message("speak", {"utterance": "Hello"}))

```

See [async_client.md](async-client.md) for the full reference and benchmarks.

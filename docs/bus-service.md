# Bus Service

The **Message Bus** is the central nervous system of the OVOS platform. All services communicate by publishing and subscribing to typed `Message` objects through this central WebSocket broker.

**In plain terms:** every OVOS service (core, audio, listener, GUI) connects to one shared WebSocket. Whatever any service sends, every other service receives — there is no central router deciding who gets what. Services just listen for the message types they care about and ignore the rest.

---

## Overview

`ovos-messagebus` is a pure fan-out WebSocket broker. Every message received from one client is broadcast verbatim to every connected client. The bus performs no filtering, routing, or transformation.

```
┌─────────────────────────────────────────────┐
│              ovos-messagebus                │
│                                             │
│  Tornado IOLoop (daemon thread)             │
│  ┌──────────────────────────────────────┐   │
│  │  MessageBusEventHandler             │   │
│  │  (Tornado WebSocketHandler)         │   │
│  │  ┌──────────────────────────────┐   │   │
│  │  │  client_connections: list    │   │   │
│  │  │  Fan-out broadcast           │   │   │
│  │  └──────────────────────────────┘   │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
         │           │           │
    ovos-core   ovos-audio   ovos-gui
    (clients via ovos-bus-client)

```

---

## Running the Server

```bash
ovos-messagebus

# or
python -m ovos_messagebus

```

The server reads connection parameters from `mycroft.conf` (`websocket` section) and starts listening on a daemon thread. On SIGTERM/SIGINT the daemon thread exits with the main process — no explicit cleanup is required.

---

## Configuration

All settings live under the `websocket` key in `mycroft.conf`:

```json
{
  "websocket": {
    "host": "127.0.0.1",
    "port": 8181,
    "route": "/core",
    "ssl": false,
    "max_msg_size": 10,
    "filter": false,
    "filter_logs": ["gui.status.request", "gui.page.upload"]
  }
}

```

| Key | Default | Description |
|---|---|---|
| `host` | `"0.0.0.0"` | Bind address. The shipped default binds all interfaces; set `"127.0.0.1"` to restrict to localhost. |
| `port` | `8181` | TCP port. The GUI service uses a separate port (`18181`). |
| `route` | `"/core"` | WebSocket URL path. Full URL: `ws://host:port/core`. |
| `ssl` | `false` | Enable WSS/TLS. |
| `max_msg_size` | `10` | Max WebSocket frame size in megabytes. |
| `filter` | `false` | Enable debug logging of message types before broadcast. |
| `filter_logs` | `["gui.status.request", "gui.page.upload"]` | Message types excluded from filter logging. |

> **Security:** Never expose the messagebus to the public internet. It provides full control over the OVOS instance. For remote access, use [HiveMind](https://jarbashivemind.github.io/HiveMind-community-docs/).

---

## Implementation: `MessageBusEventHandler`

**Module:** `ovos_messagebus.event_handler.MessageBusEventHandler` — [`ovos_messagebus/event_handler.py`](https://github.com/OpenVoiceOS/ovos-messagebus/blob/dev/ovos_messagebus/event_handler.py)

Tornado `WebSocketHandler` subclass implementing the OVOS message bus. All connected clients share a single module-level connection list (`client_connections`).

### Broadcast Behaviour

The bus is a pure fan-out: no routing, no filtering, no topic subscriptions at the server level. Every message every client sends is forwarded to every client (including the sender):

```python

# ovos_messagebus/event_handler.py:77
for client in client_connections:
    client.write_message(message)

```

Subscription filtering is handled entirely in the client library (`ovos-bus-client`).

---

??? abstract "Technical Reference"

    - `main()` — [`ovos_messagebus/__main__.py:43`](https://github.com/OpenVoiceOS/ovos-messagebus/blob/dev/ovos_messagebus/__main__.py) — Entry point initializing the Tornado application and IOLoop.


    - `MessageBusEventHandler.on_message()` — [`ovos_messagebus/event_handler.py:61`](https://github.com/OpenVoiceOS/ovos-messagebus/blob/dev/ovos_messagebus/event_handler.py) — Core broadcast logic.


    - `load_message_bus_config()` — [`ovos_messagebus/load_config.py:33`](https://github.com/OpenVoiceOS/ovos-messagebus/blob/dev/ovos_messagebus/load_config.py) — Configuration loader using `ovos-config`.
    
    ### `open()`
    
    Called when a new WebSocket connection is established. Writes a `connected` message (with `context.session.session_id = "default"`) to the new client only, then appends `self` to `client_connections`.
    
    ### `on_message(message)`
    
    Called for each incoming WebSocket frame. Broadcasts the raw message string to **all** connections. When `filter: true`, the message type, source, destination, and session are logged before broadcast.
    
    ### `check_origin(origin) → bool`
    
    Always returns `True`. OVOS does not enforce CORS/origin checks.
    
    ### `max_message_size`
    
    ```python
    config.get("websocket", {}).get("max_msg_size", 10) * 1024 * 1024
    ```
    
    Default: 10 MB. Messages larger than this cause Tornado to close the connection.
    
    ---
    

## Message Structure

Every message on the bus is a JSON object with three fields:

```json
{
  "type": "recognizer_loop:utterance",
  "data": {"utterances": ["what time is it"], "lang": "en-us"},
  "context": {"session": {"session_id": "default"}, "source": "listener"}
}

```

- `type` — identifies the event


- `data` — arbitrary JSON payload


- `context` — routing/session metadata

The bus recognises only one special message type: `connected` (emitted to a new client immediately after it opens a connection). All other types are application-level.

See [Bus Client](bus-client-overview.md) for the `Message` Python API.

---

## Sessions

Every message may carry a `session` object inside its `context`. Sessions enable:

- Per-user conversational context


- Independent pipeline configuration per client


- Site/device identification (`site_id`)


- [Skill](skill-design-guidelines.md) and intent blacklisting per session

The default session (`session_id="default"`) is used by the local microphone. HiveMind satellites each have their own session.

See [Bus Session](session.md) for full `Session` and `SessionManager` documentation.

---

## Message Targeting and Routing

The bus itself performs no routing — every client receives every message. However, `context["source"]` and `context["destination"]` allow applications (notably HiveMind) to implement their own routing logic.

The `Message` object provides:

- `.reply(msg_type, data)` — swap `source`↔`destination`, preserving context


- `.forward(msg_type, data)` — copy context verbatim under a new type


- `.response(data)` — shorthand for `reply(self.msg_type + ".response", ...)`

---

## Key Message Categories

### Core / Intent Pipeline

| Message type | Publisher | Consumers |
|---|---|---|
| `recognizer_loop:utterance` | `ovos-dinkum-listener` | `ovos-core` |
| `speak` | `ovos-core` (skills) | `ovos-audio` |
| `complete_intent_failure` | `ovos-core` | fallback skills |
| `ovos.utterance.handled` | `ovos-core` | GUI clients |

### Skill Manager

| Message type | Publisher | Consumers |
|---|---|---|
| `mycroft.skills.initialized` | `ovos-core` | GUI clients, tools |
| `skillmanager.list` | * | `ovos-core` |
| `ovos.skills.install` | * | `ovos-core` |

### Session Sync

| Message type | Publisher | Consumers |
|---|---|---|
| `ovos.session.sync` | new client | `ovos-core` |
| `ovos.session.update_default` | `ovos-core` | all clients |

### Connectivity / [PHAL](ovoscope-phal.md)

| Message type | Publisher | Consumers |
|---|---|---|
| `mycroft.network.connected` | `ovos-PHAL` | `ovos-core`, skills |
| `mycroft.internet.connected` | `ovos-PHAL` | `ovos-core`, skills |

---

## Services That Connect to the Bus

| Service | Role |
|---|---|
| [ovos-core](core.md) | Intent pipeline, skill orchestration |
| ovos-audio | [TTS](tts-plugins.md) rendering and audio playback |
| ovos-gui | GUI namespace management |
| ovos-dinkum-listener | Wake word detection and [STT](stt-plugins.md) transcription |
| ovos-PHAL | Hardware abstraction layer |

GUI clients connect to `ovos-gui`'s own WebSocket (`ws://localhost:18181/gui`), not directly to the messagebus.

---

## Alternative Implementations

`ovos-messagebus` is the reference **Tornado**-based server and is all you need for a normal install (`pip install ovos-messagebus`). Tornado is the current default and the only backend on `dev`. Because the wire protocol is just JSON frames over a WebSocket, the server is interchangeable — any process that fans messages out to all connected clients on the same route will work.

A separate, drop-in Rust implementation exists as its own project for deployments that want lower overhead:

- [OscillateLabsLLC/ovos-rust-messagebus](https://github.com/OscillateLabsLLC/ovos-rust-messagebus) — speaks the same OVOS wire protocol; build and run it in place of the Python server. See that project's README for build and configuration details.

**In plain terms:** on a stable install, run the default Python (Tornado) server; only reach for the Rust build if profiling shows the bus is a bottleneck.

!!! warning "Upcoming — unreleased"
    Pluggable high-performance backends are in flight via
    [OpenVoiceOS/ovos-messagebus#51](https://github.com/OpenVoiceOS/ovos-messagebus/pull/51)
    (branch `webrockets`). It keeps **Tornado** as the default reference server and adds two
    optional alternatives, benchmarked side by side with `benchmark/run_benchmark.py` at four
    load levels (5 / 20 / 50 / 100 concurrent clients):

    - **webrockets** — a high-performance websocket backend, written in Python.
    - **Rust** — the [`ovos-rust-messagebus`](https://github.com/OscillateLabsLLC/ovos-rust-messagebus)
      v1.1.2 server, run in place of the Python process.

    Throughput vs the Tornado baseline from the PR's measurements:

    | Load | webrockets | Rust |
    |---|---|---|
    | 5 clients × 200 msgs | +11% | +18% |
    | 20 clients × 1000 msgs | +9% | +20% |
    | 50 clients × 2000 msgs | +24% | +20% |
    | 100 clients × 500 msgs | +4% | connection errors (saturation) |

    webrockets leads at higher concurrency; the Rust backend showed connection
    saturation (28 connection errors) at the 100-client level. None of this is on a
    published release — do not rely on it on a stable install.

---

## Filter / Debug Mode

Set `websocket.filter: true` in `mycroft.conf` to log all message types before broadcasting. This does not affect message delivery.

```
DEBUG: <msg_type> source: [...] destination: [...]
       SESSION: {...}

```

Messages listed in `filter_logs` are excluded from the log to reduce noise (default: `["gui.status.request", "gui.page.upload"]`).

When `filter` is off (the default), the bus never deserializes messages — it emits and re-broadcasts the raw frame as-is. Deserialization only happens in `filter` mode for the log line; if a frame fails to deserialize there, it is dropped (not logged, not re-broadcast).

---

## Related Pages

- [Bus Client](bus-client-overview.md) — `MessageBusClient`, `Message`, `Session` Python API


- [Bus Session](session.md) — `Session`, `SessionManager`, `IntentContextManager`


- [ovos-core](core.md) — Intent service, skill manager


- [Configuration](config.md) — `mycroft.conf` configuration

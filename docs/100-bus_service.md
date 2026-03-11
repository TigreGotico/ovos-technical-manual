# Bus Service

The **Message Bus** is the central nervous system of the OVOS platform. All services communicate by publishing and subscribing to typed `Message` objects through this central WebSocket broker.

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
    "max_msg_size": 25,
    "filter": false,
    "filter_logs": ["gui.status.request", "gui.page.upload"]
  }
}
```

| Key | Default | Description |
|---|---|---|
| `host` | `"127.0.0.1"` | Bind address. Use `"0.0.0.0"` only if remote clients (e.g. HiveMind) need to connect. |
| `port` | `8181` | TCP port. The GUI service uses a separate port (`18181`). |
| `route` | `"/core"` | WebSocket URL path. Full URL: `ws://host:port/core`. |
| `ssl` | `false` | Enable WSS/TLS. Requires `ssl_cert` and `ssl_key` paths. |
| `max_msg_size` | `25` | Max WebSocket frame size in megabytes. |
| `filter` | `false` | Enable debug logging of message types before broadcast. |
| `filter_logs` | `["gui.status.request", ...]` | Message types excluded from filter logging. |

> **Security:** Never expose the messagebus to the public internet. It provides full control over the OVOS instance. For remote access, use [HiveMind](https://jarbashivemind.github.io/HiveMind-community-docs/).

---

## Implementation: `MessageBusEventHandler`

**Module:** `ovos_messagebus.event_handler.MessageBusEventHandler`

Tornado `WebSocketHandler` subclass implementing the OVOS message bus. All connected clients share a single module-level connection list (`client_connections`).

### Broadcast Behaviour

The bus is a pure fan-out: no routing, no filtering, no topic subscriptions at the server level. Every message every client sends is forwarded to every client (including the sender):

```python
# ovos_messagebus/event_handler.py:77
for client in client_connections:
    client.write_message(message)
```

Subscription filtering is handled entirely in the client library (`ovos-bus-client`).

### `open()`

Called when a new WebSocket connection is established. Writes a `connected` message (with `context.session.session_id = "default"`) to the new client only, then appends `self` to `client_connections`.

### `on_message(message)`

Called for each incoming WebSocket frame. Broadcasts the raw message string to **all** connections. When `filter: true`, the message type, source, destination, and session are logged before broadcast.

### `check_origin(origin) → bool`

Always returns `True`. OVOS does not enforce CORS/origin checks.

### `max_message_size`

```python
config.get("websocket", {}).get("max_msg_size", 25) * 1024 * 1024
```

Default: 25 MB. Messages larger than this cause Tornado to close the connection.

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

See [Bus Client](900-bus_client.md) for the `Message` Python API.

---

## Sessions

Every message may carry a `session` object inside its `context`. Sessions enable:

- Per-user conversational context
- Independent pipeline configuration per client
- Site/device identification (`site_id`)
- Skill and intent blacklisting per session

The default session (`session_id="default"`) is used by the local microphone. HiveMind satellites each have their own session.

See [Bus Session](901-bus-session.md) for full `Session` and `SessionManager` documentation.

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

### Connectivity / PHAL

| Message type | Publisher | Consumers |
|---|---|---|
| `mycroft.network.connected` | `ovos-PHAL` | `ovos-core`, skills |
| `mycroft.internet.connected` | `ovos-PHAL` | `ovos-core`, skills |

---

## Services That Connect to the Bus

| Service | Role |
|---|---|
| [ovos-core](102-core.md) | Intent pipeline, skill orchestration |
| ovos-audio | TTS rendering and audio playback |
| ovos-gui | GUI namespace management |
| ovos-dinkum-listener | Wake word detection and STT transcription |
| ovos-PHAL | Hardware abstraction layer |

GUI clients connect to `ovos-gui`'s own WebSocket (`ws://localhost:18181/gui`), not directly to the messagebus.

---

## Alternative Backends

`ovos-messagebus` ships the Tornado backend by default. Two additional backends are available for deployments needing higher throughput:

| Backend | Install | Notes |
|---|---|---|
| **Tornado** (default) | `pip install ovos-messagebus` | Pure Python, most compatible |
| **webrockets** | `pip install "ovos-messagebus[webrockets]"` | Rust-powered; +24% throughput at 50+ clients |
| **ovos-rust-messagebus** | Build from [source](https://github.com/OscillateLabsLLC/ovos-rust-messagebus) | +18-20% throughput at 5-20 clients |

All backends expose the same OVOS wire protocol.

Run the webrockets backend:

```bash
python -m ovos_messagebus.backends.webrockets_backend
```

Run the Rust binary:

```bash
git clone https://github.com/OscillateLabsLLC/ovos-rust-messagebus
cd ovos-rust-messagebus && cargo build --release
./target/release/ovos-rust-messagebus
```

### Benchmark Summary (localhost, CPython 3.11)

```
Scenario          Tornado       webrockets    Rust
─────────────────────────────────────────────────
5c × 200m       48,820/s      54,103/s      57,770/s  ← Rust best
20c × 1,000m    65,937/s      71,841/s      78,849/s  ← Rust best
50c × 2,000m    63,858/s      78,891/s      76,585/s  ← webrockets best
100c × 500m     74,154/s      76,799/s      ⚠ errors  ← webrockets best
```

**Summary:**
- Rust wins at low-to-medium concurrency (5–20 clients): +18–20% over Tornado
- webrockets wins at high concurrency (50+ clients): +24% over Tornado and more stable than Rust
- Tornado has the lowest minimum latency at low concurrency and zero setup friction
- For typical OVOS deployments (1–20 services), the Rust binary is fastest; for HiveMind hubs with 50+ nodes, webrockets is more stable

### webrockets Known Limitations

- `max_msg_size` config key is silently ignored — use a reverse proxy
- No TLS support — terminate TLS at a reverse proxy and forward plain WebSocket traffic

### Rust Configuration (via environment variables)

| Variable | Default | Description |
|---|---|---|
| `OVOS_BUS_HOST` | `0.0.0.0` | Bind address |
| `OVOS_BUS_PORT` | `8181` | TCP port |
| `OVOS_BUS_MAX_MSG_SIZE` | `25` MB | Maximum message payload size |

---

## Filter / Debug Mode

Set `websocket.filter: true` in `mycroft.conf` to log all message types before broadcasting. This does not affect message delivery.

```
DEBUG: <msg_type> source: [...] destination: [...]
       SESSION: {...}
```

Messages listed in `filter_logs` are excluded from the log to reduce noise (default: `["gui.status.request", "gui.page.upload"]`).

Deserialization failures are logged at DEBUG level and the raw payload is forwarded unchanged.

---

## Related Pages

- [Bus Client](900-bus_client.md) — `MessageBusClient`, `Message`, `Session` Python API
- [Bus Session](901-bus-session.md) — `Session`, `SessionManager`, `IntentContextManager`
- [ovos-core](102-core.md) — Intent service, skill manager
- [Configuration](110-config.md) — `mycroft.conf` configuration

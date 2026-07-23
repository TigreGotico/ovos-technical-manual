# Bus Service

!!! abstract "In a nutshell"
    The messagebus is the shared channel that lets all the separate parts of OpenVoiceOS talk to one another. Picture a group radio frequency: whatever one part says is heard by everyone tuned in, and each part simply pays attention to the messages meant for it and ignores the rest. There's no traffic controller deciding who gets what — every message goes to everybody. It's how the listener, the brain, the audio, and the screen all stay in sync. See the [Architecture Overview](architecture-overview.md) for how the pieces fit together, or the [Glossary](glossary.md) for unfamiliar terms.

??? info "📐 Formal specification"
    The `{type, data, context}` envelope, the `source`/`destination` routing keys, the `forward`/`reply`/`response` derivations, and the session carrier that rides in every message are all normative. See **[OVOS-MSG-1 — Bus Message](https://github.com/OpenVoiceOS/architecture/blob/dev/msg-1.md)**, **[OVOS-SESSION-1 — Session Carrier](https://github.com/OpenVoiceOS/architecture/blob/dev/session-1.md)**, **[OVOS-SESSION-2 — Session Lifecycle](https://github.com/OpenVoiceOS/architecture/blob/dev/session-2.md)**, and **[OVOS-BRIDGE-1 — Bus Bridge & Opaque Relay](https://github.com/OpenVoiceOS/architecture/blob/dev/bridge-1.md)** (how satellites relay messages across a [HiveMind](hivemind-agents.md) mesh), plus the [spec index](architecture-specs.md). This page describes the reference implementation; where it diverges from the spec, the spec wins.

The **messagebus** is the central nervous system of the OVOS platform. All services communicate by publishing and subscribing to typed `Message` objects through this central WebSocket broker.

**In plain terms:** every OVOS service (core, audio, listener, GUI) connects to one shared WebSocket. Whatever any service emits, every other service receives — there is no central router deciding who gets what. Services just listen for the message types they care about and ignore the rest.

---

## Overview

`ovos-messagebus` is a pure fan-out WebSocket broker. Every message received from one client is broadcast verbatim to every connected client. The bus performs no filtering, routing, or transformation.

```text
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

The broker itself has no logic beyond fan-out: it holds a list of open WebSocket connections and,
for every message any one client sends, writes that same message to every other open connection
(the Tornado I/O loop shown in the box runs this on its own daemon thread, so it does not block
whichever process embeds it). `ovos-core`, `ovos-audio`, and `ovos-gui` above are just three
example clients — anything speaking the same WebSocket protocol, including your own scripts, can
connect and take part on equal footing.

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
    "shared_connection": true,
    "max_msg_size": 25
  }
}

```

| Key | Default | Description |
|---|---|---|
| `host` | `"127.0.0.1"` | Bind address. The shipped default restricts to localhost; set `"0.0.0.0"` to bind all interfaces. |
| `port` | `8181` | TCP port. The GUI service uses a separate port (`18181`). |
| `route` | `"/core"` | WebSocket URL path. Full URL: `ws://host:port/core`. |
| `ssl` | `false` | Enable WSS/TLS. |
| `shared_connection` | `true` | When `true`, all skills share ovos-core's single bus connection. Set `false` to give each skill its own connection (so one skill cannot manipulate another's bus traffic). |
| `max_msg_size` | `25` | Max WebSocket frame size in megabytes. |

`filter` / `filter_logs` are also recognized (code-level defaults in the messagebus event
handler — `filter` off, `filter_logs` `["gui.status.request", "gui.page.upload"]`) but are not
part of the shipped `mycroft.conf` `websocket` section.

!!! danger "Security: the bus has no authentication — keep it local"
    The messagebus has **no authentication and no encryption**, and **any** client that can
    connect gets **full control** of the device (it can trigger skills, read everything on the
    bus, even run code via some plugins). Treat it like an open door to the whole assistant.

    - **Keep it bound to localhost** (`host: "127.0.0.1"`, the shipped default). Only set
      `"0.0.0.0"` if you fully control the network, and **never port-forward 8181** to the
      internet.
    - For **remote access** (satellites, phones, other rooms), don't expose the bus — use
      [HiveMind](hivemind-agents.md), which adds authentication and encryption on top.
    - This is also why the bus is a trust boundary: a malicious skill or plugin on the device
      already has full access, so only install software you trust.

---

## Implementation: `MessageBusEventHandler`

**Module:** `ovos_messagebus.event_handler.MessageBusEventHandler` — [`ovos_messagebus/event_handler.py`](https://github.com/OpenVoiceOS/ovos-messagebus/blob/dev/ovos_messagebus/event_handler.py)

Tornado `WebSocketHandler` subclass implementing the OVOS messagebus. All connected clients share a single module-level connection list (`client_connections`).

### Broadcast Behavior

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


    - `MessageBusEventHandler.on_message()` — [`ovos_messagebus/event_handler.py:50`](https://github.com/OpenVoiceOS/ovos-messagebus/blob/dev/ovos_messagebus/event_handler.py) — Core broadcast logic.


    - `load_message_bus_config()` — [`ovos_messagebus/load_config.py:31`](https://github.com/OpenVoiceOS/ovos-messagebus/blob/dev/ovos_messagebus/load_config.py) — Configuration loader using `ovos-config`.
    
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
    
    The shipped `mycroft.conf` sets `max_msg_size` to 25, so the effective default is
    25 MB (the code's hardcoded fallback of 10 only applies if the key is absent).
    Tornado closes the connection when a message exceeds this size.
    
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

See [Bus Client](core-libraries.md#ovos-bus-client) for the `Message` Python API.

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

The `Message` object provides the three derivations defined in [OVOS-MSG-1 §5](https://github.com/OpenVoiceOS/architecture/blob/dev/msg-1.md) (the spec mandates the resulting message *shape*, not the method names):

- `.reply(msg_type, data)` — swap `source`↔`destination`, preserving context (MSG-1 §5.2)


- `.forward(msg_type, data)` — copy context verbatim under a new type (MSG-1 §5.1)


- `.response(data)` — shorthand for `reply(self.msg_type + ".response", ...)` (MSG-1 §5.3)

There is **no** central correlation/in-reply-to mechanism: messages are fully async and self-contained, and an asker that wants to match a `.response` back to its request does so itself, keyed on the `session` (MSG-1 §5.4).

---

## Key Message Categories

### Core / Intent Pipeline

Topic names below are the canonical spec names ([OVOS-PIPELINE-1 §9](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)); the legacy name is shown where current code still emits it. Both names are usable on the wire — see [Namespace migration](#namespace-migration) below for how `ovos-bus-client` bridges the two.

| Message type | Publisher | Consumers |
|---|---|---|
| `ovos.utterance.handle` (legacy: `recognizer_loop:utterance`) | `ovos-dinkum-listener` | the orchestrator (`ovos-core`) |
| `ovos.utterance.speak` (legacy: `speak`) | handler / skill | `ovos-audio` |
| `ovos.intent.unmatched` (legacy: `complete_intent_failure`) | the orchestrator | fallback handlers |
| `ovos.utterance.handled` | the orchestrator | GUI clients (universal end-marker, §9.5) |

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

### Connectivity / [PHAL](phal.md)

| Message type | Publisher | Consumers |
|---|---|---|
| `mycroft.network.connected` | `ovos-PHAL` | `ovos-core`, skills |
| `mycroft.internet.connected` | `ovos-PHAL` | `ovos-core`, skills |

---

## Namespace migration

The [Formal Specifications](architecture-specs.md) rename many bus topics into
the `ovos.*` namespace — for example `recognizer_loop:utterance` →
`ovos.utterance.handle`, `mycroft.skill.handler.*` → `ovos.intent.handler.*`,
`complete_intent_failure` → `ovos.intent.unmatched`. Renaming a topic across an
ecosystem of independently-released repos cannot happen in one coordinated step,
so **`ovos-bus-client` migrates automatically and incrementally** — the legacy
and the new names interoperate transparently while the ecosystem moves over.

The canonical legacy ↔ spec topic map lives in the `NamespaceTranslator` from
[`ovos-spec-tools`](spec-tooling.md), and the bus client applies it in two
orthogonal directions, both **on by default**:

- **emit** — a migrated message is *dual-sent* on **both** the legacy and the
  `ovos.*` topic. The mirrored copy is reshaped into the counterpart topic's
  payload shape (identity for payload-compatible renames; a per-topic transform
  where the shape changed), so a consumer on either topic receives it in *its*
  expected shape.
- **listen** — subscribing to *either* name (`bus.on(...)`) also subscribes to
  its counterpart, with **de-duplication** so a handler that would match both
  fires exactly once.

The result: a producer and a consumer can each switch from a legacy topic to its
`ovos.*` spec name **in any order, with no coordination** — there is no flag day.
A repo that has fully adopted `ovos.*` keeps working against one that has not,
and vice-versa.

### Turning the bridges off

Each direction is independently controllable (default `true`), via environment
variable or bus configuration:

| Direction | Env var | Config key | Effect |
|---|---|---|---|
| modernize | `OVOS_BUS_MODERNIZE` | `modernize` | emitting a **legacy** topic also emits the `ovos.*` one |
| emit_legacy | `OVOS_BUS_EMIT_LEGACY` | `emit_legacy` | emitting an **`ovos.*`** topic also emits the legacy one |

A deployment whose components all speak `ovos.*` can set `emit_legacy=false` to
drop the legacy copies (and the extra bus traffic); one with no legacy producers
left can also disable `modernize`. Until then, leave both on — that is what keeps
adoption gradual and safe.

!!! note "Bridged ≠ conformant"
    [`ovos-test-harness`](spec-tooling.md) asserts spec behavior on the
    canonical `ovos.*` topics. A component becomes *spec-conformant* once it
    speaks `ovos.*` directly; the bridge keeps it **interoperable** in the
    meantime, it does not make it conformant.

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
    Pluggable high-performance backends are in development. The work
    keeps **Tornado** as the default reference server and adds two
    optional alternatives, benchmarked side by side with `benchmark/run_benchmark.py` at four
    load levels (5 / 20 / 50 / 100 concurrent clients):

    - **webrockets** — a high-performance websocket backend, written in Python. Tracked in
      [ovos-messagebus#51](https://github.com/OpenVoiceOS/ovos-messagebus/pull/51).
    - **Rust** — the [`ovos-rust-messagebus`](https://github.com/OscillateLabsLLC/ovos-rust-messagebus)
      server, run in place of the Python process.

    Throughput vs the Tornado baseline, measured with the included benchmark script:

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

```text
DEBUG: <msg_type> source: [...] destination: [...]
       SESSION: {...}

```

Messages listed in `filter_logs` are excluded from the log to reduce noise (default: `["gui.status.request", "gui.page.upload"]`).

When `filter` is off (the default), the bus never deserializes messages — it emits and re-broadcasts the raw frame as-is. Deserialization only happens in `filter` mode for the log line; if a frame fails to deserialize there, it is dropped (not logged, not re-broadcast).

---

## Bus recipes

A few small, runnable patterns for talking to a live bus directly, without going through a skill.

### Connect, emit, and wait for a response

```python
from ovos_bus_client import MessageBusClient, Message

bus = MessageBusClient()
bus.run_in_thread()  # connects on a background daemon thread

# fire-and-forget
bus.emit(Message("ovos.utterance.handle", {"utterances": ["what time is it"], "lang": "en-us"}))

# request/response: send a message, then wait for a specific reply type
response = bus.wait_for_response(
    Message("ovos.session.sync"),
    reply_type="ovos.session.update_default",
    timeout=3.0,
)
if response is not None:
    print(response.data)

bus.close()
```

`MessageBusClient()` with no arguments reads `host`/`port`/`route` from `mycroft.conf`'s
`websocket` section (see [Configuration](#configuration) above). `run_in_thread()` starts the
WebSocket loop on a daemon thread so the call returns immediately; `wait_for_response` blocks the
calling thread until a message of `reply_type` arrives or the timeout elapses, returning `None` on
timeout.

### From the command line

The [`ovos-bus-client` CLI tools](cli-tools.md#talking-to-a-running-ovos-ovos-bus-client) wrap
the same client for quick, no-code interaction with a running assistant:

- `ovos-say-to "what time is it"` — inject an utterance as if spoken.
- `ovos-listen` — trigger listening, as if the wake word fired.
- `ovos-speak "hello"` — make OVOS speak a phrase.

### Watching the bus live

For interactively inspecting every message flowing across the bus (useful when a recipe above
isn't behaving as expected), run `ovos-busmon` — a terminal viewer for live bus traffic. It
subscribes like any other client and prints each message as it is broadcast.

---

## Related Pages

- [Bus Client](core-libraries.md#ovos-bus-client) — `MessageBusClient`, `Message`, `Session` Python API


- [Bus Session](session.md) — `Session`, `SessionManager`, `IntentContextManager`


- [ovos-core](core.md) — Intent service, skill manager


- [Configuration](config.md) — `mycroft.conf` configuration

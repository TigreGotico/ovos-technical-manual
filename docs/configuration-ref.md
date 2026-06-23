# Configuration

!!! abstract "In a nutshell"
    Settings tell OVOS how its parts should behave and how to find each other, much like the preferences screen on a phone. This is a developer reference listing those settings and their defaults; the good news is that everything comes with sensible defaults, so most people never need to change anything here. It is mainly for people setting up or fine-tuning a system. See the [Glossary](glossary.md).

Connection parameters are loaded from `mycroft.conf` via `ovos-config`. All values have sensible defaults for local development.

## MessageBus (Core)

Read by `load_message_bus_config()` from the `websocket` section.

```json
{
  "websocket": {
    "host": "127.0.0.1",
    "port": 8181,
    "route": "/core",
    "ssl": false
  }
}

```

| Key | Default | Description |
|---|---|---|
| `host` | `"127.0.0.1"` | MessageBus host |
| `port` | `8181` | MessageBus port |
| `route` | `"/core"` | WebSocket route |
| `ssl` | `false` | Enable WSS |
| `shared_connection` | `true` | If true, each skill gets its own websocket connection |
| `max_msg_size` | `25` | Reject bus messages larger than this (MB) |

`load_message_bus_config()` returns a `MessageBusConfig` namedtuple with exactly four fields: `host`, `port`, `route`, `ssl`. Other `websocket.*` keys are read directly from the merged config by the components that use them.

## GUI Bus

Read by `load_gui_message_bus_config()` from the `gui` section. Note that the
default `mycroft.conf` defines the GUI socket under a **separate** `gui_websocket`
section (`host: "0.0.0.0"`, `base_port: 18181`, `route: "/gui"`); the loader reads
`gui.host`/`gui.port`/`gui.route`, which are absent by default, so it falls back to
the hardcoded values below.

```json
{
  "gui": {
    "disable_gui": false
  },
  "gui_websocket": {
    "host": "0.0.0.0",
    "base_port": 18181,
    "route": "/gui",
    "ssl": false
  }
}

```

| Key | Default (loader fallback) | Description |
|---|---|---|
| `host` | `"127.0.0.1"` | GUI bus host (read from `gui.host`) |
| `port` | `18181` | GUI bus port (read from `gui.port`) |
| `route` | `"/"` | WebSocket route (read from `gui.route`) |
| `ssl` | `false` | Enable WSS |
| `disable_gui` | `false` | If true, suppresses GUI bus messages |

## Session

Read by `Session.__init__` from the `session` section.

```json
{
  "session": {
    "ttl": -1
  }
}

```

| Key | Default | Description |
|---|---|---|
| `ttl` | `-1` | Session TTL in seconds. `-1` = never expires. |

## Context (Intent Context Manager)

Read by `IntentContextManager.__init__` from the `context` section.

```json
{
  "context": {
    "timeout": 2,
    "max_frames": 3,
    "greedy": false,
    "keywords": []
  }
}

```

| Key | Default | Description |
|---|---|---|
| `timeout` | `2` | Minutes before a context frame expires |
| `max_frames` | `3` | Max frames of context to keep |
| `greedy` | `false` | Inject all entities, not just tracked keywords |
| `keywords` | `[]` | Adapt keyword names to automatically track as context |

## Loading Config Programmatically

```python
from ovos_bus_client.conf import (
    load_message_bus_config,
    load_gui_message_bus_config,
    client_from_config,
    MessageBusClientConf,
)

# From mycroft.conf
config = load_message_bus_config()

# config.host, config.port, config.route, config.ssl

# Override specific keys
config = load_message_bus_config(host="192.168.1.100", port=9000)

# From a standalone JSON file (useful in embedded setups)
bus = client_from_config(subconf="core", file_path="/etc/mycroft/bus.conf")

```

`/etc/mycroft/bus.conf` format:

```json
{
  "core": {"route": "/core", "port": "8181"},
  "gui":  {"route": "/gui",  "port": "18181"}
}

```

## Environment / Remote Config

Since connection parameters come from `ovos-config`, they inherit its full config stack: XDG user config overrides system defaults, and remote config can be pushed via `mycroft.skills.settings.changed`. See `ovos-config` documentation for the full config resolution order.

---

*Source code: [OpenVoiceOS/ovos-bus-client](https://github.com/OpenVoiceOS/ovos-bus-client).*

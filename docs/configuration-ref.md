# Configuration

Connection parameters are loaded from `mycroft.conf` via `ovos-config`. All values have sensible defaults for local development.

## MessageBus (Core)

Read by `load_message_bus_config()` from the `websocket` section.

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

| Key | Default | Description |
|---|---|---|
| `host` | `"127.0.0.1"` | MessageBus host |
| `port` | `8181` | MessageBus port |
| `route` | `"/core"` | WebSocket route |
| `ssl` | `false` | Enable WSS |
| `secret_key` | `null` | AES encryption key. If set, all messages are encrypted. |
| `allow_unencrypted` | `true` | When `secret_key` is set, whether to accept plaintext messages. Set to `false` to enforce encryption. |

## GUI Bus

Read by `load_gui_message_bus_config()` from the `gui` section.

```json
{
  "gui": {
    "host": "127.0.0.1",
    "port": 18181,
    "route": "/",
    "ssl": false,
    "disable_gui": false
  }
}

```

| Key | Default | Description |
|---|---|---|
| `host` | `"127.0.0.1"` | GUI bus host |
| `port` | `18181` | GUI bus port |
| `route` | `"/"` | WebSocket route |
| `ssl` | `false` | Enable WSS |
| `disable_gui` | `false` | If true, `GUIInterface.gui_disabled` returns True |

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
  "gui":  {"route": "/gui",  "port": "8811"}
}

```

## Environment / Remote Config

Since connection parameters come from `ovos-config`, they inherit its full config stack: XDG user config overrides system defaults, and remote config can be pushed via `mycroft.skills.settings.changed`. See `ovos-config` documentation for the full config resolution order.

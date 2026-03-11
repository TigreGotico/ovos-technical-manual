# PHAL — Platform/Hardware Abstraction Layer

PHAL (Platform/Hardware Abstraction Layer) provides a plugin-based system for integrating
hardware-specific and platform-level functionality into OVOS. PHAL plugins run as
independent services alongside the core voice assistant, receive the OVOS MessageBus
client at construction, and may listen to or emit any bus event.

Two services are provided:

| Service | Entry point | Config section | Default enable | Privilege |
|---|---|---|---|---|
| `PHAL` | `opm.phal` | `mycroft.conf["PHAL"]` | Auto (validator + not `enabled: false`) | Current user |
| `AdminPHAL` | `opm.phal.admin` | `mycroft.conf["PHAL"]["admin"]` | Opt-in (`"enabled": true` required) | Root / privileged |

```
┌──────────────────────────────────────────────────────┐
│  ovos-core  /  ovos-audio  /  skills                 │
│           (OVOS MessageBus)                          │
└──────────────┬───────────────────────────────────────┘
               │
      ┌────────┴─────────────────────────────────────┐
      │  PHAL  (user-space)                          │
      │    ovos-PHAL-plugin-alsa                     │
      │    ovos-PHAL-plugin-network-manager          │
      │    ovos-PHAL-plugin-wifi-setup               │
      │    …                                         │
      └────────────────────────────────────────────┬─┘
                                                   │
                                           ┌───────┴───────┐
                                           │  AdminPHAL    │
                                           │  (root)       │
                                           │  plugin-mk2   │
                                           │  plugin-system│
                                           └───────────────┘
```

---

## PHAL Service

**Module:** `ovos_PHAL.service.PHAL`

```python
from ovos_PHAL import PHAL

phal = PHAL(
    config=None,      # dict from mycroft.conf["PHAL"], or None to auto-read
    bus=None,         # MessageBusClient; created automatically if None
    skill_id="PHAL",
    on_ready=...,
    on_error=...,
    on_stopping=...,
    on_started=...,
    on_alive=...,
    watchdog=lambda: None
)
phal.start()     # load_plugins(), set ProcessStatus to ready
phal.shutdown()  # set ProcessStatus to stopping
```

### Plugin loading rules

`load_plugins()` iterates over all plugins discovered via `find_phal_plugins()` (entry
point group `opm.phal`) and applies these rules in order:

1. **Admin-only check** — if the plugin name appears in `admin_config`, skip it (it will
   be loaded by `AdminPHAL` instead).
2. **Explicit disable** — if `config.get("enabled") is False`, skip.
3. **Validator** — if the plugin class has a `validator` attribute, call
   `plug.validator.validate(config)`:
   - Returns `True` → load
   - Returns `False` → silently skip (hardware not present)
   - Raises exception → skip, log error
4. **No validator** — defaults to enabled; only `enabled: false` can disable.
5. **Instantiation** — `plug(bus=self.bus, config=config)`; stored in `self.drivers[name]`.

### ProcessStatus lifecycle

| State | When |
|---|---|
| `alive` | Service object created |
| `started` | `start()` called |
| `ready` | All plugins loaded |
| `error` | Exception during `load_plugins()` |
| `stopping` | `shutdown()` called |

### Configuration

```json
{
  "PHAL": {
    "ovos-PHAL-plugin-alsa": {},
    "ovos-PHAL-plugin-display-manager-ipc": {
      "enabled": true
    },
    "ovos-PHAL-plugin-gpio": {
      "enabled": false
    }
  }
}
```

| Config key | Effect |
|---|---|
| `"enabled": false` | Explicitly disable this plugin |
| `"enabled": true` | Force-enable even if validator would skip |
| Any other keys | Passed as `config` to the plugin constructor |

Plugins with a passing validator and no `enabled: false` are loaded automatically —
no config entry is needed just to enable a plugin.

---

## AdminPHAL Service

**Module:** `ovos_PHAL.admin.AdminPHAL`

A subclass of `PHAL` that loads admin-privilege plugins. Run as `root` or with the
hardware capabilities required by its plugins.

```python
from ovos_PHAL import AdminPHAL

admin = AdminPHAL(
    config=None,
    bus=None,
    skill_id="PHAL.admin",
    ...
)
```

```bash
# Typically run via systemd as root
sudo ovos_PHAL_admin
```

### Key differences from `PHAL`

| | `PHAL` (user) | `AdminPHAL` (admin) |
|---|---|---|
| Entry point group | `opm.phal` | `opm.phal.admin` |
| Config section | `PHAL` | `PHAL.admin` |
| Default enable | Yes (validator + not `enabled: false`) | **No — requires `"enabled": true`** |
| Skip logic | Skips plugins in `admin_config` | Skips plugins in `user_config` |

### Security model

Admin plugins are intended for hardware requiring elevated permissions: I²C, SPI, GPIO,
system power management, thermal control. The explicit `enabled: true` requirement is a
security boundary — installed-but-unconfigured admin plugins never run accidentally.
Skills and the core pipeline never run as root.

### Configuration

```json
{
  "PHAL": {
    "admin": {
      "ovos-PHAL-plugin-system": {
        "enabled": true
      },
      "ovos-PHAL-plugin-mk2": {
        "enabled": true,
        "some_option": "value"
      }
    }
  }
}
```

---

## Writing PHAL Plugins

### Base class

```python
from ovos_plugin_manager.templates.phal import PHALPlugin

class MyHardwarePlugin(PHALPlugin):
    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, config=config)
        # hardware setup
        self.bus.on("mycroft.stop", self.handle_stop)

    def handle_stop(self, message):
        pass  # respond to bus events

    def shutdown(self):
        pass  # clean up hardware
```

The base class:
- Stores `self.bus` and `self.config`
- Provides `self.skill_id` (the entry point name)
- Calls `self.initialize()` at the end of `__init__` if defined

### Validator

Controls whether the plugin is auto-enabled:

```python
from ovos_plugin_manager.templates.phal import PHALPlugin, PHALValidator

class MyValidator(PHALValidator):
    @staticmethod
    def validate(config=None) -> bool:
        """Return True if hardware is present and plugin should load."""
        try:
            import smbus
            smbus.SMBus(1).read_byte(0x1a)
            return True
        except Exception:
            return False

class MyHardwarePlugin(PHALPlugin):
    validator = MyValidator
```

For admin plugins, the validator runs **after** the explicit `enabled: true` check.

### Entry points

**User PHAL plugin:**

```toml
# pyproject.toml
[project.entry-points."opm.phal"]
my-phal-plugin = "my_package:MyHardwarePlugin"
```

**Admin PHAL plugin:**

```toml
[project.entry-points."opm.phal.admin"]
my-admin-phal-plugin = "my_package:MyAdminPlugin"
```

**Dual registration** (plugin can run as either user or admin — the service that has the
plugin name in its config section loads it; the other skips it):

```toml
[project.entry-points."opm.phal"]
my-phal-plugin = "my_package:MyPlugin"

[project.entry-points."opm.phal.admin"]
my-phal-plugin = "my_package:MyPlugin"
```

### Plugin configuration

```json
{
  "PHAL": {
    "my-phal-plugin": {
      "enabled": true,
      "i2c_bus": 1,
      "brightness": 80
    }
  }
}
```

```python
class MyPlugin(PHALPlugin):
    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, config=config)
        self.brightness = self.config.get("brightness", 100)
```

### Lifecycle

- Set up bus listeners in `__init__`
- Provide a `shutdown()` method for clean teardown
- No hot-reload — configuration changes require restarting the PHAL service

---

## Choosing Between PHAL and a Skill

| Use PHAL when… | Use a Skill when… |
|---|---|
| Low-level system or hardware integration | Voice interactions and user-facing features |
| No voice trigger needed — reacts to hardware events | Responds to user utterances |
| Needs to run at startup regardless of voice activity | Should only activate when invoked |
| Requires root (`AdminPHAL`) | Always runs unprivileged |

In some cases both are appropriate: a PHAL plugin for backend hardware support and a
skill as a voice frontend.

![Should you use a skill or a PHAL plugin?](img/phal_or_skill.png)

---

## Available Plugins

| Plugin | Description |
|---|---|
| [ovos-PHAL-plugin-alsa](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-alsa) | Volume control |
| [ovos-PHAL-plugin-system](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-system) | Reboot, shutdown, factory reset (admin) |
| [ovos-PHAL-plugin-mk1](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk1) | Mycroft Mark 1 hardware integration |
| [ovos-PHAL-plugin-wifi-setup](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-wifi-setup) | Central Wi-Fi setup |
| [ovos-PHAL-plugin-gui-network-client](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-gui-network-client) | GUI-based Wi-Fi setup |
| [ovos-PHAL-plugin-balena-wifi](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-balena-wifi) | Wi-Fi hotspot setup |
| [ovos-PHAL-plugin-network-manager](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-network-manager) | Network Manager integration |
| [ovos-PHAL-plugin-ipgeo](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-ipgeo) | Geolocation using IP address |
| [ovos-PHAL-plugin-gpsd](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-gpsd) | Geolocation using GPS |
| [ovos-PHAL-plugin-respeaker-2mic](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-respeaker-2mic) | ReSpeaker 2-mic HAT support |
| [ovos-PHAL-plugin-respeaker-4mic](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-respeaker-4mic) | ReSpeaker 4-mic HAT support |
| [neon-phal-plugin-linear_led](https://github.com/NeonGeckoCom/neon-phal-plugin-linear_led) | LED control for Mark 2 |

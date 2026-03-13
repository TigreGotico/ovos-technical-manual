# PHAL — Platform/Hardware Abstraction Layer

PHAL (Platform/Hardware Abstraction Layer) provides a plugin-based system for integrating
hardware-specific and platform-level functionality into OVOS. PHAL plugins run as
independent services alongside the core voice assistant, receive the OVOS [MessageBus](bus-service.md)
client at construction, and may listen to or emit any bus event.

---

??? abstract "Technical Reference"

    - `PHAL.run()` — [`ovos_PHAL/service.py:35`](https://github.com/OpenVoiceOS/ovos-PHAL/blob/dev/ovos_PHAL/service.py) — Main service thread for user-level plugins.


    - `AdminPHAL.run()` — [`ovos_PHAL/admin.py:65`](https://github.com/OpenVoiceOS/ovos-PHAL/blob/dev/ovos_PHAL/admin.py) — Main service thread for privileged/root-level plugins.


    - `PHAL.load_plugins()` — [`ovos_PHAL/service.py:80`](https://github.com/OpenVoiceOS/ovos-PHAL/blob/dev/ovos_PHAL/service.py) — logic for discovery and validation of plugins via OPM.
    
    ---
    

## Overview

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

## Choosing Between PHAL and a [Skill](skill-design-guidelines.md)

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

# PHAL plugins Reference

| Plugin | Description |
|--------|-------------|
| [ovos-PHAL-plugin-network-manager](#ovos-phal-plugin-network-manager) | Provides the network manager interface for NetworkManager based plugins. |
| [ovos-PHAL-plugin-dotstar](#ovos-phal-plugin-dotstar) | **Compatible with** |
| [ovos-PHAL-plugin-wallpaper-manager](#ovos-phal-plugin-wallpaper-manager) | This PHAL plugin provides a central wallpaper management interface for homescreens and other desktops |
| [ovos-PHAL-plugin-ipgeo](#ovos-phal-plugin-ipgeo) | Autoconfigure default location based on ip address via [ip-api.com](https://ip-api.com) |
| [ovos-PHAL-sensors](#ovos-phal-sensors) | No description available |
| [ovos-PHAL-plugin-alsa](#ovos-phal-plugin-alsa) | controls system volume with alsa |
| [ovos-PHAL-plugin-mk2-v6-fan-control](#ovos-phal-plugin-mk2-v6-fan-control) | **Compatible with** |
| [ovos-PHAL-plugin-gpsd](#ovos-phal-plugin-gpsd) | No description available |
| [ovos-PHAL-plugin-mk1](#ovos-phal-plugin-mk1) | handles integration with the Mycroft Mark1 hardware |
| [ovos-PHAL-plugin-connectivity-events](#ovos-phal-plugin-connectivity-events) | No description available |
| [ovos-PHAL-plugin-camera](#ovos-phal-plugin-camera) | This plugin allows users to interact with cameras using OpenCV or libcamera, take snapshots, and serve video streams over HTTP. It also provides methods for handling camera operations via message bus events. |
| [ovos-PHAL-plugin-pulseaudio](#ovos-phal-plugin-pulseaudio) | controls system volume with pulseaudio |
| [ovos-PHAL-plugin-oauth](#ovos-phal-plugin-oauth) | Stable |
| [ovos-PHAL-plugin-system](#ovos-phal-plugin-system) | Provides system specific commands to OVOS. |
| [ovos-PHAL-plugin-hotkeys](#ovos-phal-plugin-hotkeys) | plugin for Keyboard hotkeys, define key combos to trigger bus events |
| [ovos-PHAL-plugin-termux](#ovos-phal-plugin-termux) | controls system volume with termux |

## ovos-PHAL-plugin-network-manager

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-network-manager](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-network-manager)


- **Description**: Provides the network manager interface for NetworkManager based plugins.

---

## ovos-PHAL-plugin-dotstar

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-dotstar](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-dotstar)


- **Description**: **Compatible with**

---

## ovos-PHAL-plugin-wallpaper-manager

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-wallpaper-manager](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-wallpaper-manager)


- **Description**: This PHAL plugin provides a central wallpaper management interface for homescreens and other desktops

---

## ovos-PHAL-plugin-ipgeo

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-ipgeo](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-ipgeo)


- **Description**: Autoconfigure default location based on ip address via [ip-api.com](https://ip-api.com)

---

## ovos-PHAL-sensors

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-sensors](https://github.com/OpenVoiceOS/ovos-PHAL-sensors)


- **Description**: No description available

---

## ovos-PHAL-plugin-alsa

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-alsa](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-alsa)


- **Description**: controls system volume with alsa

---

## ovos-PHAL-plugin-mk2-v6-fan-control

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk2-v6-fan-control](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk2-v6-fan-control)


- **Description**: **Compatible with**

---

## ovos-PHAL-plugin-gpsd

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-gpsd](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-gpsd)


- **Description**: No description available

---

## ovos-PHAL-plugin-mk1

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk1](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk1)


- **Description**: handles integration with the Mycroft Mark1 hardware

---

## ovos-PHAL-plugin-connectivity-events

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-connectivity-events](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-connectivity-events)


- **Description**: No description available

---

## ovos-PHAL-plugin-camera

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-camera](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-camera)


- **Description**: This plugin allows users to interact with cameras using OpenCV or libcamera, take snapshots, and serve video streams over HTTP. It also provides methods for handling camera operations via message bus events.

---

## ovos-PHAL-plugin-pulseaudio

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-pulseaudio](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-pulseaudio)


- **Description**: controls system volume with pulseaudio

---

## ovos-PHAL-plugin-oauth

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-oauth](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-oauth)


- **Description**: Handles OAuth authentication flows for OVOS skills and services.

---

## ovos-PHAL-plugin-system

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-system](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-system)


- **Description**: Provides system specific commands to OVOS.

---

## ovos-PHAL-plugin-hotkeys

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-hotkeys](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-hotkeys)


- **Description**: plugin for Keyboard hotkeys, define key combos to trigger bus events

---

## ovos-PHAL-plugin-termux

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-termux](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-termux)


- **Description**: controls system volume with termux

---


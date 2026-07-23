# PHAL — Platform/Hardware Abstraction Layer

!!! abstract "In a nutshell"
    PHAL is how OpenVoiceOS talks to the physical device it runs on — things like volume controls, Wi-Fi setup, buttons, LEDs, and other hardware. It works through small add-ons (plugins) that each handle one piece of hardware and quietly run in the background, so the assistant can adjust the speaker volume or set up a network connection without you saying a word. Some hardware needs extra system permissions, so PHAL comes in a regular version and a privileged "admin" version. If you're building your own hardware and want to write a PHAL plugin for it, see [Building Hardware on OVOS](hardware-integrators.md). New to the terms? See the [Glossary](glossary.md).

PHAL (Platform/Hardware Abstraction Layer) provides a plugin-based system for integrating
hardware-specific and platform-level functionality into OVOS. PHAL plugins run as
independent services alongside the core voice assistant, receive the OVOS [messagebus](bus-service.md)
client at construction, and may listen to or emit any bus event.

---

??? abstract "Technical Reference"

    - `PHAL.start()` — [`ovos_PHAL/service.py:97`](https://github.com/OpenVoiceOS/ovos-PHAL/blob/dev/ovos_PHAL/service.py) — Loads user-level plugins and reports `ProcessStatus` ready. `PHAL` is a plain object, not a thread.


    - `AdminPHAL.load_plugins()` — [`ovos_PHAL/admin.py:45`](https://github.com/OpenVoiceOS/ovos-PHAL/blob/dev/ovos_PHAL/admin.py) — Discovery/validation for privileged/root-level plugins (`find_admin_plugins`).


    - `PHAL.load_plugins()` — [`ovos_PHAL/service.py:67`](https://github.com/OpenVoiceOS/ovos-PHAL/blob/dev/ovos_PHAL/service.py) — discovery and validation of user plugins via OPM (`find_phal_plugins`).
    
    ---
    

## Overview

Two services are provided. Each discovers plugins from its own OPM entry-point group
and is launched by its own console script (`ovos_PHAL` / `ovos_PHAL_admin`):

| Service | OPM group | Console script | Config section | Default enable | Privilege |
|---|---|---|---|---|---|
| `PHAL` | `opm.phal` | `ovos_PHAL` | `mycroft.conf["PHAL"]` | Auto (validator + not `enabled: false`) | Current user |
| `AdminPHAL` | `opm.phal.admin` | `ovos_PHAL_admin` | `mycroft.conf["PHAL"]["admin"]` | Opt-in (`"enabled": true` required) | Root / privileged |

```text
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
   Note: the `PHALPlugin` base sets `validator = PHALValidator` by default, so most
   plugins do take the validator path. The default validator just returns
   `config.get("enabled", True) is True`; a subclass overrides `validate()` to add a
   real hardware probe.


5. **Instantiation** — `plug(bus=self.bus, config=config)`; stored in `self.drivers[name]`.

### ProcessStatus lifecycle

`start()` and `shutdown()` drive a `ProcessStatus` object (`ovos-utils`) that other
services can query over the bus:

| State | When |
|---|---|
| `started` | `start()` called (`set_started()`) |
| `ready` | `load_plugins()` returned without raising (`set_ready()`) |
| `error` | Exception during `load_plugins()` (`set_error()`) |
| `stopping` | `shutdown()` called (`set_stopping()`) |

The `alive` callback exists in the hook map but `PHAL.start()` does not call
`set_alive()`; the status goes straight to `started` then `ready`.

### Configuration

```json
{
  "PHAL": {
    "ovos-PHAL-plugin-alsa": {},
    "ovos-PHAL-plugin-dotstar": {
      "enabled": true
    },
    "ovos-PHAL-plugin-connectivity-events": {
      "enabled": false
    }
  }
}

```

| Config key | Effect |
|---|---|
| `"enabled": false` | Explicitly disable this plugin (skipped before the validator runs) |
| `"enabled": true` | Passed to the validator; the default validator treats it as enabled, but a custom `validate()` can still skip on missing hardware |
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
    # same on_ready / on_error / on_stopping / on_started / on_alive / watchdog
    # hooks as PHAL above
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
    def __init__(self, bus=None, name="MyHardwarePlugin", config=None):
        super().__init__(bus=bus, name=name, config=config)
        # hardware setup
        self.bus.on("mycroft.stop", self.handle_stop)

    def handle_stop(self, message):
        pass  # respond to bus events

    def shutdown(self):
        super().shutdown()  # unregisters the base enclosure handlers
        pass  # clean up hardware

```

The base class (`PHALPlugin`) is a `threading.Thread`. Key points:

- Stores `self.bus`, `self.config` and `self.name`. There is **no** `self.skill_id`
  attribute; when it emits events it derives a per-plugin id of the form
  `ovos.PHAL.<name>`.


- Its `__init__` calls `self.start()` itself — instantiating a plugin already runs
  its thread. Do all setup **before** `super().__init__()` returns, or guard against
  the thread already running.


- It auto-registers a large set of legacy enclosure (`enclosure.eyes.*`,
  `enclosure.mouth.*`) and `recognizer_loop:*` bus handlers; override the matching
  `on_*` methods to react to them. Call `super().shutdown()` to unregister them.

!!! note "Hardware-interface ABCs live in `ovos-hardware-helpers`"
    The abstract base classes that hardware PHAL plugins implement —
    `AbstractLed`, `AbstractFan`, and `AbstractSwitches` (plus a suite of ready-made
    LED animations) — live in the
    [`ovos-hardware-helpers`](https://github.com/OpenVoiceOS/ovos-hardware-helpers)
    library; subclass them there when writing a hardware PHAL plugin. See
    [Building Hardware on OVOS](hardware-integrators.md#writing-your-own-hardware-driver-abstractled-abstractswitches)
    for a worked example.

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
|--------|-------------|
| [ovos-PHAL-plugin-alsa](#ovos-phal-plugin-alsa) | Controls system volume with ALSA |
| [ovos-PHAL-plugin-pulseaudio](#ovos-phal-plugin-pulseaudio) | Controls system volume with PulseAudio |
| [ovos-PHAL-plugin-system](#ovos-phal-plugin-system) | Reboot, shutdown, factory reset, and other system commands (admin) |
| [ovos-PHAL-plugin-mk1](#ovos-phal-plugin-mk1) | Mycroft Mark 1 hardware integration |
| [ovos-PHAL-plugin-mk2-v6-fan-control](#ovos-phal-plugin-mk2-v6-fan-control) | Fan control for the Mycroft Mark 2 dev kit |
| [ovos-PHAL-plugin-dotstar](#ovos-phal-plugin-dotstar) | Dotstar/APA102 LED ring driver for Respeaker mic HATs and the Adafruit Voice Bonnet |
| [ovos-PHAL-plugin-respeaker-2mic](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-respeaker-2mic) | ReSpeaker 2-mic HAT support |
| [ovos-PHAL-plugin-respeaker-4mic](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-respeaker-4mic) | ReSpeaker 4-mic HAT support |
| [ovos-PHAL-plugin-wifi-setup](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-wifi-setup) | Central Wi-Fi setup |
| [ovos-PHAL-plugin-gui-network-client](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-gui-network-client) | GUI-based Wi-Fi setup |
| [ovos-PHAL-plugin-balena-wifi](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-balena-wifi) | Wi-Fi hotspot setup |
| [ovos-PHAL-plugin-network-manager](#ovos-phal-plugin-network-manager) | Provides the network manager interface for NetworkManager-based plugins |
| [ovos-PHAL-plugin-connectivity-events](#ovos-phal-plugin-connectivity-events) | Reports network connectivity changes to the messagebus |
| [ovos-PHAL-plugin-ipgeo](#ovos-phal-plugin-ipgeo) | Autoconfigure default location based on IP address via [ip-api.com](https://ip-api.com) |
| [ovos-PHAL-plugin-gpsd](#ovos-phal-plugin-gpsd) | Provides GPS location to OVOS via gpsd |
| [ovos-PHAL-plugin-camera](#ovos-phal-plugin-camera) | Interact with cameras using OpenCV or libcamera: snapshots, video streams over HTTP, and messagebus control |
| [ovos-PHAL-plugin-wallpaper-manager](#ovos-phal-plugin-wallpaper-manager) | Central wallpaper management interface for homescreens and other desktops |
| [ovos-PHAL-plugin-oauth](#ovos-phal-plugin-oauth) | Handles OAuth authentication flows for OVOS skills and services |
| [ovos-PHAL-plugin-hotkeys](#ovos-phal-plugin-hotkeys) | Keyboard hotkeys — define key combos to trigger bus events |
| [ovos-PHAL-sensors](#ovos-phal-sensors) | Exposes the OVOS device and its sensors to Home Assistant |

## ovos-PHAL-plugin-network-manager

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-network-manager](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-network-manager)


- **Description**: Provides the network manager interface for NetworkManager based plugins.

---

## ovos-PHAL-plugin-dotstar

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-dotstar](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-dotstar)


- **Description**: Dotstar/APA102 LED ring driver, compatible with the Respeaker 2/4/6/8-mic i2c HATs and the Adafruit Voice Bonnet

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


- **Description**: Exposes the OVOS device and its sensors to Home Assistant.

---

## ovos-PHAL-plugin-alsa

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-alsa](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-alsa)


- **Description**: controls system volume with alsa

---

## ovos-PHAL-plugin-mk2-v6-fan-control

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk2-v6-fan-control](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk2-v6-fan-control)


- **Description**: Fan control for the Mycroft Mark 2 dev kit

---

## ovos-PHAL-plugin-gpsd

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-gpsd](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-gpsd)


- **Description**: Provides GPS location to OVOS via gpsd.

---

## ovos-PHAL-plugin-mk1

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk1](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk1)


- **Description**: handles integration with the Mycroft Mark1 hardware

---

## ovos-PHAL-plugin-connectivity-events

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-connectivity-events](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-connectivity-events)


- **Description**: Reports network connectivity changes to the messagebus.

---

## ovos-PHAL-plugin-camera

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-PHAL-plugin-camera](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-camera)


- **Description**: This plugin allows users to interact with cameras using OpenCV or libcamera, take snapshots, and serve video streams over HTTP. It also provides methods for handling camera operations via messagebus events.

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


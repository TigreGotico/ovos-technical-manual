# Building Hardware on OVOS

!!! abstract "In a nutshell"
    If you're designing a physical gadget — a smart speaker, a robot, a Halloween prop, a
    custom kiosk — and want it to listen and talk using OVOS, most of the software underneath
    it doesn't care what board you're running on. What *does* care about specific hardware is
    a small layer called [PHAL](phal.md) (Platform/Hardware Abstraction Layer), which is also
    where you plug in your own LEDs, buttons, and sensors. This page is the map for makers:
    what's generic vs Raspberry-Pi-specific, how to write a driver for your own LED ring or
    button panel, what resources your device actually needs, and what OVOS does and doesn't
    do for you around over-the-air updates and on-screen UI.

---

## SBC-agnostic vs Raspberry-Pi-only

Most of the OVOS stack is just Python talking to ALSA (Linux's standard sound system) and the
network — it runs the same on a Raspberry Pi, an x86 mini-PC, an Orange Pi, or a laptop. A
handful of pieces are genuinely tied to specific Raspberry-Pi/Mycroft hardware:

| Component | Portability | Why |
|---|---|---|
| `ovos-messagebus`, `ovos-core`, `ovos-audio`, `ovos-dinkum-listener`, `ovos-PHAL`, skills | **Any Linux SBC / PC** | Pure Python + ALSA + network; no board-specific code |
| Wake word / STT / TTS / VAD plugins | **Any Linux SBC / PC** | CPU (or GPU) inference; heavier models just need more RAM/CPU |
| [`ovos-i2csound`](i2c-sound.md) | **Raspberry Pi (i2c HATs)** | Auto-detects and configures i2c sound HATs specific to the Pi's i2c bus layout |
| [`VocalFusionDriver`](mark2.md#the-ovos-kernel-driver-vocalfusiondriver) | **Raspberry Pi (SJ201/Mark 2 hardware)** | Out-of-tree kernel module + device-tree overlays for the XMOS VocalFusion DSP mic array |
| [`ovos-PHAL-plugin-mk1`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk1), [`ovos-PHAL-plugin-mk2-v6-fan-control`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk2-v6-fan-control) | **Mycroft Mark 1 / Mark 2 only** | Drive specific hardware that only exists on those boards |
| [raspOVOS](install-raspovos.md) image | **Raspberry Pi only** | It's a Raspberry Pi OS image |

If you're designing new hardware, the practical takeaway is: **use a generic microphone/ALSA
sound card and a plain Linux install** (the [`ovos-installer`](ovos-installer.md) works the
same way on a Pi or an x86 box), and only reach for the Pi-specific pieces above if you are
specifically reusing an i2c HAT or the SJ201 board design.

---

## Writing your own hardware driver: `AbstractLed` / `AbstractSwitches`

`ovos-hardware-helpers` also ships an `AbstractFan` base (covered below) for
fan-speed and thermal-shutdown control.

!!! note "Illustrative skeletons"
    The `MyRingLed` and switch examples below are illustrative skeletons, not complete,
    copy-pasteable drivers — real hardware needs the actual bus/SPI/GPIO calls for your board
    filled in where the example stops short.

Custom LEDs and buttons are the two things almost every maker adds. Rather than writing your
own bus-message plumbing, subclass the abstract base classes in
[`ovos-hardware-helpers`](https://github.com/OpenVoiceOS/ovos-hardware-helpers) and wrap the
result in a [PHAL plugin](phal.md#writing-phal-plugins) — see that page for the entry-point and
validator mechanics; this section is about the hardware interface itself.

### LEDs: `AbstractLed`

```python
from ovos_hardware_helpers.led import AbstractLed


class MyRingLed(AbstractLed):
    """Minimal LED ring driver — replace set_led/fill/show with real hardware calls."""

    def __init__(self, num_leds: int = 12):
        self._num_leds = num_leds
        self._state = [(0, 0, 0)] * num_leds

    @property
    def num_leds(self) -> int:
        return self._num_leds

    @property
    def capabilities(self) -> dict:
        return {"num_leds": self._num_leds, "brightness_control": True}

    def set_led(self, led_idx: int, color: tuple, immediate: bool = True):
        self._state[led_idx] = color
        if immediate:
            self.show()

    def fill(self, color: tuple):
        self._state = [color] * self._num_leds
        self.show()

    def show(self):
        # Push self._state to real hardware here (SPI/I2C/GPIO write).
        pass

    def shutdown(self):
        self.fill((0, 0, 0))
```

For a full, real-hardware reference implementation, see
[`ovos-PHAL-plugin-dotstar`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-dotstar) — it wraps
a DotStar (APA102) LED strip's SPI driver in an `AbstractLed` subclass and the surrounding PHAL
plugin/validator boilerplate.

`AbstractLed` also ships a `scale_brightness(color_val, bright_val)` static helper for dimming,
and the library's `eval_color()` helper (in `ovos_hardware_helpers.led`) turns a color name,
hex string, or RGB tuple into a normalized color object using
[`ovos-color-parser`](color-parser.md) — useful if you want your plugin to accept
`"Mycroft blue"` as well as `(0, 168, 255)`.

### Buttons: `AbstractSwitches`

```python
from ovos_hardware_helpers.switches import AbstractSwitches


class MyButtonPanel(AbstractSwitches):
    @property
    def capabilities(self) -> dict:
        return {"volume": True, "mute": True, "action": True}

    def on_action(self):
        pass  # e.g. bus.emit(Message("mycroft.mic.listen"))

    def on_vol_up(self):
        pass

    def on_vol_down(self):
        pass

    def on_mute(self):
        pass

    def on_unmute(self):
        pass

    def shutdown(self):
        pass
```

### Fans: `AbstractFan`

```python
from ovos_hardware_helpers.fan import AbstractFan


class MyFanController(AbstractFan):
    def set_fan_speed(self, percent: int):
        pass  # drive a PWM pin, 0-100

    def get_fan_speed(self) -> int:
        return 0  # last commanded 0-100 speed

    def get_cpu_temp(self) -> float:
        return -1.0  # celsius, or -1.0 if not available

    def shutdown(self):
        pass  # set the fan to a reasonable speed before exit
```

Wire an instance of any of these classes up inside a `PHALPlugin.__init__`, polling your GPIO/i2c
hardware on a background thread (or driving it from an interrupt callback) and calling the
matching `on_*`/`set_led`/`set_fan_speed` methods. See [PHAL: Writing PHAL Plugins](phal.md#writing-phal-plugins)
for the full plugin lifecycle, validator, and entry-point registration.

---

## Resource footprint

There is no published, current benchmark of OVOS's CPU/RAM footprint across hardware targets —
treat any specific number you see elsewhere with suspicion, since it depends entirely on which
STT/TTS/wake-word plugins you pick (a tiny wake-word model and a cloud STT server cost almost
nothing locally; a local Whisper model needs real CPU or a GPU). Rather than repeat an unverified
number, measure it on your own target hardware:

```bash
# Memory: sum RSS of every OVOS process
ps -u ovos -o rss,comm --sort=-rss | grep -E 'ovos|mycroft'

# Or per systemd unit, if using the units above
systemctl --user status ovos-skills.service | grep Memory

# CPU, live, while you talk to it
top -b -n 1 -u ovos
```

Run the same commands idle and mid-conversation; the delta tells you what your wake-word/STT/TTS
choice actually costs on your board, which matters far more than any generic published figure.

---

## Over-the-air updates

!!! warning "OVOS does not ship an OTA update system"
    There is no built-in over-the-air update mechanism, update server, or delta-update
    protocol. Updating an OVOS device means running `pip`/`uv` against a
    [release channel's constraints file](release-channels.md#choosing-a-release-channel), the
    same command whether you run it by hand over SSH or push it out via your own fleet
    tooling (Ansible, a custom MDM agent, a cron job). See
    [Production Operations: staged upgrades](production-operations.md#staged-upgrades-and-rollback)
    for the update-and-rollback pattern. If your product needs image-level OTA (swapping the
    whole OS image, not just Python packages), you will need to bring your own solution
    (e.g. Mender, SWUpdate, RAUC) — OVOS has no opinion on that layer.

---

## Screens: where things stand today

If your device has a display, [`ovos-gui`](gui-service.md) provides the protocol and
[`ovos-shell`](ovos-shell.md) (or a Qt5/QML client speaking the same
[GUI protocol](gui-protocol.md)) renders it, with a [homescreen](homescreen.md) skill as the
default idle view — this part is real and works today on Linux desktops and the
[GUI-capable installer path](ovos-installer.md). If you are starting a from-scratch hardware
design, plan for a voice-first experience with an optional screen rather than the other way
around: the GUI layer is functional but is going through active rework, so treat it as a nice
extra your device can degrade gracefully without, not a hard dependency for launch.

---

## See also

- [PHAL — Platform/Hardware Abstraction Layer](phal.md) — the plugin system this page builds on
- [i2c Sound & Audio Setup](i2c-sound.md) — Raspberry Pi HAT-specific audio bring-up
- [Mycroft Mark 2 Hardware](mark2.md) — a worked example of a full custom-board bring-up
- [Production Operations](production-operations.md) — fleet management once your hardware exists

## Further reading

- [Running HiveMind Player on ArkOS with the R36S](https://blog.openvoiceos.org/posts/2025-10-11-r36s) — OVOS blog

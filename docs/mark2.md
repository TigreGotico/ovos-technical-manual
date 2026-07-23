# Mycroft Mark 2 Hardware

!!! abstract "In a nutshell"
    The **Mark 2** is Mycroft's second smart-speaker — a Raspberry Pi 4 with a touchscreen and a
    custom audio board (the **SJ201** HAT). Unlike the faceplate-only [Mark 1](mark1.md), it runs
    the *complete* OVOS software stack plus a graphical shell. Getting its hardware working takes
    a custom kernel driver, a firmware (EEPROM) update, and board-specific tweaks, so the Mark 2
    is a **best-effort, not-actively-maintained legacy platform** — even more so than the
    [Mark 1](mark1.md). There are also **two slightly different boards** (an early "dev kit" and
    the retail unit) that need slightly different setup. This page documents the OVOS way to set
    it up (via the [ovos-installer](ovos-installer.md)), the kernel driver involved, and the one
    thing you must **not** do — mix in Neon packages (see the warning below). Audio, fan control,
    the touchscreen, and the hardware buttons all work through the installer today; the LED ring
    is the one piece of the SJ201 board the installer path doesn't drive yet. New to the terms
    here? See the [Glossary](glossary.md).

The **Mycroft Mark 2** is built around a **Raspberry Pi 4** carrying the **SJ201** HAT — an
audio board with a far-field microphone array (an XMOS VocalFusion DSP), a TAS5806 speaker
amplifier, an LED ring, a fan, and hardware buttons — behind a square IPS touchscreen.

!!! note "Hardware support was left in rough shape"
    Mycroft's hardware bring-up for the Mark 2 was incomplete and poorly documented. Making the
    SJ201 work needs a **custom out-of-tree kernel module**, **device-tree overlays**, a
    **bootloader/EEPROM firmware update**, and a **separate amplifier init step** — none of which
    is standard Raspberry Pi practice. OVOS has reconstructed a working path, but expect rough
    edges and treat everything below as best-effort.

---

## Two boards: dev kit vs retail Mark II

There are **two SJ201 revisions**, and they need slightly different setup:

| | **Dev kit** (early backers) | **Retail Mark II** |
|---|---|---|
| SJ201 board | revision 6 | revision 10 |
| Tell-tale | exposes an `attiny1614` micro-controller on the i2c bus | no `attiny1614` |
| Fan control | needs the [`ovos-PHAL-plugin-mk2-v6-fan-control`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk2-v6-fan-control) plugin | PWM fan handled by a device-tree overlay |

The [ovos-installer](ovos-installer.md) tells them apart automatically by probing the i2c bus: a
Raspberry Pi 4 with the `tas5806` amplifier present is treated as the "Mark 2 family", and if an
`attiny1614` is *also* present it is treated as the **dev kit**.

---

## Support status — best-effort legacy

When Mycroft AI shut down, **Neon AI** officially took over the Mark 2: they continued selling
the devices and publish their own Mark 2 software (see [Neon's hardware
packages](#neon-mark-2-packages-official-but-separate) below). OVOS still runs on the Mark 2 but
treats it as a **best-effort, not actively maintained legacy platform**.

!!! danger "Do not install Neon packages on an OVOS system (and vice-versa)"
    Neon is **downstream of OVOS** and runs on a **completely different release cycle**: Neon
    packages **pin older versions of OVOS packages**. If you install Neon's Mark 2 packages on
    top of an OVOS install, `pip` will happily **downgrade your OVOS packages** to satisfy those
    pins, leaving you in a broken, half-downgraded, non-functional state that is very hard to
    untangle.

    Pick **one** stack and stay on it. The OVOS path is the [ovos-installer](ovos-installer.md),
    which uses **only OVOS repositories** — it pulls in **no** Neon packages. If you want Neon's
    Mark 2 software instead, use their image/packages on their own and don't mix OVOS packages
    into it.

---

## How OVOS runs on the Mark 2

Unlike the [Mark 1](mark1.md), the Mark 2 has a real display, so it runs the **graphical**
OVOS experience:

- The standard [core services](architecture-overview.md) run exactly as on any other device —
  there is no Mark 2 fork of `ovos-core`.
- The screen is driven by the [GUI service](gui-service.md) feeding the
  **[`ovos-shell`](ovos-shell.md)** Qt5/[Kirigami](qt5-gui.md) application. The
  [ovos-installer](ovos-installer.md) installs `ovos-shell` on Mark 2 devices so they keep a
  screen until the [GUI rework](gui-adapters.md) replacement lands.
- The microphone is read through the **`ovos-microphone-plugin-sounddevice`** plugin (the
  installer tunes its block size and latency for the SJ201), *not* an ALSA/i2c helper.

---

## What the ovos-installer does for the Mark 2

When the [ovos-installer](ovos-installer.md) detects Mark 2 hardware it applies a dedicated
`ovos_hardware_mark2` role. (On the Mark 2 you must use the installer's **`virtualenv`** method —
the container method is not supported there.) That role:

1. **Builds and installs the OVOS kernel driver.** It clones
   [`VocalFusionDriver`](#the-ovos-kernel-driver-vocalfusiondriver), copies the SJ201
   **device-tree overlays** (soundcard, buttons, PWM fan; Pi-5 variants auto-selected), enables
   the UART, compiles the **`vocalfusion-soundcard.ko`** kernel module against the running kernel
   headers, installs it, and registers it to load at boot.
2. **Updates the bootloader firmware.** It sets the Raspberry Pi EEPROM release channel and runs
   an EEPROM update (a reboot may be required).
3. **Initialises the amplifier and board.** It creates an SJ201 helper virtualenv and runs the
   XMOS flash tool plus the TAS5806 amplifier init.
4. **Sets up the touchscreen.** It adds the `rpi-backlight` overlay and switches the display
   driver overlay (`vc4-kms-v3d` → `vc4-fkms-v3d`) for the Mark 2 panel.
5. **Configures audio routing** via a Mark 2 WirePlumber/PipeWire profile.
6. **Writes a tuned [`mycroft.conf`](config.md)** — the `sounddevice` microphone settings above,
   Mark-2 wake-word sensitivity/VAD tuning, the [legacy OCP audio](ocp-audio-plugin.md) playback
   path, and (on the **dev kit** only) the `ovos-PHAL-plugin-mk2-v6-fan-control` fan plugin.

!!! warning "`ovos-i2csound` is *not* used by the installer"
    A common misconception: the [ovos-installer](ovos-installer.md) does **not** use
    `ovos-i2csound` or any other [raspOVOS](i2c-sound.md) helper
    script. `ovos-i2csound` belongs to the raspOVOS image. The installer's Mark 2 audio comes
    entirely from the `VocalFusionDriver` kernel module above.

!!! info "LED ring support is incomplete via the installer"
    The installer brings up audio, fan, touchscreen and buttons, but **LED-ring support on the
    Mark 2 is currently incomplete** in the ovos-installer path.

---

## The OVOS kernel driver: `VocalFusionDriver`

[`OpenVoiceOS/VocalFusionDriver`](https://github.com/OpenVoiceOS/VocalFusionDriver) is OVOS's
out-of-tree Linux **kernel driver and device-tree overlays** for the SJ201 HAT. It builds a
`vocalfusion-soundcard.ko` module that wires up the SJ201's **XMOS VocalFusion** DSP microphone
over I2S (configuring the master clock on a GPIO, plus reset/power lines), and ships the
device-tree overlays for the soundcard, the hardware **buttons**, and the **PWM fan** — with
both standard and Raspberry-Pi-5 variants, and separate **rev6 vs rev10** handling for the two
board versions. The TAS5806 **amplifier** is initialised separately at boot rather than inside
the module.

It is actively used (the installer builds it on every Mark 2 setup) and is kept working against
current kernel versions. Historically it derives from earlier community XMOS-loader code, adapted
for OVOS by Peter Steenbergen (j1nx).

---

## The raspOVOS image path

[`ovos-installer`](ovos-installer.md) is one way to get OVOS onto a device; the other is
**[raspOVOS](install-raspovos.md)**, a ready-made Raspberry Pi OS image
([`OpenVoiceOS/raspOVOS`](https://github.com/OpenVoiceOS/raspOVOS)) with OVOS layered on top.

The two paths set the SJ201 up **differently**. The installer builds the
[`VocalFusionDriver`](#the-ovos-kernel-driver-vocalfusiondriver) kernel module (above); the raspOVOS
image instead detects and configures i2c sound HATs with `ovos-i2csound` and friends — see
**[i2c Sound & Audio Setup](i2c-sound.md)** for those tools.

!!! note "`ovos-i2csound` belongs to the raspOVOS image, not the installer"
    `ovos-i2csound` is **not** invoked by the ansible [ovos-installer](ovos-installer.md), which
    uses the [`VocalFusionDriver`](#the-ovos-kernel-driver-vocalfusiondriver) kernel module for the
    Mark 2 instead. Don't expect `ovos-i2csound` on an installer-provisioned system.

---

## Neon Mark 2 packages (official, but separate)

Because Neon AI is the platform's official maintainer, they publish their own Mark 2 hardware
packages. These are **Neon-maintained and downstream of OVOS** — useful to know about, but see
the [downgrade warning](#support-status-best-effort-legacy) before installing any of them on an
OVOS system.

| Neon package | Purpose |
|---|---|
| `sj201-interface` ([repo](https://github.com/NeonGeckoCom/sj201-interface)) | Python library + `sj201` CLI for the board itself — detect revision (`get-revision` → 6 or 10), reset the LED ring, set fan speed, init the TI/TAS5806 amplifier, patch `config.txt`. Derived from Mycroft's `mark-ii-hardware-testing`. |
| `neon-phal-plugin-linear_led` ([repo](https://github.com/NeonGeckoCom/neon-phal-plugin-linear_led)) | PHAL plugin driving the LED ring (listening/speaking/muted/error animations). |
| `neon-phal-plugin-fan` ([repo](https://github.com/NeonGeckoCom/neon-phal-plugin-fan)) | CPU-temperature-based fan control. |
| `neon-phal-plugin-switches` ([repo](https://github.com/NeonGeckoCom/neon-phal-plugin-switches)) | Reads the SJ201 hardware buttons (volume up/down, action, mute). |

---

## Buildroot: where OVOS originated

[`OpenVoiceOS/ovos-buildroot`](https://github.com/OpenVoiceOS/ovos-buildroot) is the original
**Buildroot-based** embedded Linux distribution that first brought `ovos-core` to devices like
the Raspberry Pi and the Mark 2 — the project where OpenVoiceOS itself began (drawing on Mycroft
AI, HassOS and SkiffOS). It builds the SJ201 audio stack from its own Buildroot packages for the
VocalFusion/XVF3510 driver, baked into the image at build time.

It is now a **legacy / dormant** project: it is not formally archived, but it has no current
releases and little recent activity. New installs should use the
[ovos-installer](ovos-installer.md) or the [raspOVOS](#the-raspovos-image-path)
images instead. It is documented here because it is a meaningful part of OVOS history and still
the ancestor of today's Mark 2 audio packaging.

---

## Related Resources

- **[ovos-installer](ovos-installer.md)** — the supported way to provision a Mark 2.
- **[ovos-shell](ovos-shell.md)** — the graphical shell the Mark 2 displays.
- **[PHAL](phal.md)** — how hardware-abstraction plugins work and load.
- **[OCP Audio Plugin](ocp-audio-plugin.md)** — the legacy media-playback path the installer enables.
- **[Mark 1 Hardware](mark1.md)** — the faceplate-based predecessor.

---

*Source code: [OpenVoiceOS/ovos-installer](https://github.com/OpenVoiceOS/ovos-installer) (`ovos_hardware_mark2` role) and [OpenVoiceOS/VocalFusionDriver](https://github.com/OpenVoiceOS/VocalFusionDriver).*

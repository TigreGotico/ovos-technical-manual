# Mycroft Mark 2 Hardware

!!! abstract "In a nutshell"
    The **Mark 2** is Mycroft's second smart-speaker, and unlike the [Mark 1](mark1.md)
    (which only had a tiny LED "face") it is a full little computer with a **touchscreen**.
    Because of that screen, the Mark 2 runs the *complete* OVOS software stack plus a graphical
    shell — there is no special "Mark 2 build" of OVOS, just standard OVOS with the right
    hardware drivers switched on. Be aware that the Mark 2 is a **best-effort, legacy platform**
    (even less actively maintained than the [Mark 1](mark1.md)). This page explains how OVOS
    uses the Mark 2's screen, microphone, LED ring, and fan — and the one thing you must **not**
    do (mix in Neon packages; see the warning below). New to the terms here? See the
    [Glossary](glossary.md).

The **Mycroft Mark 2** is built around a **Raspberry Pi 4** carrying the **SJ201** audio/HAT
board (microphones, speaker amplifier, LED ring, fan, and buttons) behind a square IPS
touchscreen. OpenVoiceOS supports the Mark 2 and is the platform you get when you flash an OVOS
image with the [ovos-installer](ovos-installer.md).

---

## Support status — best-effort legacy

When Mycroft AI shut down, **Neon AI** officially took over the Mark 2: they continued selling
the devices and are the party nominally responsible for ongoing Mark 2 support. OVOS still runs
on the Mark 2, but treats it as a **best-effort, not actively maintained legacy platform** —
even more so than the [Mark 1](mark1.md). Expect rough edges (for example, LED support is
currently incomplete in the [ovos-installer](ovos-installer.md) path).

!!! danger "Do not install Neon packages on an OVOS system"
    Neon is **downstream of OVOS** and runs on a **completely different release cycle**: Neon
    packages **pin older versions of OVOS packages**. If you install Neon's Mark 2 packages on
    top of an OVOS install, `pip` will happily **downgrade your OVOS packages** to satisfy those
    pins, leaving you in a broken, half-downgraded, non-functional state that is very hard to
    untangle.

    Pick **one** stack and stay on it. The OVOS path is the [ovos-installer](ovos-installer.md),
    which uses **only OVOS repositories** — it does not pull in any Neon packages. If you want
    Neon's Mark 2 image instead, flash that and don't mix OVOS packages into it. Do not combine
    the two.

---

## How OVOS runs on the Mark 2

Unlike the [Mark 1](mark1.md), the Mark 2 has a real display, so it runs the **graphical**
OVOS experience rather than a faceplate API:

- The standard [core services](architecture-overview.md) run exactly as they do on any other
  device — there is no Mark 2 fork of `ovos-core`.
- The screen is driven by the [GUI service](gui-service.md) feeding the
  **[`ovos-shell`](ovos-shell.md)** Qt5/[Kirigami](qt5-gui.md) application (the same shell used
  on any Raspberry Pi with a touchscreen). The [ovos-installer](ovos-installer.md) installs
  `ovos-shell` on Mark 2 devices so they keep a screen until the
  [GUI rework](gui-adapters.md) replacement lands.
- Hardware peripherals (microphones, LED ring, fan, buttons) are handled by individual
  **[PHAL](phal.md) plugins** plus a low-level i2c setup script, described below.

---

## Audio setup — `ovos-i2csound`

The SJ201 microphones and amplifier sit on the Raspberry Pi's i2c bus.
**[`ovos-i2csound`](https://github.com/OpenVoiceOS/ovos-i2csound)** is the install-time script
that detects the attached i2c sound card (the SJ201, or a Respeaker HAT) and writes the correct
ALSA configuration so the mic array and speaker work. It is a system-level helper run once with
`sudo`, not a Python plugin, and is set up automatically by the [ovos-installer](ovos-installer.md)
on supported boards.

---

## Hardware PHAL plugins

The Mark 2's discrete hardware features are each driven by a small
[PHAL](phal.md) plugin, enabled under the `"PHAL"` section of
[`mycroft.conf`](config.md):

| Feature | Plugin | Notes |
|---|---|---|
| Cooling fan (Mark 2 "dev kit" / v6 board) | [`ovos-PHAL-plugin-mk2-v6-fan-control`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk2-v6-fan-control) | Auto-enabled by `ovos-i2csound` when the board is detected |
| LED ring (Respeaker / VoiceBonnet HATs) | [`ovos-PHAL-plugin-dotstar`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-dotstar) | For DotStar-style addressable LEDs; **LED support on the Mark 2 is currently incomplete in the ovos-installer path** |
| Speaker volume / mixer (ALSA) | [`ovos-PHAL-plugin-alsa`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-alsa) | Volume control over the message bus |
| System actions (reboot, shutdown, factory reset) | [`ovos-PHAL-plugin-system`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-system) | Used by the shell's settings UI |
| Wi-Fi onboarding | [`ovos-PHAL-plugin-wifi-setup`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-wifi-setup) | First-boot network setup on the touchscreen |

Enable a plugin manually like this:

```json
{
  "PHAL": {
    "ovos-PHAL-plugin-mk2-v6-fan-control": {
      "enabled": true
    }
  }
}
```

!!! note "The old all-in-one `ovos-PHAL-plugin-mk2` is deprecated"
    Early images shipped a single `ovos-PHAL-plugin-mk2` plugin that bundled LED, fan and
    button handling. It is **deprecated and should not be installed** — its functions were split
    into the focused, individually-installable plugins listed above so each board variant only
    loads what it actually has.

---

## Related Resources

- **[ovos-shell](ovos-shell.md)** — the graphical shell the Mark 2 displays.
- **[PHAL](phal.md)** — how hardware-abstraction plugins work and load.
- **[ovos-installer](ovos-installer.md)** — flashing and provisioning a Mark 2.
- **[Mark 1 Hardware](mark1.md)** — the faceplate-based predecessor.

---

*Source code: [OpenVoiceOS/ovos-i2csound](https://github.com/OpenVoiceOS/ovos-i2csound).*

# i2c Sound & Audio Setup

!!! abstract "In a nutshell"
    Many Raspberry Pi voice devices use an add-on **sound board (a "HAT")** for their microphones
    and speaker — the [Mark 2](mark2.md)'s SJ201, a Respeaker, and so on. Before OVOS can hear or
    speak, that board has to be **detected**, given the **right driver**, and wired into the
    system's **audio config**. This page covers the small OVOS tools that do that on the
    [raspOVOS](install-raspovos.md) image. (The [ovos-installer](ovos-installer.md) handles the
    Mark 2 differently — see [Mark 2 Hardware](mark2.md).) See the [Glossary](glossary.md) for terms.

Raspberry Pi sound HATs sit on the **i2c bus** and need three things before audio works: the board
must be **identified**, the correct **kernel driver / ALSA settings** applied, and the system's
**audio routing** (sound server, default device, volume) configured. OVOS splits this across a few
focused tools, used mainly by the [raspOVOS](install-raspovos.md) image.

!!! info "Two different hardware paths"
    The tools on this page are the **raspOVOS image** path. The ansible
    [ovos-installer](ovos-installer.md) does **not** use them for the [Mark 2](mark2.md) — it builds
    the [`VocalFusionDriver`](mark2.md#the-ovos-kernel-driver-vocalfusiondriver) kernel module
    instead. Pick the path that matches how you installed OVOS.

---

## `ovos-i2c-detection` — identify the board

[`OpenVoiceOS/ovos-i2c-detection`](https://github.com/OpenVoiceOS/ovos-i2c-detection) is a small set
of scripts that probe the i2c bus and answer "what board is this?". It exposes checks such as:

- `is_sj201_v6` — Mycroft SJ201 **dev kit** board (revision 6)
- `is_sj201_v10` — SJ201 **production** board (revision 10)
- `is_texas_tas5806` — the TAS5806 amplifier (used to confirm an SJ201 v10)
- `is_wm8960` — WM8960-based HATs (ReSpeaker 2-mic, Adafruit 2-mic)

This is the primitive that tells the [Mark 2](mark2.md) dev kit apart from the retail unit, and is
used by the detection/configuration tools below.

## `ovos-i2csound` — detect and configure at boot

[`OpenVoiceOS/ovos-i2csound`](https://github.com/OpenVoiceOS/ovos-i2csound) is a shell script plus a
systemd service (`i2csound.service`) that runs at boot, **auto-detects the attached i2c sound HAT,
and configures ALSA** for it. It writes the detected board name to **`/etc/OpenVoiceOS/i2c_platform`**
— a marker other components read to know what hardware they are on (an absent file means no supported
card was found). It supports the SJ201 and a range of Respeaker-style HATs, and is the piece that
"makes the microphone and speaker exist" on a raspOVOS image.

Install is a one-time `sudo ./install.sh` (apt-based systems) followed by a reboot; on a raspOVOS
image it is already baked in.

## `raspovos-audio-setup` — manage the audio configuration

[`OpenVoiceOS/raspovos-audio-setup`](https://github.com/OpenVoiceOS/raspovos-audio-setup) is the
ongoing **audio-configuration** layer (scripts + systemd services) that sits above detection. Where
`ovos-i2csound` brings the card up, `raspovos-audio-setup` keeps audio working as things change:

- set the default soundcard, combine audio sinks, manage USB-soundcard volume;
- survive hardware changes (plugging in a USB soundcard live, or moving the SD card to different
  hardware);
- expose more complex setups (e.g. echo cancellation) in a friendlier way;
- work across `alsa`, `pipewire`, or `pulseaudio`, and even on non-OVOS Raspberry Pi images.

!!! note "Alpha"
    `raspovos-audio-setup` is an alpha-stage project — useful, but still stabilising.

## `ovos-tools` — raspOVOS shell helpers

[`OpenVoiceOS/ovos-tools`](https://github.com/OpenVoiceOS/ovos-tools) is a grab-bag of helper bash
utilities used by [raspOVOS](install-raspovos.md) (and usable on other Linux systems), including some
of the audio/diagnostic helpers exposed by the image's [command set](install-raspovos.md#helpful-commands).

---

## Related Pages

- [Mark 2 Hardware](mark2.md) — the SJ201 board, and the installer's `VocalFusionDriver` path.
- [Mark 1 Hardware](mark1.md) — the faceplate device.
- [RaspOVOS image](install-raspovos.md) — the image these tools ship on.
- [PHAL](phal.md) — the hardware-abstraction plugins for buttons, LEDs, fans, etc.

---

*Source code: [OpenVoiceOS/ovos-i2csound](https://github.com/OpenVoiceOS/ovos-i2csound), [OpenVoiceOS/ovos-i2c-detection](https://github.com/OpenVoiceOS/ovos-i2c-detection), [OpenVoiceOS/raspovos-audio-setup](https://github.com/OpenVoiceOS/raspovos-audio-setup).*

# Coming From Alexa or Google Assistant?

!!! abstract "In a nutshell"
    OVOS is a voice assistant you run yourself, not a product you buy off a shelf — so the
    on-ramp looks different from Alexa or Google Assistant. This page is an honest comparison:
    what's the same, what's missing, what setup looks like, and what actually works the moment
    you're done, so you know what you're getting into before you start.

## The short version

- There is **no retail OVOS device** you can buy today and plug in. The closest equivalent is
  flashing the [RaspOVOS](install-raspovos.md) image onto a Raspberry Pi and its SD card — a
  half-hour, one-time setup rather than an unbox-and-go experience.
- There is **no companion phone app** for pairing or day-to-day control, the way the Alexa or
  Google Home apps work. Setup and configuration happen over SSH in a terminal, or by editing a
  text file — see [Make It Yours](personalize.md).
- There is **no generally usable on-screen visual assistant** right now — see
  [Screens on OVOS Today](gui-status.md) for the honest state of that. OVOS is voice-first; a
  screen, where present, is a bonus, not the primary interface.
- **Smart-home control isn't automatic.** Alexa/Google devices come with smart-home skills
  built in; OVOS needs a one-time Home Assistant setup — see
  [OVOS & Home Assistant](home-assistant.md).
- In exchange, you get an assistant that runs on hardware you choose, is not tied to one
  company's cloud, and — for the parts you choose to run locally — doesn't have to send your
  voice anywhere at all. See [Privacy & Security](privacy-security.md) for exactly what a
  default install does and doesn't send over the network.

## What setup actually looks like

There's no pairing screen or app-based wizard. You either:

1. Flash the [RaspOVOS](install-raspovos.md) image to an SD card and boot a Raspberry Pi with
   it — the closest thing to "unbox and go" that exists today, or
2. Run the [ovos-installer](ovos-installer.md) against an existing Linux install (Raspberry Pi
   OS or a regular desktop/laptop) — a guided, menu-driven wizard, but one you run from a
   terminal, typically over SSH if the device is headless.

If you've never used SSH before, budget a bit of extra time for that step, or lean on the
RaspOVOS image, which needs none of it.

## What works on day one

Once installed, these work immediately with no extra setup, roughly matching what you'd expect
from Alexa or Google Assistant out of the box:

- Timers, alarms, and reminders
- Weather
- General knowledge questions (via DuckDuckGo, Wikipedia, and similar)
- Internet radio
- Jokes and small talk

See [What can I say?](skill-examples.md) for the full, browsable list, and
[Screens on OVOS Today](gui-status.md) if you're wondering about visual responses on a device
with a screen.

## What needs extra setup

- **Smart-home control** (lights, thermostats, scenes) needs a Home Assistant instance and a
  one-time skill setup — see [OVOS & Home Assistant](home-assistant.md).
- **A specific wake word, voice, or language** other than the defaults needs an edit to a config
  file (not a voice command or an app toggle) — see [Make It Yours](personalize.md).
- **Playing your own music library or a streaming service** beyond internet radio needs an
  additional plugin — see [What can I say?](skill-examples.md).

## Related pages

- [ovos-installer](ovos-installer.md) — the guided install wizard
- [RaspOVOS](install-raspovos.md) — the closest thing to a ready-made device image
- [OVOS & Home Assistant](home-assistant.md) — smart-home setup
- [Screens on OVOS Today](gui-status.md) — the honest state of on-device visuals
- [What can I say?](skill-examples.md) — everything OVOS can do out of the box
- [Privacy & Security](privacy-security.md) — what a default install sends over the network

# OVOS & Home Assistant

!!! abstract "In a nutshell"
    OVOS and [Home Assistant](https://www.home-assistant.io/) (HA) are two different open-source
    projects that can work together in **two separate, independent directions**: OVOS can *lend
    its speech engines to* Home Assistant's own voice pipeline, or a skill on OVOS can *control
    devices inside* Home Assistant. You can use either one alone, or both at once — they don't
    depend on each other. This page explains both directions and links to the details.

There is no single "OVOS + Home Assistant" switch — there are two unrelated integrations, and
it's easy to conflate them. Pick the one (or both) that matches what you're trying to do:

| Direction | What it does | Runs where | Details |
|---|---|---|---|
| **HA uses OVOS's engines** | Home Assistant's own [Assist](https://www.home-assistant.io/voice_control/) voice pipeline uses an OVOS wake-word, speech-to-text, or text-to-speech plugin instead of (or alongside) its built-in ones | A small OVOS-side bridge process, reachable from HA over the network | [Wyoming Bridges](wyoming-bridges.md) |
| **OVOS controls HA devices** | Your OVOS assistant understands utterances like "turn on the lights" and relays them to your Home Assistant instance | A skill running inside OVOS | See below |

---

## Direction 1: Home Assistant uses OVOS's speech engines

Home Assistant's own voice assistant feature (Assist) can use external speech components over the
[Wyoming protocol](https://github.com/rhasspy/wyoming) — the same protocol Rhasspy and other
open voice tools speak. OVOS ships three small bridge packages
(`wyoming-ovos-stt`, `wyoming-ovos-tts`, `wyoming-ovos-wakeword`) that each expose one installed
OVOS plugin as a Wyoming server, so Home Assistant can point Assist at, say, an OVOS STT plugin
without knowing anything about the OVOS plugin system underneath.

This is useful if you already have OVOS plugins configured and tuned (a particular STT model, a
particular TTS voice) and want Home Assistant's own Assist pipeline to use them, instead of
running a second, separately-configured set of speech engines just for HA.

See [Wyoming Bridges](wyoming-bridges.md) for installation, configuration, and the exact HA-side
setup (adding a Wyoming integration pointed at the bridge's host and port).

---

## Direction 2: OVOS controls Home Assistant devices

To have your OVOS assistant turn on lights, adjust a thermostat, or run a scene, you install a
skill that talks to your existing Home Assistant instance over its REST/WebSocket API.

!!! note "The old PHAL plugin is gone"
    An earlier integration, `ovos-PHAL-plugin-homeassistant`, has been removed. The current,
    maintained path is the `skill-homeassistant` skill (maintained by OscillateLabs) listed
    below — see [Deprecated & Removed Repositories](deprecated-repos.md) for the retirement
    note.

### Setting it up

You need two things from your Home Assistant instance before installing the skill:

1. **The URL** of your Home Assistant instance (e.g. `http://homeassistant.local:8123`).
2. **A long-lived access token** — generate one from your Home Assistant user profile page
   (*Settings → your profile → Long-Lived Access Tokens → Create Token*) and keep it secret; it
   grants the same access as your account.

With those two in hand, either:

- Tick the `homeassistant` feature in the [ovos-installer](ovos-installer.md#feature-selection)
  (offered for the `ovos`/`listener` profiles on the `virtualenv` or `containers` install
  method) — the installer prompts you for the URL and token during setup, or
- Install the skill yourself afterwards:
  ```bash
  pip install skill-homeassistant
  ```
  then configure it with your instance's URL and token (see the skill's own repository for the
  current configuration key names), and restart OVOS to load it.

### Example utterances

Actual phrasing and which devices respond depend entirely on how your own devices, areas, and
scenes are named inside Home Assistant:

- "Turn on the living room lights."
- "Turn off the kitchen lights."
- "Set the thermostat to 20 degrees."
- "Activate the movie night scene."

See [What can I say? — Smart Home](skill-examples.md#smart-home) for the skill's catalog entry.

---

## Related pages

- [ovos-installer](ovos-installer.md#feature-selection) — the `homeassistant` install-time feature
- [Wyoming Bridges](wyoming-bridges.md) — OVOS engines exposed to Home Assistant/Rhasspy
- [What can I say?](skill-examples.md) — the full skill catalog, including Smart Home
- [Deprecated & Removed Repositories](deprecated-repos.md) — retired integrations, including the
  old PHAL plugin

# The OCP Audio Plugin (`ovos-plugin-common-play`)

!!! abstract "In a nutshell"
    **OCP** ("OVOS Common Play") is the voice media player behind "play some jazz" or "play the
    news". Today it ships as a plugin for the old [audio service](audio-service.md) — the package
    `ovos-plugin-common-play`, which registers as an *audio backend* called `ovos_common_play`.
    This is the **default** way OVOS plays media right now. It still works and is enabled out of
    the box, but it is **legacy**: a dedicated replacement, [`ovos-media`](ovos-media.md), is
    being built to take over the playback job. This page explains what the OCP audio plugin is,
    why it lives inside the audio service, and how `ovos-media` will replace it. For the *intent*
    side of OCP (deciding that "play X" is a media request) see the
    [OCP Pipeline](ocp-pipeline.md); for the skills that supply results see
    [Media Skills](ocp-skills.md).

---

## What it is

The **OCP audio plugin** is OCP packaged as a classic [audio service](audio-service.md) backend.
The pieces:

- **Package / repo:** [`ovos-ocp-audio-plugin`](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin)
  (PyPI name `ovos-plugin-common-play`, import name `ovos_plugin_common_play`).
- **Entry point:** registers in the legacy `mycroft.plugin.audioservice` group under the type
  name **`ovos_common_play`**.
- **What it does:** the full OCP player — it receives the chosen media (search results gathered
  by the [OCP pipeline](ocp-pipeline.md) from [OCP skills](ocp-skills.md)), manages the
  now-playing queue and player state, runs [stream extractors](ocp-plugins.md), exposes the
  player over [MPRIS](#mpris), and drives the actual audio output through a lower-level audio
  backend (`mpv`, `vlc`, or `simple`).

OCP is a *coordinator*, not an audio codec: it does the voice/queue/MPRIS logic and then hands
the raw stream to one of the simple audio backends to make sound.

---

## Background — why OCP is an "audio service plugin"

OVOS inherited its [audio service](audio-service.md) from Mycroft. In that original design the
audio service had one job — play a sound file — and it loaded small *audio backend* plugins (a
VLC backend, an mpv backend) to do it. The only supported extension point for "something that
plays media" was therefore the `mycroft.plugin.audioservice` group.

When OCP was built to add a real voice-controlled media player (search across skills, media
types, playlists, resume/next/previous, MPRIS), it was slotted into that **existing** extension
point — it became "just another audio backend", the `ovos_common_play` type. That is why a
full-blown media player ends up living inside the humble audio service: it was the hook that
existed at the time. The [`ovos-media`](ovos-media.md) refactor exists precisely to give the
media player its own home instead of riding on the TTS-playback service.

---

## Status today — legacy, but the default

The OCP audio plugin is **still the default media playback path**:

- It is installed as part of [`ovos-audio`](audio-service.md)'s media extra
  (`ovos_plugin_common_play[extractors]`), so most installs already have it.
- The default config ships with **`"enable_old_audioservice": true`**, which turns on the old
  audio service that loads OCP.
- In the default config the `"OCP"` backend (`type: ovos_common_play`) is `active`.

So unless you have explicitly switched to `ovos-media`, your OVOS device is playing media through
this plugin.

---

## Configuration

OCP is configured as a backend under the `Audio` section of [`mycroft.conf`](config.md):

```json
{
  "enable_old_audioservice": true,
  "Audio": {
    "backends": {
      "OCP": {
        "type": "ovos_common_play",
        "preferred_audio_services": ["mpv", "vlc", "simple"],
        "dbus_type": "session",
        "manage_external_players": false,
        "active": true
      }
    }
  }
}
```

- **`preferred_audio_services`** — order in which OCP picks a lower-level audio backend to
  actually emit sound.
- **`dbus_type`** / MPRIS keys — see [MPRIS](#mpris) below.

!!! warning "`default-backend` must not be `"OCP"`"
    The audio service's `default-backend` selects the backend for *plain* `speak`/audio output
    (it defaults to `mpv`). OCP installs itself as the `OCP` backend, but **`"OCP"` is not a
    valid `default-backend` value** — it only appears in `backends` for legacy reasons. Leave
    `default-backend` as `mpv` (or another simple backend).

---

## MPRIS

OCP exposes the player over **MPRIS** (the standard Linux D-Bus media-control interface), so
phones, desktops, and physical media keys can see and control playback. With
`manage_external_players` enabled, OCP can also reach the other direction — voice-controlling
third-party MPRIS apps (Spotify, a browser) and pausing them when OCP starts its own playback.

---

## Standalone mode

Normally OCP is started by [`ovos-audio`](audio-service.md). The package also ships an
`ovos-ocp-standalone` console script to run OCP as its own process, reading the usual
`~/.config/mycroft/mycroft.conf`. This is useful in distributed setups — e.g. running OCP at a
[HiveMind](hivemind-agents.md) Core rather than on a satellite, since the satellite cannot
register OCP's intents.

---

## How `ovos-media` replaces it

[`ovos-media`](ovos-media.md) is the **upcoming, opt-in** replacement. Instead of cramming the
media player into the audio service, it is a **dedicated media daemon** with a cleaner design:

| | OCP audio plugin (legacy, default) | `ovos-media` (upcoming) |
|---|---|---|
| Where it runs | Inside [`ovos-audio`](audio-service.md) as a `mycroft.plugin.audioservice` backend | Its own service/daemon |
| Player plugins | One bundled player; delegates to `mpv`/`vlc`/`simple` audio backends | Typed plugins on `opm.media.audio` / `opm.media.video` / `opm.media.web` (see [Media Playback](media-plugins.md)) |
| Video / web | Limited | First-class audio **and** video **and** web players |
| Status | Enabled by default | Opt-in |

What stays the same: the **search layer is shared**. The [OCP pipeline](ocp-pipeline.md)
(intent matching) and [OCP skills](ocp-skills.md) (media providers) are used by *both* — only the
*playback backend* changes. `ovos-media` also keeps a **backwards-compatibility bridge** that
translates the old `mycroft.audio.service.*` bus messages, so existing skills and clients keep
working.

To switch to `ovos-media`: set **`"enable_old_audioservice": false`** in `mycroft.conf` and run
the `ovos-media` daemon. See the [ovos-media](ovos-media.md) page for the full setup and the list
of player plugins.

!!! note "Don't run both at once"
    `enable_old_audioservice: true` (OCP) and a running `ovos-media` daemon both want to own
    media playback. Pick one. When `ovos-media` is in use, the OCP backend config above does
    nothing.

---

## Related Pages

- [OCP Pipeline](ocp-pipeline.md) — how "play X" is recognised as a media request.
- [Media Skills (OCP)](ocp-skills.md) — writing skills that provide media results.
- [OCP Stream Extractors](ocp-plugins.md) — turning page URLs into playable streams.
- [Audio Service](audio-service.md) — the service this plugin loads into.
- [ovos-media](ovos-media.md) — the dedicated replacement.

---

*Source code: [OpenVoiceOS/ovos-ocp-audio-plugin](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin).*

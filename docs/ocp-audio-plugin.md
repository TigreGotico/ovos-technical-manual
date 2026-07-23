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

OCP predates OVOS as a standalone project — it was first built for **mycroft-core**, which was
not extensible enough to add a real media player cleanly. At the time the **only** way to
intercept playback requests (and to sync with the GUI for things like video) was the audio
service, which had one job — play a sound file — and loaded small *audio backend* plugins (a VLC
backend, an mpv backend) to do it. The only extension point for "something that plays media" was
therefore the `mycroft.plugin.audioservice` group.

So OCP was bolted on as a **hack**: it registered itself as **the** audio backend (the
`ovos_common_play` type, set as the default backend), **captured** every playback request, and
then **delegated** the actual sound output back to a real audio backend (`mpv`/`vlc`/`simple`).
Messy, but it slotted into the machinery that existed. The result was a **monolith**: a single
plugin doing *everything* — NLP/intent matching, cross-skill search, the player state machine,
and MPRIS.

Since OVOS became its own project that monolith has been **split apart, repo by repo, and
properly integrated** into OVOS: intent matching moved to the [OCP pipeline](ocp-pipeline.md),
stream resolution to [stream-extractor plugins](ocp-plugins.md), shared types to `ovos-utils`,
and so on. [`ovos-media`](ovos-media.md) is the **final step** — it gives the media player itself
a proper home as a standalone service instead of masquerading as an audio backend inside
[`ovos-audio`](audio-service.md).

!!! note "This is *media* playback, not TTS/sound playback"
    The OCP audio plugin (and the `ovos-media` daemon that replaces it) handles **media**
    playback only — music, podcasts, video, streams. The spoken-response and sound-effect
    playback queue inside [`ovos-audio`](audio-service.md) is a **separate subsystem** that is
    unaffected: turning OCP off (or switching to `ovos-media`) does not change how TTS or
    notification sounds are played.

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

!!! warning "Upcoming — breaking"
    This legacy audioservice subsystem — including the OCP backend described on this page —
    is planned for removal from `ovos-audio` entirely. Media playback will then live wholly
    in [`ovos-media`](ovos-media.md); plan a migration if you have not already switched.

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
        "preferred_audio_services": ["vlc", "mplayer", "simple"],
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

[`ovos-media`](ovos-media.md) is the **final step** of the decomposition described
[above](#background-why-ocp-is-an-audio-service-plugin) and the **upcoming, opt-in** replacement
for this plugin. With the NLP, search, and extraction layers already split out into their own
repos, what remains is the player itself — and instead of cramming it into the audio service,
`ovos-media` gives it a **dedicated media daemon** with a cleaner design:

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

The full switch touches two config keys — turning the legacy audio service's OCP backend off, and
making sure the OCP intent pipeline (which both backends share) is still enabled in `ovos-core`:

```json
{
  "enable_old_audioservice": false,
  "intents": {
    "pipeline": [
      "ovos-ocp-pipeline-plugin-high",
      "...",
      "ovos-ocp-pipeline-plugin-medium",
      "..."
    ]
  }
}
```

!!! note "Don't run both at once"
    `enable_old_audioservice: true` (OCP) and a running `ovos-media` daemon both want to own
    media playback. Pick one. When `ovos-media` is in use, the OCP backend config above does
    nothing.

---

## Related Pages

- [OCP Pipeline](ocp-pipeline.md) — how "play X" is recognized as a media request.
- [Media Skills (OCP)](ocp-skills.md) — writing skills that provide media results.
- [OCP Stream Extractors](ocp-plugins.md) — turning page URLs into playable streams.
- [Audio Service](audio-service.md) — the service this plugin loads into.
- [ovos-media](ovos-media.md) — the dedicated replacement.

---

*Source code: [OpenVoiceOS/ovos-ocp-audio-plugin](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin).*

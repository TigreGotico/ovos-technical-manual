# Media Plugins Reference

!!! abstract "In a nutshell"
    These plugins are the **playback backends** that actually push audio/video to your
    speakers or screen (VLC, MPV, Chromecast, Spotify…). OVOS is mid-migration between two
    playback systems, and a single plugin **package is meant to ship a version for both** —
    see [Media playback: legacy vs. ovos-media](ovos-media.md).

## Two interfaces, one package

A playback plugin can implement **two separate entry-point families**:

- **Old audio service** — `mycroft.plugin.audioservice` (used by the deprecated
  [`ovos-ocp-audio-plugin`](#ovos-ocp-audio-plugin) / "old audio service", the shipped default).
- **[`ovos-media`](ovos-media.md)** — `opm.media.{audio,video,web}` (the upcoming daemon).

These two families are **separate** (different entry-point groups and base classes), **but a
plugin package is meant to ship a version for *both*** — so a single `pip install` gives you a
backend that works whichever playback system you run. Where a package currently ships only one
family, adding the other is a **TODO**.

| Package | Player | Ships for |
|---|---|---|
| [ovos-media-plugin-spotify](#ovos-media-plugin-spotify) | Spotify Connect | ✅ both (old audio service + ovos-media) |
| [ovos-media-plugin-chromecast](#ovos-media-plugin-chromecast) | Chromecast (audio + video) | ✅ both |
| [ovos-media-plugin-vlc](#ovos-media-plugin-vlc) | headless VLC (audio + video) | ovos-media only — *old audio service: TODO* |
| [ovos-media-plugin-mplayer](#ovos-media-plugin-mplayer) | MPlayer (audio + video) | ovos-media only — *old audio service: TODO* |
| [ovos-media-plugin-simple](#ovos-media-plugin-simple) | minimal/default audio | ovos-media only — *old audio service: TODO* |
| [ovos-plugin-vlc](#ovos-plugin-vlc) | VLC | old audio service only (legacy) — use ovos-media-plugin-vlc for ovos-media |
| [ovos-audio-plugin-mpv](#ovos-audio-plugin-mpv) | MPV | old audio service only (legacy) |
| [ovos-audio-plugin-simple](#ovos-audio-plugin-simple) | minimal audio | old audio service only — ⚠️ ovos ≤ 0.0.7 |

The [`ovos-ocp-audio-plugin`](#ovos-ocp-audio-plugin) below is not a playback backend — it is the
**old audio service itself** (deprecated, still the shipped default).

---

## ovos-media-plugin-spotify

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-plugin-spotify](https://github.com/OpenVoiceOS/ovos-media-plugin-spotify)


- **Description**: Spotify Connect playback. Ships entry points for **both** the old audio service (`mycroft.plugin.audioservice`) and [ovos-media](https://github.com/OpenVoiceOS/ovos-media) (`opm.media.audio`).

---

## ovos-media-plugin-vlc

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-plugin-vlc](https://github.com/OpenVoiceOS/ovos-media-plugin-vlc)


- **Description**: Headless VLC audio/video playback. Currently ships the [ovos-media](https://github.com/OpenVoiceOS/ovos-media) version (`opm.media.audio` / `opm.media.video`) only; an old-audio-service version is a TODO (use [ovos-plugin-vlc](#ovos-plugin-vlc) on the old audio service for now).

---

## ovos-media-plugin-chromecast

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-plugin-chromecast](https://github.com/OpenVoiceOS/ovos-media-plugin-chromecast)


- **Description**: Cast audio/video to a Chromecast. Ships entry points for **both** the old audio service and [ovos-media](https://github.com/OpenVoiceOS/ovos-media) (`opm.media.audio` / `opm.media.video`).

---

## ovos-ocp-audio-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin)


- **Description**: The legacy **"old audio service"** OCP backend. It crams OCP search orchestration, the player state machine, MPRIS and the GUI into a single `ovos-audio` `AudioBackend`. ⚠️ **Deprecated but still shipped and enabled by default** (`enable_old_audioservice: true`); superseded by the standalone [ovos-media](ovos-media.md) daemon.

---

## ovos-media-plugin-simple

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-plugin-simple](https://github.com/OpenVoiceOS/ovos-media-plugin-simple)


- **Description**: Minimal/default audio playback for [ovos-media](https://github.com/OpenVoiceOS/ovos-media) (`opm.media.audio`). An old-audio-service version is a TODO.

---

## ovos-audio-plugin-simple

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-audio-plugin-simple](https://github.com/OpenVoiceOS/ovos-audio-plugin-simple)


- **Description**: ⚠️ Legacy old-audio-service backend (`mycroft.plugin.audioservice`). This plugin was made for old OCP and only works on ovos ≤ 0.0.7.

---

## ovos-plugin-vlc

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-plugin-vlc](https://github.com/OpenVoiceOS/ovos-plugin-vlc)


- **Description**: VLC `AudioBackend` for the **old audio service** (`mycroft.plugin.audioservice`). For the [ovos-media](ovos-media.md) backend use [ovos-media-plugin-vlc](#ovos-media-plugin-vlc).

---

## ovos-media-plugin-mplayer

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-plugin-mplayer](https://github.com/OpenVoiceOS/ovos-media-plugin-mplayer)


- **Description**: MPlayer audio/video playback for [ovos-media](https://github.com/OpenVoiceOS/ovos-media) (`opm.media.audio` / `opm.media.video`). An old-audio-service version is a TODO.

---

## ovos-audio-plugin-mpv

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-audio-plugin-mpv](https://github.com/OpenVoiceOS/ovos-audio-plugin-mpv)


- **Description**: MPV `AudioBackend` for the **old audio service** (`mycroft.plugin.audioservice`).

---

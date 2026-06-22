# Media Plugins Reference

!!! abstract "In a nutshell"
    These plugins are the **playback backends** that actually push audio/video to your
    speakers or screen (VLC, MPV, Chromecast, Spotify…). OVOS is mid-migration between two
    playback systems, so there are **two families** of these plugins. Which one you need
    depends on which backend you run — see [Media playback: legacy vs. ovos-media](ovos-media.md).

OVOS has two media-playback backends that share the same [OCP](ocp-pipeline.md) search
framework but use **different, non-interchangeable** playback plugins:

- **Legacy "old audio service"** — the [`ovos-ocp-audio-plugin`](#ovos-ocp-audio-plugin)
  inside [`ovos-audio`](audio-service.md), with `AudioBackend`-style plugins. **Deprecated but
  still the shipped default.**
- **[`ovos-media`](ovos-media.md) (upcoming)** — a standalone daemon with `opm.media.*`
  plugins you can mix per request. **Opt-in; not the default yet.**

A plugin written for one backend does **not** work in the other. Pick the family that
matches your configured backend.

---

## ovos-media plugins (upcoming)

Used by the [`ovos-media`](ovos-media.md) daemon (`opm.media.{audio,video,web}`). Enable
them by listing them under `media` → `audio_players` / `video_players` in `mycroft.conf`.

| Plugin | Description |
|--------|-------------|
| [ovos-media-plugin-vlc](#ovos-media-plugin-vlc) | Headless VLC audio/video playback for ovos-media. |
| [ovos-media-plugin-mplayer](#ovos-media-plugin-mplayer) | MPlayer playback backend for ovos-media. |
| [ovos-media-plugin-simple](#ovos-media-plugin-simple) | Minimal/default playback backend for ovos-media. |
| [ovos-media-plugin-spotify](#ovos-media-plugin-spotify) | Spotify Connect playback (works with ovos-audio and ovos-media). |
| [ovos-media-plugin-chromecast](#ovos-media-plugin-chromecast) | Cast playback to a Chromecast (works with ovos-audio and ovos-media). |

## Legacy audio backends (old audio service — deprecated)

Used by the legacy [`ovos-ocp-audio-plugin`](#ovos-ocp-audio-plugin) / "old audio service"
in [`ovos-audio`](audio-service.md). **Deprecated** — kept because the old audio service is
still shipped and on by default. New setups should prefer the ovos-media plugins above.

| Plugin | Description |
|--------|-------------|
| [ovos-ocp-audio-plugin](#ovos-ocp-audio-plugin) | The "old audio service" itself — bundles OCP search, player state, MPRIS and GUI into one `ovos-audio` backend. ⚠️ Deprecated; superseded by [ovos-media](ovos-media.md). |
| [ovos-plugin-vlc](#ovos-plugin-vlc) | VLC `AudioBackend` for the old audio service. |
| [ovos-audio-plugin-mpv](#ovos-audio-plugin-mpv) | MPV `AudioBackend` for the old audio service. |
| [ovos-audio-plugin-simple](#ovos-audio-plugin-simple) | ⚠️ Very old simple backend — only works on ovos ≤ 0.0.7. |

---

## ovos-media-plugin-spotify

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-plugin-spotify](https://github.com/OpenVoiceOS/ovos-media-plugin-spotify)


- **Description**: spotify plugin for [ovos-audio](https://github.com/OpenVoiceOS/ovos-audio) and [ovos-media](https://github.com/OpenVoiceOS/ovos-media)

---

## ovos-media-plugin-vlc

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-plugin-vlc](https://github.com/OpenVoiceOS/ovos-media-plugin-vlc)


- **Description**: vlc plugin for [ovos-media](https://github.com/OpenVoiceOS/ovos-media)

---

## ovos-media-plugin-chromecast

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-plugin-chromecast](https://github.com/OpenVoiceOS/ovos-media-plugin-chromecast)


- **Description**: chromecast plugin for [ovos-audio](https://github.com/OpenVoiceOS/ovos-audio) and [ovos-media](https://github.com/OpenVoiceOS/ovos-media)

---

## ovos-ocp-audio-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin)


- **Description**: The legacy **"old audio service"** OCP backend. It crams OCP search orchestration, the player state machine, MPRIS and the GUI into a single `ovos-audio` `AudioBackend`. ⚠️ **Deprecated but still shipped and enabled by default** (`enable_old_audioservice: true`); superseded by the standalone [ovos-media](ovos-media.md) daemon.

---

## ovos-media-plugin-simple

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-plugin-simple](https://github.com/OpenVoiceOS/ovos-media-plugin-simple)


- **Description**: simple plugin for [ovos-media](https://github.com/OpenVoiceOS/ovos-media)

---

## ovos-audio-plugin-simple

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-audio-plugin-simple](https://github.com/OpenVoiceOS/ovos-audio-plugin-simple)


- **Description**: ⚠️ Legacy old-audio-service backend. This plugin was made for old OCP, it only works in ovos <= 0.0.7

---

## ovos-plugin-vlc

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-plugin-vlc](https://github.com/OpenVoiceOS/ovos-plugin-vlc)


- **Description**: The VLC OVOS Plugin integrates VLC media player capabilities with the Open Voice OS (OVOS) ecosystem, providing an audio backend for playing various media formats. ⚠️ Legacy old-audio-service `AudioBackend`; for ovos-media use [ovos-media-plugin-vlc](#ovos-media-plugin-vlc).

---

## ovos-media-plugin-mplayer

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-plugin-mplayer](https://github.com/OpenVoiceOS/ovos-media-plugin-mplayer)


- **Description**: Mplayer plugin for [ovos-media](https://github.com/OpenVoiceOS/ovos-media)

---

## ovos-audio-plugin-mpv

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-audio-plugin-mpv](https://github.com/OpenVoiceOS/ovos-audio-plugin-mpv)


- **Description**: The MPV OVOS Plugin integrates MPV media player capabilities with the Open Voice OS (OVOS) ecosystem, providing an audio backend for playing various media formats. ⚠️ Legacy old-audio-service `AudioBackend`.

---

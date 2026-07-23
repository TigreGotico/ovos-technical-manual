# Media Plugins Reference

!!! abstract "In a nutshell"
    These plugins are the **playback backends** that actually push audio/video to your
    speakers or screen (VLC, MPV, Chromecast, Spotify…). OVOS is mid-migration between the
    legacy audio-service backend and the upcoming [`ovos-media`](ovos-media.md) daemon, and a
    single plugin **package is meant to ship a version for both** — see
    [Media playback: legacy vs. ovos-media](ovos-media.md).

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
| [ovos-media-plugin-vlc](#ovos-media-plugin-vlc) | headless VLC (audio + video) | ✅ both |
| [ovos-media-plugin-mplayer](#ovos-media-plugin-mplayer) | MPlayer (audio + video) | ✅ both |
| [ovos-audio-plugin-mpv](#ovos-audio-plugin-mpv) | MPV (audio + video) | ✅ both |
| [ovos-media-plugin-ffplay](#ovos-media-plugin-ffplay) | ffplay (audio) | ✅ both |
| [ovos-media-plugin-cli](#ovos-media-plugin-cli) | generic CLI-command player (audio) | ✅ both |
| [ovos-plugin-vlc](#ovos-plugin-vlc) | VLC | old audio service only (legacy) — use ovos-media-plugin-vlc for ovos-media |

The [`ovos-ocp-audio-plugin`](#ovos-ocp-audio-plugin) below is not a playback backend — it is the
**old audio service itself** (deprecated, still the shipped default).

---

## ovos-media-plugin-spotify

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-plugin-spotify](https://github.com/OpenVoiceOS/ovos-media-plugin-spotify)


- **Description**: Spotify Connect playback. Ships entry points for **both** the old audio service (`mycroft.plugin.audioservice`) and [ovos-media](https://github.com/OpenVoiceOS/ovos-media) (`opm.media.audio`).

---

## ovos-media-plugin-vlc

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-plugin-vlc](https://github.com/OpenVoiceOS/ovos-media-plugin-vlc)


- **Description**: Headless VLC audio/video playback. Ships entry points for both
  [ovos-media](https://github.com/OpenVoiceOS/ovos-media) (`opm.media.audio` / `opm.media.video`,
  classes `VLCOCPAudioService` / `VLCOCPVideoService`) and the old audio service
  (`mycroft.plugin.audioservice`, type `ovos_vlc`). The older, old-audio-service-only
  [ovos-plugin-vlc](#ovos-plugin-vlc) still exists as a separate package.

---

## ovos-media-plugin-chromecast

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-plugin-chromecast](https://github.com/OpenVoiceOS/ovos-media-plugin-chromecast)


- **Description**: Cast audio/video to a Chromecast. Ships entry points for **both** the old audio service and [ovos-media](https://github.com/OpenVoiceOS/ovos-media) (`opm.media.audio` / `opm.media.video`).

---

## ovos-ocp-audio-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin)


- **Description**: The legacy **"old audio service"** OCP backend. It crams OCP search orchestration, the player state machine, MPRIS and the GUI into a single `ovos-audio` `AudioBackend`. ⚠️ **Deprecated but still shipped and enabled by default** (`enable_old_audioservice: true`); superseded by the standalone [ovos-media](ovos-media.md) daemon. See the dedicated **[OCP Audio Plugin](ocp-audio-plugin.md)** page for the full background, configuration, and migration path.

---

## ovos-plugin-vlc

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-plugin-vlc](https://github.com/OpenVoiceOS/ovos-plugin-vlc)


- **Description**: VLC `AudioBackend` for the **old audio service** (`mycroft.plugin.audioservice`). For the [ovos-media](ovos-media.md) backend use [ovos-media-plugin-vlc](#ovos-media-plugin-vlc).

---

## ovos-media-plugin-mplayer

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-plugin-mplayer](https://github.com/OpenVoiceOS/ovos-media-plugin-mplayer)


- **Description**: MPlayer audio/video playback. Ships entry points for both
  [ovos-media](https://github.com/OpenVoiceOS/ovos-media) (`opm.media.audio` / `opm.media.video`)
  and the old audio service (`mycroft.plugin.audioservice`, type `ovos_mplayer`).

---

## ovos-audio-plugin-mpv

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-plugin-mpv](https://github.com/OpenVoiceOS/ovos-media-plugin-mpv)
  (the repo lives under this name; the PyPI package is still published as `ovos-audio-plugin-mpv`).


- **Description**: MPV audio/video playback. Ships entry points for both
  [ovos-media](https://github.com/OpenVoiceOS/ovos-media) (`opm.media.audio` / `opm.media.video`)
  and the old audio service (`mycroft.plugin.audioservice`, type `ovos_mpv`).

---

## ovos-media-plugin-ffplay

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-plugin-ffplay](https://github.com/OpenVoiceOS/ovos-media-plugin-ffplay)


- **Description**: ffplay-based audio playback backend. Ships entry points for both
  [ovos-media](https://github.com/OpenVoiceOS/ovos-media) (`opm.media.audio`, class
  `FFPlayOCPAudioService`) and the old audio service (`mycroft.plugin.audioservice`, type
  `ovos_ffplay`). Direct programmatic access is available via `FFPlayAudioPlayer`.

---

## ovos-media-plugin-cli

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-plugin-cli](https://github.com/OpenVoiceOS/ovos-media-plugin-cli)


- **Description**: Generic command-line playback backend — shells out to any CLI media
  player. With an explicit `command` set (e.g. `"mpv --no-terminal"`, `"ffplay -nodisp
  -autoexit"`), it appends the track URI as the final argument; with no `command` set it
  auto-detects the best available player for the platform (`sox`/`play` preferred, then
  `mpg123`/`paplay`/`aplay` on Linux, `afplay` on macOS). Pause/resume use process signals
  (`SIGSTOP`/`SIGCONT`). Ships entry points for both ovos-media (`opm.media.audio`, class
  `CLIAudioService`) and the old audio service (`mycroft.plugin.audioservice`, type
  `ovos_cli`).

---

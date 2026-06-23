# Audio Service

!!! abstract "In a nutshell"
    `ovos-audio` is the part of OVOS that actually makes sound come out of the speakers. When a skill wants to say something, this service turns that text into speech (using a [TTS](tts-plugins.md) plugin) and plays it, while making sure only one thing talks at a time and turning down background music so you can hear the reply. Think of it as the assistant's mouth and its audio mixer rolled into one. See [TTS Plugins](tts-plugins.md) or the [Glossary](glossary.md) for related terms.

`ovos-audio` is the component responsible for [TTS](tts-plugins.md) synthesis and audio playback. It ensures that only one thing is speaking at a time and manages audio focus between different media sources.

**In plain terms:** when a skill says "tell the user X", that `speak` message lands here. `ovos-audio` turns the text into sound with a TTS plugin and plays it, ducking any background music while it talks.

!!! info "TTS is current; the built-in *media* playback is the legacy path"
    The **TTS / speech** side of `ovos-audio` (described here) is fully current. Its bundled
    **media-playback** path — the [old audio service](media-plugins.md#ovos-ocp-audio-plugin)
    (`enable_old_audioservice`, on by default) — is **deprecated** and being superseded by the
    standalone [`ovos-media`](ovos-media.md) daemon. See [Media playback: legacy vs. ovos-media](ovos-media.md).

---

??? abstract "Technical Reference"

    - `PlaybackService.run()` — [`ovos_audio/service.py`](https://github.com/OpenVoiceOS/ovos-audio/blob/dev/ovos_audio/service.py) — Main service thread; registers the `speak` handler and drives the [TTS](tts-plugins.md) queue.


    - `PlaybackThread.run()` — [`ovos_audio/playback.py:163`](https://github.com/OpenVoiceOS/ovos-audio/blob/dev/ovos_audio/playback.py) — logic for playing back the synthesized audio chunks.


    - `AudioService.play()` — [`ovos_audio/audio.py:395`](https://github.com/OpenVoiceOS/ovos-audio/blob/dev/ovos_audio/audio.py) — routes media playback to the correct backend by URI scheme (MPV, VLC, etc.).
    
    ---
    

## Overview

The audio service receives `speak` messages from the [MessageBus](bus-service.md), sends them to a [TTS](tts-plugins.md) engine, and plays the resulting audio. It also manages a "media" pipeline for playing music, news, and other streams.

### Key Responsibilities

- **[TTS](tts-plugins.md) Synthesis**: Converts text to speech using various plugins.


- **Playback Management**: Handles multiple audio streams and ensures smooth transitions.


- **Audio Focus**: Prioritizes speech over music or other background sounds.


- **Viseme Generation**: Provides lip-sync data for [GUI](qt5-gui.md) animations.

## Architecture

```
[MessageBus] --(speak)--> [PlaybackService] --(synthesis)--> [TTS Plugin]
                               |
                               +--(playback)--> [PlaybackThread] --(ALSA/Pulse)--> [Speakers]

```

## Configuration

Settings for the audio service are located in the `tts` and `Audio` sections of `mycroft.conf`.

```json
{
  "tts": {
    "module": "ovos-tts-plugin-server",
    "ovos-tts-plugin-server": {
      "url": "https://tts.openvoiceos.org"
    }
  },
  "Audio": {
    "default-backend": "mpv",
    "backends": {
      "mpv": {
        "type": "ovos_mpv",
        "active": true
      }
    }
  }
}

```

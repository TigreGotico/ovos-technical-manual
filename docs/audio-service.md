# Audio Service

`ovos-audio` is the component responsible for [TTS](tts-plugins.md) synthesis and audio playback. It ensures that only one thing is speaking at a time and manages audio focus between different media sources.

---

??? abstract "Technical Reference"

    - `PlaybackService.run()` — [`ovos_audio/service.py:180`](https://github.com/OpenVoiceOS/ovos-audio/blob/dev/ovos_audio/service.py) — Main service thread handling the [TTS](tts-plugins.md) queue.


    - `PlaybackThread.run()` — [`ovos_audio/playback.py:45`](https://github.com/OpenVoiceOS/ovos-audio/blob/dev/ovos_audio/playback.py) — logic for playing back the synthesized audio chunks.


    - `AudioService.play()` — [`ovos_audio/audio.py:150`](https://github.com/OpenVoiceOS/ovos-audio/blob/dev/ovos_audio/audio.py) — logic for routing media playback to the correct backend (MPV, VLC, etc.).
    
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

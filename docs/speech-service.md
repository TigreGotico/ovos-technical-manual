# Speech Service

`ovos-dinkum-listener` is the service responsible for audio capture, [Wake Word](wake-word-plugins.md) detection, and [Speech-to-Text](stt-plugins.md) ([STT](stt-plugins.md)).

---

??? abstract "Technical Reference"

    - `OVOSDinkumVoiceService.run()` — [`ovos_dinkum_listener/service.py:185`](https://github.com/OpenVoiceOS/ovos-dinkum-listener/blob/dev/ovos_dinkum_listener/service.py) — Main service thread managing the voice loop.


    - `DinkumVoiceLoop.step()` — [`ovos_dinkum_listener/voice_loop/__init__.py`](https://github.com/OpenVoiceOS/ovos-dinkum-listener/blob/dev/ovos_dinkum_listener/voice_loop/__init__.py) — The core loop that processes audio chunks for [VAD](vad-plugins.md) and [Wake Word](wake-word-plugins.md).


    - `OVOSDinkumVoiceService.handle_utterance()` — [`ovos_dinkum_listener/service.py:410`](https://github.com/OpenVoiceOS/ovos-dinkum-listener/blob/dev/ovos_dinkum_listener/service.py) — logic for sending audio to [STT](stt-plugins.md) and emitting the `recognizer_loop:utterance` message.
    
    ---
    

## Overview

The speech service is the "ears" of OpenVoiceOS. It continuously listens to the environment, waiting for a specific [Wake Word](wake-word-plugins.md). When the word is detected, it records the user's command and sends it to an [STT](stt-plugins.md) engine for transcription.

### Key Components

- **Microphone Plugin**: Captures raw audio from the hardware.


- **[Voice Activity Detection](vad-plugins.md) ([VAD](vad-plugins.md))**: Identifies when a user starts and stops speaking.


- **[Wake Word](wake-word-plugins.md) Plugin**: Monitors the audio stream for the trigger phrase.


- **[STT](stt-plugins.md) Plugin**: Transcribes the recorded command into text.

## Architecture

```
[Microphone] --(audio)--> [VAD/Wake Word] --(trigger)--> [Recording]
                                                            |
                                                            +--(audio)--> [STT Plugin] --(text)--> [MessageBus]

```

## Configuration

The speech service is configured in the `listener`, `hotwords`, and `stt` sections of `mycroft.conf`.

```json
{
  "listener": {
    "microphone": {
      "module": "ovos-microphone-plugin-alsa"
    },
    "VAD": {
      "module": "ovos-vad-plugin-silero"
    }
  },
  "stt": {
    "module": "ovos-stt-plugin-server"
  }
}

```

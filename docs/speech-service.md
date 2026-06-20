# Speech Service

> Specification: the audio-input service contract is defined by [OVOS-AUDIO-IN-1: Audio Input Service](https://github.com/OpenVoiceOS/architecture/blob/dev/ovos-audio-in-1.md).

`ovos-dinkum-listener` is the service responsible for audio capture, [Wake Word](wake-word-plugins.md) detection, and [Speech-to-Text](stt-plugins.md) ([STT](stt-plugins.md)). It is the default, full-featured listener; `ovos-simple-listener` is a lighter alternative that emits the same `recognizer_loop:*` bus events but without the full state machine.

---

??? abstract "Technical Reference"

    - `OVOSDinkumVoiceService` — [`ovos_dinkum_listener/service.py:98`](https://github.com/OpenVoiceOS/ovos-dinkum-listener/blob/dev/ovos_dinkum_listener/service.py) — the service `Thread`; `run()` (`:381`) connects to the bus and drives the voice loop.


    - `DinkumVoiceLoop.run()` — [`ovos_dinkum_listener/voice_loop/voice_loop.py:275`](https://github.com/OpenVoiceOS/ovos-dinkum-listener/blob/dev/ovos_dinkum_listener/voice_loop/voice_loop.py) — the per-chunk state machine that drives [VAD](vad-plugins.md), [Wake Word](wake-word-plugins.md) and [STT](stt-plugins.md) via per-state handlers (`_detect_ww`, `_wait_cmd`, `_in_cmd`, …).


    - `OVOSDinkumVoiceService._stt_text()` — [`ovos_dinkum_listener/service.py:765`](https://github.com/OpenVoiceOS/ovos-dinkum-listener/blob/dev/ovos_dinkum_listener/service.py) — emits the utterance message after [STT](stt-plugins.md) returns text: `recognizer_loop:utterance` by default, or `ovos.utterance.handle` when the top-level `legacy_namespace` config is `false`.
    
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

## Listening State Machine

`DinkumVoiceLoop` is a per-chunk state machine, not a single "listen" call. It has a
global **mode** (set in `listener.mode` / over the bus) and an internal **state** that
advances chunk by chunk:

- **Modes** (`ListeningMode`): `wakeword` (default — wait for the wake word),
  `continuous` (always transcribe), `hybrid` (continuous but only act after the wake
  word), `sleeping`.


- **States** (`ListeningState`): `wakeword` → `recording` → `in_cmd` → `after_cmd`,
  plus `sleeping` / `wake_up`, `confirmation`, `before_cmd`, `pre_wake_vad`.

Source: `ovos_dinkum_listener/voice_loop/voice_loop.py:36` (`ListeningState`) and `:53`
(`ListeningMode`).

## Bus Events

The listener publishes its activity on the OVOS [MessageBus](bus-service.md). The most
useful events for downstream services:

| Message | Payload | Meaning |
|---|---|---|
| `recognizer_loop:record_begin` | none | Command recording started |
| `recognizer_loop:record_end` | none | Command recording ended |
| `recognizer_loop:wakeword` | `{"utterance", "lang"}` | Wake word fired |
| `recognizer_loop:utterance` | `{"utterances": [str], "lang"}` | Transcribed command (the main result) |
| `recognizer_loop:speech.recognition.unknown` | none | STT returned nothing (silence / failure) |
| `recognizer_loop:awoken` | none | Listener woke from sleep |

It also reacts to inbound commands such as `recognizer_loop:sleep`,
`recognizer_loop:wake_up`, `recognizer_loop:record_stop` and `recognizer_loop:state.get`.
The full table lives in the bus-message spec (`message_spec/dinkum.md`).

!!! note "Gotcha — utterance namespace"

    By default the transcribed command is published as `recognizer_loop:utterance`.
    Setting the top-level `legacy_namespace: false` config switches **all** utterance
    entry points to the spec topic `ovos.utterance.handle` instead — make sure your
    pipeline subscribes to the matching topic.

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

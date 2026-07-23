# Speech Service

!!! abstract "In a nutshell"
    The speech service is the "ears" of OpenVoiceOS. It listens through the microphone, waits for a wake word (like "Hey Mycroft"), and then turns whatever you say next into text so the rest of the system can act on it. Think of it as the part that hears you and writes down your request. From here that text is handed off to the [Intent Service](intent-service.md), which works out what to do. New to the terms? See the [Glossary](glossary.md).

??? info "📐 Formal specification"
    The capture → audio-transformer chain → STT → utterance flow and the listening-lifecycle signals are specified by **[OVOS-AUDIO-IN-1 — Audio Input Service](https://github.com/OpenVoiceOS/architecture/blob/dev/audio-in.md)**; the audio-transformer chain that runs on the raw audio before STT by **[OVOS-TRANSFORM-1 — Transformer Plugins](https://github.com/OpenVoiceOS/architecture/blob/dev/transformer.md)** (§3.1). See also the [spec index](architecture-specs.md). `ovos-dinkum-listener` is the reference implementation; the spec topic names below are canonical, with the legacy name noted once.

`ovos-dinkum-listener` is the service responsible for audio capture, [Wake Word](wake-word-plugins.md) detection, and [Speech-to-Text](stt-plugins.md) ([STT](stt-plugins.md)). It is the default, full-featured listener; `ovos-simple-listener` is a lighter alternative that emits the same `recognizer_loop:*` bus events but without the full state machine.

A third, even more minimal option is `mycroft-classic-listener` — the original mycroft-core listener ported to the OVOS plugin ecosystem. It implements the same `recognizer_loop:*` contract but does **not** support `instant_listen`, multiple hotwords, VAD, listening modes, or fallback STT (fallback hotwords via OPM are supported).

---

??? abstract "Technical Reference"

    - `OVOSDinkumVoiceService` — [`ovos_dinkum_listener/service.py`](https://github.com/OpenVoiceOS/ovos-dinkum-listener/blob/dev/ovos_dinkum_listener/service.py) — the service `Thread`; `run()` connects to the bus and drives the voice loop.


    - `DinkumVoiceLoop.run()` — [`ovos_dinkum_listener/voice_loop/voice_loop.py`](https://github.com/OpenVoiceOS/ovos-dinkum-listener/blob/dev/ovos_dinkum_listener/voice_loop/voice_loop.py) — the per-chunk state machine that drives [VAD](vad-plugins.md), [Wake Word](wake-word-plugins.md) and [STT](stt-plugins.md) via per-state handlers.


    - `OVOSDinkumVoiceService._stt_text()` — [`ovos_dinkum_listener/service.py`](https://github.com/OpenVoiceOS/ovos-dinkum-listener/blob/dev/ovos_dinkum_listener/service.py) — emits the utterance message after [STT](stt-plugins.md) returns text: the listener itself emits `recognizer_loop:utterance`; `ovos-bus-client`'s automatic namespace bridge (see [Bus Service](bus-service.md#namespace-migration)) mirrors it to `ovos.utterance.handle` for consumers on the spec topic.
    
    ---
    

## Overview

The speech service is the "ears" of OpenVoiceOS. It continuously listens to the environment, waiting for a specific [Wake Word](wake-word-plugins.md). When the word is detected, it records the user's command and sends it to an [STT](stt-plugins.md) engine for transcription.

### Key Components

- **Microphone Plugin**: Captures raw audio from the hardware.


- **[Voice Activity Detection](vad-plugins.md) ([VAD](vad-plugins.md))**: Identifies when a user starts and stops speaking.


- **[Wake Word](wake-word-plugins.md) Plugin**: Monitors the audio stream for the trigger phrase.


- **[STT](stt-plugins.md) Plugin**: Transcribes the recorded command into text.

## Architecture

```text
[Microphone] --(audio)--> [VAD/Wake Word] --(trigger)--> [Recording]
                                                            |
                                                            +--(audio)--> [Audio-transformer chain] --> [STT Plugin] --(text)--> [MessageBus]
                                                                          (TRANSFORM-1 §3.1)            emits ovos.utterance.handle

```

## Listening State Machine

`DinkumVoiceLoop` is a per-chunk state machine, not a single "listen" call. It has a
global **mode** (set in `listener.mode` / over the bus) and an internal **state** that
advances chunk by chunk:

- **Modes** (`ListeningMode`): `wakeword` (default — wait for the wake word),
  `continuous` (always transcribe), `hybrid` (continuous but only act after the wake
  word), `sleeping`.


- **States** (`ListeningState`): `wakeword` → `recording` → `in_cmd` → `after_cmd`,
  plus `sleeping` / `wake_up`, `confirmation`, `before_cmd`, `pre_wake_vad`, and
  `WAITING_CMD = "continuous"` — the state used while continuous/hybrid listening waits
  for an utterance without a wake word.

Source: `ovos_dinkum_listener/voice_loop/voice_loop.py:36` (`ListeningState`) and `:53`
(`ListeningMode`).

## Bus Events

The listener emits its activity on the OVOS [messagebus](bus-service.md). The most
useful events for downstream services:

Canonical (spec) names are shown first, with the legacy name current code still emits in parentheses. The `ovos.listener.*` and `ovos.utterance.handle` names come from [OVOS-AUDIO-IN-1 §5–§6](https://github.com/OpenVoiceOS/architecture/blob/dev/audio-in.md); `ovos-dinkum-listener` itself still emits only the legacy names, and `ovos-bus-client`'s automatic namespace bridge (see [Bus Service](bus-service.md#namespace-migration)) mirrors them onto the spec topics by default.

| Message | Payload | Meaning |
|---|---|---|
| `ovos.listener.record.started` (legacy: `recognizer_loop:record_begin`) | none | Command recording started (§6.1) |
| `ovos.listener.record.ended` (legacy: `recognizer_loop:record_end`) | none | Command recording ended (§6.2) |
| `recognizer_loop:wakeword` | `{"utterance", "lang"}` | Wake word fired (implementation event; not respecified by AUDIO-IN-1 §6) |
| `ovos.utterance.handle` (legacy: `recognizer_loop:utterance`) | `{"utterances": [str], "lang"}` | Transcribed command — the main result (§5, OVOS-PIPELINE-1 §9.1) |
| `recognizer_loop:speech.recognition.unknown` | none | STT returned nothing (silence / failure) |
| `ovos.listener.awoken` (legacy: `mycroft.awoken`) | none | Listener woke from sleep (§6.4) |

It also reacts to inbound commands such as `recognizer_loop:sleep`,
`recognizer_loop:wake_up`, `recognizer_loop:record_stop` and `recognizer_loop:state.get`.
The full table lives in the bus-message spec (`message_spec/dinkum.md`).

!!! note "Gotcha — utterance namespace"

    The listener publishes the transcribed command as `recognizer_loop:utterance`.
    `ovos-bus-client`'s namespace bridge (on by default) also mirrors it onto
    `ovos.utterance.handle`, so subscribers can use either topic name — see
    [Bus Service — Namespace migration](bus-service.md#namespace-migration) for how
    to turn that bridging off once every consumer speaks the spec namespace.

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

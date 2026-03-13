# Architecture Overview

OpenVoiceOS (OVOS) is a **modular voice assistant platform**. Unlike monolithic systems, OVOS is composed of independent services that communicate over a common **[MessageBus](bus-service.md)**. This modularity allows you to run only the components you need, swap out plugins for different backends, and even distribute services across multiple devices.

## High-Level Flow

![Full Flow](img/Full%20flow.jpeg)

The diagram above illustrates how a user utterance moves through the system:

1. **Microphone Input**: Captured by a microphone plugin.


2. **[Wake Word](wake-word-plugins.md) Detection**: The `ovos-dinkum-listener` (or similar) monitors the stream for the wake word.


3. **[Speech-to-Text](stt-plugins.md) ([STT](stt-plugins.md))**: Once the wake word is detected, the subsequent audio is sent to an STT engine.


4. **MessageBus**: The transcribed text is published to the bus as a `recognizer_loop:utterance`.


5. **[Intent Service](intent-service.md)**: `ovos-core` picks up the utterance and routes it through the **Intent Pipeline**.


6. **[Skill](skill-design-guidelines.md) Execution**: If a match is found, the corresponding skill is triggered.


7. **Response**: The skill emits a `speak` message.


8. **[Text-to-Speech](tts-plugins.md) ([TTS](tts-plugins.md))**: `ovos-audio` converts the response text to audio and plays it.

---

## Component Map

```
ovos-messagebus  (WebSocket pub/sub)
      │
      ├── ovos-core
      │     ├── SkillManager          – loads/unloads skill plugins
      │     ├── IntentService         – routes utterances through the pipeline
      │     │     ├── UtteranceTransformersService
      │     │     ├── MetadataTransformersService
      │     │     ├── IntentTransformersService
      │     │     └── Pipeline plugins (Adapt, Padatious, Converse, Fallback, …)
      │     ├── SkillsStore           – runtime pip install/uninstall
      │     └── EventScheduler        – timed bus events
      │
      ├── ovos-dinkum-listener  – STT / wake-word → recognizer_loop:utterance
      ├── ovos-audio            – TTS playback
      ├── ovos-gui              – GUI layer
      └── ovos-phal             – hardware/platform plugins

```

## Key Services

### MessageBus
The backbone of OVOS. All components communicate via this WebSocket-based bus. It ensures loose coupling and enables remote control and multi-device setups.

### ovos-core
The "brain" of the system. It manages the lifecycle of skills and coordinates intent matching through a sophisticated, multi-stage pipeline.

### Speech Service
Handles audio capture, wake word detection, and STT. It is responsible for turning "sound" into "data".

### Audio Service
The output layer. It manages TTS generation and audio playback, ensuring that only one thing is speaking at a time and handling audio focus.

### GUI Service
Provides a visual interface for skills. It uses a specialized protocol to push [QML](qt5-gui.md)-based or HTML-based views to a screen.

### PHAL (Platform & Hardware Abstraction Layer)
Handles hardware-specific tasks like volume control, battery monitoring, and connectivity management.

---

## Modularity and Plugins

One of OVOS's greatest strengths is its plugin-based architecture. Almost every major function is a plugin:

- **Microphone Plugins**: ALSA, PyAudio, etc.


- **STT/TTS Plugins**: Google, Whisper, Coqui, etc.


- **Wake Word Plugins**: Precise, PocketSphinx, Snowboy, etc.


- **Intent Plugins**: [Adapt](adapt-pipeline.md), [Padatious](padatious-pipeline.md), [Common Query](cq-pipeline.md), etc.

This allows OVOS to run on everything from a high-end server to a Raspberry Pi Zero.

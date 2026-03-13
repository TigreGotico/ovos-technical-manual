# Glossary of Terms

This glossary defines common terms, acronyms, and concepts used throughout the OpenVoiceOS (OVOS) ecosystem.

| Term | Definition |
|---|---|
| **[Adapt](adapt-pipeline.md)** | A keyword-based intent parser used for simple, high-confidence commands. |
| **[Agent Engine](agent-plugins.md)** | (Formerly [Solver](agent-plugins.md)) A plugin that provides answers to questions or interacts with LLMs (e.g., ChatEngine, RetrievalEngine). |
| **Audio Service** | The OVOS component (`ovos-audio`) responsible for [TTS](tts-plugins.md) synthesis and audio playback. |
| **Bus / [MessageBus](bus-service.md)** | The WebSocket-based communication backbone of OVOS. |
| **[Common Play](ocp-pipeline.md) ([OCP](ocp-pipeline.md))** | A framework and intent handler specialized in finding and playing media (music, video, podcasts). |
| **[Converse](converse-pipeline.md)** | A mechanism that allows skills to intercept utterances during an active session (continuous conversation). |
| **Enclosure** | The physical hardware housing the assistant (e.g., Mycroft Mark 1). |
| **Entity** | A specific piece of data extracted from an utterance (e.g., "London" in "What is the weather in London?"). |
| **[Fallback](fallback-pipeline.md)** | A stage in the intent pipeline where skills can attempt to handle utterances that weren't matched by high-priority parsers. |
| **G2P (Grapheme-to-Phoneme)** | The process of converting written text into phonetic representations for pronunciation. |
| **GUI Service** | The component (`ovos-gui`) that manages visual displays and [QML](qt5-gui.md)/HTML interfaces. |
| **[HiveMind](hivemind-agents.md)** | A protocol and ecosystem for connecting "satellites" (limited hardware) to a central OVOS "hub". |
| **Intent** | The identified goal or request of a user's utterance (e.g., "WeatherIntent"). |
| **Intent Pipeline** | The ordered sequence of parsers and matchers used to resolve an utterance into an intent. |
| **[Kirigami](qt5-gui.md)** | A UI framework from KDE used for building responsive OVOS GUI interfaces. |
| **Message** | A JSON object sent over the MessageBus, containing a `type`, `data`, and `context`. |
| **MiniCroft** | A lightweight, in-process version of OVOS Core used for end-to-end testing with `ovoscope`. |
| **OCP Stream Extractor** | A plugin that resolves abstract URIs (like YouTube links) into playable media streams. |
| **OPM (ovos-plugin-manager)** | The library responsible for discovering and loading OVOS plugins. |
| **[Padatious](padatious-pipeline.md)** | An expression-based intent parser that uses neural networks to match utterances based on examples. |
| **[PHAL](ovoscope-phal.md)** | [Platform & Hardware Abstraction Layer](ovoscope-phal.md); a service that handles low-level hardware interactions (volume, buttons, etc.). |
| **QML** | A declarative language used for designing the user interface of OVOS skills. |
| **[Session](session.md)** | A data structure representing a specific user interaction or conversation state across multiple turns. |
| **[Skill](skill-design-guidelines.md)** | A modular plugin that adds specific functionality to OVOS (e.g., "Weather Skill"). |
| **[STT](stt-plugins.md) ([Speech-to-Text](stt-plugins.md))** | The process of transcribing spoken audio into text. |
| **[Transformer](transformer-plugins.md)** | A plugin that modifies audio, text, or metadata as it moves through the pipeline. |
| **TTS ([Text-to-Speech](tts-plugins.md))** | The process of synthesizing spoken audio from text. |
| **[Utterance](life-of-an-utterance.md)** | The text transcription of a user's spoken command. |
| **[VAD](vad-plugins.md) ([Voice Activity Detection](vad-plugins.md))** | The process of detecting when a user starts and stops speaking. |
| **Visemes** | Visual representations of phonemes used for lip-sync animations on a GUI. |
| **[Wake Word](wake-word-plugins.md)** | The specific phrase (e.g., "Hey Mycroft") that triggers the listener to start recording. |

# Glossary of Terms

This glossary defines common terms, acronyms, and concepts used throughout the OpenVoiceOS (OVOS) ecosystem. New to OVOS? Skim this first — most pages assume these words.

| Term | Definition |
|---|---|
| **[Adapt](adapt-pipeline.md)** | A keyword-based intent parser used for simple, high-confidence commands. |
| **[Agent Engine](agent-plugins.md)** | (Formerly [Solver](agent-plugins.md)) A plugin that provides answers to questions or interacts with LLMs (e.g., ChatEngine, RetrievalEngine). |
| **ASR (Automatic Speech Recognition)** | Another name for [STT](stt-plugins.md) — turning spoken audio into text. |
| **Audio Service** | The OVOS component (`ovos-audio`) responsible for [TTS](tts-plugins.md) synthesis and audio playback. |
| **Bus / [MessageBus](bus-service.md)** | The WebSocket-based communication backbone of OVOS. Every service talks by sending JSON [messages](bus-service.md) over it. |
| **[Common Play](ocp-pipeline.md) ([OCP](ocp-pipeline.md))** | OpenVoiceOS Common Play — a framework and intent handler specialized in finding and playing media (music, video, podcasts). |
| **Constraints file** | A version "filter" (a pip [constraints file](release-channels.md)) that pins which package versions a [release channel](release-channels.md) allows. |
| **[Converse](converse-pipeline.md)** | A mechanism that allows skills to intercept utterances during an active session (continuous conversation). |
| **[Dialog](statements.md)** | A `.dialog` file holding sentences **OVOS speaks** (often with `{variables}`). The output counterpart of an intent. |
| **Dinkum Listener** | `ovos-dinkum-listener`, the default [voice loop](speech-service.md): wake word → record → [VAD](vad-plugins.md) → [STT](stt-plugins.md). |
| **Embeddings** | Numeric vectors that capture the *meaning* of text (or audio/images), so similar things sit close together. Used for semantic search and [RAG memory](persona-memory.md). |
| **Enclosure** | The physical hardware housing the assistant (e.g., Mycroft [Mark 1](mark1.md)). |
| **Entity** | A specific piece of data extracted from an utterance (e.g., "London" in "What is the weather in London?"). |
| **Entry point** | A line in a package's `pyproject.toml` / `setup.py` that advertises a plugin or skill class to OVOS, so [OPM](plugin-manager.md) can discover it (e.g. under `opm.stt` or `opm.skill`). |
| **Extras** | Optional install bundles in brackets, e.g. `ovos-core[mycroft]`, that pull in predefined groups of components. See [Installation](release-channels.md). |
| **[Fallback](fallback-pipeline.md)** | A stage in the intent pipeline where skills can attempt to handle utterances that weren't matched by high-priority parsers. |
| **G2P (Grapheme-to-Phoneme)** | The process of converting written text into phonetic representations for pronunciation. See [G2P plugins](g2p-plugins.md). |
| **GUI Service** | The component (`ovos-gui`) that manages visual displays and [QML](qt5-gui.md)/HTML interfaces. ⚠️ The current ("legacy") GUI is [deprecated](gui-service.md) — there is no usable OVOS GUI right now; a replacement is in progress. |
| **Headless** | A device with no monitor or keyboard (e.g. a Raspberry Pi you control over SSH). OVOS runs happily headless. |
| **[HiveMind](hivemind-agents.md)** | A protocol and ecosystem for connecting "satellites" (limited hardware) to a central OVOS server. |
| **`hivemind-core`** | In [HiveMind](hivemind-agents.md), the central server that satellites and clients connect to for the heavy work (skills, [STT](stt-plugins.md)/[TTS](tts-plugins.md), LLM). |
| **Intent** | The identified goal or request of a user's utterance (e.g., "WeatherIntent"). |
| **Intent file (`.intent`)** | A list of example sentences **a user might say** to trigger a [skill](skill-design-guidelines.md) — a *template (example-based)* intent matched by [Padatious](padatious-pipeline.md). |
| **[Intent Pipeline](pipelines-overview.md)** | The ordered sequence of parsers and matchers used to resolve an utterance into an intent. |
| **IPA (International Phonetic Alphabet)** | A standard notation for the individual sounds of speech, used by [G2P](g2p-plugins.md) / phonemizers. |
| **[Kirigami](qt5-gui.md)** | A UI framework from KDE used for building responsive OVOS GUI interfaces. |
| **Listener** | The service that captures microphone audio, detects the [wake word](wake-word-plugins.md), and records speech for transcription. See [Speech Service](speech-service.md). |
| **[Mark 1 / Mark 2](mark1.md)** | Mycroft's reference hardware devices. OVOS still supports the Mark 1 faceplate and the Mark 2. |
| **Message** | A JSON object sent over the MessageBus, containing a `type`, `data`, and `context`. |
| **MiniCroft** | A lightweight, in-process version of OVOS Core used for end-to-end testing with `ovoscope`. |
| **`mycroft.conf`** | OVOS's main [configuration](config.md) file (JSON). The same filename is layered across system → distribution → user locations, with the user's copy winning. |
| **OCP Stream Extractor** | A plugin that resolves abstract URIs (like YouTube links) into playable media streams. |
| **ONNX** | An open, portable model format OVOS uses to run STT / TTS / wake-word neural models efficiently across platforms (CPU-friendly). |
| **OPM ([ovos-plugin-manager](plugin-manager.md))** | The library responsible for discovering and loading OVOS plugins. |
| **OVOS (OpenVoiceOS)** | The whole open-source, privacy-respecting voice assistant platform this manual documents. |
| **ovos-core** | The "brain" service that runs skills and decides which one should answer an utterance. See [ovos-core](core.md). |
| **[ovos-installer](ovos-installer.md)** | The guided installer (a TUI wizard) that sets OVOS up for you — the recommended way to install. |
| **[Padatious](padatious-pipeline.md)** | An example-based intent parser that uses a small neural network to match utterances against sample sentences. |
| **[Persona](personas.md)** | A configurable AI personality (backed by an [agent engine](agent-plugins.md) / LLM) that answers open-ended questions. |
| **[PHAL](phal.md)** | Platform & Hardware Abstraction Layer; a service that handles low-level hardware interactions (volume, buttons, etc.). |
| **Plugin** | A swappable building block (a [STT](stt-plugins.md), [TTS](tts-plugins.md), [wake word](wake-word-plugins.md), [VAD](vad-plugins.md)… engine). Plugins change *how* OVOS works; [skills](skill-design-guidelines.md) add *what* it can do. |
| **QML** | A declarative language used for designing the user interface of OVOS skills. |
| **RAG (Retrieval-Augmented Generation)** | Fetching relevant remembered/retrieved context and giving it to an LLM *before* it answers. See [Persona Memory](persona-memory.md). |
| **Release Channel** | A stability track — *stable*, *testing*, or *alpha* — that controls how new the installed packages are. See [Release Channels](release-channels.md). |
| **Satellite** | In [HiveMind](hivemind-agents.md), a lightweight device (e.g. a small Pi) that captures voice and forwards it to `hivemind-core`. |
| **[Session](session.md)** | A data structure representing a specific user interaction or conversation state across multiple turns. |
| **[Skill](skill-design-guidelines.md)** | A modular add-on that gives OVOS a new ability (e.g., "Weather Skill"). |
| **Skill Settings** | Per-skill configuration, optionally editable by the user. See [Skill Settings](skill-settings.md). |
| **`skill_id`** | A skill's unique identifier (e.g. `ovos-skill-weather.openvoiceos`), taken from its [entry point](plugin-manager.md). Used to namespace its settings, events, and resources. |
| **Solver** | The former name for an [Agent Engine](agent-plugins.md) — you'll still see it in older configs and code. |
| **SSML (Speech Synthesis Markup Language)** | Tags that control *how* [TTS](tts-plugins.md) speaks a sentence — pauses, emphasis, pitch, rate. See [SSML](ssml.md). |
| **[STT](stt-plugins.md) ([Speech-to-Text](stt-plugins.md))** | The process of transcribing spoken audio into text. |
| **[Transformer](transformer-plugins.md)** | A plugin that modifies audio, text, or metadata as it moves through the pipeline. |
| **TTS ([Text-to-Speech](tts-plugins.md))** | The process of synthesizing spoken audio from text. |
| **[Utterance](life-of-an-utterance.md)** | The text transcription of a user's spoken command. |
| **[VAD](vad-plugins.md) ([Voice Activity Detection](vad-plugins.md))** | The process of detecting when a user starts and stops speaking. |
| **Visemes** | Visual representations of phonemes used for lip-sync animations on a GUI. |
| **Vocabulary (`.voc`)** | A file of keywords / sentence fragments (not full sentences) used by *keyword (rule-based)* intents — what [Adapt](adapt-pipeline.md) and skills match against. |
| **[Wake Word](wake-word-plugins.md)** | The specific phrase (e.g., "Hey Mycroft") that triggers the listener to start recording. |
| **[Wyoming](wyoming-bridges.md)** | A simple voice protocol (from the Home Assistant world) that OVOS can bridge to and from. |
| **XDG** | The freedesktop standard for *where* config / data / cache files live (`~/.config`, `~/.local/share`, …). OVOS follows it, so your settings aren't scattered. |

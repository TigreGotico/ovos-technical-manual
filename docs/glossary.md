# Glossary of Terms

This glossary defines common terms, acronyms, and concepts used throughout the OpenVoiceOS (OVOS) ecosystem. New to OVOS? Skim this first — most pages assume these words.

??? info "📐 Formal specification"
    Entries marked **📐** name part of the **formal vocabulary** of the OVOS
    architecture — concepts with a normative, implementation-agnostic
    definition. Each links to its authoritative spec; for the full set and how
    they fit together see the **[spec index](architecture-specs.md)**. You can
    safely skip these on a first read — they matter once you're checking a
    component for spec conformance, not for everyday use.

| Term | Definition |
|---|---|
| **[Adapt](adapt-pipeline.md)** | A keyword-based intent parser used for simple, high-confidence commands. Its `.voc` keywords use the shared template grammar (📐 [OVOS-INTENT-1](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-1.md)). |
| **[Agent Engine](agent-plugins.md)** | (Formerly [Solver](agent-plugins.md)) A plugin that provides answers to questions or interacts with LLMs (e.g., ChatEngine, RetrievalEngine). |
| **ASR (Automatic Speech Recognition)** | Another name for [STT](stt-plugins.md) — turning spoken audio into text. |
| **Audio Service** | The OVOS component (`ovos-audio`) responsible for [TTS](tts-plugins.md) synthesis and audio playback. |
| **Bus / [messagebus](bus-service.md)** | The WebSocket-based communication backbone of OVOS. Every service talks by sending JSON [messages](bus-service.md) over it. |
| **[Common Play](ocp-pipeline.md) ([OCP](ocp-pipeline.md))** | OpenVoiceOS Common Play — a framework and intent handler specialized in finding and playing media (music, video, podcasts). The per-session *virtual media player* it arbitrates is specified by 📐 [OVOS-OCP-1](https://github.com/OpenVoiceOS/architecture/blob/dev/ocp-1.md). |
| **Constraints file** | A version "filter" (a pip [constraints file](release-channels.md)) that pins which package versions a [release channel](release-channels.md) allows. |
| **[Converse](converse-pipeline.md)** | A mechanism that allows skills to intercept utterances during an active session (continuous conversation). Specified by 📐 [OVOS-CONVERSE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/converse.md). |
| **[Dialog](statements.md)** | A `.dialog` file holding sentences **OVOS speaks** (often with `{variables}`). The output counterpart of an intent. Its format is specified by 📐 [OVOS-INTENT-2](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-2.md), its grammar by 📐 [OVOS-INTENT-1](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-1.md). |
| **Dinkum Listener** | `ovos-dinkum-listener`, the default [voice loop](speech-service.md): wake word → record → [VAD](vad-plugins.md) → [STT](stt-plugins.md). |
| **📐 Dispatch-shaped topic** | A bus topic containing `:`, assembled from identifiers to address one specific registered handler — canonically `<skill_id>:<intent_name>`. The `:` is the marker; only a formal specification may define a colon-bearing topic shape. 📐 [OVOS-MSG-1 §2.1.1](https://github.com/OpenVoiceOS/architecture/blob/dev/msg-1.md). |
| **📐 Dotted addressed topic** | An ordinary `:`-free dotted topic (`<x>.<y>.<verb>`) that names a specific recipient in one of its segments — e.g. `<skill_id>.common_query.request` — an addressed message, not a dispatch. 📐 [OVOS-MSG-1 §2.1.1](https://github.com/OpenVoiceOS/architecture/blob/dev/msg-1.md), [OVOS-COMMON-QUERY-1 §7](https://github.com/OpenVoiceOS/architecture/blob/dev/common-query.md). |
| **Embeddings** | Numeric vectors that capture the *meaning* of text (or audio/images), so similar things sit close together. Used for semantic search and [RAG memory](persona-memory.md). |
| **Enclosure** | The physical hardware housing the assistant (e.g., Mycroft [Mark 1](mark1.md)). |
| **Entity** | A specific piece of data extracted from an utterance (e.g., "London" in "What is the weather in London?"). |
| **Entry point** | A line in a package's `pyproject.toml` / `setup.py` that advertises a plugin or skill class to OVOS, so [OPM](plugin-manager.md) can discover it (e.g. under `opm.stt` or `opm.skill`). |
| **Extras** | Optional install bundles in brackets, e.g. `ovos-core[mycroft]`, that pull in predefined groups of components. See [Installation](release-channels.md). |
| **[Fallback](fallback-pipeline.md)** | A stage in the intent pipeline where skills can attempt to handle utterances that weren't matched by high-priority parsers. Specified by 📐 [OVOS-FALLBACK-1](https://github.com/OpenVoiceOS/architecture/blob/dev/fallback.md). |
| **📐 First-match-wins** | The pipeline's arbitration model: the orchestrator walks the **pipeline plugins** in `session.pipeline` order and dispatches the **first** one that returns a `Match` — ordering is *policy*, and an earlier plugin gets to answer before any later plugin is asked. This (not a confidence ranking) is what lets a stage such as [Converse](converse-pipeline.md) intercept an utterance ahead of normal intent matching. 📐 [OVOS-PIPELINE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md). |
| **G2P (Grapheme-to-Phoneme)** | The process of converting written text into phonetic representations for pronunciation. See [G2P plugins](g2p-plugins.md). |
| **GUI Service** | The component (`ovos-gui`) that manages visual displays and [QML](qt5-gui.md)/HTML interfaces. ⚠️ The current ("legacy") GUI is [deprecated](gui-service.md) — there is no usable OVOS GUI right now; a replacement is in progress. |
| **Headless** | A device with no monitor or keyboard (e.g. a Raspberry Pi you control over SSH). OVOS runs happily headless. |
| **home.mycroft.ai** | The old Mycroft AI cloud account/backend portal used for device pairing, remote skill settings, and STT. OVOS has no equivalent — it is **backendless** by design, with no account or pairing step required. See [Deprecated & Archived Repositories](deprecated-repos.md) and [Migrating from Mycroft](migrating-from-mycroft.md). |
| **[HiveMind](hivemind-agents.md)** | A protocol and ecosystem for connecting "satellites" (limited hardware) to a central OVOS server. |
| **`hivemind-core`** | In [HiveMind](hivemind-agents.md), the central server that satellites and clients connect to for the heavy work (skills, [STT](stt-plugins.md)/[TTS](tts-plugins.md), LLM). |
| **Intent** | The identified goal or request of a user's utterance (e.g., "WeatherIntent"). |
| **Intent file (`.intent`)** | A list of example sentences **a user might say** to trigger a [skill](skill-design-guidelines.md) — a *template (example-based)* intent matched by [Padatious](padatious-pipeline.md). |
| **[Intent Pipeline](pipelines-overview.md)** | The ordered sequence of parsers and matchers used to resolve an utterance into an intent. Specified by 📐 [OVOS-PIPELINE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md). |
| **IPA (International Phonetic Alphabet)** | A standard notation for the individual sounds of speech, used by [G2P](g2p-plugins.md) / phonemizers. |
| **[Kirigami](qt5-gui.md)** | A UI framework from KDE used for building responsive OVOS GUI interfaces. |
| **Listener** | The service that captures microphone audio, detects the [wake word](wake-word-plugins.md), and records speech for transcription. See [Speech Service](speech-service.md). |
| **[Mark 1](mark1.md) / [Mark 2](mark2.md)** | Mycroft's reference hardware devices. The Mark 1 is a faceplate-only speaker; the Mark 2 is a Raspberry Pi 4 device with a touchscreen running the full OVOS GUI stack. Both are still supported. |
| **📐 Match Contract** | The single method every **pipeline plugin** exposes: `match(utterances, lang, session) → Match \| None`. It is the "system-call ABI" of the voice OS — the orchestrator knows nothing about a plugin except this signature. Returning a `Match` claims the utterance; returning `None` declines it. 📐 [OVOS-PIPELINE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md). |
| **Message** | A JSON object sent over the messagebus, containing a `type`, `data`, and `context`. |
| **MiniCroft** | A lightweight, in-process version of OVOS Core used for end-to-end testing with `ovoscope`. |
| **`mycroft.conf`** | OVOS's main [configuration](config.md) file (JSON). The same filename is layered across system → distribution → user locations, with the user's copy winning. |
| **OCP Stream Extractor** | A plugin that resolves abstract URIs (like YouTube links) into playable media streams. |
| **ONNX** | An open, portable model format OVOS uses to run STT / TTS / wake-word neural models efficiently across platforms (CPU-friendly). |
| **OPM ([ovos-plugin-manager](plugin-manager.md))** | The library responsible for discovering and loading OVOS plugins. |
| **📐 Orchestrator** | The logical role that drives the [intent pipeline](pipelines-overview.md): it iterates the **pipeline plugins**, dispatches the winning **Match** to the owning handler on `<skill_id>:<intent_name>`, and emits the handler-lifecycle events (`ovos.intent.handler.start` / `.complete` / `.error`). In OVOS this role is filled by [ovos-core](core.md), but the spec is implementation-agnostic — any conformant orchestrator works. 📐 [OVOS-PIPELINE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md). |
| **OVOS (OpenVoiceOS)** | The whole open-source, privacy-respecting voice assistant platform this manual documents. |
| **ovos-core** | The "brain" service that runs skills and decides which one should answer an utterance. See [ovos-core](core.md). |
| **[ovos-installer](ovos-installer.md)** | The guided installer (a TUI wizard) that sets OVOS up for you — the recommended way to install. |
| **[Padatious](padatious-pipeline.md)** | An example-based intent parser that uses a small neural network to match utterances against sample sentences. |
| **[Persona](personas.md)** | A configurable AI personality (backed by an [agent engine](agent-plugins.md) / LLM) that answers open-ended questions. |
| **[PHAL](phal.md)** | Platform & Hardware Abstraction Layer; a service that handles low-level hardware interactions (volume, buttons, etc.). |
| **📐 Pipeline Plugin** | A matcher that exposes the **match contract** — `match(utterances, lang, session) → Match \| None`. The **orchestrator** iterates the installed pipeline plugins in `session.pipeline` order, **first-match-wins**; a plugin returns a `Match` to claim the utterance or `None` to pass. [Adapt](adapt-pipeline.md), [Padatious](padatious-pipeline.md), [Converse](converse-pipeline.md), [Fallback](fallback-pipeline.md), [OCP](ocp-pipeline.md) and [Persona](personas.md) are all pipeline plugins. 📐 [OVOS-PIPELINE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md). |
| **Plugin** | A swappable building block (a [STT](stt-plugins.md), [TTS](tts-plugins.md), [wake word](wake-word-plugins.md), [VAD](vad-plugins.md)… engine). Plugins change *how* OVOS works; [skills](skill-design-guidelines.md) add *what* it can do. |
| **QML** | A declarative language used for designing the user interface of OVOS skills. |
| **RAG (Retrieval-Augmented Generation)** | Fetching relevant remembered/retrieved context and giving it to an LLM *before* it answers. See [Persona Memory](persona-memory.md). |
| **📐 Recency-targeted stop** | The stop plugin's fallback when no handler answers the stoppability poll in time: target the most recently activated `active_handlers` entry instead of escalating to a global stop. 📐 [OVOS-STOP-1 §4.1](https://github.com/OpenVoiceOS/architecture/blob/dev/stop-1.md). |
| **Release Channel** | A stability track — *stable*, *testing*, or *alpha* — that controls how new the installed packages are. See [Release Channels](release-channels.md). |
| **📐 Reserved `intent_name`** | A small set of intent names — `stop`, `converse`, `response`, `fallback`, `common_query` — that skills **must not** register, because the orchestrator dispatches them on `<skill_id>:<intent_name>` on behalf of a pipeline plugin (e.g. [Converse](converse-pipeline.md) emits `response`, **Stop** emits `stop`). Each is leased to its owning spec. 📐 [OVOS-PIPELINE-1 §7.3](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md). |
| **Satellite** | In [HiveMind](hivemind-agents.md), a lightweight device (e.g. a small Pi) that captures voice and forwards it to `hivemind-core`. |
| **[Session](session.md)** | A data structure representing a specific user interaction or conversation state across multiple turns. See **Session (carrier)** below; its wire shape is 📐 [OVOS-SESSION-1](https://github.com/OpenVoiceOS/architecture/blob/dev/session-1.md), its lifecycle 📐 [OVOS-SESSION-2](https://github.com/OpenVoiceOS/architecture/blob/dev/session-2.md). |
| **📐 Session (carrier)** | The per-conversation JSON state that rides inside `Message.context.session` on **every** bus message — the voice OS's "shared memory". 📐 [OVOS-SESSION-1](https://github.com/OpenVoiceOS/architecture/blob/dev/session-1.md) fixes its *wire shape* and the field registry other specs extend (e.g. `session.pipeline`, `session.response_mode`, `session.persona_id`); 📐 [OVOS-SESSION-2](https://github.com/OpenVoiceOS/architecture/blob/dev/session-2.md) fixes its *lifecycle* — who owns it, when it may be mutated, and the reserved `"default"` device session. |
| **[Skill](skill-design-guidelines.md)** | A modular add-on that gives OVOS a new ability (e.g., "Weather Skill"). |
| **Skill Settings** | Per-skill configuration, optionally editable by the user. See [Skill Settings](skill-settings.md). |
| **`skill_id`** | A skill's unique identifier (e.g. `ovos-skill-weather.openvoiceos`), taken from its [entry point](plugin-manager.md). Used to namespace its settings, events, and resources. |
| **Solver** | The former name for an [Agent Engine](agent-plugins.md) — you'll still see it in older configs and code. |
| **SSML (Speech Synthesis Markup Language)** | Tags that control *how* [TTS](tts-plugins.md) speaks a sentence — pauses, emphasis, pitch, rate. Experimental and engine-dependent: most TTS plugins ignore it. See [SSML](ssml.md). |
| **[STT](stt-plugins.md) ([Speech-to-Text](stt-plugins.md))** | The process of transcribing spoken audio into text. |
| **[Transformer](transformer-plugins.md)** | A plugin that modifies audio, text, or metadata as it moves through the pipeline. Specified by 📐 [OVOS-TRANSFORM-1](https://github.com/OpenVoiceOS/architecture/blob/dev/transformer.md); see **Transformer Chain** below. |
| **📐 Transformer Chain** | One of **six** ordered chains — *audio*, *utterance*, *metadata*, *intent*, *dialog*, *tts* — that reshape an artifact at a fixed point in the utterance lifecycle. Unlike a **pipeline plugin** (which decides whether to claim an utterance), every transformer in a chain **always runs** at its injection point. 📐 [OVOS-TRANSFORM-1](https://github.com/OpenVoiceOS/architecture/blob/dev/transformer.md). |
| **TTS ([Text-to-Speech](tts-plugins.md))** | The process of synthesizing spoken audio from text. |
| **[Utterance](life-of-an-utterance.md)** | The text transcription of a user's spoken command. |
| **[VAD](vad-plugins.md) ([Voice Activity Detection](vad-plugins.md))** | The process of detecting when a user starts and stops speaking. |
| **Visemes** | Visual representations of phonemes used for lip-sync animations on a GUI. |
| **📐 Voice Operating System** | The framing the formal specs are built around: OVOS is a **platform, not a product**. Like a general-purpose OS, it defines the boundary between user input and computation, arbitrates which application handles each utterance, and exposes a stable ABI (the **match contract**) that third-party [skills](skill-design-guidelines.md) and [plugins](plugin-manager.md) run against without knowing about each other. See the [spec index](architecture-specs.md) for the OS-concept ↔ voice-OS mapping. 📐 [OVOS-PIPELINE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md). |
| **Vocabulary (`.voc`)** | A file of keywords / sentence fragments (not full sentences) used by *keyword (rule-based)* intents — what [Adapt](adapt-pipeline.md) and skills match against. |
| **[Wake Word](wake-word-plugins.md)** | The specific phrase (e.g., "Hey Mycroft") that triggers the listener to start recording. |
| **[Wyoming](wyoming-bridges.md)** | A simple voice protocol (from the Home Assistant world) that OVOS can bridge to and from. |
| **XDG** | The freedesktop standard for *where* config / data / cache files live (`~/.config`, `~/.local/share`, …). OVOS follows it, so your settings aren't scattered. |

## Deprecated & alias terms

Older docs, code comments, and community posts sometimes use terms that have since been replaced.
These still mean the same thing — you don't need to update anything working, but prefer the
current name in new writing:

| Old term | Current term |
|---|---|
| Solver | [Agent Engine](agent-plugins.md) |
| Intent engine / intent parser | [Pipeline plugin](pipelines-overview.md) |
| Hotword / wakeword (as a standalone term) | [Wake Word](wake-word-plugins.md) — note this stays as written inside real identifiers, such as the `wakeword` config keys and the `recognizer_loop:wakeword` bus message. |

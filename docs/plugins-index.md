# Plugins Index

!!! abstract "In a nutshell"
    OpenVoiceOS is built from interchangeable building blocks called *plugins* — small add-ons that each handle one job, like turning speech into text or text into speech. This works much like apps on a phone: you can mix and match the pieces you want and swap them out later. This page is a map of every plugin **type**, each linking to its catalog of available plugins. See the [Glossary](glossary.md) for related terms, or the [Plugin Manager](plugin-manager.md) for how they are discovered and loaded.

Every plugin registers under an **entry-point group** (the `opm.*` name below) so the
[Plugin Manager](plugin-manager.md) can find it. Pick a type to see the available plugins,
their config, and install commands.

## Speech & Audio

| Type | Entry point | What it does |
|---|---|---|
| [Microphone](mic-plugins.md) | `opm.microphone` | Captures audio from a microphone or audio source |
| [VAD](vad-plugins.md) (Voice Activity Detection) | `opm.VAD` | Detects when speech starts and stops |
| [Wake Word](wake-word-plugins.md) | `opm.wake_word` | Listens for the activation phrase (e.g. "hey Mycroft") |
| [Wake Word Verifiers](ww-verifier.md) | `opm.wake_word.verifier` | Second-stage check to reject false wake-word triggers |
| [STT](stt-plugins.md) (Speech-to-Text) | `opm.stt` | Transcribes captured speech into text |
| [TTS](tts-plugins.md) (Text-to-Speech) | `opm.tts` | Turns reply text back into spoken audio |
| [G2P](g2p-plugins.md) (Grapheme-to-Phoneme) | `opm.g2p` | Converts text to phonemes (e.g. for mouth/visemes) |

## Language

| Type | Entry point | What it does |
|---|---|---|
| [Translation & Language Detection](translation-plugins.md) | `opm.lang.translate` / `opm.lang.detect` | Detect a text's language and translate between languages |
| [Utterance Transformers](utterance-transformers.md) | `opm.transformer.text` | Modify the recognized text before intent matching |

## Intent & Dialog Pipeline

| Type | Entry point | What it does |
|---|---|---|
| [Pipeline matchers](pipelines-overview.md) | `opm.pipeline` | Decide which skill handles an utterance (Adapt, Padatious, …) |
| [Transformers](transformer-plugins.md) | `opm.transformer.*` | Hook into the text / metadata / dialog / TTS stages |

## Media & GUI

| Type | Entry point | What it does |
|---|---|---|
| [OCP Stream Extractors](ocp-plugins.md) | `opm.ocp.extractor` | Resolve a playable stream from a URL (YouTube, RSS, …) |
| [Media Playback](media-plugins.md) | `opm.media.audio` / `.video` / `.web` | Backend players for [ovos-media](ovos-media.md) |
| [GUI Adapters](gui-adapters.md) | `opm.gui_adapter` | Render backends for the GUI *(**Upcoming** — tracked in [ovos-plugin-manager#377](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/377), see page)* |

## AI Agents & Personas

| Type | Entry point | What it does |
|---|---|---|
| [Agent Engines](agent-plugins.md) | `opm.agents.*` | Chat / retrieval / summarizer / reranker brains |
| [Persona Memory](persona-memory.md) | `opm.agents.memory` | What a persona remembers between turns |
| [Agent Tools](tool-plugins.md) | `opm.agents.toolbox` | Give an agent callable tools |
| [Personas](personas.md) | `opm.plugin.persona` | Bundle engines into a conversational identity |

## System & Hardware

| Type | Entry point | What it does |
|---|---|---|
| [PHAL](phal.md) (Platform/Hardware Abstraction Layer) | `opm.phal` | Hardware and platform integrations |

For the full machine-readable list of plugin types and template base classes, see the
**[Plugin Manager → Plugin Types](plugin-manager.md#plugin-types)** table. To create your own
plugin, each catalog page above includes a template and entry-point example.

# Transformer Plugins

!!! abstract "In a nutshell"
    As your voice travels through the assistant — from raw sound, to written words, to a matched request, to the spoken reply — transformer plugins are optional helpers that can tidy or tweak the information at each step. Think of them as filters on an assembly line: one might clean up background noise, another might fix a misheard word before the system tries to understand it. They don't take over any step; they just polish what passes between steps. See the [Glossary](glossary.md) for related terms.

Transformer plugins let you intercept and modify data as it flows through the OVOS pipeline. Each type is a small class with a `transform()` method that runs at a fixed stage — turning raw audio into cleaner audio, fixing transcribed text before intent matching, enriching a matched intent, or post-processing speech before playback.

A transformer never *replaces* a stage; it sits between two stages and reshapes what passes through. Several plugins of the same type can be active at once — they run in sequence, sorted by `priority` (highest first), so each one builds on the output of the previous.

## Transformer Types

All base classes live in `ovos_plugin_manager.templates.transformers` and share the same constructor: `__init__(self, name, priority=50, config=None)`, plus `bind(bus)` and `initialize()`.

| Type | Stage | Base Class | Entry-point group |
|------|-------|------------|-------------------|
| **Audio** | Before STT | `AudioTransformer` | `opm.transformer.audio` |
| **Utterance** | After STT, before Intent | `UtteranceTransformer` | `opm.transformer.text` |
| **Metadata** | After Utterance, before Intent | `MetadataTransformer` | `opm.transformer.metadata` |
| **Intent** | After Intent match, before Skill | `IntentTransformer` | `opm.transformer.intent` |
| **Dialog** | Before TTS | `DialogTransformer` | `opm.transformer.dialog` |
| **TTS** | After TTS, before Playback | `TTSTransformer` | `opm.transformer.tts` |

The runner classes that load and chain these plugins (`UtteranceTransformersService`, `MetadataTransformersService`, `IntentTransformersService`) live in `ovos-core` (`ovos_core/transformers.py`). Audio, dialog, and TTS transformers are run by the listener and the audio/TTS stacks respectively.

---

## 1. Audio Transformers
**Entry point:** `opm.transformer.audio`

Used to process or transform raw audio before it reaches the STT engine. Common use cases include noise reduction, volume normalization, or streaming language detection.

### Template

```python
from ovos_plugin_manager.templates.transformers import AudioTransformer

class MyAudioTransformer(AudioTransformer):
    def on_audio(self, audio_data):
        # Process non-speech chunks
        return audio_data

    def on_speech(self, audio_data):
        # Process speech chunks during recording
        return audio_data

    def transform(self, audio_data):
        # Final transformation and optional context injection
        return audio_data, {"extra_metadata": "value"}

```

---

## 2. Utterance Transformers
**Entry point:** `opm.transformer.text`

Used to modify the transcribed text (utterances) before they are sent to the intent service. Common use cases include spelling correction, filtering, or expansion. See [Utterance Transformers](utterance-transformers.md) for details.

### Template

```python
from ovos_plugin_manager.templates.transformers import UtteranceTransformer

class MyUtteranceTransformer(UtteranceTransformer):
    def transform(self, utterances, context=None):
        # utterances is a list of strings
        transformed = [u.upper() for u in utterances]
        return transformed, context

```

---

## 3. Metadata Transformers
**Entry point:** `opm.transformer.metadata`

Used to inject or modify metadata in the message context. This runs after utterance transformers but before intent matching. `transform(context)` returns a (possibly modified) context dict.

---

## 4. Intent Transformers
**Entry point:** `opm.transformer.intent`

Used to modify the `IntentHandlerMatch` object. This runs after a pipeline match is found but before the skill is triggered. See [Intent Transformers](intent-transformers.md) for details.

---

## 5. Dialog Transformers
**Entry point:** `opm.transformer.dialog`

Used to modify the text that OVOS is about to speak, just before it is sent to the TTS engine.

---

## 6. TTS Transformers
**Entry point:** `opm.transformer.tts`

Used to process the generated WAV file after TTS synthesis but before it is played back.

---

## Standalone Usage

You can use transformers independently of the full OVOS stack. Here is an example with an `UtteranceTransformer`:

```python
from ovos_plugin_manager.text_transformers import find_utterance_transformer_plugins

# Find and load the plugin (returns {plugin_name: class})
plugins = find_utterance_transformer_plugins()
transformer_class = plugins["ovos-utterance-normalizer"]
transformer = transformer_class()  # base __init__ supplies the name

# Transform an utterance (utterances is a list of strings)
utterances = ["hello world"]
transformed, context = transformer.transform(utterances)
print(f"Transformed: {transformed}")

```

The discovery helpers (`find_*_transformer_plugins`, `load_*_transformer_plugin`) live in
`ovos_plugin_manager.text_transformers`, `.intent_transformers`, `.metadata_transformers`,
`.audio_transformers`, and `.dialog_transformers` (the dialog module also exposes the
`find_tts_transformer_plugins` / `load_tts_transformer_plugin` helpers — there is no
separate `tts_transformers` module).

## Creating a Plugin

1.  **Inherit** from the appropriate base class.


2.  **Implement** the `transform` method (or specific audio hooks).


3.  **Register** the entry point in your `pyproject.toml`, using the group for your transformer type (here, an utterance transformer):

```toml
[project.entry-points."opm.transformer.text"]
my-transformer = "my_package.module:MyTransformer"

```

# Transformer plugins Reference

| Plugin | Description |
|--------|-------------|
| [ovos-dialog-normalizer-plugin](#ovos-dialog-normalizer-plugin) | a dialog transformer plugins for OVOS |
| [ovos_tts_transformer_FlashSR](#ovos_tts_transformer_flashsr) | No description available |
| [ovos-transcription-validator-plugin](#ovos-transcription-validator-plugin) | A plugin for [OVOS](https://openvoiceos.com) that uses an OpenAI-compatible Large Language Model (LLM) to validate |
| [ovos-bidirectional-translation-plugin](#ovos-bidirectional-translation-plugin) | This package includes a UtteranceTransformer plugin and a DialogTransformer plugin, they work together to allow OVOS to speak in ANY language |
| [ovos-audio-transformer-plugin-speechbrain-langdetect](#ovos-audio-transformer-plugin-speechbrain-langdetect) | spoken language detector for ovos |
| [ovos-utterance-corrections-plugin](#ovos-utterance-corrections-plugin) | This plugin provides tools to correct or adjust speech-to-text (STT) outputs for better intent matching or improved user experience. |
| [ovos-utterance-normalizer](#ovos-utterance-normalizer) | normalizes utterances before intent parsing |
| [ovos-tts-transformer-NovaSR](#ovos-tts-transformer-novasr) | No description available |
| [ovos-utterance-plugin-cancel](#ovos-utterance-plugin-cancel) | plugin to look at the tail end of the transcribed phrase, ignoring the utterance if it ends with "nevermind that" or "cancel it" or "ignore that". |
| [ovos-tts-transformer-FlashSR](#ovos-tts-transformer-flashsr) | No description available |
| [ovos-audio-transformer-plugin-ggwave](#ovos-audio-transformer-plugin-ggwave) | plugin for https://github.com/ggerganov/ggwave |
| [ovos-tts-transformer-sox-plugin](#ovos-tts-transformer-sox-plugin) | This repository contains a Python package for a Text-to-Speech (TTS) transformer that utilizes SoX (Sound eXchange) for audio processing. The transformer applies various effects to the generated audio before playback. |
| [ovos_tts_transformer_NovaSR](#ovos_tts_transformer_novasr) | No description available |

## ovos-dialog-normalizer-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-dialog-normalizer-plugin](https://github.com/OpenVoiceOS/ovos-dialog-normalizer-plugin)


- **Description**: a dialog transformer plugins for OVOS

---

## ovos_tts_transformer_FlashSR

- **GitHub**: [https://github.com/OpenVoiceOS/ovos_tts_transformer_FlashSR](https://github.com/OpenVoiceOS/ovos_tts_transformer_FlashSR)


- **Description**: No description available

---

## ovos-transcription-validator-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-transcription-validator-plugin](https://github.com/OpenVoiceOS/ovos-transcription-validator-plugin)


- **Description**: A plugin for [OVOS](https://openvoiceos.com) that uses an OpenAI-compatible Large Language Model (LLM) to validate

---

## ovos-bidirectional-translation-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-bidirectional-translation-plugin](https://github.com/OpenVoiceOS/ovos-bidirectional-translation-plugin)


- **Description**: This package includes a UtteranceTransformer plugin and a DialogTransformer plugin, they work together to allow OVOS to speak in ANY language

---

## ovos-audio-transformer-plugin-speechbrain-langdetect

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-audio-transformer-plugin-speechbrain-langdetect](https://github.com/OpenVoiceOS/ovos-audio-transformer-plugin-speechbrain-langdetect)


- **Description**: spoken language detector for ovos

---

## ovos-utterance-corrections-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-utterance-corrections-plugin](https://github.com/OpenVoiceOS/ovos-utterance-corrections-plugin)


- **Description**: This plugin provides tools to correct or adjust speech-to-text (STT) outputs for better intent matching or improved user experience.

---

## ovos-utterance-normalizer

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-utterance-normalizer](https://github.com/OpenVoiceOS/ovos-utterance-normalizer)


- **Description**: normalizes utterances before intent parsing

---

## ovos-tts-transformer-NovaSR

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-transformer-NovaSR](https://github.com/OpenVoiceOS/ovos-tts-transformer-NovaSR)


- **Description**: No description available

---

## ovos-utterance-plugin-cancel

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-utterance-plugin-cancel](https://github.com/OpenVoiceOS/ovos-utterance-plugin-cancel)


- **Description**: plugin to look at the tail end of the transcribed phrase, ignoring the utterance if it ends with "nevermind that" or "cancel it" or "ignore that".

---

## ovos-tts-transformer-FlashSR

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-transformer-FlashSR](https://github.com/OpenVoiceOS/ovos-tts-transformer-FlashSR)


- **Description**: No description available

---

## ovos-audio-transformer-plugin-ggwave

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-audio-transformer-plugin-ggwave](https://github.com/OpenVoiceOS/ovos-audio-transformer-plugin-ggwave)


- **Description**: plugin for https://github.com/ggerganov/ggwave

---

## ovos-tts-transformer-sox-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-transformer-sox-plugin](https://github.com/OpenVoiceOS/ovos-tts-transformer-sox-plugin)


- **Description**: This repository contains a Python package for a Text-to-Speech (TTS) transformer that utilizes SoX (Sound eXchange) for audio processing. The transformer applies various effects to the generated audio before playback.

---

## ovos_tts_transformer_NovaSR

- **GitHub**: [https://github.com/OpenVoiceOS/ovos_tts_transformer_NovaSR](https://github.com/OpenVoiceOS/ovos_tts_transformer_NovaSR)


- **Description**: No description available

---


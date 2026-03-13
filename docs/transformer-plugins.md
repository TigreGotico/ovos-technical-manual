# Transformer Plugins

Transformer plugins in OVOS are powerful tools that allow you to intercept and modify data at various stages of the voice interaction pipeline. They can transform audio, text, metadata, and even intent matches.

## Transformer Types

| Type | Stage | Base Class |
|------|-------|------------|
| **Audio** | Before STT | `AudioTransformer` |
| **Utterance** | After STT, before Intent | `UtteranceTransformer` |
| **Metadata** | After Utterance, before Intent | `MetadataTransformer` |
| **Intent** | After Intent Match, before Skill | `IntentTransformer` |
| **Dialog** | Before TTS | `DialogTransformer` |
| **TTS** | After TTS, before Playback | `TTSTransformer` |

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
**Entry point:** `opm.utterance_transformer`

Used to modify the transcribed text (utterances) before they are sent to the intent service. Common use cases include spelling correction, filtering, or expansion.

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
**Entry point:** `opm.metadata_transformer`

Used to inject or modify metadata in the message context. This runs after utterance transformers but before intent matching.

---

## 4. Intent Transformers
**Entry point:** `opm.intent_transformer`

Used to modify the `IntentHandlerMatch` object. This runs after a pipeline match is found but before the skill is triggered.

---

## 5. Dialog Transformers
**Entry point:** `opm.dialog_transformer`

Used to modify the text that OVOS is about to speak, just before it is sent to the TTS engine.

---

## 6. TTS Transformers
**Entry point:** `opm.tts_transformer`

Used to process the generated WAV file after TTS synthesis but before it is played back.

---

## Standalone Usage

You can use transformers independently of the full OVOS stack. Here is an example with an `UtteranceTransformer`:

```python
from ovos_plugin_manager.utterance_transformers import find_utterance_transformer_plugins

# Find and load the plugin
plugins = find_utterance_transformer_plugins()
transformer_class = plugins["ovos-utterance-normalizer"]
transformer = transformer_class(name="normalizer")

# Transform an utterance
utterances = ["hello world"]
transformed, context = transformer.transform(utterances)
print(f"Transformed: {transformed}")

```

## Creating a Plugin

1.  **Inherit** from the appropriate base class.


2.  **Implement** the `transform` method (or specific audio hooks).


3.  **Register** the entry point in your `pyproject.toml`.

```toml
[project.entry-points."opm.utterance_transformer"]
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


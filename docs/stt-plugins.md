# STT Plugins

!!! abstract "In a nutshell"
    STT stands for *Speech-to-Text*: this is the part that listens to your spoken words and writes them down as text the assistant can read. It is the same idea as the dictation feature on a phone. Different STT plugins offer different trade-offs in speed, accuracy, and whether they run on your own device or in the cloud, so you can pick the one that suits you. See the [Glossary](glossary.md) for related terms.

??? info "📐 Formal specification"
    STT sits inside the audio input service, specified by **[OVOS-AUDIO-IN-1 — Audio Input Service](https://github.com/OpenVoiceOS/architecture/blob/dev/audio-in.md)**: capture → audio-transformer chain → STT → utterance. The transcript is emitted on `ovos.utterance.handle` ([OVOS-PIPELINE-1 §9.1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)). See the [spec index](architecture-specs.md).

!!! note "Audio format contract"
    Everything upstream of an STT plugin — the [microphone plugin](mic-plugins.md#the-microphone-interface) and any audio transformers — hands over raw PCM in a fixed shape: **16 kHz sample rate, 16-bit samples, mono, little-endian**, delivered in **4096-byte chunks** by default (the `Microphone` template's `sample_rate`/`sample_width`/`sample_channels`/`chunk_size` defaults). A batch `STT.execute()` plugin gets this bundled into a `speech_recognition.AudioData` object; a `StreamingSTT` plugin receives it chunk-by-chunk, still at this same format, unless a deployment explicitly reconfigures the microphone. Neither the `STT` nor the `StreamingSTT` template resamples on the plugin's behalf: if the wrapped model expects a different native rate, converting the incoming 16 kHz PCM is the plugin's own job.

STT (Speech-to-Text) plugins convert spoken audio into text. They are the bridge
between the listener and the intent pipeline.

## Using an STT plugin

Install a plugin and point your `mycroft.conf` at it:

```bash
pip install ovos-stt-plugin-fasterwhisper
```

```json
{
  "stt": {
    "module": "ovos-stt-plugin-fasterwhisper",
    "ovos-stt-plugin-fasterwhisper": {
      "model": "small"
    }
  }
}
```

The roster below lists available plugins and their default configurations.

## `STT`

The base STT, this handles the audio in "batch mode" taking a complete audio file, and returning the complete transcription.

Each STT plugin class needs to define the `execute()` method taking two arguments:

* `audio` \([AudioData](https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst#audiodataframe_data-bytes-sample_rate-int-sample_width-int---audiodata) object\) - the audio data to be transcribed.  


* `language` \(str\) - _optional_ - the BCP-47 language code; when omitted the plugin uses its
  configured or detected language

The bare minimum STT class will look something like

```python
from ovos_plugin_manager.templates.stt import STT

class MySTT(STT):
    def execute(self, audio, language=None):
        # Handle audio data and return transcribed text
        [...]
        return text

```

### N-best hypotheses — `transcribe()`

`execute()` returns a single best string. The richer method is `transcribe(audio, lang=None)`,
which returns a **list of `(transcript, confidence)` tuples**, confidence a float in `0.0`–`1.0`.
The template implements it for you as `[(self.execute(audio, lang), 1.0)]`, so a plugin that
only knows its single best answer needs to implement nothing extra.

If the wrapped engine can produce several hypotheses with scores, **override `transcribe()`**
— it is the preferred entry point, and consumers that rescore or disambiguate between
candidates read it. `execute()` then remains the single-best convenience wrapper.

```python
class MySTT(STT):
    def execute(self, audio, language=None):
        return self.transcribe(audio, language)[0][0]

    def transcribe(self, audio, lang=None):
        # return hypotheses best-first
        return [("turn on the lights", 0.91),
                ("turn on the light", 0.62)]
```

### Language detection

An STT plugin can be paired with an audio language detector. The audio service calls
`bind(detector)` to hand the plugin an `AudioLanguageDetector`; the plugin then exposes:

* `detect_language(audio, valid_langs=None)` → `(lang, confidence)`. It delegates to the bound
  detector, defaulting `valid_langs` to the plugin's own `available_languages`. With no detector
  bound it raises `NotImplementedError` — language detection is opt-in per deployment.

* `transcribe(audio, lang="auto")` — the `"auto"` sentinel runs `detect_language()` first and
  transcribes in whatever it returns. If detection fails, the plugin falls back to `self.lang`
  and transcribes anyway, so `"auto"` never turns a detector problem into a failed
  transcription.

## `StreamingSTT`

A more advanced STT class for streaming data to the STT. This will receive chunks of audio data as they become available and they are streamed to an STT engine.

The plugin author needs to implement the `create_streaming_thread()` method creating a thread for handling data sent through `self.queue`. 

The thread this method creates should be based on the `StreamThread` class. Its abstract `handle_audio_stream(audio, language)` method also needs to be implemented — it receives a generator of audio chunks and should set `self.text` to the transcript; `finalize()` returns that stored text once the stream ends.

### Chunk semantics

Audio arrives synchronously per chunk: `stream_data()` is called once per captured
chunk on the mic thread, so it must return well under the per-chunk time budget
(the same real-time cadence constraint a wake-word plugin's `update(chunk)` runs
under — see [Wake Word Plugins: Key Methods](wake-word-plugins.md#key-methods)). Do any
slow work (network calls, heavy inference) on the `StreamThread` this class
manages, not inline in `stream_data()`.

`StreamingSTT` runs the streaming work on a background thread, fed through a queue:

- `stream_start(language=None)` creates a fresh `Queue`, builds a `StreamThread` via `create_streaming_thread()`, and starts it.
- Each call to `stream_data(chunk)` puts one raw PCM `bytes` chunk (16 kHz/16-bit/mono, `chunk_size`-sized — see the audio format contract above) onto that queue.
- The `StreamThread`'s `run()` calls your `handle_audio_stream(audio, language)` with `audio` as a **generator** that yields chunks off the queue until a `None` sentinel appears — your implementation should loop over it (e.g. `for chunk in audio:`) and feed each chunk to the underlying engine, setting `self.text` as partial/final results arrive.
- `stream_stop()` pushes the `None` sentinel, joins the thread, and calls `finalize()` on it to retrieve the stored `self.text` as the final transcript — this is also what `execute()` returns for a `StreamingSTT` plugin.

A complete minimal streaming plugin:

```python
from queue import Queue
from threading import Thread
from ovos_plugin_manager.templates.stt import StreamingSTT, StreamThread


class MyStreamThread(StreamThread):
    def __init__(self, queue: Queue, language: str, engine):
        super().__init__(queue, language)
        self.engine = engine

    def handle_audio_stream(self, audio, language):
        # `audio` is a generator of raw PCM byte chunks; `self.queue.get()`
        # returns None once the caller closes the stream.
        for chunk in audio:
            partial = self.engine.feed(chunk, language)
            if partial:
                self.text = partial
        return self.text


class MyStreamingSTT(StreamingSTT):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = MyStreamingEngine()

    def create_streaming_thread(self):
        return MyStreamThread(self.queue, self.lang, self.engine)

    @property
    def available_languages(self):
        return {"en-us"}
```

## Entry point

To make the class detectable as an STT plugin, the package needs to provide an entry point under the `opm.stt` namespace.

```python
setup([...],
      entry_points = {'opm.stt': 'example_stt = my_stt:mySTT'}
      )

```

Where `example_stt` is the STT plugin name, `my_stt` is the Python module and `mySTT` is the class in the module to return.

To expose your sample configurations (the `MySTTConfig` dict below) for UI discovery, register them under `opm.stt.config`:

```python
entry_points = {
    'opm.stt': 'example_stt = my_stt:mySTT',
    'opm.stt.config': 'example_stt.config = my_stt:MySTTConfig'
}
```

> 💡 **Backward Compatibility**: `ovos-plugin-manager` still supports legacy `mycroft.plugin.stt` entry points, but new plugins should use the `opm.*` namespace.

## Standalone Usage

STT plugins can be used in your own projects, without a running OVOS instance, by
importing the plugin class directly. For example, with `ovos-stt-plugin-vosk`:

```python
from ovos_stt_plugin_vosk import VoskKaldiSTT
from ovos_plugin_manager.utils.audio import AudioFile

plug = VoskKaldiSTT()

# verify lang is supported
lang = "en-us"
assert lang in plug.available_languages

# read the whole file into an AudioData object
with AudioFile("test.wav") as source:
    audio = source.read()

# transcribe
transcript = plug.execute(audio, lang)

```

## Plugin Template

```python
from ovos_plugin_manager.templates.stt import STT


# base plugin class
class MySTTPlugin(STT):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # read config settings for your plugin
        lm = self.config.get("language-model")
        hmm = self.config.get("acoustic-model")

    def execute(self, audio, language=None):
        # Implement STT engine logic here
        transcript = "You said this"
        return transcript

    @property
    def available_languages(self):
        """Return languages supported by this STT implementation in this state
        This property should be overridden by the derived class to advertise
        what languages that engine supports.
        Returns:
            set: supported languages
        """
        # Return a set of supported BCP-47 language codes
        return {"en-us", "es-es"}


# sample valid configurations per language

# "display_name" and "offline" provide metadata for UI

# "priority" is used to calculate position in selection dropdown 

#       0 - top, 100-bottom

# all other keys represent an example valid config for the plugin 
MySTTConfig = {
    lang: [{"lang": lang,
            "display_name": f"MySTT ({lang}",
            "priority": 70,
            "offline": True}]
    for lang in ["en-us", "es-es"]
}

```

# STT plugins Reference

Code license is the SPDX license of the plugin's own repository; where the plugin wraps a
separately-licensed model, that is called out under "model".

| Plugin | Description | License |
|--------|-------------|---------|
| [ovos-stt-plugin-wav2vec](#ovos-stt-plugin-wav2vec) | OVOS plugin for [Wav2Vec2](https://ai.meta.com/blog/wav2vec-20-learning-the-structure-of-speech-from-raw-audio/) | Apache-2.0 (model: see model card) |
| [ovos-stt-plugin-azure](#ovos-stt-plugin-azure) | Microsoft Azure cloud speech-to-text. | Apache-2.0 |
| [ovos-stt-plugin-chromium](#ovos-stt-plugin-chromium) | Speech-to-text using the Google Chrome browser speech API. | Apache-2.0 |
| [ovos-stt-plugin-mms](#ovos-stt-plugin-mms) | OVOS plugin for [The Massively Multilingual Speech (MMS) project](https://huggingface.co/docs/transformers/main/en/model_doc/mms) ⚠️ **Archived** — MMS models also run under [ovos-stt-plugin-wav2vec2](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec2). | Apache-2.0 (model: see model card) |
| [ovos-stt-server-plugin](#ovos-stt-server-plugin) | OpenVoiceOS companion plugin for [OpenVoiceOS STT Server](https://github.com/OpenVoiceOS/ovos-stt-http-server) | Apache-2.0 |
| [ovos-stt-http-server](#ovos-stt-http-server) | Turn any OVOS STT plugin into a micro service! | Apache-2.0 |
| [ovos-stt-plugin-whisper](#ovos-stt-plugin-whisper) | OpenVoiceOS STT plugin for [Whisper](https://github.com/guillaumekln/faster-whisper), using transformers library | Apache-2.0 (default model: [openai/whisper-large-v3-turbo](https://huggingface.co/openai/whisper-large-v3-turbo)) |
| [ovos-stt-plugin-whispercpp](#ovos-stt-plugin-whispercpp) | OpenVoiceOS STT plugin for [whispercpp](https://github.com/ggerganov/whisper.cpp) | Apache-2.0 (model: see model card) |
| [ovos-stt-plugin-fasterwhisper](#ovos-stt-plugin-fasterwhisper) | OpenVoiceOS STT plugin for [Faster Whisper](https://github.com/guillaumekln/faster-whisper) | Apache-2.0 (default model: [mobiuslabsgmbh/faster-whisper-large-v3-turbo](https://huggingface.co/mobiuslabsgmbh/faster-whisper-large-v3-turbo)) |
| [ovos-stt-plugin-nemo](#ovos-stt-plugin-nemo) | OpenVoiceOS STT plugin for [Nemo](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/models.html), GPU is **strongly recommended** | Apache-2.0 (model: see model card) |
| [ovos-stt-plugin-whisper-lm](#ovos-stt-plugin-whisper-lm) | OpenVoiceOS STT plugin for [Whisper-LM-transformers](https://github.com/hitz-zentroa/whisper-lm-transformers), KenLM and Large language model integration with Whisper ASR models implemented in Hugging Face library. | Apache-2.0 (model: see model card) |
| [ovos-stt-plugin-citrinet](#ovos-stt-plugin-citrinet) | OpenVoiceOS STT plugin | Apache-2.0 (model: see model card) |
| [ovos-stt-plugin-nos](#ovos-stt-plugin-nos) | Galician STT using Proxecto Nós wav2vec2 models. ⚠️ Archived — superseded by [ovos-stt-plugin-wav2vec2](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec2). | Apache-2.0 (model: see model card) |
| [ovos-stt-plugin-HiTZ](#ovos-stt-plugin-hitz) | OpenVoiceOS STT plugin for **Basque** models trained by [HiTZ](https://huggingface.co/HiTZ) ⚠️ **Archived/deprecated.** | see repo (no license file) |
| [ovos-stt-plugin-vosk](#ovos-stt-plugin-vosk) | Mycroft STT plugin for [Vosk](https://alphacephei.com/vosk/) | Apache-2.0 (model: see model card) |
| [ovos-stt-plugin-onnx-asr](#ovos-stt-plugin-onnx-asr) | Runs [onnx-asr](https://github.com/istupakov/onnx-asr) models (NeMo Parakeet/Canary, Whisper, wav2vec2, …) fully offline via ONNX Runtime — a strong default for on-device, offline recognition. | Apache-2.0 (model: see model card) |

## ovos-stt-plugin-wav2vec

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec) (aliased by
  [ovos-stt-plugin-wav2vec2](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec2) — a
  separate GitHub repo that installs the same package and module id, `ovos-stt-plugin-wav2vec`;
  the repo name differs but the entry point does not, so both resolve to the same plugin)


- **Description**: OVOS plugin for [Wav2Vec2](https://ai.meta.com/blog/wav2vec-20-learning-the-structure-of-speech-from-raw-audio/)

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-wav2vec",
    "ovos-stt-plugin-wav2vec": {
        "model": "proxectonos/Nos_ASR-wav2vec2-large-xlsr-53-gl-with-lm"
    }
  }

```

There is no single hardcoded default model: the plugin picks a model from an internal
per-language table (keyed by BCP-47 language code) unless `model` is set explicitly, and
raises an error if the configured `lang` has no entry and no `model` is given. The
`proxectonos/Nos_ASR-...` model above is only the entry for Galician (`gl`); other
languages resolve to different pretrained models.

---

## ovos-stt-plugin-azure

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-azure](https://github.com/OpenVoiceOS/ovos-stt-plugin-azure)


- **Description**: Microsoft Azure cloud speech-to-text.

---

## ovos-stt-plugin-chromium

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-chromium](https://github.com/OpenVoiceOS/ovos-stt-plugin-chromium)


- **Description**: Speech-to-text using the Google Chrome browser speech API.

---

## ovos-stt-plugin-mms

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-mms](https://github.com/OpenVoiceOS/ovos-stt-plugin-mms)


- **Description**: OVOS plugin for [The Massively Multilingual Speech (MMS) project](https://huggingface.co/docs/transformers/main/en/model_doc/mms)

### Default Configuration

```jsonc
"stt": {
    "module": "ovos-stt-plugin-mms",
    "ovos-stt-plugin-mms": {
      "model": "facebook/mms-1b-all"
    }
}

```

---

## ovos-stt-server-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-server-plugin](https://github.com/OpenVoiceOS/ovos-stt-server-plugin)


- **Description**: OpenVoiceOS companion plugin for [OpenVoiceOS STT Server](https://github.com/OpenVoiceOS/ovos-stt-http-server)

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-server",
    "ovos-stt-plugin-server": {
      "urls": ["https://0.0.0.0:8080/stt"],
      "verify_ssl": true
    },
 }

```

Leaving `urls` unset falls back to public community-run STT servers rather than failing — see
[stt-server](stt-server.md#companion-plugin) for a self-hosted alternative, or pick a fully
offline engine from the table above.

--8<-- "snippets/community-servers.md"

---

## ovos-stt-http-server

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-http-server](https://github.com/OpenVoiceOS/ovos-stt-http-server)


- **Description**: Turn any OVOS STT plugin into a micro service!

---

## ovos-stt-plugin-whisper

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-whisper](https://github.com/OpenVoiceOS/ovos-stt-plugin-whisper)


- **Description**: OpenVoiceOS STT plugin for [Whisper](https://github.com/guillaumekln/faster-whisper), using transformers library

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-whisper",
    "ovos-stt-plugin-whisper": {
        "model": "openai/whisper-large-v3",
        "use_cuda": true
    }
  }

```

---

## ovos-stt-plugin-whispercpp

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-whispercpp](https://github.com/OpenVoiceOS/ovos-stt-plugin-whispercpp)


- **Description**: OpenVoiceOS STT plugin for [whispercpp](https://github.com/ggerganov/whisper.cpp)

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-whispercpp",
    "ovos-stt-plugin-whispercpp": {
        "model": "tiny"
    }
  }
 

```

---

## ovos-stt-plugin-fasterwhisper

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-fasterwhisper](https://github.com/OpenVoiceOS/ovos-stt-plugin-fasterwhisper)


- **Description**: OpenVoiceOS STT plugin for [Faster Whisper](https://github.com/guillaumekln/faster-whisper)

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-fasterwhisper",
    "ovos-stt-plugin-fasterwhisper": {
        "model": "large-v3",
        "use_cuda": true,
        "compute_type": "float16",
        "beam_size": 5,
        "cpu_threads": 4
    }
  }

```

---

## ovos-stt-plugin-nemo

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-nemo](https://github.com/OpenVoiceOS/ovos-stt-plugin-nemo)


- **Description**: OpenVoiceOS STT plugin for [Nemo](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/models.html), GPU is **strongly recommended**

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-nemo",
    "ovos-stt-plugin-nemo": {
        "model": "stt_eu_conformer_ctc_large",
        "use_cuda": false
    }
  }

```

---

## ovos-stt-plugin-whisper-lm

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-whisper-lm](https://github.com/OpenVoiceOS/ovos-stt-plugin-whisper-lm)


- **Description**: OpenVoiceOS STT plugin for [Whisper-LM-transformers](https://github.com/hitz-zentroa/whisper-lm-transformers), KenLM and Large language model integration with Whisper ASR models implemented in Hugging Face library.

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-whisper-lm",
    "ovos-stt-plugin-whisper-lm": {
        "model": "zuazo/whisper-medium-eu",
        "lm_repo": "HiTZ/whisper-lm-ngrams",
        "lm_model": "5gram-eu.bin",
        "lm_alpha": 0.33582369,
        "lm_beta": 0.68825565,
        "use_cuda": true
    }
  }

```

---

## ovos-stt-plugin-citrinet

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-citrinet](https://github.com/OpenVoiceOS/ovos-stt-plugin-citrinet)


- **Description**: OpenVoiceOS STT plugin

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-citrinet",
    "ovos-stt-plugin-citrinet": {
      "lang": "ca"
    }
  }

```

---

## ovos-stt-plugin-nos

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-nos](https://github.com/OpenVoiceOS/ovos-stt-plugin-nos)


- **Description**: Galician STT using [Proxecto Nós](https://github.com/proxectonos) wav2vec2 models. ⚠️ **Archived** — superseded by [ovos-stt-plugin-wav2vec2](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec2).

### Default Configuration

```jsonc
"stt": {
    "module": "ovos-stt-plugin-nos"
}

```

---

## ovos-stt-plugin-HiTZ

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-HiTZ](https://github.com/OpenVoiceOS/ovos-stt-plugin-HiTZ)


- **Description**: OpenVoiceOS STT plugin for **Basque** models trained by [HiTZ](https://huggingface.co/HiTZ)

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-HiTZ",
    "ovos-stt-plugin-HiTZ": {
        "model": "stt_eu_conformer_transducer_large"
    }
  }

```

---

## ovos-stt-plugin-vosk

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-vosk](https://github.com/OpenVoiceOS/ovos-stt-plugin-vosk)


- **Description**: Mycroft STT plugin for [Vosk](https://alphacephei.com/vosk/)

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-vosk",
    "ovos-stt-plugin-vosk": {
        "model": "/path/to/unzipped/model/folder"
    }
  }
 

```

---

## ovos-stt-plugin-onnx-asr

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-onnx-asr](https://github.com/OpenVoiceOS/ovos-stt-plugin-onnx-asr)


- **Description**: Runs [onnx-asr](https://github.com/istupakov/onnx-asr) models fully offline via ONNX Runtime — no cloud call, no PyTorch/transformers dependency. Supports NeMo Parakeet and Canary, Whisper, and wav2vec2 model families.

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-onnx-asr",
    "ovos-stt-plugin-onnx-asr": {
        "model": "nemo-parakeet-tdt-0.6b-v3"
    }
  }

```

Besides the built-in aliases and the `onnx-asr` repository's own model hub, the plugin loads any repo id from the [OpenVoiceOS/stt-asr-onnx](https://huggingface.co/collections/OpenVoiceOS/stt-asr-onnx) collection — curated single-language and regional ONNX conversions of NeMo Conformer/Parakeet and Whisper checkpoints, grouped roughly by family: AI4Bharat/Vaani models for Indian languages, NVIDIA Conformer/Parakeet models for major European languages (plus Kabyle, Belarusian, Esperanto, Kinyarwanda), Iberian-language Conformer models, and per-language Whisper finetunes. Most ship both fp32 and int8 weights (`quantization: "int8"` works); a few large models are fp32-only. See the collection itself for the exhaustive, current list — it grows independently of this plugin's release cycle.

---

## Further reading

- [Real-Time Offline Speech Recognition on OVOS (ONNX ASR)](https://blog.openvoiceos.org/posts/2026-02-16-onnx-asr) — OVOS blog

# STT Plugins

STT plugins are responsible for converting spoken audio into text

## `STT`

The base STT, this handles the audio in "batch mode" taking a complete audio file, and returning the complete transcription.

Each STT plugin class needs to define the `execute()` method taking two arguments:

* `audio` \([AudioData](https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst#audiodataframe_data-bytes-sample_rate-int-sample_width-int---audiodata) object\) - the audio data to be transcribed.  


* `lang` \(str\) - _optional_ - the BCP-47 language code

The bare minimum STT class will look something like

```python
from ovos_plugin_manager.templates.stt import STT

class MySTT(STT):
    def execute(audio, language=None):
        # Handle audio data and return transcribed text
        [...]
        return text

```

## `StreamingSTT`

A more advanced STT class for streaming data to the STT. This will receive chunks of audio data as they become available and they are streamed to an STT engine.

The plugin author needs to implement the `create_streaming_thread()` method creating a thread for handling data sent through `self.queue`. 

The thread this method creates should be based on the [StreamThread class](). `handle_audio_data()` method also needs to be implemented.

## Entry point

To make the class detectable as an STT plugin, the package needs to provide an entry point under the `opm.plugin.stt` namespace.

```python
setup([...],
      entry_points = {'opm.plugin.stt': 'example_stt = my_stt:mySTT'}
      )

```

Where `example_stt` is the STT plugin name, `my_stt` is the Python module and `mySTT` is the class in the module to return.

> 💡 **Backward Compatibility**: `ovos-plugin-manager` still supports legacy `mycroft.plugin.stt` entry points, but new plugins should use the `opm.*` namespace.

## Standalone Usage

STT plugins can be used in your owm projects as follows

```python
from speech_recognition import Recognizer, AudioFile

plug = STTPlug()

# verify lang is supported
lang = "en-us"
assert lang in plug.available_languages

# read file
with AudioFile("test.wav") as source:
    audio = Recognizer().record(source)

# transcribe AudioData object
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

| Plugin | Description |
|--------|-------------|
| [ovos-stt-plugin-wav2vec](#ovos-stt-plugin-wav2vec) | OVOS plugin for [Wav2Vec2](https://ai.meta.com/blog/wav2vec-20-learning-the-structure-of-speech-from-raw-audio/) |
| [ovos-stt-plugin-azure](#ovos-stt-plugin-azure) | No description available |
| [ovos-stt-plugin-chromium](#ovos-stt-plugin-chromium) | No description available |
| [ovos-stt-plugin-onnxasr](#ovos-stt-plugin-onnxasr) | An OpenVoiceOS Speech-to-Text plugin backed by the lightweight [onnx-asr](https://github.com/istupakov/onnx-asr) library. This plugin runs offline and supports high-performance models like Nvidia Canary, Parakeet, and OpenAI Whisper via ONNX Runtime. |
| [ovos-stt-plugin-mms](#ovos-stt-plugin-mms) | OVOS plugin for [The Massively Multilingual Speech (MMS) project](https://huggingface.co/docs/transformers/main/en/model_doc/mms) |
| [ovos-stt-server-plugin](#ovos-stt-server-plugin) | OpenVoiceOS companion plugin for [OpenVoiceOS STT Server](https://github.com/OpenVoiceOS/ovos-stt-http-server) |
| [ovos-stt-http-server](#ovos-stt-http-server) | Turn any OVOS STT plugin into a micro service! |
| [ovos-stt-plugin-wav2vec2](#ovos-stt-plugin-wav2vec2) | OVOS plugin for [Wav2Vec2](https://ai.meta.com/blog/wav2vec-20-learning-the-structure-of-speech-from-raw-audio/) |
| [ovos-stt-plugin-whisper](#ovos-stt-plugin-whisper) | OpenVoiceOS STT plugin for [Whisper](https://github.com/guillaumekln/faster-whisper), using transformers library |
| [ovos-stt-plugin-MyNorthAI](#ovos-stt-plugin-mynorthai) | No description available |
| [ovos-stt-plugin-ROVER](#ovos-stt-plugin-rover) | This plugin provides a **meta-STT engine** for OVOS that aggregates the output of multiple individual STT backends using the **ROVER** (Recognizer Output Voting Error Reduction) algorithm. |
| [ovos-stt-plugin-whispercpp](#ovos-stt-plugin-whispercpp) | OpenVoiceOS STT plugin for [whispercpp](https://github.com/ggerganov/whisper.cpp) |
| [ovos-stt-plugin-fasterwhisper](#ovos-stt-plugin-fasterwhisper) | OpenVoiceOS STT plugin for [Faster Whisper](https://github.com/guillaumekln/faster-whisper) |
| [ovos-stt-plugin-coreml](#ovos-stt-plugin-coreml) | An OVOS Speech-to-Text plugin that runs speech recognition models natively on Apple devices using CoreML. |
| [ovos-stt-plugin-nemo](#ovos-stt-plugin-nemo) | OpenVoiceOS STT plugin for [Nemo](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/models.html), GPU is **strongly recommended** |
| [ovos-stt-plugin-sherpa-onnx](#ovos-stt-plugin-sherpa-onnx) | An OpenVoiceOS Speech-to-Text plugin that uses [Sherpa-ONNX](https://github.com/k2-fsa/sherpa-onnx), the next-generation Kaldi-based speech recognition toolkit. This plugin runs completely offline and supports a wide variety of state-of-the-art architectures including Transducer, Whisper, Moonshine, Paraformer, and various CTC models. |
| [ovos-stt-plugin-whisper-lm](#ovos-stt-plugin-whisper-lm) | OpenVoiceOS STT plugin for [Whisper-LM-transformers](https://github.com/hitz-zentroa/whisper-lm-transformers), KenLM and Large language model integration with Whisper ASR models implemented in Hugging Face library. |
| [ovos-stt-plugin-rover](#ovos-stt-plugin-rover) | This plugin provides a **meta-STT engine** for OVOS that aggregates the output of multiple individual STT backends using the **ROVER** (Recognizer Output Voting Error Reduction) algorithm. |
| [ovos-stt-plugin-citrinet](#ovos-stt-plugin-citrinet) | OpenVoiceOS STT plugin |
| [ovos-stt-plugin-onnx-asr](#ovos-stt-plugin-onnx-asr) | An OpenVoiceOS Speech-to-Text plugin backed by the lightweight [onnx-asr](https://github.com/istupakov/onnx-asr) library. This plugin runs offline and supports high-performance models like Nvidia Canary, Parakeet, and OpenAI Whisper via ONNX Runtime. |
| [ovos-stt-plugin-nos](#ovos-stt-plugin-nos) | `pip install ovos-stt-plugin-nos` |
| [ovos-stt-plugin-HiTZ](#ovos-stt-plugin-hitz) | OpenVoiceOS STT plugin for **Basque** models trained by [HiTZ](https://huggingface.co/HiTZ) |
| [ovos-stt-plugin-vosk](#ovos-stt-plugin-vosk) | Mycroft STT plugin for [Vosk](https://alphacephei.com/vosk/) |

## ovos-stt-plugin-wav2vec

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec)


- **Description**: OVOS plugin for [Wav2Vec2](https://ai.meta.com/blog/wav2vec-20-learning-the-structure-of-speech-from-raw-audio/)

### Default Configuration

```json
  "stt": {
    "module": "ovos-stt-plugin-wav2vec",
    "ovos-stt-plugin-wav2vec": {
        "model": "proxectonos/Nos_ASR-wav2vec2-large-xlsr-53-gl-with-lm"
    }
  }

```

---

## ovos-stt-plugin-azure

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-azure](https://github.com/OpenVoiceOS/ovos-stt-plugin-azure)


- **Description**: No description available

---

## ovos-stt-plugin-chromium

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-chromium](https://github.com/OpenVoiceOS/ovos-stt-plugin-chromium)


- **Description**: No description available

---

## ovos-stt-plugin-onnxasr

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-onnxasr](https://github.com/OpenVoiceOS/ovos-stt-plugin-onnxasr)


- **Description**: An OpenVoiceOS Speech-to-Text plugin backed by the lightweight [onnx-asr](https://github.com/istupakov/onnx-asr) library. This plugin runs offline and supports high-performance models like Nvidia Canary, Parakeet, and OpenAI Whisper via ONNX Runtime.

### Default Configuration

```json
{
  "stt": {
    "module": "ovos-stt-plugin-onnx-asr",
    "ovos-stt-plugin-onnx-asr": {
      "model": "nemo-canary-1b-v2",
      "quantization": "int8"
    }
  }
}

```

---

## ovos-stt-plugin-mms

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-mms](https://github.com/OpenVoiceOS/ovos-stt-plugin-mms)


- **Description**: OVOS plugin for [The Massively Multilingual Speech (MMS) project](https://huggingface.co/docs/transformers/main/en/model_doc/mms)

### Default Configuration

```json
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

```json
  "stt": {
    "module": "ovos-stt-plugin-server",
    "ovos-stt-plugin-server": {
      "urls": ["https://0.0.0.0:8080/stt"],
      "verify_ssl": true
    },
 }

```

---

## ovos-stt-http-server

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-http-server](https://github.com/OpenVoiceOS/ovos-stt-http-server)


- **Description**: Turn any OVOS STT plugin into a micro service!

---

## ovos-stt-plugin-wav2vec2

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec2](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec2)


- **Description**: OVOS plugin for [Wav2Vec2](https://ai.meta.com/blog/wav2vec-20-learning-the-structure-of-speech-from-raw-audio/)

### Default Configuration

```json
  "stt": {
    "module": "ovos-stt-plugin-wav2vec",
    "ovos-stt-plugin-wav2vec": {
        "model": "proxectonos/Nos_ASR-wav2vec2-large-xlsr-53-gl-with-lm"
    }
  }

```

---

## ovos-stt-plugin-whisper

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-whisper](https://github.com/OpenVoiceOS/ovos-stt-plugin-whisper)


- **Description**: OpenVoiceOS STT plugin for [Whisper](https://github.com/guillaumekln/faster-whisper), using transformers library

### Default Configuration

```json
  "stt": {
    "module": "ovos-stt-plugin-whisper",
    "ovos-stt-plugin-whisper": {
        "model": "openai/whisper-large-v3",
        "use_cuda": true
    }
  }

```

---

## ovos-stt-plugin-MyNorthAI

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-MyNorthAI](https://github.com/OpenVoiceOS/ovos-stt-plugin-MyNorthAI)


- **Description**: No description available

---

## ovos-stt-plugin-ROVER

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-ROVER](https://github.com/OpenVoiceOS/ovos-stt-plugin-ROVER)


- **Description**: This plugin provides a **meta-STT engine** for OVOS that aggregates the output of multiple individual STT backends using the **ROVER** (Recognizer Output Voting Error Reduction) algorithm.

### Default Configuration

```json
{
  "stt": {
    "module": "ovos-stt-plugin-rover",
    "ovos-stt-plugin-rover": {
        "timeout": 12,
        "workers": 4,
        "backends": [
          {
            "module": "ovos-stt-plugin-whisper",
            "config": {
              "model": "small.en"
            }
          },
          {
            "module": "ovos-stt-plugin-vosk",
            "config": {
              "model": "vosk-model-en-us"
            }
          },
          {
            "module": "ovos-stt-plugin-xxx",
            "config": {
              "model": "..."
            }
          }
        ]
    }
  }
}

```

---

## ovos-stt-plugin-whispercpp

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-whispercpp](https://github.com/OpenVoiceOS/ovos-stt-plugin-whispercpp)


- **Description**: OpenVoiceOS STT plugin for [whispercpp](https://github.com/ggerganov/whisper.cpp)

### Default Configuration

```json
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

```json
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

## ovos-stt-plugin-coreml

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-coreml](https://github.com/OpenVoiceOS/ovos-stt-plugin-coreml)


- **Description**: An OVOS Speech-to-Text plugin that runs speech recognition models natively on Apple devices using CoreML.

### Default Configuration

```json
{
  "stt": {
    "module": "ovos-stt-plugin-coreml",
    "ovos-stt-plugin-coreml": {
      "metadata": "/path/to/parakeet_ctc_coreml/metadata.json",
      "vocab":    "/path/to/parakeet_ctc_coreml/vocab.json",
      "encoder":  "/path/to/parakeet_ctc_coreml/parakeet_ctc_mel_encoder.mlpackage",
      "decoder":  "/path/to/parakeet_ctc_coreml/parakeet_ctc_decoder.mlpackage"
    }
  }
}

```

---

## ovos-stt-plugin-nemo

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-nemo](https://github.com/OpenVoiceOS/ovos-stt-plugin-nemo)


- **Description**: OpenVoiceOS STT plugin for [Nemo](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/models.html), GPU is **strongly recommended**

### Default Configuration

```json
  "stt": {
    "module": "ovos-stt-plugin-nemo",
    "ovos-stt-plugin-nemo": {
        "model": "stt_eu_conformer_ctc_large",
        "use_cuda": false
    }
  }

```

---

## ovos-stt-plugin-sherpa-onnx

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-sherpa-onnx](https://github.com/OpenVoiceOS/ovos-stt-plugin-sherpa-onnx)


- **Description**: An OpenVoiceOS Speech-to-Text plugin that uses [Sherpa-ONNX](https://github.com/k2-fsa/sherpa-onnx), the next-generation Kaldi-based speech recognition toolkit. This plugin runs completely offline and supports a wide variety of state-of-the-art architectures including Transducer, Whisper, Moonshine, Paraformer, and various CTC models.

### Default Configuration

```json
{
  "stt": {
    "module": "ovos-stt-plugin-sherpa-onnx",
    "ovos-stt-plugin-sherpa-onnx": {
      "model": "sherpa-onnx-zipformer-en-libriheavy-20230830-large-punct-case",
      "model_type": "transducer",
      "encoder": "encoder-epoch-16-avg-2.int8.onnx",
      "decoder": "decoder-epoch-16-avg-2.int8.onnx",
      "joiner": "joiner-epoch-16-avg-2.int8.onnx",
      "tokens": "tokens.txt"
    }
  }
}

```

---

## ovos-stt-plugin-whisper-lm

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-whisper-lm](https://github.com/OpenVoiceOS/ovos-stt-plugin-whisper-lm)


- **Description**: OpenVoiceOS STT plugin for [Whisper-LM-transformers](https://github.com/hitz-zentroa/whisper-lm-transformers), KenLM and Large language model integration with Whisper ASR models implemented in Hugging Face library.

### Default Configuration

```json
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

## ovos-stt-plugin-rover

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-rover](https://github.com/OpenVoiceOS/ovos-stt-plugin-rover)


- **Description**: This plugin provides a **meta-STT engine** for OVOS that aggregates the output of multiple individual STT backends using the **ROVER** (Recognizer Output Voting Error Reduction) algorithm.

### Default Configuration

```json
{
  "stt": {
    "module": "ovos-stt-plugin-rover",
    "ovos-stt-plugin-rover": {
        "timeout": 12,
        "workers": 4,
        "backends": [
          {
            "module": "ovos-stt-plugin-whisper",
            "config": {
              "model": "small.en"
            }
          },
          {
            "module": "ovos-stt-plugin-vosk",
            "config": {
              "model": "vosk-model-en-us"
            }
          },
          {
            "module": "ovos-stt-plugin-xxx",
            "config": {
              "model": "..."
            }
          }
        ]
    }
  }
}

```

---

## ovos-stt-plugin-citrinet

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-citrinet](https://github.com/OpenVoiceOS/ovos-stt-plugin-citrinet)


- **Description**: OpenVoiceOS STT plugin

### Default Configuration

```json
  "stt": {
    "module": "ovos-stt-plugin-citrinet",
    "ovos-stt-plugin-citrinet": {
      "lang": "ca"
    }
  }

```

---

## ovos-stt-plugin-onnx-asr

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-onnx-asr](https://github.com/OpenVoiceOS/ovos-stt-plugin-onnx-asr)


- **Description**: An OpenVoiceOS Speech-to-Text plugin backed by the lightweight [onnx-asr](https://github.com/istupakov/onnx-asr) library. This plugin runs offline and supports high-performance models like Nvidia Canary, Parakeet, and OpenAI Whisper via ONNX Runtime.

### Default Configuration

```json
{
  "stt": {
    "module": "ovos-stt-plugin-onnx-asr",
    "ovos-stt-plugin-onnx-asr": {
      "model": "nemo-canary-1b-v2",
      "quantization": "int8"
    }
  }
}

```

---

## ovos-stt-plugin-nos

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-nos](https://github.com/OpenVoiceOS/ovos-stt-plugin-nos)


- **Description**: `pip install ovos-stt-plugin-nos`

### Default Configuration

```json
"stt": {
    "module": "ovos-stt-plugin-nos"
}

```

---

## ovos-stt-plugin-HiTZ

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-stt-plugin-HiTZ](https://github.com/OpenVoiceOS/ovos-stt-plugin-HiTZ)


- **Description**: OpenVoiceOS STT plugin for **Basque** models trained by [HiTZ](https://huggingface.co/HiTZ)

### Default Configuration

```json
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

```json
  "stt": {
    "module": "ovos-stt-plugin-vosk",
    "ovos-stt-plugin-vosk": {
        "model": "/path/to/unzipped/model/folder"
    }
  }
 

```

---


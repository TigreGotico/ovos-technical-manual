# TTS Plugins

!!! abstract "In a nutshell"
    TTS stands for *Text-to-Speech*: this is the part that gives your assistant its voice, turning written replies into spoken audio you can hear. It is the opposite of dictation — instead of listening to you, it talks back. Different TTS plugins offer different voices and qualities, and some run on your own device while others use a cloud service. See the [Glossary](glossary.md) for related terms.

!!! info "📐 Formal specification"
    TTS sits inside the audio output service, specified by **[OVOS-AUDIO-1 — Audio Output Service](https://github.com/OpenVoiceOS/architecture/blob/dev/audio-out.md)**: an `ovos.utterance.speak` response runs through the dialog-transformer chain → TTS → tts-transformer chain → playback queue. See the [spec index](architecture-specs.md).

TTS plugins are responsible for converting text into audio for playback.

## TTS

All OVOS TTS plugins need to define a class based on the TTS base class from `ovos_plugin_manager`.

```python
from ovos_plugin_manager.templates.tts import TTS

class MyTTS(TTS):
    def get_tts(self, sentence, wav_file, lang=None, voice=None):
        # Synthesize `sentence` and write the audio to `wav_file`
        [...]
        # return the output path and optional per-phoneme visemes (or None)
        return wav_file, phonemes

```

## Entry point

To make the class detectable as a TTS plugin, the package needs to provide an entry point under the `opm.tts` namespace.

```python
setup([...],
      entry_points = {'opm.tts': 'example_tts = my_tts:myTTS'}
      )

```

To expose your sample configurations (the `MyTTSConfig` dict below) for UI discovery, register them under `opm.tts.config`:

```python
entry_points = {
    'opm.tts': 'example_tts = my_tts:myTTS',
    'opm.tts.config': 'example_tts.config = my_tts:MyTTSConfig'
}
```

> 💡 **Backward Compatibility**: `ovos-plugin-manager` still supports legacy `mycroft.plugin.tts` entry points, but new plugins should use the `opm.*` namespace.

## Standalone Usage

You can use TTS plugins independently of the full OVOS stack:

```python
from ovos_plugin_manager.tts import find_tts_plugins

# Find and load the plugin
plugins = find_tts_plugins()
tts_class = plugins["ovos-tts-plugin-mimic"]

# Initialize (requires lang and config)
tts = tts_class(lang="en-us", config={})

# Generate audio
wav_file = "hello.wav"
tts.get_tts("Hello world", wav_file)
print(f"Audio saved to {wav_file}")

```

## Plugin Template

```python
from ovos_plugin_manager.templates.tts import TTS

class MyTTSPlugin(TTS):
    def __init__(self, *args, **kwargs):
        # Output format, and the SSML tags this engine GENUINELY handles.
        # Most engines support none — if so, omit ssml_tags (it defaults to
        # empty) and OVOS strips all SSML before get_tts() runs. Only list a
        # tag here if your engine actually understands it; listed tags are
        # passed through to get_tts() (optionally rewritten via modify_tag()).
        ssml_tags = ["speak", "s", "w", "voice", "prosody",
                     "say-as", "break", "sub", "phoneme"]
        super().__init__(*args, **kwargs, audio_ext="wav", ssml_tags=ssml_tags)
        
        # Read plugin-specific settings from config
        self.voice = self.config.get("voice", "default")

    def get_tts(self, sentence, wav_file, lang=None, voice=None):
        """Generate audio data and save to wav_file."""
        # Implement your synthesis logic here
        # self.my_engine.synthesize(sentence, output_path=wav_file)
        
        # Return path to file and optional visemes for lip-sync
        return wav_file, None

    @property
    def available_languages(self):
        """Return languages supported by this TTS implementation."""
        return {"en-us", "es-es", "pt-pt"}

# Sample valid configurations for plugin discovery
MyTTSConfig = {
    lang: [{"lang": lang,
            "display_name": f"MyTTS ({lang})",
            "priority": 50,
            "offline": True}]
    for lang in ["en-us", "es-es", "pt-pt"]
}

```

# TTS Plugins Reference

| Plugin | Description |
|--------|-------------|
| [ovos-tts-server](#ovos-tts-server) | Turn any OVOS TTS plugin into a micro service! |
| [ovos-tts-plugin-polly](#ovos-tts-plugin-polly) | Amazon Polly cloud text-to-speech. |
| [ovos-tts-plugin-google-tx](#ovos-tts-plugin-google-tx) | OVOS TTS plugin for [gTTS](https://github.com/pndurette/gTTS) |
| [ovos-tts-plugin-edge-tts](#ovos-tts-plugin-edge-tts) | TTS plugin for [OVOS](https://openvoiceos.org) based on [Edge-TTS](https://github.com/rany2/edge-tts) |
| [ovos-tts-plugin-matxa-multispeaker-cat](#ovos-tts-plugin-matxa-multispeaker-cat) | 🍵 [Matxa-TTS](https://huggingface.co/projecte-aina/matxa-tts-cat-multiaccent), the multispeaker, multidialectal neural TTS model.  It works together with the vocoder model 🥑 [alVoCat](https://huggingface.co/projecte-aina/alvocat-vocos-22khz), to generate high quality and expressive speech efficiently in four Catalan dialects: ⚠️ **Archived/deprecated.** |
| [ovos-tts-plugin-marytts](#ovos-tts-plugin-marytts) | TTS Plugin for [MaryTTS](https://github.com/marytts/marytts) |
| [ovos-tts-plugin-espeakNG](#ovos-tts-plugin-espeakng) | eSpeak NG offline text-to-speech (robotic, supports many languages). |
| [ovos-tts-plugin-beepspeak](#ovos-tts-plugin-beepspeak) | Novelty R2-D2-style beep text-to-speech. |
| [ovos-tts-plugin-cotovia](#ovos-tts-plugin-cotovia) | OVOS TTS plugin for [Cotovia TTS](http://gtm.uvigo.es/cotovia) |
| [ovos-tts-plugin-mimic](#ovos-tts-plugin-mimic) | OVOS TTS plugin for [Mimic](https://github.com/MycroftAI/mimic1) |
| [ovos-tts-plugin-SAM](#ovos-tts-plugin-sam) | S.A.M. — Software Automatic Mouth, the classic retro speech synthesizer. |
| [ovos-tts-plugin-azure](#ovos-tts-plugin-azure) | This TTS service for OpenVoiceOS requires a subscription to Microsoft Azure and the creation of a Speech resource (https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/overview#create-the-azure-resource) |
| [ovos-tts-plugin-ahotts](#ovos-tts-plugin-ahotts) | OVOS TTS plugin for [AhoTTS](https://github.com/aholab/AhoTTS) |
| [ovos-tts-server-plugin](#ovos-tts-server-plugin) | OpenVoiceOS companion plugin for [OpenVoiceOS TTS Server](https://github.com/OpenVoiceOS/ovos-tts-server) |
| [ovos-tts-plugin-coqui](#ovos-tts-plugin-coqui) | OVOS TTS plugin for [Coqui TTS](https://coqui-tts.readthedocs.io/en/latest) |
| [ovos-tts-plugin-pico](#ovos-tts-plugin-pico) | SVOX Pico lightweight offline text-to-speech. |
| [ovos-tts-plugin-lux](https://github.com/OpenVoiceOS/ovos-tts-plugin-lux) | LuxTTS — zipvoice-based voice-cloning TTS (48 kHz, en-US). |
| [ovos-tts-plugin-phoonnx](#ovos-tts-plugin-phoonnx) | Built into [phoonnx](https://pypi.org/project/phoonnx), OVOS's own ONNX-based multilingual neural TTS engine — the default choice for fully offline synthesis, with automatic model fetching. |
| [ovos-tts-plugin-omnivoice](https://github.com/OpenVoiceOS/ovos-tts-plugin-omnivoice) | Wraps [OmniVoice](https://github.com/k2-fsa/OmniVoice), a massively multilingual (600+ languages) zero-shot TTS model with `auto`, voice-design (`instruct`), and voice-cloning (`ref_audio`) modes. ⚠️ No packaged release yet — install from source. |

## ovos-tts-server

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-server](https://github.com/OpenVoiceOS/ovos-tts-server)


- **Description**: Turn any OVOS TTS plugin into a micro service!

---

## ovos-tts-plugin-polly

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-polly](https://github.com/OpenVoiceOS/ovos-tts-plugin-polly)


- **Description**: Amazon Polly cloud text-to-speech.

---

## ovos-tts-plugin-google-tx

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-google-tx](https://github.com/OpenVoiceOS/ovos-tts-plugin-google-tx)


- **Description**: OVOS TTS plugin for [gTTS](https://github.com/pndurette/gTTS)

### Default Configuration

```jsonc
  "tts": {
    "module": "ovos-tts-plugin-google-tx"
  }
 

```

---

## ovos-tts-plugin-edge-tts

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-edge-tts](https://github.com/OpenVoiceOS/ovos-tts-plugin-edge-tts)


- **Description**: TTS plugin for [OVOS](https://openvoiceos.org) based on [Edge-TTS](https://github.com/rany2/edge-tts)

---

## ovos-tts-plugin-matxa-multispeaker-cat

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-matxa-multispeaker-cat](https://github.com/OpenVoiceOS/ovos-tts-plugin-matxa-multispeaker-cat)


- **Description**: 🍵 [Matxa-TTS](https://huggingface.co/projecte-aina/matxa-tts-cat-multiaccent), the multispeaker, multidialectal neural TTS model.  It works together with the vocoder model 🥑 [alVoCat](https://huggingface.co/projecte-aina/alvocat-vocos-22khz), to generate high quality and expressive speech efficiently in four Catalan dialects:

### Default Configuration

```jsonc
  "tts": {
    "module": "ovos-tts-plugin-matxa-multispeaker-cat",
    "ovos-tts-plugin-matxa-multispeaker-cat": {
      "voice": "valencia/gina",
    }
  }

```

---

## ovos-tts-plugin-marytts

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-marytts](https://github.com/OpenVoiceOS/ovos-tts-plugin-marytts)


- **Description**: TTS Plugin for [MaryTTS](https://github.com/marytts/marytts)

### Default Configuration

```jsonc
"tts": {
    "module": "ovos-tts-plugin-marytts",
    "ovos-tts-plugin-marytts": {
      "url": "http://0.0.0.0:59125",
      "voice": "cmu-slt-hsmm"
    }
}

```

---

## ovos-tts-plugin-espeakNG

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-espeakNG](https://github.com/OpenVoiceOS/ovos-tts-plugin-espeakNG)


- **Description**: eSpeak NG offline text-to-speech (robotic, supports many languages).

---

## ovos-tts-plugin-beepspeak

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-beepspeak](https://github.com/OpenVoiceOS/ovos-tts-plugin-beepspeak)


- **Description**: Novelty R2-D2-style beep text-to-speech.

---

## ovos-tts-plugin-cotovia

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-cotovia](https://github.com/OpenVoiceOS/ovos-tts-plugin-cotovia)


- **Description**: OVOS TTS plugin for [Cotovia TTS](http://gtm.uvigo.es/cotovia)

### Default Configuration

```jsonc
  "tts": {
    "module": "ovos-tts-plugin-cotovia",
    "ovos-tts-plugin-cotovia": {
      "voice": "iago"
    }
  }
 

```

---

## ovos-tts-plugin-mimic

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-mimic](https://github.com/OpenVoiceOS/ovos-tts-plugin-mimic)


- **Description**: OVOS TTS plugin for [Mimic](https://github.com/MycroftAI/mimic1)

### Default Configuration

```jsonc
  "tts": {
    "module": "ovos-tts-plugin-mimic",
    "ovos-tts-plugin-mimic": {
      "voice": "ap",
    }
  }

```

---

## ovos-tts-plugin-SAM

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-SAM](https://github.com/OpenVoiceOS/ovos-tts-plugin-SAM)


- **Description**: S.A.M. — Software Automatic Mouth, the classic retro speech synthesizer.

---

## ovos-tts-plugin-azure

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-azure](https://github.com/OpenVoiceOS/ovos-tts-plugin-azure)


- **Description**: This TTS service for OpenVoiceOS requires a subscription to Microsoft Azure and the creation of a Speech resource (https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/overview#create-the-azure-resource)

### Default Configuration

```jsonc
"tts": {
    "module": "ovos-tts-plugin-azure",
    "ovos-tts-plugin-azure": {
        "api_key": "insert_your_key_here",
        "voice": "en-US-JennyNeural",  // optional, default "en-US-Guy24kRUS"
        "region": "westus" // optional, if your region is westus
    }
}

```

---

## ovos-tts-plugin-ahotts

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-ahotts](https://github.com/OpenVoiceOS/ovos-tts-plugin-ahotts)


- **Description**: OVOS TTS plugin for [AhoTTS](https://github.com/aholab/AhoTTS)

### Default Configuration

```jsonc
  "tts": {
    "module": "ovos-tts-plugin-ahotts",
    "ovos-tts-plugin-ahotts": {
        "lang": "eu"
    }
  }

```

---

## ovos-tts-server-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-server-plugin](https://github.com/OpenVoiceOS/ovos-tts-server-plugin)


- **Description**: OpenVoiceOS companion plugin for [OpenVoiceOS TTS Server](https://github.com/OpenVoiceOS/ovos-tts-server)

### Default Configuration

```jsonc
  "tts": {
    "module": "ovos-tts-plugin-server",
    "ovos-tts-plugin-server": {
        "host": "https://tts.smartgic.io/piper",
        "v2": true,
        "verify_ssl": true,
        "tts_timeout": 5
     }
 } 

```

---

## ovos-tts-plugin-coqui

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-coqui](https://github.com/OpenVoiceOS/ovos-tts-plugin-coqui)


- **Description**: OVOS TTS plugin for [Coqui TTS](https://coqui-tts.readthedocs.io/en/latest)

### Default Configuration

```jsonc
  "tts": {
    "module": "ovos-tts-plugin-coqui",
    "ovos-tts-plugin-coqui": {}
  }
 

```

---

## ovos-tts-plugin-pico

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-pico](https://github.com/OpenVoiceOS/ovos-tts-plugin-pico)


- **Description**: SVOX Pico lightweight offline text-to-speech.

---

## ovos-tts-plugin-phoonnx

- **GitHub**: [https://github.com/OpenVoiceOS/phoonnx](https://github.com/OpenVoiceOS/phoonnx)


- **Description**: OVOS's own multilingual, ONNX-based neural TTS engine, distributed as part of the `phoonnx` package. Registering the plugin only requires `pip install phoonnx` — model files are fetched and cached automatically the first time a voice is used.

### Default Configuration

```jsonc
  "tts": {
    "module": "ovos-tts-plugin-phoonnx",
    "ovos-tts-plugin-phoonnx": {
      "voice": "OpenVoiceOS/phoonnx_pt-PT_miro_tugaphone"
    }
  }

```

> If `"voice"` is omitted, the plugin picks the first bundled model that supports the configured language.

---

## Further reading

- [Introducing phoonnx — OVOS's next-gen TTS engine](https://blog.openvoiceos.org/posts/2025-10-06-phoonnx) — OVOS blog
- [Making Synthetic Voices From Scratch](https://blog.openvoiceos.org/posts/2025-06-26-making-synthetic-voices-from-scratch) — OVOS blog

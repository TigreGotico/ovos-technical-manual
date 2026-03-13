# TTS Plugins

TTS plugins are responsible for converting text into audio for playback.

## TTS

All OVOS TTS plugins need to define a class based on the TTS base class from `ovos_plugin_manager`.

```python
from ovos_plugin_manager.templates.tts import TTS

class MyTTS(TTS):
    def get_tts(self, sentence, wav_file):
        # Generate audio data and save to wav_file
        [...]
        return wav_file, phonemes

```

## Entry point

To make the class detectable as a TTS plugin, the package needs to provide an entry point under the `opm.plugin.tts` namespace.

```python
setup([...],
      entry_points = {'opm.plugin.tts': 'example_tts = my_tts:myTTS'}
      )

```

> 💡 **Backward Compatibility**: `ovos-plugin-manager` still supports legacy `mycroft.plugin.tts` entry points, but new plugins should use the `opm.*` namespace.

## Standalone Usage

You can use TTS plugins independently of the full OVOS stack:

```python
from ovos_plugin_manager.tts import find_tts_plugins

# Find and load the plugin
plugins = find_tts_plugins()
tts_class = plugins["ovos-tts-plugin-piper"]

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
        # Specify output format and supported SSML tags
        ssml_tags = ["speak", "s", "w", "voice", "prosody",
                     "say-as", "break", "sub", "phoneme"]
        super().__init__(*args, **kwargs, audio_ext="wav", ssml_tags=ssml_tags)
        
        # Read plugin-specific settings from config
        self.voice = self.config.get("voice", "default")

    def get_tts(self, sentence, wav_file):
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
| [ovos-tts-plugin-polly](#ovos-tts-plugin-polly) | No description available |
| [ovos-tts-plugin-google-tx](#ovos-tts-plugin-google-tx) | OVOS TTS plugin for [gTTS](https://github.com/pndurette/gTTS) |
| [ovos-tts-plugin-edge-tts](#ovos-tts-plugin-edge-tts) | TTS plugin for [OVOS](https://openvoiceos.org) based on [Edge-TTS](https://github.com/rany2/edge-tts) |
| [ovos-tts-plugin-matxa-multispeaker-cat](#ovos-tts-plugin-matxa-multispeaker-cat) | 🍵 [Matxa-TTS](https://huggingface.co/projecte-aina/matxa-tts-cat-multiaccent), the multispeaker, multidialectal neural TTS model.  It works together with the vocoder model 🥑 [alVoCat](https://huggingface.co/projecte-aina/alvocat-vocos-22khz), to generate high quality and expressive speech efficiently in four Catalan dialects: |
| [ovos-tts-plugin-marytts](#ovos-tts-plugin-marytts) | TTS Plugin for [MaryTTS](https://github.com/marytts/marytts) |
| [ovos-tts-plugin-espeakNG](#ovos-tts-plugin-espeakng) | No description available |
| [ovos-tts-plugin-beepspeak](#ovos-tts-plugin-beepspeak) | No description available |
| [ovos-tts-plugin-cotovia](#ovos-tts-plugin-cotovia) | OVOS TTS plugin for [Cotovia TTS](http://gtm.uvigo.es/cotovia) |
| [ovos-tts-plugin-mimic](#ovos-tts-plugin-mimic) | OVOS TTS plugin for [Mimic](https://github.com/MycroftAI/mimic1) |
| [ovos-tts-plugin-SAM](#ovos-tts-plugin-sam) | No description available |
| [ovos-tts-plugin-azure](#ovos-tts-plugin-azure) | This TTS service for OpenVoiceOS requires a subscription to Microsoft Azure and the creation of a Speech resource (https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/overview#create-the-azure-resource) |
| [ovos-tts-plugin-ahotts](#ovos-tts-plugin-ahotts) | OVOS TTS plugin for [AhoTTS](https://github.com/aholab/AhoTTS) |
| [ovos-tts-server-plugin](#ovos-tts-server-plugin) | OpenVoiceOS companion plugin for [OpenVoiceOS TTS Server](https://github.com/OpenVoiceOS/ovos-tts-server) |
| [ovos-tts-plugin-coqui](#ovos-tts-plugin-coqui) | OVOS TTS plugin for [Coqui TTS](https://coqui-tts.readthedocs.io/en/latest) |
| [ovos-tts-plugin-pico](#ovos-tts-plugin-pico) | No description available |

## ovos-tts-server

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-server](https://github.com/OpenVoiceOS/ovos-tts-server)


- **Description**: Turn any OVOS TTS plugin into a micro service!

---

## ovos-tts-plugin-polly

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-polly](https://github.com/OpenVoiceOS/ovos-tts-plugin-polly)


- **Description**: No description available

---

## ovos-tts-plugin-google-tx

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-google-tx](https://github.com/OpenVoiceOS/ovos-tts-plugin-google-tx)


- **Description**: OVOS TTS plugin for [gTTS](https://github.com/pndurette/gTTS)

### Default Configuration

```json
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

```json
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

```json
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


- **Description**: No description available

---

## ovos-tts-plugin-beepspeak

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-beepspeak](https://github.com/OpenVoiceOS/ovos-tts-plugin-beepspeak)


- **Description**: No description available

---

## ovos-tts-plugin-cotovia

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-cotovia](https://github.com/OpenVoiceOS/ovos-tts-plugin-cotovia)


- **Description**: OVOS TTS plugin for [Cotovia TTS](http://gtm.uvigo.es/cotovia)

### Default Configuration

```json
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

```json
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


- **Description**: No description available

---

## ovos-tts-plugin-azure

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-azure](https://github.com/OpenVoiceOS/ovos-tts-plugin-azure)


- **Description**: This TTS service for OpenVoiceOS requires a subscription to Microsoft Azure and the creation of a Speech resource (https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/overview#create-the-azure-resource)

### Default Configuration

```json
"tts": {
    "module": "ovos-tts-plugin-azure",
    "ovos-tts-plugin-azure": {
        "api_key": "insert_your_key_here",
        "voice": "en-US-JennyNeural",  # optional, default "en-US-Guy24kRUS"
        "region": "westus" # optional, if your region is westus
    }
}

```

---

## ovos-tts-plugin-ahotts

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-ahotts](https://github.com/OpenVoiceOS/ovos-tts-plugin-ahotts)


- **Description**: OVOS TTS plugin for [AhoTTS](https://github.com/aholab/AhoTTS)

### Default Configuration

```json
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

```json
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

```json
  "tts": {
    "module": "ovos-tts-plugin-coqui",
    "ovos-tts-plugin-coqui": {}
  }
 

```

---

## ovos-tts-plugin-pico

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-pico](https://github.com/OpenVoiceOS/ovos-tts-plugin-pico)


- **Description**: No description available

---


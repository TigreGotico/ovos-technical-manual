# TTS Transformers

**TTS Transformers** in OpenVoiceOS (OVOS) are plugins that process synthesized speech audio after the [Text-to-Speech](tts-plugins.md) (TTS) engine generates it but before it's played back to the user. 

They enable post-processing of audio to apply effects, enhance clarity, voice clone or tailor the output to specific needs.

---

## How They Work

The typical flow for speech output in OVOS is:

1. **Dialog Generation**: The assistant formulates a textual response.


2. **Dialog Transformation**: Optional plugins modify the text to adjust tone or style.


3. **Text-to-Speech (TTS)**: The text is converted into speech audio.


4. **TTS Transformation**: Plugins apply audio effects or modifications to the speech.


5. **Playback**: The final audio is played back to the user.

TTS Transformers operate in step 4, allowing for dynamic audio enhancements without altering the original TTS output.

They run inside the **ovos-audio** service, in the playback path: once the TTS engine has written a wav file, each loaded transformer's `transform(wav_file, context)` is called and is expected to return the path to the (possibly new) wav file to play. Transformers run in **descending priority** order (higher `priority` first), each receiving the previous one's output path.

---

## Configuration

To enable TTS Transformers, add them to your `mycroft.conf` under the `tts_transformers` section:

```json
"tts_transformers": {
  "plugin_name": {
    // plugin-specific configuration
  }
}

```

Replace `"plugin_name"` with the identifier of the desired plugin and provide any necessary configuration parameters.

---

## Available TTS [Transformer](transformer-plugins.md) Plugins

### **OVOS SoX TTS Transformer**

* **Purpose**: Applies various audio effects using SoX (Sound eXchange) to the TTS output.


* **Features**:


    * Pitch shifting


    * Reverb


    * Tempo adjustment


    * Equalization


    * Noise reduction


    * And many more


* **Installation**:

```bash
  pip install ovos-tts-transformer-sox-plugin

```

* **Configuration Example**:

```json
  "tts_transformers": {
    "ovos-tts-transformer-sox-plugin": {
      "effects": ["pitch 300", "reverb"]
    }
  }

```

* **Requirements**: Ensure SoX is installed and available in your system's PATH.


* **Source**: [GitHub Repository](https://github.com/OpenVoiceOS/ovos-tts-transformer-sox-plugin)

---

## Creating Custom TTS Transformers

To develop your own TTS Transformer:

**Create a Python Class**:

```python
from typing import Tuple
from ovos_plugin_manager.templates.transformers import TTSTransformer


class MyCustomTTSTransformer(TTSTransformer):
    def __init__(self, name="my-custom-tts-transformer", priority=10, config=None):
        super().__init__(name, priority, config)

    def transform(self, wav_file: str, context: dict = None) -> Tuple[str, dict]:
        """Transform passed wav_file and return path to transformed file"""
        # Apply custom audio processing to wav_file, write the result,
        # and return the path to the file that should be played
        modified_wav_file = wav_file  # replace with your processed file path
        return modified_wav_file, context
```


**Register as a Plugin**:
Expose the class under the `opm.transformer.tts` entry-point group in your `pyproject.toml`:

```toml
[project.entry-points."opm.transformer.tts"]
"my-custom-tts-transformer" = "my_module:MyCustomTTSTransformer"
```


**Install and Configure**:
After installation, add your transformer to the `mycroft.conf`:

```json
"tts_transformers": {
 "my-custom-tts-transformer": {}
}

```

---

By leveraging TTS Transformers, you can enhance the auditory experience of your OVOS assistant, tailoring speech output to better suit your preferences or application requirements.


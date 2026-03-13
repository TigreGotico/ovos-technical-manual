# Voice Activity Detection (VAD) Plugins

Voice Activity Detection (VAD) is a critical component in the OVOS listener pipeline. It is responsible for identifying segments of audio that contain human speech, allowing the system to ignore silence and background noise.

## How it works

The VAD engine continuously monitors the microphone's audio stream. Its primary roles are:

1.  **Speech Start Detection**: Triggering the recording of a command after the wake word is detected.


2.  **Speech End Detection**: Identifying when the user has finished speaking, so the audio can be sent for processing (STT).

## Configuration

You can configure the VAD plugin in your `mycroft.conf`:

```json
{
 "listener": {
   "VAD": {
     "module": "ovos-vad-plugin-webrtc",
     "ovos-vad-plugin-webrtc": {
       "vad_mode": 3
     }
   }
 }
}

```

## Supported VAD Plugins

| Plugin | Description |
|--------|-------------|
| [ovos-vad-plugin-webrtc](https://github.com/OpenVoiceOS/ovos-vad-plugin-webrtc) | Based on Google's WebRTC VAD. Highly efficient and widely used. |
| [ovos-vad-plugin-silero](https://github.com/OpenVoiceOS/ovos-vad-plugin-silero) | Uses a deep learning model for high-accuracy VAD, particularly in noisy environments. |

---

## Technical Explanation

All VAD plugins inherit from the `VADEngine` base class provided by `ovos-plugin-manager`.

### The VADEngine Interface

```python
class VADEngine:
    def __init__(self, config=None, sample_rate=None):
        self.config = config or {}
        self.sample_rate = sample_rate or 16000

    @abc.abstractmethod
    def is_silence(self, chunk) -> bool:
        """Return True if the chunk is silence, False if it is speech."""
        return False

```

## Creating Your Own VAD Plugin

### 1. Implementation Template

To create a new VAD plugin, you only need to implement the `is_silence` method.

```python
from ovos_plugin_manager.templates.vad import VADEngine

class MyCustomVAD(VADEngine):
    def is_silence(self, chunk) -> bool:
        # Implement your VAD logic here
        # Return True for silence, False for speech
        is_speech = self.my_model.predict(chunk)
        return not is_speech

```

### 2. Registration

Register your plugin in `pyproject.toml`:

```toml
[project.entry-points."opm.plugin.vad"]
my-custom-vad = "my_package.module:MyCustomVAD"

```

## Standalone Usage

You can use the VAD engine in your own scripts:

```python
from ovos_plugin_manager.vad import find_vad_plugins

# Load the plugin
plugins = find_vad_plugins()
vad_class = plugins["ovos-vad-plugin-webrtc"]
vad = vad_class()

# Process an audio chunk
is_silence = vad.is_silence(audio_chunk)
if not is_silence:
    print("Speech detected!")

```

# VAD Plugins Reference

| Plugin | Description |
|--------|-------------|
| [ovos-vad-plugin-webrtcvad](#ovos-vad-plugin-webrtcvad) | No description available |
| [ovos-vad-plugin-noise](#ovos-vad-plugin-noise) | simple VAD plugin extracted from the old [ovos-listener](https://github.com/OpenVoiceOS/ovos-listener/blob/dev/ovos_listener/silence.py) |
| [ovos-vad-plugin-silero](#ovos-vad-plugin-silero) | Silero Voice Activity Detection (VAD) plugin. |

## ovos-vad-plugin-webrtcvad

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-vad-plugin-webrtcvad](https://github.com/OpenVoiceOS/ovos-vad-plugin-webrtcvad)


- **Description**: No description available

---

## ovos-vad-plugin-noise

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-vad-plugin-noise](https://github.com/OpenVoiceOS/ovos-vad-plugin-noise)


- **Description**: simple VAD plugin extracted from the old [ovos-listener](https://github.com/OpenVoiceOS/ovos-listener/blob/dev/ovos_listener/silence.py)

---

## ovos-vad-plugin-silero

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-vad-plugin-silero](https://github.com/OpenVoiceOS/ovos-vad-plugin-silero)


- **Description**: Silero Voice Activity Detection (VAD) plugin.

### Default Configuration

```json
{
    "listener": {
        "VAD": {
            "module": "ovos-vad-plugin-silero",
            "ovos-vad-plugin-silero": {
                "model": "/optional/path/to/model.onnx"
            }
        }
    }
}

```

---


# Voice Activity Detection (VAD) Plugins

!!! abstract "In a nutshell"
    *Voice Activity Detection* (VAD) is how the assistant tells the difference between someone actually speaking and plain silence or background noise. It is what lets the system know when you have started talking and, just as importantly, when you have finished, so it knows when to stop listening and respond. Without it, the assistant wouldn't know where your command begins and ends. See the [Glossary](glossary.md) for related terms.

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
     "module": "ovos-vad-plugin-webrtcvad",
     "ovos-vad-plugin-webrtcvad": {
       "vad_mode": 3
     }
   }
 }
}

```

## Supported VAD Plugins

| Plugin | Description |
|--------|-------------|
| [ovos-vad-plugin-webrtcvad](https://github.com/OpenVoiceOS/ovos-vad-plugin-webrtcvad) | Based on Google's WebRTC VAD (`webrtcvad-wheels`). Lightweight, CPU-only, widely used. `vad_mode` (0–3) trades sensitivity for aggressiveness. |
| [ovos-vad-plugin-silero](https://github.com/OpenVoiceOS/ovos-vad-plugin-silero) | Uses the Silero deep-learning model for high-accuracy VAD, particularly in noisy environments. |
| [ovos-vad-plugin-noise](https://github.com/OpenVoiceOS/ovos-vad-plugin-noise) | Simple energy/noise-threshold VAD with no model download. |

> Specification: audio capture and VAD are deployer-defined components feeding the listener; see [OVOS-AUDIO-IN-1](https://github.com/OpenVoiceOS/architecture/blob/dev/ovos-audio-in-1.md) for the audio-input service that consumes their output.

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

    def reset(self):
        """Reset any internal state between utterances (optional)."""

```

Subclasses only need to implement `is_silence`. The base class provides
`extract_speech(audio)`, which uses `is_silence` over a sliding window to trim
leading/trailing silence from a buffer, and a `runtime_requirements` classmethod
used by the plugin manager to advertise network/offline behaviour.

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

Register your plugin in `pyproject.toml` under the `opm.VAD` group (note the uppercase `VAD`):

```toml
[project.entry-points."opm.VAD"]
my-custom-vad = "my_package.module:MyCustomVAD"

```

> 💡 The legacy alias `ovos.plugin.VAD` is still accepted, but new plugins should use `opm.VAD`.

## Standalone Usage

You can use the VAD engine in your own scripts:

```python
from ovos_plugin_manager.vad import find_vad_plugins

# Load the plugin
plugins = find_vad_plugins()
vad_class = plugins["ovos-vad-plugin-webrtcvad"]
vad = vad_class()

# Process an audio chunk
is_silence = vad.is_silence(audio_chunk)
if not is_silence:
    print("Speech detected!")

```

# VAD Plugins Reference

| Plugin | Description |
|--------|-------------|
| [ovos-vad-plugin-webrtcvad](#ovos-vad-plugin-webrtcvad) | Voice activity detection using webrtcvad. |
| [ovos-vad-plugin-noise](#ovos-vad-plugin-noise) | simple VAD plugin extracted from the old [ovos-listener](https://github.com/OpenVoiceOS/ovos-listener/blob/dev/ovos_listener/silence.py) |
| [ovos-vad-plugin-silero](#ovos-vad-plugin-silero) | Silero Voice Activity Detection (VAD) plugin. |

## ovos-vad-plugin-webrtcvad

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-vad-plugin-webrtcvad](https://github.com/OpenVoiceOS/ovos-vad-plugin-webrtcvad)


- **Description**: Voice activity detection using webrtcvad.

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

## Further reading

- [OVOS Just Got a Noise Filter (Pre-Wake VAD)](https://blog.openvoiceos.org/posts/2025-11-06-prewake-vad) — OVOS blog

# Microphone Plugins in OVOS

Microphone plugins in Open Voice OS (OVOS) are responsible for capturing audio input and feeding it to the listener. Since `ovos-core` version **0.0.8**, these plugins allow for flexible integration with different audio backends and platforms.

## Usage Guide

To use a microphone plugin in OVOS:

- Install the desired plugin with `pip`:

```bash
pip install ovos-microphone-plugin-<name>

```

- Update your `mycroft.conf` (or `mycroft.conf`) to specify the plugin:

```json
{
 "listener": {
   "microphone": {
     "module": "ovos-microphone-plugin-alsa"  // or another plugin
   }
 }
}

```

- Restart OVOS to apply the new microphone plugin configuration.

## Supported Microphone Plugins

| Plugin | Description | OS Compatibility |
|--------|-------------|------------------|
| [ovos-microphone-plugin-alsa](https://github.com/OpenVoiceOS/ovos-microphone-plugin-alsa) | Based on [pyalsaaudio](http://larsimmisch.github.io/pyalsaaudio). Offers low-latency and high performance on ALSA-compatible devices. | Linux |
| [ovos-microphone-plugin-pyaudio](https://github.com/OpenVoiceOS/ovos-microphone-plugin-pyaudio) | Uses [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/). Good general-purpose plugin for Linux. | Linux |
| [ovos-microphone-plugin-sounddevice](https://github.com/OpenVoiceOS/ovos-microphone-plugin-sounddevice) | Built on [python-sounddevice](https://github.com/spatialaudio/python-sounddevice). Offers cross-platform support. | Linux, macOS, Windows |
| [ovos-microphone-plugin-files](https://github.com/OpenVoiceOS/ovos-microphone-plugin-files) | Uses audio files as input instead of a live microphone—ideal for testing and debugging. | Linux, macOS, Windows |
| [ovos-microphone-plugin-arecord](https://github.com/OVOSHatchery/ovos-microphone-plugin-arecord) | Wraps `arecord` using subprocess calls. Simple and effective on systems with ALSA. | Linux |
| [ovos-microphone-plugin-socket](https://github.com/OVOSHatchery/ovos-microphone-plugin-socket) | Receives audio over a socket connection. Useful for remote microphone setups. | Linux, macOS, Windows |

## Technical Explanation

OVOS uses a plugin architecture to decouple the audio input system from the rest of the voice stack. Microphone plugins implement a common interface, making it easy to swap between different audio sources or backends without changing application code.

### The Microphone Interface

All microphone plugins inherit from the `Microphone` dataclass found in `ovos_plugin_manager.templates.microphone`.

```python
@dataclass
class Microphone:
    sample_rate: int = 16000
    sample_width: int = 2
    sample_channels: int = 1
    chunk_size: int = 4096

    def start(self):
        """Initialize the microphone and start recording."""
        pass

    def read_chunk(self) -> Optional[bytes]:
        """Read a single chunk of audio data from the microphone."""
        pass

    def stop(self):
        """Stop recording and release any resources."""
        pass

```

## Creating Your Own Plugin

To create a new microphone plugin, you need to implement the `Microphone` base class and register it as an entry point.

### 1. Implementation Template

```python
from ovos_plugin_manager.templates.microphone import Microphone

class MyCustomMic(Microphone):
    def __init__(self, sample_rate=16000, sample_width=2, sample_channels=1, chunk_size=4096):
        super().__init__(sample_rate, sample_width, sample_channels, chunk_size)
        self.device = None

    def start(self):
        # Open your audio device here
        self.device = open_my_device()

    def read_chunk(self):
        # Return raw PCM bytes
        return self.device.read(self.chunk_size)

    def stop(self):
        # Close the device
        if self.device:
            self.device.close()

```

### 2. Registration

In your `pyproject.toml`, register the plugin under the `opm.plugin.microphone` group:

```toml
[project.entry-points."opm.plugin.microphone"]
my-custom-mic = "my_package.module:MyCustomMic"

```

## Standalone Usage

You can use microphone plugins independently of the full OVOS stack:

```python
from ovos_plugin_manager.microphone import find_microphone_plugins

# Find and load the plugin
plugins = find_microphone_plugins()
mic_class = plugins["ovos-microphone-plugin-alsa"]
mic = mic_class()

mic.start()
try:
    while True:
        chunk = mic.read_chunk()
        if chunk:
            # Process your audio data here
            print(f"Captured {len(chunk)} bytes")
finally:
    mic.stop()

```

## Tips & Caveats

- **Performance**: For best results on Linux, the ALSA plugin typically provides the lowest latency.


- **Cross-platform development**: Use the `sounddevice` or `files` plugin when developing on non-Linux systems.


- **Testing**: The `files` plugin is ideal for automated testing environments where live input isn’t available.


- **Remote audio**: The `socket` plugin is a proof-of-concept for networked microphones and is not recommended for production use without customization.# Microphone Plugins Reference

| Plugin | Description |
|--------|-------------|
| [ovos-microphone-plugin-alsa](#ovos-microphone-plugin-alsa) | OpenVoiceOS Microphone plugin |
| [ovos-microphone-plugin-sounddevice](#ovos-microphone-plugin-sounddevice) | Open Voice OS microphone plugin for [python-sounddevice](https://github.com/spatialaudio/python-sounddevice/) library. |
| [ovos-microphone-plugin-files](#ovos-microphone-plugin-files) | OpenVoiceOS Microphone Files plugin |
| [ovos-microphone-plugin-pyaudio](#ovos-microphone-plugin-pyaudio) | OpenVoiceOS Microphone plugin |

## ovos-microphone-plugin-alsa

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-microphone-plugin-alsa](https://github.com/OpenVoiceOS/ovos-microphone-plugin-alsa)


- **Description**: OpenVoiceOS Microphone plugin

---

## ovos-microphone-plugin-sounddevice

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-microphone-plugin-sounddevice](https://github.com/OpenVoiceOS/ovos-microphone-plugin-sounddevice)


- **Description**: Open Voice OS microphone plugin for [python-sounddevice](https://github.com/spatialaudio/python-sounddevice/) library.

### Default Configuration

```json
{
  "listener": {
    "microphone": {
      "module": "ovos-microphone-plugin-sounddevice",
      "ovos-microphone-plugin-sounddevice": {}
    }
  }
}

```

---

## ovos-microphone-plugin-files

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-microphone-plugin-files](https://github.com/OpenVoiceOS/ovos-microphone-plugin-files)


- **Description**: OpenVoiceOS Microphone Files plugin

---

## ovos-microphone-plugin-pyaudio

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-microphone-plugin-pyaudio](https://github.com/OpenVoiceOS/ovos-microphone-plugin-pyaudio)


- **Description**: OpenVoiceOS Microphone plugin

---


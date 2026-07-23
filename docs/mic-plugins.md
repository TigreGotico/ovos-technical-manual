# Microphone Plugins in OVOS

!!! abstract "In a nutshell"
    A microphone plugin is the part that listens — it grabs the sound coming in from your device's microphone and hands it to the rest of the assistant so it can hear you. Different devices and setups need different ways of capturing that sound, so these plugins let you switch the "ears" without changing anything else. Think of it like choosing which microphone to plug into a recorder. See the [Glossary](glossary.md) for unfamiliar terms.

Microphone plugins in Open Voice OS (OVOS) are responsible for capturing audio input and feeding the raw PCM stream to the listener. They let you swap audio backends and platforms without touching the rest of the voice stack.

> The audio-capture mechanism is **deployer-defined** and sits outside the formal audio-input service contract — the listener consumes whatever a microphone plugin produces. See the [OVOS-AUDIO-IN-1](https://github.com/OpenVoiceOS/architecture/blob/dev/audio-in.md) specification for how captured audio enters the utterance lifecycle.

## Usage Guide

To use a microphone plugin in OVOS:

- Install the desired plugin with `pip`:

```bash
pip install ovos-microphone-plugin-<name>

```

- Update your `mycroft.conf` (or `mycroft.conf`) to specify the plugin:

```jsonc
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
| [ovos-microphone-plugin-pyaudio](https://github.com/OpenVoiceOS/ovos-microphone-plugin-pyaudio) | Uses the [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) PortAudio bindings directly (no `speech_recognition` dependency). Good cross-platform general-purpose plugin. | Linux, macOS, Windows |
| [ovos-microphone-plugin-sounddevice](https://github.com/OpenVoiceOS/ovos-microphone-plugin-sounddevice) | Built on [python-sounddevice](https://github.com/spatialaudio/python-sounddevice). Offers cross-platform support. | Linux, macOS, Windows |
| [ovos-microphone-plugin-files](https://github.com/OpenVoiceOS/ovos-microphone-plugin-files) | Uses audio files as input instead of a live microphone — ideal for testing and debugging. | Linux, macOS, Windows |
| [ovos-microphone-plugin-arecord](https://github.com/OVOSHatchery/ovos-microphone-plugin-arecord) | Wraps `arecord` using subprocess calls. Simple and effective on systems with ALSA. **Hatchery-only** — not published to PyPI, install from source if you need it. | Linux |
| [ovos-microphone-plugin-socket](https://github.com/OVOSHatchery/ovos-microphone-plugin-socket) | Receives audio over a socket connection. Useful for remote microphone setups. **Hatchery-only** — not published to PyPI, install from source if you need it. | Linux, macOS, Windows |

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

    @property
    def frames_per_chunk(self) -> int:
        return self.chunk_size // (self.sample_width * self.sample_channels)

    @property
    def seconds_per_chunk(self) -> float:
        return self.frames_per_chunk / self.sample_rate

    @abc.abstractmethod
    def start(self):
        """Initialize the microphone and start recording."""

    @abc.abstractmethod
    def read_chunk(self) -> Optional[bytes]:
        """Read a single chunk of audio data from the microphone."""

    @abc.abstractmethod
    def stop(self):
        """Stop recording and release any resources."""

```

`read_chunk` returns raw little-endian PCM bytes of `chunk_size` length. The default
format (16 kHz, 16-bit, mono) is what the listener expects downstream.

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

In your `pyproject.toml`, register the plugin under the `opm.microphone` group:

```toml
[project.entry-points."opm.microphone"]
my-custom-mic = "my_package.module:MyCustomMic"

```

> 💡 The legacy alias `ovos.plugin.microphone` is still accepted by `ovos-plugin-manager`, but new plugins should register under `opm.microphone`.

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


- **Testing**: The `files` plugin is ideal for automated testing environments where live input isn't available.


- **Remote audio**: The `socket` plugin is a proof-of-concept for networked microphones and is not recommended for production use without customization.

# Microphone Plugins Reference

Default configuration for the plugins listed in [Supported Microphone Plugins](#supported-microphone-plugins)
above (OS compatibility and a one-line description live in that table; this section only adds
config where a plugin has one). `ovos-microphone-plugin-arecord` and `ovos-microphone-plugin-socket`
have no dedicated section here — see the table above and [Tips & Caveats](#tips-caveats).

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


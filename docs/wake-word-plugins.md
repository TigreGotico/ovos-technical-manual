# Wake Word Plugins

!!! abstract "In a nutshell"
    A *wake word* is the special phrase that gets your assistant's attention — like "Hey Mycroft" — so it only starts paying attention when you mean to talk to it, instead of listening all the time. Wake word plugins are the different tools that listen for that phrase. Some are more accurate for a fixed phrase, while others let you pick your own wake word with less setup. See the [Glossary](glossary.md) and the [listener service](speech-service.md) for related details.

Wake Word plugins allow Open Voice OS to detect specific words or sounds, typically the assistant’s name (e.g., "Hey Mycroft"), but can be customized for various use cases. These plugins enable the system to listen for and react to activation commands or phrases.

## Available Plugins

OVOS supports different wake word detection plugins, each with its own strengths and use cases

The default OVOS plugins are:

- **[ovos-ww-plugin-precise-lite](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-lite)**: The default model-based plugin, running a trained Precise wake-word model exported to TFLite. The bundled default `mycroft.conf` sets this up for `hey_mycroft`, with a fallback chain to `ovos-ww-plugin-precise` (classic Precise), then `ovos-ww-plugin-vosk`, then `ovos-ww-plugin-pocketsphinx` if a plugin further up the chain is not installed.


- **[ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx)**: Runs the same family of Precise models exported to ONNX instead of TFLite — a drop-in alternative for deployments that prefer the ONNX runtime.


- **[ovos-ww-plugin-vosk](https://github.com/OpenVoiceOS/ovos-ww-plugin-vosk)**: A text-based plugin leveraging Vosk, which lets you define a wake word without training a model. This is useful during the initial stages of data collection.

Each plugin has its pros and cons: the Precise model is the most accurate for the
default `hey mycroft`, while Vosk offers faster setup for arbitrary wake phrases
without model training.

> Specification: wake-word detection is one of the deployer-defined capture mechanisms that trigger the audio-input service (referenced in [OVOS-AUDIO-IN-1 §5.1](https://github.com/OpenVoiceOS/architecture/blob/dev/audio-in.md) as the source of a `request_lang` hint).

## Wakeword Configuration

The `hotwords` section in your `mycroft.conf` allows you to configure the wakeword detection parameters for each plugin. For instance:

```json
"hotwords": {
  "hey_mycroft": {
    "module": "ovos-ww-plugin-precise-lite",
    "model": "https://github.com/OpenVoiceOS/precise-lite-models/raw/master/wakewords/en/hey_mycroft.tflite",
    "trigger_level": 3,
    "sensitivity": 0.5,
    "listen": true
  }
}

```

> 💡 see the full docs for the [listener service](speech-service.md)


## Tips and Caveats

- **Vosk Plugin**: The Vosk plugin is useful when you need a simple setup that doesn’t require training a wake word model. It’s great for quickly gathering data during the development stage.


- **Precision and Sensitivity**: Adjust the `sensitivity` and `trigger_level` settings carefully. Too high a sensitivity can lead to false positives, while too low may miss detection.

## Plugin Development

### Key Methods

When developing a custom wake word plugin, the following methods are essential:

- **`found_wake_word()`**: This method must be defined. It returns whether the wake word has been detected and resets internal state.


- **`update(chunk)`**: Required (abstract) method for processing live audio chunks and making streaming predictions.


- **`stop()`**: An optional method to shut down the plugin, like unloading data or halting external processes.

> ⚠️ `found_wake_word()` takes no audio argument; the legacy `frame_data` parameter has been removed. Plugins are now expected to handle real time audio via the `update` method

### Registering Your Plugin

To make your plugin detectable, provide an entry point under the `opm.wake_word` namespace:

```python
setup([...], entry_points={'opm.wake_word': 'example_ww = my_ww:MyWakeWordEngine'})

```

> 💡 **Backward Compatibility**: `ovos-plugin-manager` still supports legacy `mycroft.plugin.wake_word` entry points, but new plugins should use the `opm.*` namespace.

### Example Plugin

Here’s a simple implementation of a wake word plugin:

```python
from ovos_plugin_manager.templates.hotwords import HotWordEngine
from threading import Event

class MyWWPlugin(HotWordEngine):
    def __init__(self, key_phrase="hey mycroft", config=None):
        super().__init__(key_phrase, config)
        self.detection = Event()
        self.engine = MyWW(key_phrase)

    def found_wake_word(self):
        # inference happens via the self.update method
        detected = self.detection.is_set()
        if detected:
            self.detection.clear()
        return detected

    def update(self, chunk):
        if self.engine.found_it(chunk):
            self.detection.set()

    def stop(self):
        self.engine.bye()

```

# WW Plugins Reference

| Plugin | Description |
|--------|-------------|
| [ovos-ww-plugin-openWakeWord](#ovos-ww-plugin-openwakeword) | Wake-word detection using the open-source openWakeWord neural models. |
| [ovos-ww-plugin-vosk](#ovos-ww-plugin-vosk) | Mycroft wake word plugin for [Vosk](https://alphacephei.com/vosk/) |
| [ovos-ww-plugin-precise-onnx](#ovos-ww-plugin-precise-onnx) | ONNX-exported Precise wake word model, an alternative to the TFLite-based default. |
| [ovos-ww-plugin-wakewordlab](https://github.com/OpenVoiceOS/ovos-ww-plugin-wakewordlab) | Compact (~240 KB) neural wake-word models with a Silero VAD pre-filter (`.wkw`/`.onnx`). **Not yet on PyPI** — install from source. |
| [ovos-ww-plugin-wakeforge](https://github.com/OpenVoiceOS/ovos-ww-plugin-wakeforge) | Runs custom wake-word models trained with [wakeforge](https://github.com/TigreGotico/wakeforge) — train a detector from a single phrase, export a two-file model. **Not yet on PyPI** — install from source. |
| [ovos-ww-plugin-server](https://github.com/OpenVoiceOS/ovos-ww-plugin-server) | Remote wake-word detection: streams audio to an [ovos-ww-server](https://github.com/OpenVoiceOS/ovos-ww-server) instance (offload detection from a thin satellite). **Not yet on PyPI** — install from source. |

## ovos-ww-plugin-openWakeWord

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ww-plugin-openWakeWord](https://github.com/OpenVoiceOS/ovos-ww-plugin-openWakeWord)


- **Description**: Wake-word detection using the open-source openWakeWord neural models.

---

## ovos-ww-plugin-vosk

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ww-plugin-vosk](https://github.com/OpenVoiceOS/ovos-ww-plugin-vosk)


- **Description**: Mycroft wake word plugin for [Vosk](https://alphacephei.com/vosk/)

### Default Configuration

```json
  "listener": {
    "wake_word": "hey_computer"
  },
  "hotwords": {
    "hey_computer": {
        "module": "ovos-ww-plugin-vosk",
        "listen": true
    }
  }

```

---

## ovos-ww-plugin-precise-onnx

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx)


- **Description**: Runs Precise wake word models exported to ONNX, an alternative to `ovos-ww-plugin-precise-lite` for deployments that prefer the ONNX runtime.

### Default Configuration

```json
"listener": {
  "wake_word": "hey_mycroft"
},
"hotwords": {
  "hey_mycroft": {
    "module": "ovos-ww-plugin-precise-onnx",
    "model": "https://github.com/OpenVoiceOS/precise-lite-models/raw/master/wakewords/en/hey_mycroft.onnx",
    "trigger_level": 3,
    "sensitivity": 0.5
   }
}

```

---

## Further reading

- [Precise Wake Word Engine Goes ONNX!](https://blog.openvoiceos.org/posts/2025-11-03-precise-onnx) — OVOS blog

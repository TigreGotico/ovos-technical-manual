# Wake Word Plugins

!!! abstract "In a nutshell"
    A *wake word* is the special phrase that gets your assistant's attention — like "Hey Mycroft" — so it only starts paying attention when you mean to talk to it, instead of listening all the time. Wake word plugins are the different tools that listen for that phrase. Some are more accurate for a fixed phrase, while others let you pick your own wake word with less setup. See the [Glossary](glossary.md) and the [listener service](speech-service.md) for related details.

Wake Word plugins allow Open Voice OS to detect specific words or sounds, typically the assistant's name (e.g., "Hey Mycroft"), but can be customized for various use cases. These plugins enable the system to listen for and react to activation commands or phrases.

!!! note "Audio format contract"
    Wake-word plugins receive raw PCM from the [microphone plugin](mic-plugins.md#the-microphone-interface): **16 kHz sample rate, 16-bit samples, mono, little-endian**, delivered in **4096-byte chunks** by default.

## Change your wake word

1. Open `~/.config/mycroft/mycroft.conf` (create it if it doesn't exist).
2. Add or edit the `listener.wake_word` key and a matching entry under `hotwords`:
   ```json
   {
     "listener": { "wake_word": "hey_computer" },
     "hotwords": {
       "hey_computer": { "module": "ovos-ww-plugin-vosk", "listen": true }
     }
   }
   ```
3. Save the file — it's JSON (comments are allowed, `mycroft.conf` is parsed as JSONC).
4. Restart OVOS for the change to take effect:

--8<-- "snippets/restart-ovos.md"

5. Say the new phrase — the assistant now wakes on it instead of "hey mycroft".

## Available Plugins

OVOS supports different wake word detection plugins, each with its own strengths and use cases.
The full roster with descriptions and licenses lives in one place — the
[WW Plugins Reference](#ww-plugins-reference) table below. The default OVOS plugin for
`hey_mycroft` is `ovos-ww-plugin-precise-lite`, with a fallback chain to `ovos-ww-plugin-precise`
(classic Precise), then `ovos-ww-plugin-vosk`, then `ovos-ww-plugin-pocketsphinx` if a plugin
further up the chain is not installed; `ovos-ww-plugin-precise-onnx` is the maintained successor
for new setups. Vosk offers the fastest setup for an arbitrary wake phrase without model training.

> Specification: wake-word detection is one of the deployer-defined capture mechanisms that trigger the audio-input service (referenced in [OVOS-AUDIO-IN-1 §5.1](https://github.com/OpenVoiceOS/architecture/blob/dev/audio-in.md) as the source of a `request_lang` hint).

## Wake Word Configuration

!!! tip "Too many false alarms, or not hearing you at all?"
    - **It wakes up on its own too often (false alarms)?** Raise `trigger_level` (fewer false
      positives, but needs a longer, more sustained match) — or lower `sensitivity`.
    - **It doesn't hear you when you say the wake word?** Raise `sensitivity` (each chunk of
      audio is easier to trigger) — or lower `trigger_level`.

    Both live under `hotwords.<name>` in `mycroft.conf`, next to each other — nudge one at a
    time and test before changing the other. The full technical breakdown of what each number
    actually does is below.

The `hotwords` section in your `mycroft.conf` allows you to configure the wake word detection parameters for each plugin. For instance:

```jsonc
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

- **Vosk Plugin**: The Vosk plugin is useful when you need a simple setup that doesn't require training a wake word model. It's great for quickly gathering data during the development stage.


- **Precision and Sensitivity**: Adjust the `sensitivity` and `trigger_level` settings carefully. Too high a sensitivity can lead to false positives, while too low may miss detection.

### `sensitivity` vs `trigger_level` — the technical breakdown

These two settings work together in the model-based Precise plugins (`ovos-ww-plugin-precise-lite`, `ovos-ww-plugin-precise-onnx`):

- **`sensitivity`** (float, 0.0–1.0, default `0.5`) sets how close a single audio chunk's model output has to be to "yes" before it counts as a match: a chunk counts as activated when its probability exceeds `1.0 - sensitivity`. Raising `sensitivity` makes each individual chunk easier to trigger (more false positives, more sensitive to the word).
- **`trigger_level`** (int, default `3`) is a debounce counter: it's the number of consecutive activated chunks required before the wake word actually fires, so a single lucky chunk isn't enough. Raising `trigger_level` requires a longer sustained match (fewer false positives, but a slower/stricter detection).

In short: `sensitivity` controls how easily *one* chunk counts as a hit; `trigger_level` controls how many hits in a row are needed to confirm the wake word.

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

Here's a simple implementation of a wake word plugin:

```python
from ovos_plugin_manager.templates.hotwords import HotWordEngine
from threading import Event

class MyWWPlugin(HotWordEngine):
    def __init__(self, key_phrase="hey mycroft", config=None):
        super().__init__(key_phrase, config)
        # self.config is the plugin's own sub-dict from `hotwords.<name>` in
        # mycroft.conf — read your plugin-specific settings out of it here
        threshold = self.config.get("sensitivity", 0.5)
        self.detection = Event()
        self.engine = MyWW(key_phrase, threshold=threshold)

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

## WW Plugins Reference

Code license is the SPDX license of the plugin's own repository; where the plugin wraps a
separately-licensed model, that is called out under "model".

| Plugin | Description | License |
|--------|-------------|---------|
| [ovos-ww-plugin-precise-lite](#ovos-ww-plugin-precise-lite) | Default plugin for `hey_mycroft`: a trained Precise wake-word model exported to TFLite. ⚠️ **Archived** — kept working as installed; `ovos-ww-plugin-precise-onnx` is the maintained successor. | Apache-2.0 |
| [ovos-ww-plugin-openWakeWord](#ovos-ww-plugin-openwakeword) | Wake-word detection using the open-source openWakeWord neural models. | Apache-2.0 (model: see model card) |
| [ovos-ww-plugin-vosk](#ovos-ww-plugin-vosk) | Mycroft wake word plugin for [Vosk](https://alphacephei.com/vosk/) | Apache-2.0 (model: see model card) |
| [ovos-ww-plugin-precise-onnx](#ovos-ww-plugin-precise-onnx) | ONNX-exported Precise wake word model, an alternative to the TFLite-based default. | Apache-2.0 |
| [ovos-ww-plugin-wakewordlab](https://github.com/OpenVoiceOS/ovos-ww-plugin-wakewordlab) | Compact (~240 KB) neural wake-word models with a Silero VAD pre-filter (`.wkw`/`.onnx`). **Not yet on PyPI** — install from source. | see repo (no license file) |
| [ovos-ww-plugin-wakeforge](https://github.com/OpenVoiceOS/ovos-ww-plugin-wakeforge) | Runs custom wake-word models trained with [wakeforge](https://github.com/TigreGotico/wakeforge) — train a detector from a single phrase, export a two-file model. **Not yet on PyPI** — install from source. | Apache-2.0 |
| [ovos-ww-plugin-server](https://github.com/OpenVoiceOS/ovos-ww-plugin-server) | Remote wake-word detection: streams audio to an [ovos-ww-server](https://github.com/OpenVoiceOS/ovos-ww-server) instance (offload detection from a thin satellite). **Not yet on PyPI** — install from source. | Apache-2.0 |

## ovos-ww-plugin-precise-lite

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-lite](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-lite) ⚠️ **Archived**


- **Description**: Trained Precise wake-word model exported to TFLite; the plugin the bundled default `mycroft.conf` ships for `hey_mycroft`.

### Default Configuration

```jsonc
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

---

## ovos-ww-plugin-openWakeWord

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ww-plugin-openWakeWord](https://github.com/OpenVoiceOS/ovos-ww-plugin-openWakeWord)


- **Description**: Wake-word detection using the open-source openWakeWord neural models.

---

## ovos-ww-plugin-vosk

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ww-plugin-vosk](https://github.com/OpenVoiceOS/ovos-ww-plugin-vosk)


- **Description**: Mycroft wake word plugin for [Vosk](https://alphacephei.com/vosk/)

### Default Configuration

```jsonc
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

```jsonc
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

!!! tip "Donating wake-word samples"
    The listener can optionally upload wake-word audio samples to an open-data server to help improve detection accuracy — opt-in and off by default. See [Privacy & Security](privacy-security.md#opt-in-wake-word-and-stt-sample-donation).

---

## Further reading

- [Precise Wake Word Engine Goes ONNX!](https://blog.openvoiceos.org/posts/2025-11-03-precise-onnx) — OVOS blog

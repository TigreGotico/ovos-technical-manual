# Grapheme-to-Phoneme (G2P) Plugins

Grapheme-to-Phoneme (G2P) plugins are responsible for converting written text (graphemes) into their spoken representations (phonemes). These are used by [TTS](tts-plugins.md) engines to improve pronunciation and by the GUI to provide lip-sync data (visemes).

## How it works

A G2P plugin takes a word or an utterance and returns a list of phonemes in a specific alphabet, such as **Arpabet** or **IPA**.

## Available G2P Plugins

| Plugin | Alphabet | Description |
|--------|----------|-------------|
| [ovos-g2p-plugin-phoneme-guesser](https://github.com/OpenVoiceOS/ovos-g2p-plugin-phoneme-guesser) | ARPA/IPA | Uses various heuristics and small models to guess pronunciation. |
| [ovos-g2p-plugin-mimic](https://github.com/OpenVoiceOS/ovos-g2p-plugin-mimic) | ARPA | Uses the Mimic 1 engine for G2P conversion. |

---

## Technical Explanation

All G2P plugins inherit from the `Grapheme2PhonemePlugin` base class.

### The G2P Interface

```python
class Grapheme2PhonemePlugin:
    def get_arpa(self, word, lang):
        """Return phonemes in Arpabet format."""
        pass

    def get_ipa(self, word, lang):
        """Return phonemes in IPA format."""
        pass

    def utterance2visemes(self, utterance, lang):
        """Return visemes for lip-sync animation."""
        pass

```

## Creating Your Own Plugin

### 1. Implementation Template

```python
from ovos_plugin_manager.templates.g2p import Grapheme2PhonemePlugin

class MyG2P(Grapheme2PhonemePlugin):
    def get_arpa(self, word, lang):
        # Implement your G2P logic here
        return ["HH", "EH", "L", "OW"]

    @property
    def available_languages(self):
        return {"en-us"}

```

### 2. Registration

Register your plugin in `pyproject.toml`:

```toml
[project.entry-points."opm.plugin.g2p"]
my-g2p = "my_package.module:MyG2P"

```

## Standalone Usage

```python
from ovos_plugin_manager.g2p import find_g2p_plugins

# Find and load the plugin
plugins = find_g2p_plugins()
g2p_class = plugins["ovos-g2p-plugin-phoneme-guesser"]
g2p = g2p_class()

# Convert word to phonemes
phonemes = g2p.get_arpa("hello", lang="en-us")
print(f"Phonemes: {phonemes}")

```

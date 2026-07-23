# Grapheme-to-Phoneme (G2P) Plugins

!!! abstract "In a nutshell"
    These plugins work out *how a written word should sound*. A "grapheme" is just a letter you see on the page, and a "phoneme" is a unit of sound you hear when it's spoken — so this is the part that figures out, for example, that "knight" sounds like "nite". The voice that reads text aloud uses this to pronounce words more correctly, and on-screen avatars use it to move their lips in time with the speech. For unfamiliar terms, see the [Glossary](glossary.md); to learn about the voices that speak, see [TTS Plugins](tts-plugins.md).

Grapheme-to-Phoneme (G2P) plugins are responsible for converting written text (graphemes) into their spoken representations (phonemes). These are used by [TTS](tts-plugins.md) engines to improve pronunciation and by the GUI to provide lip-sync data (visemes).

## How it works

A G2P plugin takes a word or an utterance and returns a list of phonemes in a specific alphabet, such as **Arpabet** or **IPA**.

## Available G2P Plugins

| Plugin | Alphabet | Description |
|--------|----------|-------------|
| `ovos-g2p-plugin-mimic` | ARPA | Uses the Mimic 1 engine for G2P conversion. Shipped by [ovos-tts-plugin-mimic](https://github.com/OpenVoiceOS/ovos-tts-plugin-mimic) (the TTS plugin also registers an `opm.g2p` entry point). |
| [ovos-g2p-plugin-espeak](https://github.com/OVOSHatchery/ovos-g2p-plugin-espeak) | IPA | Wraps `espeak-phonemizer` for broad multilingual IPA coverage. **Hatchery-only** — not published to PyPI, install from source if you need it. |

---

## Technical Explanation

All G2P plugins inherit from the `Grapheme2PhonemePlugin` base class.

### The G2P Interface

```python
class Grapheme2PhonemePlugin:
    def get_arpa(self, word, lang, ignore_oov=False):
        """Return phonemes in Arpabet format."""
        raise NotImplementedError

    def get_ipa(self, word, lang, ignore_oov=False):
        """Return phonemes in IPA format."""
        raise NotImplementedError

    def utterance2visemes(self, utterance, lang, default_dur=0.4):
        """Return visemes for lip-sync animation."""
        ...

```

A plugin implements whichever of `get_arpa` / `get_ipa` it can. The base class
derives `utterance2arpa`, `utterance2ipa`, and `utterance2visemes` from those, and
exposes an `available_languages` classmethod for discovery.

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
[project.entry-points."opm.g2p"]
my-g2p = "my_package.module:MyG2P"

```

## Standalone Usage

```python
from ovos_plugin_manager.g2p import find_g2p_plugins

# Find and load the plugin
plugins = find_g2p_plugins()
g2p_class = plugins["ovos-g2p-plugin-mimic"]
g2p = g2p_class()

# Convert word to phonemes
phonemes = g2p.get_arpa("hello", lang="en-us")
print(f"Phonemes: {phonemes}")

```

## Further reading

- [The First Phonemizer for Barranquenho](https://blog.openvoiceos.org/posts/2025-12-14-barranquenho) — OVOS blog

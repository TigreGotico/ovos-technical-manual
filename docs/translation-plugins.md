# Language Detection and Translation Plugins

Language detection and translation plugins in Open Voice OS (OVOS) enable the system to identify the language of text and translate it between different languages.

## Available Language Plugins

| Plugin | Detect | Translate | Type |
|--------|--------|-----------|------|
| [ovos-translate-plugin-server](https://github.com/OpenVoiceOS/ovos-translate-server-plugin) | ✔️ | ✔️ | API (self hosted) |
| [ovos-translate-plugin-nllb](https://github.com/OpenVoiceOS/ovos-translate-plugin-nllb) | ❌ | ✔️ | FOSS (Offline) |
| [ovos-lang-detector-fasttext-plugin](https://github.com/OpenVoiceOS/ovos-lang-detector-fasttext-plugin) | ✔️ | ❌ | FOSS (Offline) |
| [ovos-google-translate-plugin](https://github.com/OpenVoiceOS/ovos-google-translate-plugin) | ✔️ | ✔️ | API (free) |

---

## Technical Explanation

OVOS provides two base classes for language processing: `LanguageDetector` and `LanguageTranslator`.

### Language Detector Interface

```python
class LanguageDetector:
    def detect(self, text: str) -> str:
        """Return the detected language code (e.g., 'en')."""
        pass

    def detect_probs(self, text: str) -> Dict[str, float]:
        """Return a dictionary of languages and their probabilities."""
        pass
```

### Language Translator Interface

```python
class LanguageTranslator:
    def translate(self, text: str, target: str = None, source: str = None) -> str:
        """Translate text to the target language."""
        pass
```

## Creating Your Own Plugin

### 1. Implementation Template (Translator)

```python
from ovos_plugin_manager.templates.language import LanguageTranslator

class MyTranslator(LanguageTranslator):
    def translate(self, text, target=None, source=None):
        target = target or self.config.get("lang")
        # Implement your translation logic here
        return self.api.translate(text, target, source)

    @property
    def available_languages(self):
        return {"en", "es", "fr", "de"}
```

### 2. Registration

Register your plugin in `pyproject.toml`:

```toml
[project.entry-points."opm.plugin.translate"]
my-translator = "my_package.module:MyTranslator"

[project.entry-points."opm.plugin.detect"]
my-detector = "my_package.module:MyDetector"
```

## Standalone Usage

```python
from ovos_plugin_manager.language import find_tx_plugins, find_lang_detect_plugins

# Translation
tx_plugins = find_tx_plugins()
translator = tx_plugins["ovos-google-translate-plugin"]()
print(translator.translate("Hello", target="es"))

# Detection
detect_plugins = find_lang_detect_plugins()
detector = detect_plugins["ovos-lang-detector-fasttext-plugin"]()
print(detector.detect("Hola, como estas?"))
```

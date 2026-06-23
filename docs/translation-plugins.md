# Language Detection and Translation Plugins

!!! abstract "In a nutshell"
    These add-ons give OVOS two related abilities: working out *what language* some text is in, and *rewriting* text from one language into another. They power features like [Bidirectional Translation](bidirectional-translation.md), so your assistant can understand and reply across languages. Some run entirely offline on your device; others call an online service. You pick which ones to use in the configuration file. See the [Glossary](glossary.md) for terms.

Language detection and translation plugins let OVOS identify the language of a piece of text and translate it between languages. They are the building blocks used by features like [Bidirectional Translation](bidirectional-translation.md), and they can also be called directly from your own code.

**New here?** Two separate jobs are involved:

- **Detection** decides *what language* a string is in (e.g. `"Hola"` → `es`).
- **Translation** rewrites a string *into another language* (e.g. `"Hola"` → `"Hello"`).

A single package may ship one or both. In `mycroft.conf` you select them under the `"language"` section with `"detection_module"` (a detect plugin) and `"translation_module"` (a translate plugin).

## Available Language Plugins

| Plugin (entry-point name) | Detect | Translate | Type | Notes |
|--------|--------|-----------|------|-------|
| `ovos-translate-plugin-server` ([repo](https://github.com/OpenVoiceOS/ovos-translate-server-plugin)) | ✔️ | ✔️ | API (self/community hosted) | Client for [ovos-translate-server](https://github.com/OpenVoiceOS/ovos-translate-server); ships a built-in public-server list with failover. Detection is a separate entry-point, `ovos-lang-detector-plugin-server`. |
| `ovos-translate-plugin-nllb` ([repo](https://github.com/OpenVoiceOS/ovos-translate-plugin-nllb)) | ❌ | ✔️ | FOSS (Offline) | NLLB-200 via CTranslate2; downloads a model the first time. |
| `ovos-lang-detector-fasttext-plugin` ([repo](https://github.com/OpenVoiceOS/ovos-lang-detector-fasttext-plugin)) | ✔️ | ❌ | FOSS (Offline) | fastText language identification. |
| `ovos-lang-detector-classics-plugin` ([repo](https://github.com/OpenVoiceOS/ovos-lang-detector-classics-plugin)) | ✔️ | ❌ | FOSS (Offline) | A *voter* (`ovos-lang-detector-plugin-voter`) that averages classic detectors — by default cld2, langdetect and fastlang (cld3 is also available as a separate sub-plugin). |
| `ovos-google-translate-plugin` ([repo](https://github.com/OpenVoiceOS/ovos-google-translate-plugin)) | ✔️ | ✔️ | API (free) | Translate (`ovos-google-translate-plugin`) and detect (`ovos-google-lang-detector-plugin`) are separate entry-points. |

> **Heads up:** the package repo name, the pip name, and the **entry-point name you put in config** are not always the same. Configure plugins by their *entry-point name* (e.g. `ovos-translate-plugin-server`, not the repo `ovos-translate-server-plugin`). The names in the table above are the entry-point names.

---

## Technical Explanation

OVOS provides two base classes for language processing, both in `ovos_plugin_manager.templates.language`: `LanguageDetector` and `LanguageTranslator`. Each is constructed with a `config` dict (the plugin's section from `mycroft.conf`), exposed as `self.config`.

### Language Detector Interface

```python
from ovos_plugin_manager.templates.language import LanguageDetector

class LanguageDetector:
    def detect(self, text: str) -> str:
        """Return the single best language code (e.g. 'en')."""

    def detect_probs(self, text: str) -> Dict[str, float]:
        """Return a {language_code: probability} dict."""
```

### Language Translator Interface

```python
from ovos_plugin_manager.templates.language import LanguageTranslator

class LanguageTranslator:
    def translate(self, text: str, target: Optional[str] = None,
                  source: Optional[str] = None) -> str:
        """Abstract — every backend implements this. Translate `text` to
        `target`; if `source` is None the plugin detects it."""

    @classproperty
    def available_languages(cls) -> Set[str]:
        """Languages this backend supports (may be empty if unknown/dynamic)."""
```

> **Gotcha (advanced):** `available_languages` is a `classproperty` and several real plugins return an empty set when the backend's language list is dynamic or unknown (e.g. the server and Google plugins). Don't assume it is populated.

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

Register your plugin in `pyproject.toml` under the correct entry-point groups. Translators use `opm.lang.translate`; detectors use `opm.lang.detect`:

```toml
[project.entry-points."opm.lang.translate"]
my-translator = "my_package.module:MyTranslator"

[project.entry-points."opm.lang.detect"]
my-detector = "my_package.module:MyDetector"
```

> The legacy Neon groups `neon.plugin.lang.translate` / `neon.plugin.lang.detect` are still honoured as aliases by `ovos-plugin-manager` (this is why a plugin like `ovos-lang-detector-fasttext-plugin` keeps working), but new plugins **should** register under the `opm.lang.*` groups.

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

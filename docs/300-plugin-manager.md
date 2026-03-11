# OVOS Plugin Manager (OPM)

![image](https://github.com/OpenVoiceOS/ovos-plugin-manager/assets/33701864/8c939267-42fc-4377-bcdb-f7df65e73252)

The OVOS Plugin Manager (OPM) is the plugin discovery and loading infrastructure for the
OVOS ecosystem. It standardizes the interface for plugins via Python package entry points,
making plugins portable, independently installable, and reusable across OVOS services and
other projects.

---

## How It Works

Plugins are Python packages that register a class under a specific entry point group in
`setup.py` or `pyproject.toml`. OPM uses `importlib.metadata.entry_points()` to discover
all installed plugins of a given type at runtime — no manual registration required.

```python
from ovos_plugin_manager.stt import find_stt_plugins, load_stt_plugin

# List all installed STT plugins
print(find_stt_plugins())
# {'ovos-stt-plugin-whisper': <class ...>, 'ovos-stt-plugin-server': <class ...>}

# Load a specific plugin class
MySTT = load_stt_plugin("ovos-stt-plugin-whisper")
```

Factories handle the full lifecycle — discovery, instantiation, and configuration:

```python
from ovos_plugin_manager.stt import OVOSSTTFactory

stt = OVOSSTTFactory.create({
    "module": "ovos-stt-plugin-whisper",
    "ovos-stt-plugin-whisper": {"model": "base"}
})
transcript = stt.execute(audio_data)
```

---

## Plugin Types

All plugin types are defined in the `PluginTypes` enum (`ovos_plugin_manager.utils`).
The entry point group is the canonical identifier used in `setup.py` / `pyproject.toml`.

### Core Voice Pipeline Plugins

| Plugin type | Entry point group | Template base class |
|---|---|---|
| STT (Speech-to-Text) | `opm.stt` | `ovos_plugin_manager.templates.stt.STT` |
| TTS (Text-to-Speech) | `opm.tts` | `ovos_plugin_manager.templates.tts.TTS` |
| Wake Word | `opm.wake_word` | `ovos_plugin_manager.templates.hotwords.HotWordEngine` |
| Wake Word Verifier | `opm.wake_word.verifier` | `HotWordVerifier` |
| VAD (Voice Activity Detection) | `opm.VAD` | `VADEngine` |
| Microphone | `opm.microphone` | `OVOSMicrophone` |
| G2P (Grapheme-to-Phoneme) | `opm.g2p` | `Grapheme2PhonemePlugin` |

### System & Hardware Plugins

| Plugin type | Entry point group | Template base class |
|---|---|---|
| PHAL (user) | `opm.phal` | `PHALPlugin` |
| PHAL (admin/root) | `opm.phal.admin` | `AdminPlugin` |
| GUI Adapter | `opm.gui_adapter` | `AbstractGUIPlugin` |

### Transformer Plugins

| Plugin type | Entry point group | Template base class |
|---|---|---|
| Audio Transformer | `opm.transformer.audio` | `AudioTransformer` |
| Dialog Transformer | `opm.transformer.dialog` | `DialogTransformer` |
| TTS Transformer | `opm.transformer.tts` | `TTSTransformer` |
| Utterance Transformer | `opm.transformer.text` | `UtteranceTransformer` |
| Metadata Transformer | `opm.transformer.metadata` | `MetadataTransformer` |
| Intent Transformer | `opm.transformer.intent` | `IntentTransformer` |

### Language Processing Plugins

| Plugin type | Entry point group | Template base class |
|---|---|---|
| Language Translator | `opm.lang.translate` | `LanguageTranslator` |
| Language Detector | `opm.lang.detect` | `LanguageDetector` |
| Keyword Extraction | `opm.keywords` | `KeywordExtractor` |
| Utterance Segmentation | `opm.segmentation` | `UtteranceSegmenter` |
| Tokenization | `opm.tokenization` | `Tokenizer` |
| POS Tagger | `opm.postag` | `PosTagger` |

### Intent Pipeline Plugins

| Plugin type | Entry point group | Template base class |
|---|---|---|
| Pipeline | `opm.pipeline` | `PipelinePlugin` |

### Media Plugins

| Plugin type | Entry point group |
|---|---|
| OCP Stream Extractor | `opm.ocp.extractor` |
| Audio Player | `opm.media.audio` |
| Video Player | `opm.media.video` |
| Web Player | `opm.media.web` |

### Agent Plugins

| Plugin type | Entry point group | Template base class |
|---|---|---|
| Chat | `opm.agents.chat` | `ChatEngine` |
| Retrieval | `opm.agents.retrieval` | `RetrievalEngine` |
| Summarizer | `opm.agents.summarizer` | `SummarizerEngine` |
| Extractive QA | `opm.agents.extractive_qa` | `ExtractiveQAEngine` |
| NLI | `opm.agents.nli` | `NaturalLanguageInferenceEngine` |
| Reranker | `opm.agents.reranker` | `ReRankerEngine` |
| Memory | `opm.agents.memory` | `AgentContextManager` |

### Deprecated Types

These are still recognized (mapped to canonical names internally) but should not be used
in new plugins:

| Old entry point group | Canonical |
|---|---|
| `mycroft.plugin.stt` | `opm.stt` |
| `mycroft.plugin.tts` | `opm.tts` |
| `mycroft.plugin.wake_word` | `opm.wake_word` |
| `ovos.plugin.phal` | `opm.phal` |
| `ovos.plugin.phal.admin` | `opm.phal.admin` |
| `ovos.plugin.VAD` | `opm.VAD` |
| `neon.plugin.lang.translate` | `opm.lang.translate` |
| `neon.plugin.lang.detect` | `opm.lang.detect` |
| `neon.plugin.text` | `opm.transformer.text` |
| `neon.plugin.audio` | `opm.transformer.audio` |

---

## Writing a Plugin

### 1. Implement the base class

```python
# my_stt_plugin/__init__.py
from ovos_plugin_manager.templates.stt import STT
from typing import Optional, Set

class MySTTPlugin(STT):
    """My custom speech-to-text engine."""

    @property
    def available_languages(self) -> Set[str]:
        return {"en-US", "en-GB", "de-DE"}

    def execute(self, audio, language: Optional[str] = None) -> str:
        lang = language or self.lang
        # call your backend here and return transcript
        return "hello world"
```

```python
# my_tts_plugin/__init__.py
from ovos_plugin_manager.templates.tts import TTS, TTSValidator
from typing import Set

class MyTTSPlugin(TTS):
    """My custom text-to-speech engine."""

    def __init__(self, config=None):
        super().__init__(config, audio_ext="wav")

    @property
    def available_languages(self) -> Set[str]:
        return {"en-US"}

    def get_tts(self, sentence: str, wav_file: str, lang=None, voice=None):
        # synthesize `sentence` to `wav_file`; return (wav_file, phonemes_or_None)
        return wav_file, None

class MyTTSValidator(TTSValidator):
    def validate_lang(self):
        assert self.tts.lang in MyTTSPlugin.available_languages

    def get_tts_class(self):
        return MyTTSPlugin
```

```python
# my_ww_plugin/__init__.py
from ovos_plugin_manager.templates.hotwords import HotWordEngine

class MyWakeWord(HotWordEngine):
    """My custom wake word detector."""

    def __init__(self, key_phrase="hey mycroft", config=None):
        super().__init__(key_phrase, config)

    def update(self, chunk: bytes) -> None:
        # feed audio chunk to the model
        pass

    def found_wake_word(self) -> bool:
        # return True when wake word is detected
        return False
```

### 2. Register the entry point

Using `setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name="ovos-stt-plugin-my-engine",
    version="0.1.0",
    license="Apache-2.0",
    packages=find_packages(),
    install_requires=["ovos-plugin-manager>=0.0.1"],
    entry_points={
        "opm.stt": [
            "my-engine-stt = my_stt_plugin:MySTTPlugin"
        ],
        # Optional: language config exposure
        "opm.stt.config": [
            "my-engine-stt = my_stt_plugin:MySTTPluginConfig"
        ],
    },
)
```

Using `pyproject.toml`:

```toml
[project.entry-points."opm.stt"]
my-engine-stt = "my_stt_plugin:MySTTPlugin"

[project.entry-points."opm.stt.config"]
my-engine-stt = "my_stt_plugin:MySTTPluginConfig"
```

### 3. Install and verify

```bash
pip install -e .

python -c "
from ovos_plugin_manager.stt import find_stt_plugins
print('my-engine-stt' in find_stt_plugins())  # True
"
```

### 4. Expose language configurations (optional)

Plugins that support multiple voices/models should expose a `.config` entry point returning
`{lang: [list_of_config_dicts]}`:

```python
class MyTTSPluginConfig:
    @staticmethod
    def get_configs():
        return {
            "en-US": [
                {"lang": "en-US", "gender": "female", "priority": 50, "offline": True},
                {"lang": "en-US", "gender": "male",   "priority": 50, "offline": True},
            ],
            "de-DE": [
                {"lang": "de-DE", "gender": "female", "priority": 60, "offline": False},
            ],
        }
```

| Config key | Type | Description |
|---|---|---|
| `lang` | `str` | BCP-47 language code |
| `priority` | `int` | Lower = higher priority (default 60) |
| `gender` | `str` | `"male"` or `"female"` |
| `offline` | `bool` | Whether this variant works without internet |
| `display_name` | `str` | Human-readable name for the voice/model |

### 5. Declare `RuntimeRequirements`

Override `runtime_requirements` to declare connectivity needs. OVOS uses this to decide
whether the plugin can be loaded before network/internet is available.

```python
from ovos_utils.process_utils import RuntimeRequirements

class MySTTPlugin(STT):

    @classproperty
    def runtime_requirements(cls):
        return RuntimeRequirements(
            internet_before_load=True,
            network_before_load=True,
            requires_internet=True,
            requires_network=True,
            no_internet_fallback=False,
            no_network_fallback=False,
        )
```

---

## Configuration Utilities

`ovos_plugin_manager.utils.config` provides helpers for resolving plugin configuration
from `mycroft.conf`.

### `get_plugin_config`

```python
def get_plugin_config(
    config: Optional[dict] = None,
    section: str = None,
    module: Optional[str] = None,
) -> dict
```

Resolve a merged configuration dict for a plugin. Precedence (highest to lowest):

1. Module-specific block — `config[section][module]`
2. Section-level defaults — `config[section]` (scalar keys only)
3. Top-level `lang` — `config['lang']`

```python
from ovos_plugin_manager.utils.config import get_plugin_config

cfg = get_plugin_config(section="stt", module="ovos-stt-plugin-whisper")
# {'module': 'ovos-stt-plugin-whisper', 'lang': 'en-US', ...}
```

### `load_plugin_configs`

```python
def load_plugin_configs(
    plug_name: str,
    plug_type: Optional[PluginConfigTypes] = None,
    normalize_language_keys: bool = False,
) -> Union[dict, list]
```

Load language/variant configuration for a single plugin by calling its `.config` entry point.
Returns `{lang: [list_of_config_dicts]}`.

### `load_configs_for_plugin_type`

```python
def load_configs_for_plugin_type(plug_type: PluginTypes) -> dict
```

Load configs for **all** installed plugins of the given type.
Returns `{plugin_name: {lang: [configs]}}`.

### `get_plugin_language_configs`

```python
def get_plugin_language_configs(
    plug_type: PluginTypes,
    lang: str,
    include_dialects: bool = False,
) -> dict
```

Return configs for all plugins of `plug_type` that support `lang`.
Returns `{plugin_name: [list_of_valid_config_dicts]}`.

When `include_dialects=True`, configs for closely related dialects are included with a
+15 priority bonus (to 75).

### `get_plugin_supported_languages`

```python
def get_plugin_supported_languages(plug_type: PluginTypes) -> dict
```

Return `{lang: [plugin_name, ...]}` mapping language codes to all plugins supporting them.

### `sort_plugin_configs`

```python
def sort_plugin_configs(configs: dict) -> dict
```

Sort each plugin's config list by the `"priority"` key (lower = higher priority).
Invalid/empty config lists are removed.

---

## Configuration Priority

Within a config list, entries are sorted by their `"priority"` key. Higher values are
more preferred; factory methods iterate from the end (highest priority last). The default
priority is `60`. A dialect match boosts priority by `+15`.

---

## Voice Satellites (HiveMind)

HiveMind setups allow distributing which plugins run server-side or satellite-side:

**Skills Server** — HiveMind server runs core services and skills; satellites handle their
own STT/TTS locally:

![Server Profile](https://github.com/OpenVoiceOS/ovos-technical-manual/assets/33701864/55694b82-69c9-4288-9a89-1d9716eb3c57)

**Audio Server** — HiveMind server runs a full OVOS core and handles STT/TTS for all
satellites:

![Listener Profile](https://github.com/OpenVoiceOS/ovos-technical-manual/assets/33701864/1455a488-af0f-44b4-a5e6-0418a7cd1f96)

---

## Projects Using OPM

- [ovos-core](https://github.com/OpenVoiceOS/ovos-core) — intent pipeline, skill loading
- [ovos-audio](https://github.com/OpenVoiceOS/ovos-audio) — TTS, audio backends
- [ovos-dinkum-listener](https://github.com/OpenVoiceOS/ovos-dinkum-listener) — STT, wake word, VAD, microphone
- [ovos-tts-server](https://github.com/OpenVoiceOS/ovos-tts-server) — HTTP TTS proxy
- [ovos-stt-http-server](https://github.com/OpenVoiceOS/ovos-stt-http-server) — HTTP STT proxy
- [wyoming-ovos-stt / wyoming-ovos-tts / wyoming-ovos-wakeword](204-wyoming-bridges.md) — Wyoming protocol bridges
- [neon-core](https://github.com/NeonGeckoCom/NeonCore) — compatible fork
- [HiveMind voice satellite](https://github.com/JarbasHiveMind/HiveMind-voice-sat) — distributed voice pipeline

STT, TTS, and WakeWord plugin types retain backward compatibility with Mycroft-Core via
legacy entry point aliases (`mycroft.plugin.*`).

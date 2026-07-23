# Utterance Transformers

!!! abstract "In a nutshell"
    An "utterance" is simply the text of what you said, once the assistant has transcribed your speech into words. These plugins get to fix and tidy that text *before* the assistant tries to understand it — for example correcting misheard words, smoothing out the phrasing, or handling more than one language — so it matches your request more reliably. See [Transformer Plugins](transformer-plugins.md) and the [Glossary](glossary.md) for unfamiliar terms.

??? info "📐 Formal specification"
    Utterance transformers are the **`utterance` chain** of **[OVOS-TRANSFORM-1 — Transformer Plugins](https://github.com/OpenVoiceOS/architecture/blob/dev/transformer.md) §3.2** (a formal [architecture spec](architecture-specs.md)). The spec's post-STT, pre-intent injection point receives the **non-empty list of candidate transcriptions** (`utterances[0]` is the primary candidate, later indices are n-best alternatives), an optional `lang`, and the full `Message.context`; it returns a possibly rewritten list plus mutated `lang`/context. Returning an empty list signals "no plausible transcription"; returning empty **with** `canceled: true` + `cancel_reason` invokes utterance cancellation (§3.2, §8). **Ordering:** the chain runs by **ascending** `priority` (lowest first), matching the spec.

**Utterance Transformers** in OpenVoiceOS (OVOS) are plugins that process and modify user utterances immediately after speech-to-text ([STT](stt-plugins.md)) conversion but before intent recognition. They serve to enhance the accuracy and flexibility of the assistant by correcting errors, normalizing input, and handling multilingual scenarios.

---

## How They Work

1. **Speech Recognition**: The user's spoken input is transcribed into text by the STT engine.


2. **Transformation Phase**: The transcribed text passes through any active utterance transformers.


3. **Intent Recognition**: The transformed text is then processed by the intent recognition system to determine the appropriate response.

This sequence ensures that any necessary preprocessing is applied to the user's input, improving the reliability of intent matching.

Utterance transformers register under the `opm.transformer.text` entry-point group and subclass `UtteranceTransformer` from `ovos_plugin_manager.templates.transformers`. They are loaded and chained by `UtteranceTransformersService` in `ovos-core`.

---

## Configuration

A transformer is only loaded if its plugin name appears under the `utterance_transformers` section of your `mycroft.conf`; an empty `{}` is enough to enable it. Set `"active": false` to load-skip it. When several are active they run sorted by `priority` (lowest first), each operating on the output of the previous.

```jsonc
"utterance_transformers": {
  "plugin_name": {
    // plugin-specific configuration
  }
}

```

Replace `"plugin_name"` with the identifier of the desired plugin and provide any necessary configuration parameters.

---

## Available Utterance [Transformer](transformer-plugins.md) Plugins

### **OVOS Utterance Normalizer Plugin**

* **Purpose**: Standardizes user input by expanding contractions, converting numbers to words, and removing unnecessary punctuation.


* **Example**:


    * Input: `"I'm 5 years old."`


    * Output: `"I am five years old"`


* **Installation**:

```bash
pip install ovos-utterance-normalizer

```

* **Configuration**:

```jsonc
"utterance_transformers": {
  "ovos-utterance-normalizer": {}
}

```

* **Source**: [GitHub Repository](https://github.com/OpenVoiceOS/ovos-utterance-normalizer)

---

### **OVOS Utterance Corrections Plugin**

* **Purpose**: Applies predefined corrections to common misrecognitions or user-defined replacements to improve intent matching.


* **Features**:


    * Full utterance replacements via `corrections.json`


    * Word-level replacements via `word_corrections.json`


    * Regex-based pattern replacements via `regex_corrections.json`


* **Example**:


    * Input: `"shalter is a switch"`


    * Output: `"schalter is a switch"`


* **Installation**:

```bash
pip install ovos-utterance-corrections-plugin

```

* **Configuration**:

```jsonc
"utterance_transformers": {
  "ovos-utterance-corrections-plugin": {}
}

```

* **Source**: [GitHub Repository](https://github.com/OpenVoiceOS/ovos-utterance-corrections-plugin)

---

### **OVOS Utterance Cancel Plugin**

* **Purpose**: Detects phrases indicating the user wishes to cancel or ignore the current command and prevents further processing.


* **Example**:


    * Input: `"Hey Mycroft, can you tell me the... umm... oh, nevermind that"`


    * Output: *Utterance is discarded; no action taken*


* **Installation**:

```bash
pip install ovos-utterance-plugin-cancel

```

* **Configuration** (the installed package is `ovos-utterance-plugin-cancel`, but its registered plugin name is `ovos-utterance-cancel-plugin`):

```jsonc
"utterance_transformers": {
  "ovos-utterance-cancel-plugin": {}
}

```

* **Source**: [GitHub Repository](https://github.com/OpenVoiceOS/ovos-utterance-plugin-cancel)

---

### **OVOS Bidirectional Translation Plugin**

* **Purpose**: Detects the language of the user's input and translates it to the assistant's primary language if necessary, enabling multilingual interactions.


* **Features**:


    * Language detection and translation to primary language


    * Optional translation of responses back to the user's language


* **Example**:


    * Input: `"¿Cuál es el clima hoy?"` (Spanish)


    * Output: `"What is the weather today?"` (translated to English for processing)


* **Installation**:

```bash
pip install ovos-bidirectional-translation-plugin

```

* **Configuration** (the utterance half registers under the entry-point name `ovos-utterance-translation-plugin`):

```jsonc
"utterance_transformers": {
    "ovos-utterance-translation-plugin": {
      "verify_lang": true,
      "ignore_invalid_langs": true
    }
}

```

* **Source**: [GitHub Repository](https://github.com/OpenVoiceOS/ovos-bidirectional-translation-plugin)

---

## Creating Custom Utterance Transformers

To develop your own utterance transformer:

**Create a Python Class**:

```python
from typing import List, Tuple
from ovos_plugin_manager.templates.transformers import UtteranceTransformer

class MyCustomTransformer(UtteranceTransformer):
   def __init__(self, config=None):
       super().__init__("my-custom-transformer", priority=10, config=config)

   def transform(self, utterances: List[str],
                 context: dict = None) -> Tuple[List[str], dict]:
       # utterances is a list of strings; return (utterances, extra_context)
       context = context or {}
       modified_utterances = [u.lower() for u in utterances]
       return modified_utterances, context

```

The second return value is *additional* context that gets merged into the message context, not a replacement for it.

**Register as a Plugin**:
In your `pyproject.toml`, register under the `opm.transformer.text` group:

```toml
[project.entry-points."opm.transformer.text"]
my-custom-transformer = "my_module:MyCustomTransformer"

```

**Install and Configure**:
After installation, add your transformer to the `mycroft.conf`:

```jsonc
"utterance_transformers": {
 "my-custom-transformer": {}
}

```

### **OVOS Transcription Validator Plugin**

* **Purpose**: Uses an OpenAI-compatible LLM to judge whether an STT transcription is a
  plausible utterance at all, filtering out garbled or nonsensical speech-to-text output
  before it reaches intent matching.

!!! note
    This plugin makes a network call per utterance (to the configured LLM endpoint), so
    it trades latency for robustness against noisy STT.

* **Installation**:

```bash
pip install ovos-transcription-validator-plugin

```

* **Configuration**:

```jsonc
"utterance_transformers": {
  "ovos-transcription-validator-plugin": {}
}

```

* **Source**: [GitHub Repository](https://github.com/OpenVoiceOS/ovos-transcription-validator-plugin)

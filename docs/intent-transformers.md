# Intent Transformers

!!! abstract "In a nutshell"
    Once the assistant has figured out *what you want* (your "intent" — for example, "set a timer"), these plugins can add extra detail or tidy up that request before the matching feature actually runs. It's a chance to fill in or pull out the specifics — like spotting names, places, or numbers in what you said — in one shared place instead of repeating that work everywhere. See [Transformer Plugins](transformer-plugins.md) and the [Glossary](glossary.md) for unfamiliar terms.

**Intent Transformers** are a pluggable mechanism in OVOS that allow you to enrich or transform intent data **after** an intent is matched by an engine ([Padatious](padatious-pipeline.md), [Adapt](adapt-pipeline.md), etc.), but **before** it is passed to the skill handler.

This is useful for:

* Named Entity Recognition (NER)


* Keyword extraction


* Slot filling


* Contextual enrichment

Each transformer subclasses `IntentTransformer` (`ovos_plugin_manager.templates.transformers`), registers under the `opm.transformer.intent` entry-point group, and operates on the `IntentHandlerMatch` object returned by the matching pipeline. They are loaded and chained by `IntentTransformersService` in `ovos-core` (`ovos_core/transformers.py`).

Transformers run sorted by `priority`, **highest first** — so a transformer with `priority` 1 runs *last* and gets the final say over `match_data`. This lets you reimplement entity logic once instead of in every skill.

---

## Default Transformers

`ovos-core` declares these two plugins as dependencies, so a standard install ships with them present. Each one only *runs* when its plugin name is listed under `intent_transformers` in your config:

| Plugin name (config key)        | PyPI package                | Description                                                                                         | Priority |
|---------------------------------|-----------------------------| -------------------------------------------------------------------------------------------------- | -------- |
| `ovos-keyword-template-matcher` | `keyword-template-matcher`  | Extracts values from `{placeholder}`-style intent templates                                        | 1        |
| `ovos-ahocorasick-ner-plugin`   | `ahocorasick-ner`           | Performs NER using Aho-Corasick keyword matching based on registered entities from skill templates | 5        |

A transformer is loaded only if its plugin name appears under `intent_transformers`; set `"active": false` to skip it. (Note: `ahocorasick-ner` runs before `keyword-template-matcher`, since 5 > 1.)

---

## Configuration

To enable or disable specific transformers, modify your `mycroft.conf`:

```json
"intent_transformers": {
  "ovos-keyword-template-matcher": {
    "active": true
  },
  "ovos-ahocorasick-ner-plugin": {
    "active": false
  }
}

```


---

## How It Works

### Example Workflow

1. An utterance matches an intent via Padatious, Adapt, or another engine, producing an `IntentHandlerMatch`.


2. The `IntentService` passes that match to `IntentTransformersService.transform(match)`.


3. Each registered transformer plugin runs its `transform()` method in priority order (highest first), each receiving the match returned by the previous one.


4. Extracted entities are injected into the intent's `match_data`.


5. The updated `match_data` is passed to the skill via the `Message` object.

### Skill Access

Entities extracted by transformers are made available to your skill in the `message.data` dictionary:

```python
location = message.data.get("location")
person = message.data.get("person")

```

---

## Default Plugins

### `ovos-ahocorasick-ner-plugin`

This plugin builds a per-skill Aho-Corasick automaton using keywords explicitly provided by the developer via registered entities.

> ❗ It will **only match keywords that the skill developer has accounted for**

It does **not** use external data or extract entities generically.

---

### `ovos-keyword-template-matcher`

This plugin parses registered intent templates like:

```
what's the weather in {location}

```

It uses the template structure to extract `{location}` directly from the utterance.

If the user says "what's the weather in Tokyo", the plugin will populate:

```python
match_data = {
  "location": "Tokyo"
}

```

---

## Writing Your Own Intent [Transformer](transformer-plugins.md)

Subclass `IntentTransformer` and implement `transform()` (the base declares it abstract). The method receives and must return an `IntentHandlerMatch`; mutate its `match_data` in place and return it. Register under the `opm.transformer.intent` entry-point group.

```python
from ovos_plugin_manager.templates.transformers import IntentTransformer
from ovos_plugin_manager.templates.pipeline import IntentHandlerMatch

class MyCustomTransformer(IntentTransformer):
    def __init__(self, config=None):
        super().__init__("my-transformer", priority=10, config=config)

    def transform(self, intent: IntentHandlerMatch) -> IntentHandlerMatch:
        # enrich the matched intent, e.g. inject extracted entities
        intent.match_data["my_entity"] = "value"
        return intent

```

```toml
[project.entry-points."opm.transformer.intent"]
my-transformer = "my_module:MyCustomTransformer"

```

Unlike utterance transformers, intent transformers get the message bus attached (`bind(bus)`) when loaded, so `self.bus` is available inside `transform()`.


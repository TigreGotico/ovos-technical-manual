# Padatious Pipeline

!!! abstract "In a nutshell"
    Padatious is one of the tools that helps the assistant work out what you want. Instead of matching fixed keywords, a skill gives it a handful of example sentences (like "what is the weather" and "what's the weather like"), and Padatious learns the pattern so it can recognize new phrasings of the same request. It is the "learns from examples" companion to the keyword-based [Adapt](adapt-pipeline.md) tool. See the [Glossary](glossary.md) for unfamiliar terms.

The **Padatious Pipeline Plugin** brings example-based intent recognition to the **OpenVoiceOS (OVOS)** pipeline. You define each intent by listing a few example sentences in a plain-text `.intent` file; Padatious trains a small neural network (backed by [fann2](https://github.com/FutureLinkCorporation/fann2)) on those examples and scores incoming utterances against them.

**When it runs:** Padatious sits early in the pipeline. Its high-confidence stage runs before Adapt, so a strong example match wins over a keyword rule. The medium and low stages run later, as the pipeline relaxes its confidence requirements.

**Minimal example** — drop a `weather.intent` file in your skill's `locale/en-us/` folder:

```
what is the weather
tell me the weather
what's the weather like
```

and wire it up:

```python
from ovos_workshop.decorators import intent_handler

@intent_handler("weather.intent")
def handle_weather(self, message):
    ...
```

---

## Pipeline Stages

The plugin ships a single OPM entry point, `ovos-padatious-pipeline-plugin`, mapped to the `PadatiousPipeline` class. Because that class is a `ConfidenceMatcherPipeline`, OVOS exposes three matcher stages from it, selected in your pipeline config by these IDs (the short `padatious_*` aliases still work but are deprecated):

| Pipeline ID        | Legacy alias       | Matcher       | Recommended Use                       |
| ------------------ | ------------------ | ------------- | ------------------------------------- |
| `ovos-padatious-pipeline-plugin-high`   | `padatious_high`   | `match_high`  | Primary stage for Padatious use       |
| `ovos-padatious-pipeline-plugin-medium` | `padatious_medium` | `match_medium`| Backup, if confidence tuning allows   |
| `ovos-padatious-pipeline-plugin-low`    | `padatious_low`    | `match_low`   | Not recommended (often inaccurate)    |

Each stage runs at a different point in the pipeline and applies a different confidence threshold to the same scored result.

---

## Configuration

Configure Padatious thresholds in your `mycroft.conf` under `intents` → `padatious`. The defaults are:

```json
"intents": {
  "padatious": {
    "conf_high": 0.95,
    "conf_med": 0.8,
    "conf_low": 0.5
  }
}
```

These thresholds gate which matcher stage accepts a given result.

Other useful config keys read by the plugin:

| Key | Default | Effect |
|---|---|---|
| `cast_to_ascii` | `false` | Strip accents before matching |
| `stem` | `false` | Apply Snowball stemming to examples and utterances |
| `disable_padaos` | `false` | Disable the bundled regex fast-path and use only the neural matcher |
| `intent_cache` | XDG data dir | Where trained intent models are cached |

---

## Multilingual Support

Padatious is **excellent for multilingual environments** because intents are defined in plain text `.intent` files, not in code. This allows translators and non-developers to contribute new languages easily without touching Python.

To add another language, simply create a new `.intent` file in the relevant language folder, such as:

```
locale/pt-pt/weather.intent
locale/fr-fr/weather.intent

```

---

## Defining Intents

Intent examples are written line-by-line in `.intent` files:

```
what is the weather
tell me the weather
what's the weather like

```

In your skill:

```python
from ovos_workshop.decorators import intent_handler

@intent_handler("weather.intent")
def handle_weather(self, message):
    # Your code here
    pass

```

---

## Limitations

Padatious is reliable in terms of **not misclassifying** — it rarely picks the wrong intent. However, it has key limitations:

* **Weak paraphrase handling**: If the user speaks a sentence that doesn’t closely match an example, Padatious will often fail to match anything at all.


* **Rigid phrasing required**: You may end up in a “train the user to speak correctly” scenario, instead of training the system to understand variations.


* **Maintenance burden for sentence diversity**: Adding more phrasing requires adding more sentence examples per intent, increasing effort and clutter.

---

## When to Use

Padatious is a good choice in OVOS when:

* You want **easy localization/multilingual support**.


* You’re creating **simple, personal, or demo skills**.


* You can **control or guide user phrasing**, such as in kiosk or assistant environments.

Avoid Padatious for complex conversational use cases, skills with overlapping intents, or scenarios requiring broad paraphrasing support.

---

## Advanced

**Entry point and class.** The plugin registers one `opm.pipeline` entry point:

```toml
[project.entry-points."opm.pipeline"]
"ovos-padatious-pipeline-plugin" = "ovos_padatious.opm:PadatiousPipeline"
```

`PadatiousPipeline` subclasses `ConfidenceMatcherPipeline`, exposing `match_high`, `match_medium`, and `match_low`. The `_high`/`_medium`/`_low` pipeline IDs are derived from that single plugin at runtime by the plugin manager — they are not separate entry points.

**Files.** Skills register `.intent` files (example sentences) and `.entity` files (entity value lists). Registration happens over the bus via `padatious:register_intent` and `padatious:register_entity`; training is triggered by `mycroft.skills.train` and announced with `mycroft.skills.trained`.

**Gotcha — training is asynchronous.** Padatious must train its model before it can match. On a cold start (or after installing a skill), matches will silently fail until training completes. Set `instant_train` to force synchronous training when you need deterministic behavior in tests.

!!! warning "Upcoming — unreleased"
    A second entry point, `DomainPadatiousPipeline`, which trains a separate model per skill domain to reduce cross-skill collisions, is proposed in [ovos-padatious-pipeline-plugin#69](https://github.com/OpenVoiceOS/ovos-padatious-pipeline-plugin/pull/69) and is not yet on `dev`.


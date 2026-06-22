# OVOS Intent Pipeline

!!! abstract "In a nutshell"
    When you speak to your assistant, something has to figure out *what you actually want* and act on it. The intent pipeline is the part that does that: it passes your words through a series of checkpoints, each trying to understand the request, from confident exact matches down to best-guess fallbacks. The first checkpoint that recognizes your request handles it, much like a help desk that sends your question to the right department. See the [Glossary](glossary.md) and the [Fallback Pipeline](fallback-pipeline.md) for related terms.

> Specification: the utterance lifecycle is defined by [OVOS-PIPELINE-1: Utterance Lifecycle and Pipeline](https://github.com/OpenVoiceOS/architecture/blob/dev/ovos-pipeline-1.md).

The OpenVoiceOS (OVOS) Intent Pipeline is a modular and extensible system designed to interpret user utterances and map them to appropriate actions or responses. It orchestrates various intent parsers and fallback mechanisms to ensure accurate and contextually relevant responses.

---

## What is an Intent Pipeline?

An intent pipeline in OVOS is a sequence of processing stages that analyze user input to determine the user's intent. Each stage employs different strategies, ranging from high-confidence intent parsers to fallback mechanisms, to interpret the input.

This layered approach ensures that OVOS can handle a wide range of user queries with varying degrees of specificity and complexity.

---

## Pipeline Structure

When an utterance arrives, OVOS walks the pipeline in order and hands the utterance to each stage until one claims it. Stages are tried from most to least confident:

*   **High Confidence**: Primary intent parsers that provide precise matches.


*   **Medium Confidence**: Secondary parsers that handle less specific queries.


*   **Low Confidence**: [Fallback](fallback-pipeline.md) mechanisms for ambiguous or unrecognized inputs.

The first stage that matches wins, so order matters: a high-confidence Padatious match is tried before any medium-confidence stage, which is tried before any low-confidence stage. Each component is a plugin that can be enabled, disabled, or reordered in your config.

**Pipeline IDs vs. plugins.** The IDs you list in your `pipeline` config (like `adapt_high`) are not separate plugins. A confidence-aware plugin registers a single OPM entry point (e.g. `ovos-adapt-pipeline-plugin`), and OVOS derives the `_high`/`_medium`/`_low` matcher stages from it at runtime. Plugins that match at only one confidence level (such as `converse` or `common_qa`) expose a single bare ID. The legacy short IDs are mapped to plugin IDs by the `_PIPELINE_MIGRATION_MAP` in ovos-core.

---

## Available Pipeline Components

Below is a list of available pipeline components, categorized by their confidence levels and functionalities:

### High Confidence Components

| Pipeline | Description | Notes |
|---|---|---|
| `stop_high` | Exact match for stop commands | Replaces [skill-ovos-stop](https://github.com/OpenVoiceOS/skill-ovos-stop) |
| `converse` | Continuous conversation interception for skills | |
| `padatious_high` | High-confidence matches using [Padatious](padatious-pipeline.md) | |
| `adapt_high` | High-confidence matches using [Adapt](adapt-pipeline.md) | |
| `fallback_high` | High-priority fallback skill matches | |
| `ocp_high` | High-confidence media-related queries | |
| `ovos-persona-pipeline-plugin-high` | Active persona conversation (e.g., LLM integration) | |
| `ovos-m2v-pipeline-high` | Multilingual intent classifier | Only supports default skills |

### Medium Confidence Components

| Pipeline | Description | Notes |
|---|---|---|
| `stop_medium` | Medium-confidence stop command matches | Replaces [skill-ovos-stop](https://github.com/OpenVoiceOS/skill-ovos-stop) |
| `padatious_medium` | Medium-confidence matches using Padatious | |
| `adapt_medium` | Medium-confidence matches using Adapt | |
| `ocp_medium` | Medium-confidence media-related queries | |
| `fallback_medium` | Medium-priority fallback skill matches | |
| `ovos-m2v-pipeline-medium` | Multilingual intent classifier | Only supports default skills |

### Low Confidence Components

| Pipeline | Description | Notes |
|---|---|---|
| `stop_low` | Low-confidence stop command matches | Disabled by default |
| `padatious_low` | Low-confidence matches using Padatious | Disabled by default |
| `adapt_low` | Low-confidence matches using Adapt | |
| `ocp_low` | Low-confidence media-related queries | |
| `fallback_low` | Low-priority fallback skill matches | |
| `common_qa` | Sends utterance to common-query skills | Best match among skills |
| `ovos-persona-pipeline-plugin-low` | Persona catch-all fallback | |
| `ovos-m2v-pipeline-low` | Multilingual intent classifier | Only supports default skills |

---

### Other available matchers (not enabled by default)

These are additional OVOS-org intent-matcher pipeline plugins you can install and add to the
pipeline. They expose the same high/medium/low confidence tiers as Adapt/Padatious:

| Plugin | Description |
|---|---|
| [`nebulento`](https://github.com/OpenVoiceOS/nebulento) | Fuzzy / typo-tolerant template matcher (rapidfuzz); no training step. Listens on the same `padatious:register_intent` bus events, plus a hierarchical variant. |
| [`palavreado`](https://github.com/OpenVoiceOS/palavreado) | Dead-simple keyword matcher; an Adapt drop-in that responds to the same `register_vocab`/`register_intent` events (zero-change skill swap). |
| [`ovos-hierarchical-knn-pipeline`](https://github.com/OpenVoiceOS/ovos-hierarchical-knn-pipeline) | Embedding-based two-stage k-NN matcher (Granite embeddings + FAISS); a heavier alternative to [Model2Vec](m2v-pipeline.md) (~320 MB RAM, AVX2, 11 languages). |

---

## Customizing the Pipeline

OVOS allows users to customize the intent pipeline through configuration files. Users can enable or disable specific components, adjust their order, and set confidence thresholds.

```json
  "intents": {
    "ovos-adapt-pipeline-plugin": {
      "conf_high": 0.5,
      "conf_med": 0.3,
      "conf_low": 0.2
    },
    "persona": {
      "handle_fallback": true,
      "default_persona": "Remote Llama"
    },
    "pipeline": [
      "ovos-m2v-pipeline-high",
      "ocp_high",
      "stop_high",
      "converse",
      "padatious_high",
      "adapt_high",
      "stop_medium",
      "adapt_medium",
      "common_qa",
      "fallback_medium",
      "fallback_low"
    ]
  },

```

---

# Pipeline Plugins Reference

| Plugin | Description |
|--------|-------------|
| [ovos-common-query-pipeline-plugin](#ovos-common-query-pipeline-plugin) | Answer questions by gathering answers from several skills |
| [ovos-m2v-pipeline](#ovos-m2v-pipeline) | Intent matching powered by the Model2Vec model |
| [ovos-padatious-pipeline-plugin](#ovos-padatious-pipeline-plugin) | Neural network intent parser |
| [ovos-adapt-pipeline-plugin](#ovos-adapt-pipeline-plugin) | Adapt Intent Parser |
| [ovos-ocp-pipeline-plugin](#ovos-ocp-pipeline-plugin) | Specialized media handling |

## ovos-common-query-pipeline-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-common-query-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-common-query-pipeline-plugin)


- **Description**: The OVOS Common Query Framework is designed to answer questions by gathering answers from several skills and selecting the best one.

---

## ovos-m2v-pipeline

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-m2v-pipeline](https://github.com/OpenVoiceOS/ovos-m2v-pipeline)


- **Description**: An intent matching pipeline powered by the Model2Vec model for intent classification.

---

## ovos-padatious-pipeline-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-padatious-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-padatious-pipeline-plugin)


- **Description**: An efficient and agile neural network intent parser.

---

## ovos-adapt-pipeline-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-adapt-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-adapt-pipeline-plugin)


- **Description**: Adapt Intent Parser.

---

## ovos-ocp-pipeline-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ocp-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-ocp-pipeline-plugin)


- **Description**: OVOS plugin for specialized media handling.

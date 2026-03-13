# OVOS Intent Pipeline

The OpenVoiceOS (OVOS) Intent Pipeline is a modular and extensible system designed to interpret user utterances and map them to appropriate actions or responses. It orchestrates various intent parsers and fallback mechanisms to ensure accurate and contextually relevant responses.

---

## What is an Intent Pipeline?

An intent pipeline in OVOS is a sequence of processing stages that analyze user input to determine the user's intent. Each stage employs different strategies, ranging from high-confidence intent parsers to fallback mechanisms, to interpret the input.

This layered approach ensures that OVOS can handle a wide range of user queries with varying degrees of specificity and complexity.

---

## Pipeline Structure

OVOS pipelines are structured to prioritize intent matching based on confidence levels:

*   **High Confidence**: Primary intent parsers that provide precise matches.


*   **Medium Confidence**: Secondary parsers that handle less specific queries.


*   **Low Confidence**: [Fallback](fallback-pipeline.md) mechanisms for ambiguous or unrecognized inputs.

Each component in the pipeline is a plugin that can be enabled, disabled, or reordered according to user preferences.

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
| `common_query` | Sends utterance to common_query skills | Best match among skills |
| `ovos-persona-pipeline-plugin-low` | Persona catch-all fallback | |
| `ovos-m2v-pipeline-low` | Multilingual intent classifier | Only supports default skills |

---

## Customizing the Pipeline

OVOS allows users to customize the intent pipeline through configuration files. Users can enable or disable specific components, adjust their order, and set confidence thresholds.

```json
  "intents": {
    "adapt": {
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
| [ovos-ha-pipeline](#ovos-ha-pipeline) | Home Assistant integration |
| [ovos-padatious-pipeline-plugin](#ovos-padatious-pipeline-plugin) | Neural network intent parser |
| [ovos-ollama-intent-pipeline-plugin](#ovos-ollama-intent-pipeline-plugin) | Intent matching via Ollama LLMs |
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

## ovos-ha-pipeline

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ha-pipeline](https://github.com/OpenVoiceOS/ovos-ha-pipeline)


- **Description**: Home Assistant intent pipeline integration.

---

## ovos-padatious-pipeline-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-padatious-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-padatious-pipeline-plugin)


- **Description**: An efficient and agile neural network intent parser.

---

## ovos-ollama-intent-pipeline-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ollama-intent-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-ollama-intent-pipeline-plugin)


- **Description**: Powered by local or remote LLMs via Ollama.

---

## ovos-adapt-pipeline-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-adapt-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-adapt-pipeline-plugin)


- **Description**: Adapt Intent Parser.

---

## ovos-ocp-pipeline-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ocp-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-ocp-pipeline-plugin)


- **Description**: OVOS plugin for specialized media handling.

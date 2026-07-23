# OVOS Intent Pipeline

!!! abstract "In a nutshell"
    When you speak to your assistant, something has to figure out *what you actually want* and act on it. The intent pipeline is the part that does that: it passes your words through a series of checkpoints, each trying to understand the request, from confident exact matches down to best-guess fallbacks. The first checkpoint that recognizes your request handles it, much like a help desk that sends your question to the right department. See the [Glossary](glossary.md) and the [Fallback Pipeline](fallback-pipeline.md) for related terms.

??? info "📐 Formal specification"
    The utterance lifecycle and the pipeline-plugin contract are specified by **[OVOS-PIPELINE-1 — Utterance Lifecycle & Pipeline](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)**. The intents these plugins consume are specified by **[OVOS-INTENT-3 — Intent Definition](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-3.md)** (keyword and template intents) over the **[OVOS-INTENT-1 — Sentence Template Grammar](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-1.md)**. See the [spec index](architecture-specs.md) for the full set.

The OpenVoiceOS (OVOS) Intent Pipeline is a modular and extensible system designed to interpret user utterances and map them to appropriate actions or responses. It orchestrates various intent parsers and fallback mechanisms to ensure accurate and contextually relevant responses.

!!! note "Spec vocabulary in one paragraph"
    In OVOS-PIPELINE-1 terms, every stage on this page is a **pipeline plugin** identified by an opaque `pipeline_id`. Each one exposes exactly one operation to the **orchestrator**: `match(utterances, lang, session) → Match | None`. The orchestrator iterates the plugins in the order given by `session.pipeline` and stops at the **first** one that returns a `Match` — **first match wins**. There is *no* cross-plugin confidence comparison: the per-stage `conf_high/medium/low` thresholds below are each plugin's *own* internal accept/reject gate, not a score the orchestrator ranks between plugins. On a match the orchestrator dispatches the handler on the topic `<skill_id>:<intent_name>` (PIPELINE-1 §7) and emits the handler-lifecycle trio; if no plugin claims, it emits `ovos.intent.unmatched`. Several stages here — converse, stop, common-query, persona, fallback — are pipeline plugins that claim via **reserved `intent_name` values** (`converse`, `response`, `stop`, `common_query`, `fallback`) leased in PIPELINE-1 §7.3; skills may not register those names.

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

Ordering is **the arbitration model, not a missing feature** (PIPELINE-1 §6.2). Because an earlier plugin gets to answer before any later plugin is asked, a stateful interceptor that depends on session state — converse with an open response window, an active persona, OCP holding paused media to *resume*, stop — can claim "yes" / "next" / "resume" / "stop" *before* a general intent engine would match the bare words. Such selective plugins are deliberately conservative: they claim only when both the utterance and the session warrant it, and return `None` otherwise, trusting their position rather than competing on a score (heterogeneous engines share no common score space to rank across anyway).

**Pipeline IDs vs. plugins.** The IDs you list in your `pipeline` config (like `ovos-adapt-pipeline-plugin-high`) are not separate plugins. A confidence-aware plugin registers a single OPM entry point (e.g. `ovos-adapt-pipeline-plugin`), and OVOS derives the `-high`/`-medium`/`-low` matcher stages from it at runtime. Plugins that match at only one confidence level (such as `ovos-converse-pipeline-plugin` or `ovos-common-query-pipeline-plugin`) expose a single bare ID. The older short names (`adapt_high`, `common_qa`, …) are **deprecated aliases**: ovos-core rewrites them to the canonical plugin IDs via the `_PIPELINE_MIGRATION_MAP`, so existing configs keep working, but new configs should use the canonical names shown below.

---

## Available Pipeline Components

Below is a list of available pipeline components, categorized by their confidence levels and functionalities. The **Pipeline ID** column shows the canonical name to put in your `pipeline` config going forward. The **Legacy alias** column shows the older short name — this is actually what the bundled default config still ships with (ovos-core rewrites it to the canonical ID at load time), but new configs should use the canonical names.

!!! note "The bundled default pipeline"
    The default `pipeline` list shipped in `mycroft.conf` currently uses the legacy short names,
    in this order:

    --8<-- "snippets/default-pipeline.md"

    Note that Padatious/Adapt's medium and low tiers, Model2Vec,
    Persona, and the `-low` tiers of stop/padatious are **not** in the default list; you add them
    yourself if you want them.

### High Confidence Components

| Pipeline ID | Legacy alias | Description |
|---|---|---|
| `ovos-stop-pipeline-plugin-high` | `stop_high` | Exact match for stop commands (replaces [skill-ovos-stop](https://github.com/OpenVoiceOS/skill-ovos-stop)) |
| `ovos-converse-pipeline-plugin` | `converse` | Continuous conversation interception for skills |
| `ovos-padatious-pipeline-plugin-high` | `padatious_high` | High-confidence matches using [Padatious](padatious-pipeline.md) |
| `ovos-adapt-pipeline-plugin-high` | `adapt_high` | High-confidence matches using [Adapt](adapt-pipeline.md) |
| `ovos-fallback-pipeline-plugin-high` | `fallback_high` | High-priority fallback skill matches |
| `ovos-ocp-pipeline-plugin-high` | `ocp_high` | High-confidence media-related queries |
| `ovos-persona-pipeline-plugin-high` | — | Active persona conversation (e.g., LLM integration) |
| `ovos-m2v-pipeline-high` | — | Multilingual intent classifier (only supports default skills) |

> **OCP vs. Common Query:** these are two unrelated pipeline plugins that both start with "Common" —
> **OCP** (Common Play, the `ocp_*` stages above) matches media-*playback* requests like "play X";
> **Common Query** (the `common_qa` stage further below) sends a question to every skill that can
> answer it and picks the best response. Neither one calls into the other.

### Medium Confidence Components

| Pipeline ID | Legacy alias | Description |
|---|---|---|
| `ovos-stop-pipeline-plugin-medium` | `stop_medium` | Medium-confidence stop command matches |
| `ovos-padatious-pipeline-plugin-medium` | `padatious_medium` | Medium-confidence matches using Padatious |
| `ovos-adapt-pipeline-plugin-medium` | `adapt_medium` | Medium-confidence matches using Adapt |
| `ovos-ocp-pipeline-plugin-medium` | `ocp_medium` | Medium-confidence media-related queries |
| `ovos-fallback-pipeline-plugin-medium` | `fallback_medium` | Medium-priority fallback skill matches |
| `ovos-m2v-pipeline-medium` | — | Multilingual intent classifier (only supports default skills) |

### Low Confidence Components

| Pipeline ID | Legacy alias | Description |
|---|---|---|
| `ovos-stop-pipeline-plugin-low` | `stop_low` | Low-confidence stop command matches (disabled by default) |
| `ovos-padatious-pipeline-plugin-low` | `padatious_low` | Low-confidence matches using Padatious (disabled by default) |
| `ovos-adapt-pipeline-plugin-low` | `adapt_low` | Low-confidence matches using Adapt |
| `ovos-ocp-pipeline-plugin-low` | `ocp_low` | Low-confidence media-related queries |
| `ovos-fallback-pipeline-plugin-low` | `fallback_low` | Low-priority fallback skill matches |
| `ovos-common-query-pipeline-plugin` | `common_qa` | Sends utterance to common-query skills (best match among skills) |
| `ovos-persona-pipeline-plugin-low` | — | Persona catch-all fallback |
| `ovos-m2v-pipeline-low` | — | Multilingual intent classifier (only supports default skills) |

---

### Other available matchers (not enabled by default)

These are additional OVOS-org intent-matcher pipeline plugins you can install and add to the
pipeline. They expose the same high/medium/low confidence tiers as Adapt/Padatious:

| Plugin | Description |
|---|---|
| [Padacioso](padacioso.md) | Literal template matcher (simplematch); no training. A pure-Python sibling of [Padatious](padatious-pipeline.md). |
| [Nebulento](nebulento.md) | Fuzzy / typo-tolerant template matcher (rapidfuzz); no training step. Listens on the same `padatious:register_intent` bus events, plus a hierarchical variant. |
| [Palavreado](palavreado.md) | Dead-simple keyword matcher; an [Adapt](adapt-pipeline.md) drop-in that responds to the same `register_vocab`/`register_intent` events (zero-change skill swap). |
| [Hierarchical KNN](knn-pipeline.md) | Embedding-based two-stage k-NN matcher (Granite embeddings + FAISS); a heavier semantic alternative to [Model2Vec](m2v-pipeline.md) (~560 MB footprint, AVX2, 11 languages). |
| [`ovos-markov-pipeline-plugin`](https://github.com/OpenVoiceOS/ovos-markov-pipeline-plugin) | Markov-chain perplexity ensemble: trains one word-level Markov chain per intent from example utterances and picks the intent whose model has the lowest perplexity for the utterance. Lightweight, GPU-free, and trains in milliseconds — a practical baseline for small skill sets. |
| [`ovos-hivemind-pipeline-plugin`](hivemind-agents.md#as-an-intent-pipeline-stage) | Delegates the utterance to a remote [HiveMind](hivemind-agents.md) agent — a catch-all "ask a smarter OVOS" stage. |

---

## Customizing the Pipeline

OVOS allows users to customize the intent pipeline through configuration files. Users can enable or disable specific components, adjust their order, and set confidence thresholds.

```json
{
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
      "ovos-stop-pipeline-plugin-high",
      "ovos-converse-pipeline-plugin",
      "ovos-ocp-pipeline-plugin-high",
      "ovos-padatious-pipeline-plugin-high",
      "ovos-adapt-pipeline-plugin-high",
      "ovos-m2v-pipeline-high",
      "ovos-ocp-pipeline-plugin-medium",
      "ovos-fallback-pipeline-plugin-high",
      "ovos-stop-pipeline-plugin-medium",
      "ovos-adapt-pipeline-plugin-medium",
      "ovos-fallback-pipeline-plugin-medium",
      "ovos-fallback-pipeline-plugin-low"
    ]
  }
}
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

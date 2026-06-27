# Model2Vec Intent Pipeline

!!! abstract "In a nutshell"
    This is another tool that figures out which skill should handle what you said. Instead of matching exact keywords or memorized examples, it compares the *meaning* of your words to the commands it knows — so it can still understand you when you phrase things differently than expected. Think of it as recognizing that "turn the music down" and "lower the volume" are asking for the same thing. It is meant to work alongside the keyword-based [Adapt](adapt-pipeline.md) and example-based [Padatious](padatious-pipeline.md) tools, not replace them. See the [Glossary](glossary.md) for unfamiliar terms.

!!! info "📐 Formal specification"
    Model2Vec is a **pipeline plugin** under **[OVOS-PIPELINE-1 — Utterance Lifecycle & Pipeline](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)**. It serves the same **template-intent** role as Padatious in **[OVOS-INTENT-3 — Intent Definition §5](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-3.md)** — a classifier paired with a slot extractor (INTENT-3 §6.2) — only the matching strategy (static embeddings) differs; INTENT-3 §8 leaves that strategy unconstrained. Skill resources are written in the **[OVOS-INTENT-1 grammar](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-1.md)**. See the [spec index](architecture-specs.md).

The **Model2Vec Intent Pipeline** matches utterances to skill intents using
[Model2Vec](https://github.com/MinishLab/model2vec) static embeddings instead of
deterministic parsers. Where Adapt looks for keywords and Padatious learns from
example sentences, this pipeline embeds the utterance as a vector and picks the
closest known intent. That makes it more forgiving of paraphrases and word order,
and it works across languages when a multilingual model is used.

It is meant to **augment** Adapt and Padatious, not replace them: put a Model2Vec
matcher in your pipeline alongside the others and let confidence ordering decide.

---

## Quick start

Install the plugin:

```bash
pip install ovos-m2v-pipeline
```

Add a matcher to your pipeline in `mycroft.conf`:

```json
{
  "intents": {
    "ovos-m2v-pipeline": {
      "model": "Jarbas/ovos-model2vec-intents-LaBSE"
    },
    "pipeline": [
      "ovos-converse-pipeline-plugin",
      "ovos-m2v-pipeline-high",
      "ovos-padatious-pipeline-plugin-high",
      "ovos-adapt-pipeline-plugin-high",
      "ovos-fallback-pipeline-plugin-low"
    ]
  }
}
```

That is enough to get going. The model is downloaded from Hugging Face on first
run. The sections below cover how matching works and how to tune it.

---

## How it works

The plugin (`Model2VecIntentPipeline`) is a `ConfidenceMatcherPipeline`, so it
exposes three confidence tiers — `match_high`, `match_medium`, `match_low` — that
become the pipeline matcher IDs `ovos-m2v-pipeline-high` / `-medium` / `-low`.

For an utterance it:

1. Embeds the text with the configured Model2Vec model.
2. Scores every label the model knows about.
3. Keeps only labels that belong to **currently registered** Adapt/Padatious
   intents (the pipeline tracks them over the bus via
   `intent.service.adapt.manifest` / `intent.service.padatious.manifest` and the
   `register_intent` / `padatious:register_intent` / `detach_intent` /
   `detach_skill` events). Three special labels — `ocp:play`,
   `common_query:common_query`, `stop:stop` — are also allowed, but only when the
   corresponding downstream pipeline (`ovos-ocp-pipeline-plugin`,
   `ovos-common-query-pipeline-plugin`, `ovos-stop-pipeline-plugin`) is present in
   the session's pipeline list.
4. Returns the highest-scoring label as an `IntentHandlerMatch` if its score
   clears the tier threshold (`conf_high` / `conf_medium` / `conf_low`).

Because matching is restricted to intents that are actually loaded, the model can
ship knowledge of many skills without firing for skills you do not have installed.

---

## Two operating modes

The pipeline has a `mode` config key:

* **`classifier`** (default) — loads a `StaticModelPipeline` (embedding model plus
  a trained linear classifier head). Scores are softmax probabilities. This is the
  mode used by the published `Jarbas/ovos-model2vec-intents-*` models.
* **`prototype`** — loads a bare `StaticModel` (embeddings only, no trained head)
  and builds a prototype store at runtime from the example utterances skills
  provide when they register Padatious intents. Scores are cosine similarities.
  Adapt intents (which have no example sentences) are tracked by name but not
  matched in this mode.

A second entry point, `ovos-m2v-prototype-pipeline`
(`Model2VecPrototypePipeline`), is the prototype mode exposed as a standalone
plugin so it can run alongside the classifier one. It reads its config from
`intents.ovos_m2v_prototype_pipeline`.

---

## Configuration

```json
{
  "intents": {
    "ovos-m2v-pipeline": {
      "model": "Jarbas/ovos-model2vec-intents-LaBSE",
      "mode": "classifier",
      "conf_high": 0.7,
      "conf_medium": 0.5,
      "conf_low": 0.15,
      "ignore_intents": []
    }
  }
}
```

| Key | Default | Description |
|-----|---------|-------------|
| `model` | `Jarbas/ovos-model2vec-intents-distiluse-base-multilingual-cased-v2` | Local path or Hugging Face repo of the Model2Vec model. |
| `mode` | `classifier` | `classifier` (trained head, softmax) or `prototype` (runtime prototypes, cosine). |
| `conf_high` | `0.7` | Threshold for `match_high`. |
| `conf_medium` | `0.5` | Threshold for `match_medium`. |
| `conf_low` | `0.15` | Threshold for `match_low`. |
| `ignore_intents` | `[]` | Intent labels to never match. |
| `renormalize` | `false` | Classifier mode: renormalise probabilities over the surviving (registered) labels. |

Prototype mode adds `prototype_k`, `prototype_strategy`, `prototype_top_k` and
`prototype_tau` to control how prototype embeddings are selected per label.

> The model is **pretrained**. It does not learn new skills at runtime — the
> registered-intent filter just decides which of the model's known labels are
> eligible. In prototype mode the store is rebuilt at runtime, but only from the
> example utterances Padatious skills provide.

---

## Models

Two families are published on Hugging Face:

* **Multilingual** — distilled from LaBSE, larger, supports many languages and
  partially translated skills (as long as their **dialogs** are localized).
* **Language-specific** — roughly 10x smaller and nearly as accurate for a single
  language, well suited to constrained hardware (e.g. Raspberry Pi).

Browse them here:
[OVOS Model2Vec Models on Hugging Face](https://huggingface.co/collections/Jarbas/ovos-model2vec-intents-681c478aecb9979e659b17f8)

The models are trained on aggregated intent examples: LLM-augmented OVOS
utterances, music-query templates, and per-language skill intents.

---

## Gotcha: ordering against the deterministic engines

Model2Vec generalises well, which also means it can claim an utterance a more
precise parser would have nailed. The usual setup is to place
`ovos-m2v-pipeline-high` after the high tiers of Padatious/Adapt (or interleaved by
confidence) so exact matches win first and Model2Vec catches the paraphrases the
others miss. Tune `conf_high`/`conf_medium`/`conf_low` to control how aggressive it
is.

!!! warning "Upcoming — unreleased"
    A hierarchical two-stage prototype variant (domain-then-intent) is proposed in
    [ovos-m2v-pipeline#36](https://github.com/OpenVoiceOS/ovos-m2v-pipeline/pull/36)
    and is not yet on `dev`.

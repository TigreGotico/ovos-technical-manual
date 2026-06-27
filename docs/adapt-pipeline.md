# Adapt Pipeline Plugin

!!! abstract "In a nutshell"
    Adapt is one of the tools that helps the assistant figure out what you want when you speak to it. It works like a checklist: a skill says "if you hear these keywords together, this is the command for me." When you say "switch on the lamp", Adapt spots the keywords "switch on" and "lamp" and routes your request to the right skill. There is no guessing or learning involved — it simply matches the words it was told to look for. See the [Glossary](glossary.md) for terms, or [Padatious](padatious-pipeline.md) for a sister tool that learns from example sentences instead.

!!! info "📐 Formal specification"
    Adapt is a **pipeline plugin** under **[OVOS-PIPELINE-1 — Utterance Lifecycle & Pipeline](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)**. It is a **keyword-intent** engine in the sense of **[OVOS-INTENT-3 — Intent Definition §4](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-3.md)**: it matches by *which vocabularies occur* (required / optional / one-of / excluded), with each occurring vocabulary doubling as a slot. The `.voc` vocabularies are written in the **[OVOS-INTENT-1 — Sentence Template Grammar](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-1.md)** (`(a|b)` / `[optional]` expansion). See the [spec index](architecture-specs.md).

The **Adapt Pipeline Plugin** brings rule-based, keyword-driven intent parsing to the **OVOS intent pipeline** using the Adapt parser. A skill registers keywords (vocabulary) and a rule describing which keywords must appear; Adapt scores an utterance by how many of those keywords it finds. There is no training step and no neural network — matching is deterministic.

In OVOS-PIPELINE-1 terms Adapt is a pipeline plugin exposing `match(utterances, lang, session) → Match | None`; the orchestrator runs it in `session.pipeline` order and takes the first match. Its `conf_high/medium/low` thresholds are Adapt's own accept gate per stage, not a score the orchestrator ranks against other plugins (INTENT-3 §1.1 leaves scoring engine-specific). The `required`/`one-of`/`excluded` keyword roles are INTENT-3 §4.2 constraint roles; `.rx` regex entities are an OVOS implementation extension that INTENT-3 §4.4 deliberately leaves out of the spec (free-form text is better modelled as a template-intent slot).

**When it runs:** Adapt's high-confidence stage runs just after Padatious's, so an exact example match wins over a keyword rule, but a strong keyword match still beats most fallbacks. Its medium and low stages run later in the pipeline.

**Minimal example** — a skill registers vocabulary and a rule:

```python
self.register_vocabulary("Light", "lamp")        # locale/.../Light.voc
self.register_vocabulary("On", "switch on")      # locale/.../On.voc

@intent_handler(IntentBuilder("LightOnIntent")
                .require("On").require("Light"))
def handle_light_on(self, message):
    ...
```

"switch on the lamp" then matches with high confidence because both required keywords are present.

While Adapt is good for **explicit, deterministic command-and-control**, it scales poorly across many skills and is hard to localize. **It is not recommended for broad deployments** — prefer it for **personal skills** where you control the full vocabulary.

---

## Pipeline Stages

The plugin ships an OPM entry point, `ovos-adapt-pipeline-plugin`, mapped to the `AdaptPipeline` class. That class is a `ConfidenceMatcherPipeline`, so OVOS exposes three matcher stages from it, selected in your pipeline config by these IDs (the short `adapt_*` aliases still work but are deprecated):

| Pipeline ID    | Legacy alias   | Matcher        | Recommended Use        |
| -------------- | -------------- | -------------- | ---------------------- |
| `ovos-adapt-pipeline-plugin-high`   | `adapt_high`   | `match_high`   | Personal skills only   |
| `ovos-adapt-pipeline-plugin-medium` | `adapt_medium` | `match_medium` | Use with caution       |
| `ovos-adapt-pipeline-plugin-low`    | `adapt_low`    | `match_low`    | Not recommended        |

Each stage scores the utterance with Adapt and accepts it if the score clears that stage's threshold.

---

## Limitations

Adapt requires **hand-crafted rules** for every intent:

* ❌ **Poor scalability** — hard to manage with many skills


* ❌ **Difficult to localize** — rules rely on exact words and phrases


* ❌ **Prone to conflicts** — multiple skills defining overlapping rules can cause collisions or missed matches

As your skill library grows or if you operate in a multilingual setup, these problems increase.

**Recommendation:**

> 🟢 Use Adapt **only** in personal projects or controlled environments where you can fully define and test every possible phrase.

---

## Configuration

Adapt confidence thresholds can be set in `mycroft.conf`:

```json
"intents": {
  "ovos-adapt-pipeline-plugin": {
    "conf_high": 0.65,
    "conf_med": 0.45,
    "conf_low": 0.25
  }
}

```

> The config section is keyed by the pipeline's plugin id (`intents.<pipeline-id>`), here
> `ovos-adapt-pipeline-plugin`. The domain/hierarchical variants read
> `intents.ovos_adapt_domain_pipeline` / `intents.ovos_adapt_hierarchical_pipeline`.

* These thresholds gate which matcher stage accepts a result. The values shown are the source defaults.


* The plugin is included by default in OVOS.

---

## When to Use Adapt in OVOS

Use this plugin **only when**:

* You are building **a personal or private skill**.


* You need **strict, predictable matching** (e.g., command-and-control).


* You are working in **a single language** and **control all skill interactions**.

Avoid using Adapt for public-facing or general-purpose assistant skills. Modern alternatives like **[Padatious](padatious-pipeline.md)**, **LLM-based parsers**, or **neural fallback models** are more scalable and adaptable.

---

## Advanced

**Entry points.** The plugin registers three `opm.pipeline` entry points, each a different matching strategy over the same Adapt engine:

```toml
[project.entry-points."opm.pipeline"]
"ovos-adapt-pipeline-plugin"              = "ovos_adapt.opm:AdaptPipeline"
"ovos-adapt-domain-pipeline-plugin"       = "ovos_adapt.opm:DomainAdaptPipeline"
"ovos-adapt-hierarchical-pipeline-plugin" = "ovos_adapt.opm:HierarchicalAdaptPipeline"
```

`AdaptPipeline` is the flat parser most deployments use. `DomainAdaptPipeline` and `HierarchicalAdaptPipeline` partition intents per skill/domain to cut down on cross-skill keyword collisions; they read extra config under `intents.ovos_adapt_domain_pipeline` and `intents.ovos_adapt_hierarchical_pipeline`. All three subclass `ConfidenceMatcherPipeline` and expose `match_high`/`match_medium`/`match_low`.

**Vocabulary files.** Skills supply keyword lists as `.voc` files (one phrase per line, with `(a|b)` alternatives and `[optional]` words expanded at registration), and regular-expression entities as `.rx` files using Python named groups, e.g. `(?P<Location>.+)`. Registration flows over the bus via `register_vocab` and `register_intent`.

**Gotcha — collisions are silent.** Two skills that require overlapping vocabulary can shadow each other; the higher-scoring match wins with no warning. Make each skill's required keywords as specific as possible, and prefer the domain/hierarchical entry points when running many skills together.

---

*Source code: [OpenVoiceOS/ovos-adapt-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-adapt-pipeline-plugin).*

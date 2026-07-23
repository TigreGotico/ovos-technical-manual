# Common Query Pipeline

!!! abstract "In a nutshell"
    When you ask a general-knowledge question like "who wrote Hamlet?", the Common Query pipeline asks *all* your installed knowledge skills (Wikipedia, Wolfram Alpha, and so on) the same question at once, gathers their answers, and reads back the best one. Think of it as a quiz host who puts the question to every contestant and then announces the strongest reply. It never makes up answers itself — every answer comes from a skill, so if you have no knowledge skills installed it simply stays quiet. See the [Intent Pipeline overview](pipelines-overview.md) or the [Glossary](glossary.md).

??? info "📐 Formal specification"
    Common Query is specified by **[OVOS-COMMON-QUERY-1 — Common Query Pipeline Plugin](https://github.com/OpenVoiceOS/architecture/blob/dev/common-query.md)**, built on **[OVOS-PIPELINE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)**. See the [spec index](architecture-specs.md).

The **Common Query Pipeline Plugin** answers general-knowledge questions. When an
utterance looks like a question ("Who wrote Hamlet?", "How tall is Everest?"), it
broadcasts the question to every installed **CommonQuery skill**, collects their
answers, and picks the best one.

It does **not** generate text or do retrieval-augmented generation — every answer
comes from a skill. It is also not a chit-chat handler. Think of it as a referee
that asks all your knowledge skills the same question and returns the strongest
reply.

---

## Quick start

It ships with `ovos-core`, but can be installed standalone:

```bash
pip install ovos-common-query-pipeline-plugin
```

It registers one pipeline matcher: **`ovos-common-query-pipeline-plugin`** (legacy
alias `common_qa`). Add it to your pipeline, near the end, so high-confidence intents
win first:

```json
{
  "intents": {
    "pipeline": [
      "ovos-padatious-pipeline-plugin-high",
      "ovos-adapt-pipeline-plugin-high",
      "ovos-common-query-pipeline-plugin",
      "ovos-fallback-pipeline-plugin-medium"
    ]
  }
}
```

Now install one or more CommonQuery skills (e.g. Wikipedia, Wolfram Alpha) and ask
a question.

---

!!! note "Why it never blocks fallback (and spec topic names)"
    Common Query is a **scatter-gather contest** that runs *entirely inside `match`* (COMMON-QUERY-1 §2): it polls skills, collects full answers, ranks them, and only returns a `Match` if one clears the confidence threshold — otherwise it returns `None` and the orchestrator continues to fallback. The answer *is* the claim decision, so this is the spec's documented exception to PIPELINE-1 §4.4's "return fast" rule (§2.1). On a win it returns a **self-addressed** Match on the reserved `intent_name` `common_query` (PIPELINE-1 §7.3), dispatched on `<pipeline_id>:common_query`, and its own trivial handler speaks the selected answer. The spec topic names differ from the current code:

    | OVOS-COMMON-QUERY-1 (canonical) | Current code |
    |---|---|
    | `ovos.common_query.ping` / `.pong` — wants-to-answer poll | discovery handshake (same names) |
    | `<skill_id>.common_query.request` — full-answer request to a claiming skill (dotted, non-dispatch) | `question:query` broadcast |
    | `<skill_id>.common_query.response` — a skill's answer + `conf` | `question:query.response` |
    | `<pipeline_id>:common_query` — reserved-name handler dispatch (the one genuine colon/dispatch topic in this family) | `question:action.<skill_id>` |

## How it works

The matcher class is `CommonQAService` (a `PipelinePlugin`, so it exposes a single
`match()` — hence the one `ovos-common-query-pipeline-plugin` ID, not high/medium/low tiers).

1. **Question detection** — `is_question_like()` requires at least 3 words, a
   "question word" (`QuestionWord` vocab), and rejects utterances that match
   `Play`, `Weather`, `Alerts`, or a misc blacklist. Non-questions are skipped so
   the query never goes out.
2. **Broadcast** — emits `question:query` with the phrase. CommonQuery skills are
   discovered on startup via an `ovos.common_query.ping` / `ovos.common_query.pong`
   handshake.
3. **Collect** — skills reply on `question:query.response`, each with an answer and
   a self-reported confidence. A skill can ask for more time by replying with
   `searching: true`, which extends the timeout.
4. **Select** — the best answer is chosen. If a reranker plugin is configured and
   loaded, it scores the candidate answers; otherwise the skills' own confidences
   order them.
5. **Deliver** — returns an `IntentHandlerMatch`. The match type is
   `question:action.<skill_id>` (or plain `question:action` for skills still using
   the deprecated CommonQuery base class), so the selected skill is told to speak
   its answer.

---

## Configuration

```json
{
  "intents": {
    "ovos-common-query-pipeline-plugin": {
      "min_self_confidence": 0.5,
      "min_reranker_score": 0.2,
      "reranker": "<your-reranker-plugin>"
    }
  }
}
```

The config block is read from `intents.ovos-common-query-pipeline-plugin`, falling
back to the older `intents.common_query` key.

| Key | Default | Description |
|-----|---------|-------------|
| `min_self_confidence` | `0.5` | Minimum confidence a skill must self-report to be considered. |
| `min_reranker_score` | `0.2` | Minimum reranker score to accept a reranked answer. |
| `reranker` | `ovos-flashrank-reranker-plugin` | An installed `opm.agents.reranker` plugin name used to reorder candidate answers, if installed. See [Agent Plugins](agent-plugins.md). |
| `ignore_skill_scores` | `true` | When a reranker is loaded, trust its order over the skills' self-scores. |
| `min_response_wait` | `1` | Seconds to wait before evaluating responses. |
| `max_response_wait` | `4` | Hard cap (seconds) on gathering responses, regardless of extensions. |
| `extension_time` | `1` | Extra seconds granted when a skill reports it is still searching. |

The reranker is optional. Without one, selection falls back to the skills'
self-reported confidences.

!!! note "Shipped defaults differ slightly"
    The bundled `mycroft.conf` ships an `intents.ovos-common-query-pipeline-plugin`
    section that overrides some of the library defaults above: `max_response_wait: 6`
    and `extension_time: 3`. Its `reranker` is `ovos-flashrank-reranker-plugin` —
    the same plugin the library falls back to when no reranker is configured at all.

---

## Performance

* Response time tracks the slowest skill you let answer; `max_response_wait` caps
  it, so very slow skills may be dropped.
* Rerankers add latency, noticeably so on constrained hardware (e.g. Raspberry
  Pi). Tune the wait times and thresholds to taste.

---

## Notes

* **Answers come from skills only** — no generation, no RAG.
* **Not chit-chat** — strictly factual question answering.
* **Skills required** — with no CommonQuery skills installed the matcher returns
  nothing immediately.
* Skills using the old CommonQuery base class still work but log a deprecation
  warning and are matched as plain `question:action`.

---

*Source code: [OpenVoiceOS/ovos-common-query-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-common-query-pipeline-plugin).*

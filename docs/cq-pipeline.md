# Common Query Pipeline

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

It registers one pipeline matcher: **`common_qa`**. Add it to your pipeline, near
the end, so high-confidence intents win first:

```json
{
  "intents": {
    "pipeline": [
      "ovos-padatious-pipeline-plugin-high",
      "ovos-adapt-pipeline-plugin-high",
      "common_qa",
      "ovos-fallback-pipeline-plugin-medium"
    ]
  }
}
```

Now install one or more CommonQuery skills (e.g. Wikipedia, Wolfram Alpha) and ask
a question.

---

## How it works

The matcher class is `CommonQAService` (a `PipelinePlugin`, so it exposes a single
`match()` — hence the one `common_qa` ID, not high/medium/low tiers).

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
      "reranker": "ovos-flashrank-reranker-plugin",
      "ovos-flashrank-reranker-plugin": {
        "model": "ms-marco-TinyBERT-L-2-v2"
      }
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
| `reranker` | `ovos-flashrank-reranker-plugin` | Multiple-choice solver plugin used to rerank (must be installed). |
| `ignore_skill_scores` | `true` | When a reranker is loaded, trust its order over the skills' self-scores. |
| `min_response_wait` | `1` | Seconds to wait before evaluating responses. |
| `max_response_wait` | `4` | Hard cap (seconds) on gathering responses, regardless of extensions. |
| `extension_time` | `1` | Extra seconds granted when a skill reports it is still searching. |

The reranker is optional. Without one, selection falls back to the skills'
self-reported confidences.

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

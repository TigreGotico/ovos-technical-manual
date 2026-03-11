# Mixture of Solvers (MoS)

`ovos-MoS` orchestrates multiple OVOS agent plugins to produce higher-quality answers through
eight composition strategies. Any `ChatEngine` (LLM, solver, or another MoS) can serve as a
worker, king, voter, or president — enabling arbitrarily deep recursive compositions.

Repository: `OpenVoiceOS Workspace/Agent Plugins/ovos-MoS`

---

## Core Concept

Instead of relying on a single model, a MoS engine:

1. Distributes the query to multiple **worker** plugins concurrently.
2. Applies a **strategy** to combine or select from the worker responses.
3. Returns a single best answer.

Because every MoS engine is itself a `ChatEngine`, it can be used as a worker inside another
MoS, enabling recursive compositions like a Democracy of Kings or a Tournament of Committees.

---

## Class Hierarchy

```
ChatEngine (ovos_plugin_manager.templates.agents)
  ├── AbstractMoSEngine
  │     ├── KingMoSEngine          — one decider selects/synthesises
  │     ├── DemocracyMoSEngine     — majority voting
  │     ├── DuopolyMoSEngine       — multi-round founder discussion
  │     ├── TournamentMoSEngine    — bracket elimination
  │     ├── JuryMoSEngine          — weighted voting
  │     └── CommitteeMoSEngine     — multi-round convergence
  ├── CascadeMoSEngine             — sequential with early stopping
  └── ChainMoSEngine               — sequential refinement pipeline
```

`AbstractMoSEngine.gather_responses` — `ovos_MoS/agents.py:31` — queries all workers in
parallel via `ThreadPoolExecutor` and returns a `List[str]` of non-empty responses.

---

## Strategies

### King

One decider selects or synthesises the final answer from worker responses.

**ReRanker king** — scores all worker answers and returns the highest-scored:

```python
from ovos_MoS.agents import KingMoSEngine

engine = KingMoSEngine(king=my_reranker, workers=[chat1, chat2, chat3])
answer = engine.get_response("What is the speed of light?")
```

**Generative king** — an LLM receives all worker answers and synthesises a new response:

```python
engine = KingMoSEngine(king=my_llm, workers=[ddg_solver, wikipedia_solver])
```

The mode is detected automatically: `isinstance(self.king, ReRankerEngine)` at
`ovos_MoS/agents.py:85`.

### Democracy

Multiple voters each pick their preferred worker answer. Majority wins. Optional president for
tie-breaking or synthesis.

```python
from ovos_MoS.agents import DemocracyMoSEngine

engine = DemocracyMoSEngine(
    voters=[reranker1, reranker2, reranker3],
    workers=[chat1, chat2]
)
```

### Duopoly

Founders engage in `discussion_rounds` of back-and-forth discussion about the worker answers,
then a president decides the final output. Best for complex, nuanced queries.

```python
from ovos_MoS.agents import DuopolyMoSEngine

engine = DuopolyMoSEngine(
    president=my_reranker,
    founders=[llm1, llm2],
    workers=[ddg, wikipedia],
    config={"discussion_rounds": 3}
)
```

Discussion flow: workers answer concurrently → founders discuss in rounds → president decides.

### Tournament

Bracket-style elimination: worker answers compete head-to-head via a referee (ReRanker) until
one champion remains. Requires only O(log N) reranker calls.

```python
from ovos_MoS.agents import TournamentMoSEngine

engine = TournamentMoSEngine(referee=my_reranker, workers=[c1, c2, c3, c4])
```

### Cascade

Sequential querying with early stopping. Workers are tried one by one (cheapest first). After
each response, a scorer evaluates all accumulated answers. If the top score exceeds `threshold`,
querying stops early.

```python
from ovos_MoS.agents import CascadeMoSEngine

engine = CascadeMoSEngine(
    scorer=my_reranker,
    workers=[cheap_cache, web_search, expensive_llm],
    config={"threshold": 0.8}
)
```

Best for cost efficiency: cache hits stop the chain before the expensive LLM is called.

### Jury

Weighted voting — like Democracy but each juror carries a numeric weight. Assign higher weights
to more accurate or expensive models.

```python
from ovos_MoS.agents import JuryMoSEngine

engine = JuryMoSEngine(
    jurors=[cheap_rr, mid_rr, expert_rr],
    juror_weights=[1.0, 2.0, 5.0],
    workers=[chat1, chat2, chat3]
)
```

### Chain

Sequential refinement pipeline. Each worker receives the previous worker's answer as context
and improves it progressively.

```python
from ovos_MoS.agents import ChainMoSEngine

engine = ChainMoSEngine(
    workers=[fast_drafter, careful_refiner, style_polisher],
    president=quality_reranker
)
```

Worker 1 receives the raw query. Workers 2+ receive a refinement prompt with the query and
the previous answer. An optional president selects the best version or synthesises from all.

### Committee

Multi-round convergence. All workers answer independently, then see each other's answers and
revise. Repeats until convergence or `max_rounds`.

```python
from ovos_MoS.agents import CommitteeMoSEngine

engine = CommitteeMoSEngine(
    workers=[llm1, llm2, llm3],
    president=my_reranker,
    config={"max_rounds": 3}
)
```

---

## Config-Driven Usage (OPM Entry Points)

Install `ovos-MoS` and configure via `mycroft.conf` or a persona JSON using the factory entry
points registered under `opm.agents.chat`:

| Entry point | Strategy |
|---|---|
| `ovos-mos-king-reranker` | King with ReRanker |
| `ovos-mos-king-generative` | King with ChatEngine |
| `ovos-mos-democracy` | Democracy |
| `ovos-mos-duopoly-reranker` | Duopoly with ReRanker president |
| `ovos-mos-duopoly-generative` | Duopoly with generative president |
| `ovos-mos-tournament` | Tournament bracket |
| `ovos-mos-cascade` | Cascade with early stopping |
| `ovos-mos-jury` | Weighted jury |
| `ovos-mos-chain` | Sequential chain |
| `ovos-mos-committee` | Multi-round committee |

### King (ReRanker) persona example

```json
{
  "name": "My MoS Persona",
  "handlers": ["ovos-mos-king-reranker"],
  "ovos-mos-king-reranker": {
    "king": {
      "module": "ovos-reranker-claude-plugin",
      "api_key": "sk-ant-..."
    },
    "workers": [
      {"module": "ovos-solver-plugin-ddg"},
      {"module": "ovos-solver-plugin-wikipedia"}
    ],
    "max_workers": 4,
    "worker_timeout": 30
  }
}
```

### Cascade persona example

```json
{
  "name": "Cost-Efficient Assistant",
  "handlers": ["ovos-mos-cascade"],
  "ovos-mos-cascade": {
    "scorer": {"module": "ovos-reranker-claude-plugin", "api_key": "sk-ant-..."},
    "workers": [
      {"module": "ovos-solver-plugin-cache"},
      {"module": "ovos-solver-plugin-ddg"},
      {"module": "ovos-chat-openai-plugin", "key": "sk-...", "model": "gpt-4"}
    ],
    "threshold": 0.8
  }
}
```

### Committee with mixed LLMs

```json
{
  "handlers": ["ovos-mos-committee"],
  "ovos-mos-committee": {
    "workers": [
      {"module": "ovos-chat-openai-plugin", "model": "gpt-4"},
      {"module": "ovos-chat-claude-plugin", "api_key": "sk-ant-...", "model": "claude-opus-4-6"},
      {"module": "ovos-chat-gemini-plugin", "model": "gemini-pro"}
    ],
    "president": {
      "module": "ovos-reranker-cross-encoder-plugin",
      "type": "reranker"
    },
    "max_rounds": 3
  }
}
```

---

## Common Config Keys

| Key | Default | Description |
|---|---|---|
| `max_workers` | `len(workers)` | Max concurrent threads for worker querying |
| `worker_timeout` | `30.0` | Timeout in seconds per worker |
| `discussion_rounds` | `3` | Duopoly: number of founder discussion rounds |
| `threshold` | `0.8` | Cascade: score threshold for early stopping |
| `max_rounds` | `3` | Committee: maximum revision rounds |
| `juror_weights` | `[1.0, ...]` | Jury: weight per juror |
| `system_prompt` | built-in | Custom system prompt for final answer |

---

## Recursive Composition

Every MoS engine is a `ChatEngine`, so they can be nested:

```python
# Democracy of Kings
king1 = KingMoSEngine(king=reranker1, workers=[chat1, chat2])
king2 = KingMoSEngine(king=reranker2, workers=[chat3, chat4])
democracy = DemocracyMoSEngine(voters=[voter1, voter2], workers=[king1, king2])
```

Convenience helpers in `ovos_MoS.compose` build common compositions:
`democracy_of_kings`, `cascade_then_committee`, `chain_with_jury`,
`tournament_of_committees`, `duopoly_with_cascade_workers`.

**Self-loading guard:** The factory prevents any `ovos-mos-*` entry point from being loaded as
a sub-plugin of another MoS engine, blocking infinite recursion —
`_MOS_ENTRY_POINTS` — `ovos_MoS/factory.py:17`.

---

## Concurrency

`gather_concurrent` — `ovos_MoS/_concurrent.py:8` — uses `ThreadPoolExecutor`. Workers are
I/O-bound (API/network calls), making threads appropriate. Individual worker failures are caught
and logged; they do not propagate. If all workers fail, an empty list is returned.

An asyncio alternative (`gather_async` — `ovos_MoS/_async.py:18`) is available for natively
async applications.

---

## Streaming

MoS engines with generative kings or presidents support sentence-level streaming (TTS-ready):

```python
for sentence in engine.stream_sentences(messages):
    tts.speak(sentence)
```

Streaming support by strategy:

| Strategy | Generative streaming |
|---|---|
| King (generative) | Delegates to king |
| Duopoly (generative president) | Delegates to president |
| Chain (generative president) | Delegates to president |
| Others | Base class fallback |

---

## Observability

`MoSMetrics` — `ovos_MoS/metrics.py:70` — provides thread-safe timing and success rate tracking:

```python
from ovos_MoS.metrics import MoSMetrics

metrics = MoSMetrics()
with metrics.track_strategy("KingMoS"):
    with metrics.track_worker("KingMoS", "ddg"):
        answer = ddg.get_response(query)

print(metrics.report_text())
```

Use metrics to tune `max_workers`, `worker_timeout`, `threshold`, and `juror_weights` for your
specific workload.

---

## Cross-References

- [Agent Engine Types](154-agent-plugins.md) — base classes and configuration reference
- [Personas](150-personas.md) — how to use a MoS engine inside a persona
- [Claude Plugin](157-claude-plugin.md) — Claude ReRanker, Chat, and Memory engines
- [OpenAI Plugin](158-openai-plugin.md) — OpenAI-compatible Chat and Summarizer engines
- [GGUF Plugin](159-gguf-plugin.md) — local GGUF engines for offline MoS setups

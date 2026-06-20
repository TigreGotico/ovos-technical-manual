# Mixture of Solvers (MoS)

`ovos-MoS` combines several OVOS [solver plugins](advanced-solvers.md) into one, querying multiple
**worker** solvers and then using a decider to pick or synthesise the final answer. Because every
MoS class is itself a `QuestionSolver`, a whole MoS can be dropped in wherever a single solver is
expected — including as a worker inside another MoS (a "Democracy of Kings", a "Duopoly of
Democracies", and so on).

Repository: [`TigreGotico/ovos_MoS`](https://github.com/TigreGotico/ovos_MoS)

---

## Core Concept

Instead of trusting a single solver, a MoS:

1. Queries every **worker** solver and gathers their non-empty spoken answers.
2. Applies a **strategy** (King / Democracy / Duopoly) to select or synthesise one answer.
3. Returns that single answer via `get_spoken_answer`.

There are three strategy families, each available in a ReRanker-driven and a generative (LLM)
variant.

---

## Class Hierarchy

Everything lives in a single module, `ovos_MoS` (`ovos_MoS/__init__.py`). All classes subclass
`QuestionSolver` from `ovos_plugin_manager.templates.solvers`.

```
QuestionSolver (ovos_plugin_manager.templates.solvers)
  └── AbstractMoS                       — gathers worker answers
        ├── AbstractKingMoS             — one "king" decider
        │     ├── ReRankerKingMoS       — king is a reranker, picks top answer
        │     └── GenerativeKingMoS     — king is an LLM, synthesises an answer
        ├── AbstractDuopolyMoS          — founders discuss, a president decides
        │     ├── ReRankerDuopolyMoS    — president is a reranker
        │     └── GenerativeDuopolyMoS  — president is an LLM
        └── DemocracyMoS                — voters vote, majority wins
              ├── ReRankerDemocracyMoS  — president reranks the voted shortlist
              └── GenerativeDemocracyMoS— president synthesises from the shortlist
```

`AbstractMoS.gather_responses(query, lang, units)` calls `get_spoken_answer` on each worker **in
sequence** and returns a `List[str]` of non-empty answers. A worker that raises is logged and
skipped; if no worker answers, the strategy returns
`"No answer could be gathered from workers."`.

> The "king", "voter", and "president" deciders are reranker solvers
> (`MultipleChoiceSolver`, exposing `rerank` / `select_answer`) in the ReRanker variants, and
> generative `QuestionSolver`s (LLMs) in the generative variants.

---

## Strategies

### King

One decider chooses or synthesises the final answer from the worker answers.

**ReRanker king** — `ReRankerKingMoS` reranks the worker answers and returns the top one:

```python
from ovos_MoS import ReRankerKingMoS

workers = [QuestionSolver1(), QuestionSolver2(), QuestionSolver3()]
mos = ReRankerKingMoS(king=my_reranker, workers=workers)
answer = mos.spoken_answer("What is the speed of light?")
```

**Generative king** — `GenerativeKingMoS` feeds all worker answers into an LLM, which writes a
new response:

```python
from ovos_MoS import GenerativeKingMoS
from ovos_gguf_solver import GGUFSolver

king = GGUFSolver({"model": "RichardErkhov/GritLM_-_GritLM-7B-gguf",
                   "remote_filename": "*Q4_K_M.gguf", "n_gpu_layers": -1})
mos = GenerativeKingMoS(king=king, workers=[ddg_solver, wikipedia_solver])
```

### Democracy

Each **voter** (a reranker) selects its preferred worker answer; the answer with the most votes
wins (`DemocracyMoS`). The `ReRanker`/`Generative` subclasses add a **president** that, instead of
a raw majority, reranks (`ReRankerDemocracyMoS`) or synthesises from (`GenerativeDemocracyMoS`) the
deduplicated set of voted answers.

```python
from ovos_MoS import DemocracyMoS

mos = DemocracyMoS(voters=[reranker1, reranker2, reranker3],
                   workers=[chat1, chat2])
```

### Duopoly

`founders` (LLM `QuestionSolver`s) discuss the worker answers over `discussion_rounds` passes,
each founder appending to a running discussion; a **president** then produces the final output —
by reranking (`ReRankerDuopolyMoS`) or by generating from the discussion
(`GenerativeDuopolyMoS`). Best for complex, nuanced queries.

```python
from ovos_MoS import GenerativeDuopolyMoS

mos = GenerativeDuopolyMoS(
    president=my_llm,
    founders=[llm1, llm2],
    workers=[ddg, wikipedia],        # defaults to `founders` if omitted
    config={"discussion_rounds": 3},
)
```

Flow: workers answer → founders discuss in rounds → president decides.

---

## Constructor Contract

| Class | First positional | Other required |
|---|---|---|
| `ReRankerKingMoS` / `GenerativeKingMoS` | `king` | `workers` |
| `DemocracyMoS` | `voters` | `workers` |
| `ReRankerDemocracyMoS` / `GenerativeDemocracyMoS` | `president` | `voters`, `workers` |
| `ReRankerDuopolyMoS` / `GenerativeDuopolyMoS` | `president` | `founders` (`workers` optional, defaults to `founders`) |

All classes also accept the standard `QuestionSolver` keyword arguments: `config`, `translator`,
`detector`, `priority`, `enable_tx`, `enable_cache`, `internal_lang`.

The public answer method is `get_spoken_answer(query, lang=None, units=None)` (overridden per
strategy); call it via the inherited `spoken_answer(...)` wrapper, as in the examples above.

---

## Config Keys

`config` is the standard solver config dict. The keys MoS itself reads:

| Key | Used by | Default | Description |
|---|---|---|---|
| `discussion_rounds` | Duopoly | `3` | Number of founder discussion passes |
| `discuss_prompt` | Duopoly | built-in | Instruction given to founders while discussing |
| `system_prompt` | Generative King/Duopoly/Democracy | built-in | Instruction for the final-answer generation |
| `prompt_template` | Generative variants | built-in | Format string assembling `{system}`, `{query}`, `{ans}`, and (Duopoly) `{discussion}` |

There are no `max_workers`, `worker_timeout`, `threshold`, `max_rounds`, or `juror_weights` keys —
workers are queried serially and every strategy runs to completion.

---

## Recursive Composition

Because each MoS is a `QuestionSolver`, nest them by passing one MoS as a worker (or king / voter /
president) of another:

```python
from ovos_MoS import ReRankerKingMoS, DemocracyMoS

# Democracy of Kings
king1 = ReRankerKingMoS(king=reranker1, workers=[chat1, chat2])
king2 = ReRankerKingMoS(king=reranker2, workers=[chat3, chat4])
democracy = DemocracyMoS(voters=[voter1, voter2], workers=[king1, king2])
```

---

## Gotcha

`ovos-MoS` is a library of solver classes; it registers **no plugin entry points**. You construct
the MoS strategy directly in Python and pass already-instantiated solvers — there is no
`opm.solver.*` / `opm.agents.*` entry point or `mycroft.conf` factory string for it. Workers must
be `QuestionSolver` instances; the king/voters/president must be reranker
(`MultipleChoiceSolver`) instances for the ReRanker variants and generative `QuestionSolver`s for
the generative ones.

---

## Cross-References

- [Solver Plugins](advanced-solvers.md) — the `QuestionSolver` / `MultipleChoiceSolver` base classes MoS builds on
- [Personas](personas.md) — how solvers are wired into a persona
- [OpenAI Plugin](openai-plugin.md) — OpenAI-compatible solvers usable as workers or kings
- [GGUF Plugin](gguf-plugin.md) — local GGUF solvers for offline MoS setups

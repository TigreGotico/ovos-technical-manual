# Specialized [Agent Engine](agent-plugins.md) Types

!!! abstract "In a nutshell"
    Beyond plain chatting, OVOS offers a toolbox of small, specialized AI helpers — each good at one narrow job, like ranking which answer is most relevant, summarizing text, or detecting a language. Because each is a separate, swappable piece, you can mix and match them to build more capable assistants. See [Agent Plugins](agent-plugins.md) for the broader idea and the [Glossary](glossary.md) for unfamiliar terms.

OVOS provides a full suite of specialized agent engine types beyond simple chat. Each type solves
a specific NLP sub-problem and registers under its own OPM entry point group, making it
independently discoverable, configurable, and composable.

All base classes live in `ovos_plugin_manager.templates.agents`. The deprecated solver API
(`opm.solver.*`) is covered at the bottom — migrate to `opm.agents.*` for all new plugins.

---

## ReRanker — `opm.agents.reranker`

**Base class:** `ReRankerEngine`

Scores a list of candidate answers by relevance to a query and returns them ranked highest-first.
Used internally by the [Common Query pipeline](cq-pipeline.md) and
[OCP](ocp-pipeline.md) media search.

```python
from ovos_plugin_manager.templates.agents import ReRankerEngine

# Returns: List[Tuple[float, str]] sorted descending
ranked = engine.rerank("play bohemian rhapsody", ["Bohemian Rhapsody by Queen", "Bohemian Groove Mix"])
best = engine.select_answer("play bohemian rhapsody", candidates)

```

### Common Query pipeline config

```json
{
  "intents": {
    "common_query": {
      "min_self_confidence": 0.5,
      "min_reranker_score": 0.5,
      "reranker": "<your-reranker-plugin>",
      "<your-reranker-plugin>": {}
    }
  }
}

```

The `reranker` key names any installed `opm.agents.reranker` plugin — see
[Agent Plugins](agent-plugins.md) for the engine-type reference.

---

## Extractive QA — `opm.agents.extractive_qa`

**Base class:** `ExtractiveQAEngine`

Given a paragraph of evidence text and a question, returns the exact sentence(s) that answer
the question. Used by knowledge-retrieval skills (Wikipedia, news reader) to avoid speaking
entire documents.

```python
evidence = (
    "The Eiffel Tower stands 330 metres tall. "
    "It was constructed from 1887 to 1889 as the centrepiece of the 1889 World's Fair."
)
answer = engine.get_best_passage(evidence, "How tall is the Eiffel Tower?")

# "The Eiffel Tower stands 330 metres tall."

```

Available implementations: `GGUFExtractiveQAEngine` ([GGUF plugin](gguf-plugin.md)).

---

## Summarizer — `opm.agents.summarizer`

**Base class:** `SummarizerEngine`

Condenses a plain-text document into 1–3 sentences. Used by solvers and skills before passing
text to [TTS](tts-plugins.md) to avoid overwhelming the user with long responses.

```python
summary = engine.summarize(long_article_text)

```

Implementations: `OpenAISummarizer`, `GGUFSummarizerEngine`.

---

## Chat Summarizer — `opm.agents.summarizer.chat`

Converts a structured `List[AgentMessage]` chat history into a concise narrative summary. Used
internally by memory plugins (`GGUFContextManager`) to compress history
when it exceeds `max_history` turns, keeping the context window manageable.

```python
from ovos_plugin_manager.templates.agents import AgentMessage, MessageRole

messages = [
    AgentMessage(MessageRole.USER, "What's the weather?"),
    AgentMessage(MessageRole.ASSISTANT, "It's sunny and 22°C."),
]
summary_text = engine.summarize(messages)

```

Implementations: `GGUFChatSummarizerEngine`.

---

## NLI — `opm.agents.nli`

**Base class:** `NaturalLanguageInferenceEngine`

Predicts whether a *premise* logically entails a *hypothesis*. Used for reasoning chains, intent
conflict detection, and condition evaluation in skills.

```python
print(engine.predict_entailment("It is raining heavily.", "The weather is wet."))  # True
print(engine.predict_entailment("It is sunny.", "You need an umbrella."))           # False

```

Implementations: `GGUFNLIEngine`.

---

## Yes/No Classifier — `opm.agents.yesno`

Classifies a user's ambiguous confirmation as `True` (yes), `False` (no), or `None` (unclear).
Returns `None` on API error.

```python
print(engine.yes_or_no("Do you want me to set a timer?", "sure, go ahead"))  # True
print(engine.yes_or_no("Shall I call John?", "no, not now"))                  # False
print(engine.yes_or_no("Ready?", "what do you mean?"))                        # None

```

Use this in skills when `ask_yesno()` receives uncertain phrasing like "I guess" or "maybe".

Implementations: `GGUFYesNoEngine`.

---

## Option Matcher — `opm.agents.option_matcher`

**Base class:** `OptionMatcherEngine`

Resolves a free-form user reply to one entry in a fixed list of options — the engine behind a
skill's `ask_selection()`. The reference implementation,
[`ovos-option-matcher-fuzzy-plugin`](https://github.com/OpenVoiceOS/ovos-option-matcher-fuzzy-plugin)
(`FuzzyOptionMatcherPlugin`), resolves in order: fuzzy match (rapidfuzz `WRatio`) when the score
reaches `min_conf` (config key, default `0.65`), then locale-aware "last option" vocab, then
ordinal/cardinal vocab (longest match wins), then a numeric fallback via `ovos-number-parser`,
returning `None` if nothing matches.

`OVOSSkill.ask_selection()` loads the engine via `skills.ask_selection_plugin` (checked in the
skill's `settings.json` first, then `mycroft.conf`), defaulting to
`ovos-option-matcher-fuzzy-plugin` when neither is set.

---

## Coreference Resolution — `opm.agents.coref`

**Base class:** `CoreferenceEngine`

Resolves pronouns and ambiguous references in voice commands against recent conversation context.
The base class owns the *state* (a per-language context vault); the plugin subclass provides the
*intelligence* (the NLP that rewrites the text). `resolve()` first calls `contains_corefs()` to
skip expensive work when no pronouns are present.

```python

# Stateless one-shot resolution:
result = engine.resolve("Turn it off", lang="en")

# With memory: register context, then resolve future turns against it
engine.set_context("it", "Bohemian Rhapsody", lang="en")
result = engine.resolve("Turn it off", lang="en", use_memory=True)

# "Turn Bohemian Rhapsody off"

```

`use_memory` (default `False`) gates the learn/apply-context steps — pass `use_memory=True` to
have `resolve()` apply previously registered context and learn new mappings from each turn.
`context_ttl` (config key, default `120` s) controls how long a tracked context entry remains
valid before it is pruned.

Implementations: `GGUFCoreferenceEngine`.

---

## Memory / Context Manager — `opm.agents.memory`

**Base class:** `AgentContextManager`

Manages per-session conversation history. The default implementation (`BasicShortTermMemory`
from `ovos-persona`) stores history in RAM with `max_history` truncation. LLM-powered
implementations (`GGUFContextManager`) also compress old history into a SYSTEM summary message
when the history exceeds a configurable threshold.

```python
from ovos_plugin_manager.templates.agents import AgentContextManager, AgentMessage

# Abstract interface
ctx = manager.build_conversation_context(utterance, session_id)  # List[AgentMessage]
manager.update_history([user_msg, assistant_msg], session_id)

```

Compression config (`GGUFContextManager`):

```json
{
  "<your-memory-plugin>": {
    "system_prompt": "You are a helpful assistant.",
    "max_history": 20,
    "compress": true
  }
}

```

The default no-LLM memory plugin `ovos-agents-short-term-memory-plugin` (`BasicShortTermMemory`)
needs no API key and is always available when `ovos-persona` is installed.

---

## Multimodal Chat — `opm.agents.chat.multimodal`

Extends `ChatEngine` with image input. Images are passed as base64-encoded strings in
`MultimodalAgentMessage.image_content`. Data-URI headers are stripped automatically.

```python
from ovos_plugin_manager.templates.agents import MultimodalAgentMessage, MessageRole

messages = [
    MultimodalAgentMessage(
        role=MessageRole.USER,
        content="What is in this image?",
        image_content=[b64_string],
    )
]
reply = engine.continue_chat(messages)

```

Provided by any installed `opm.agents.chat.multimodal` plugin.

---

## Deprecated [Solver](agent-plugins.md) Types

The legacy `opm.solver.*` entry points are deprecated and will be removed in the next major
release. Migrate existing plugins to the corresponding `opm.agents.*` types.

| Deprecated entry point | Replacement | Why |
|---|---|---|
| `opm.solver.question` (`QuestionSolver`) | `opm.agents.chat` (`ChatEngine`) | Single-turn Q&A folds into the general chat contract; no need for a separate type. |
| `opm.solver.chat` (`ChatMessageSolver`) | `opm.agents.chat` (`ChatEngine`) | Same engine type as above — the two deprecated solvers converge on one replacement. |
| `opm.solver.summarization` (`TldrSolver`) | `opm.agents.summarizer` (`SummarizerEngine`) | Renamed for clarity; behavior is otherwise equivalent. |
| `opm.solver.reading_comprehension` (`EvidenceSolver`) | `opm.agents.extractive_qa` (`ExtractiveQAEngine`) | Renamed to match the standard NLP task name (extractive QA over evidence). |
| `opm.solver.multiple_choice` (`MultipleChoiceSolver`) | `opm.agents.reranker` (`ReRankerEngine`) | Choosing among options is really scoring/ranking candidates, so it moved under the reranker contract. |
| `opm.solver.entailment` (`EntailmentSolver`) | `opm.agents.nli` (`NaturalLanguageInferenceEngine`) | Renamed to the standard NLI task name; entailment is one of NLI's three labels. |
| `opm.coreference` | `opm.agents.coref` | Moved under the unified `opm.agents.*` namespace alongside the other engine types. |

The deprecated classes remain in `ovos_plugin_manager.templates.solvers` and are still loaded
by `PersonaService` and `QuestionSolversService` for backwards compatibility — but no new
plugins should use them.

---

## Cross-References

- [Agent Plugins](agent-plugins.md) — complete engine configuration reference


- [OpenAI Plugin](openai-plugin.md) — OpenAI-compatible engine implementations


- [GGUF Plugin](gguf-plugin.md) — local offline engine implementations


- [OPM Plugin Types](plugin-manager.md) — full solver plugin reference

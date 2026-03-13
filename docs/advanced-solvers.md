# Specialized [Agent Engine](agent-plugins.md) Types

OVOS provides a full suite of specialized agent engine types beyond simple chat. Each type solves
a specific NLP sub-problem and registers under its own OPM entry point group, making it
independently discoverable, configurable, and composable.

All base classes live in `ovos_plugin_manager.templates.agents`. The deprecated solver API
(`opm.solver.*`) is covered at the bottom — migrate to `opm.agents.*` for all new plugins.

---

## ReRanker — `opm.agents.reranker`

**Base class:** `ReRankerEngine`

Scores a list of candidate answers by relevance to a query and returns them ranked highest-first.
Used internally by the [Common Query pipeline](https://openvoiceos.github.io/ovos-technical-manual/360-solver_plugins/),
[OCP](ocp-pipeline.md) media search, and by [Mixture of Solvers](mos-plugin.md) strategies as the judge/king/referee.

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
      "reranker": "ovos-reranker-claude-plugin",
      "ovos-reranker-claude-plugin": {
        "api_key": "sk-ant-...",
        "model": "claude-haiku-4-5-20251001"
      }
    }
  }
}

```

Available implementations: `ClaudeReRankerEngine` ([Claude plugin](claude-plugin.md)),
`GGUFReRankerEngine` ([GGUF plugin](gguf-plugin.md)), `ovos-flashrank-reranker-plugin`
(local transformer-based, no API key required).

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

Available implementations: `ClaudeExtractiveQAEngine` ([Claude plugin](claude-plugin.md)),
`GGUFExtractiveQAEngine` ([GGUF plugin](gguf-plugin.md)).

---

## Summarizer — `opm.agents.summarizer`

**Base class:** `SummarizerEngine`

Condenses a plain-text document into 1–3 sentences. Used by solvers and skills before passing
text to [TTS](tts-plugins.md) to avoid overwhelming the user with long responses.

```python
summary = engine.summarize(long_article_text)

```

Implementations: `ClaudeSummarizerEngine`, `OpenAISummarizer`, `GGUFSummarizerEngine`.

---

## Chat Summarizer — `opm.agents.summarizer.chat`

Converts a structured `List[AgentMessage]` chat history into a concise narrative summary. Used
internally by memory plugins (`ClaudeContextManager`, `GGUFContextManager`) to compress history
when it exceeds `max_history` turns, keeping the context window manageable.

```python
from ovos_plugin_manager.templates.agents import AgentMessage, MessageRole

messages = [
    AgentMessage(MessageRole.USER, "What's the weather?"),
    AgentMessage(MessageRole.ASSISTANT, "It's sunny and 22°C."),
]
summary_text = engine.summarize(messages)

```

Implementations: `ClaudeChatSummarizerEngine`, `GGUFChatSummarizerEngine`.

---

## NLI — `opm.agents.nli`

**Base class:** `NaturalLanguageInferenceEngine`

Predicts whether a *premise* logically entails a *hypothesis*. Used for reasoning chains, intent
conflict detection, and condition evaluation in skills.

```python
print(engine.predict_entailment("It is raining heavily.", "The weather is wet."))  # True
print(engine.predict_entailment("It is sunny.", "You need an umbrella."))           # False

```

Implementations: `ClaudeNLIEngine`, `GGUFNLIEngine`.

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

Implementations: `ClaudeYesNoEngine`, `GGUFYesNoEngine`.

---

## Coreference Resolution — `opm.agents.coref`

Resolves pronouns and ambiguous references in voice commands against recent conversation context.
Avoids redundant API calls by first checking a per-language pronoun wordlist.

```python

# After "Play Bohemian Rhapsody":
result = engine.resolve("Turn it off", lang="en")

# "Turn Bohemian Rhapsody off"

```

`context_ttl` (default 120 s) controls how long a tracked context entry remains valid —
`ovos_claude.coref:ClaudeCoreferenceEngine.__init__`.

Implementations: `ClaudeCoreferenceEngine`, `GGUFCoreferenceEngine`.

---

## Memory / Context Manager — `opm.agents.memory`

**Base class:** `AgentContextManager`

Manages per-session conversation history. The default implementation (`BasicShortTermMemory`
from `ovos-persona`) stores history in RAM with `max_history` truncation. LLM-powered
implementations (`ClaudeContextManager`, `GGUFContextManager`) also compress old history into
a SYSTEM summary message when the history exceeds a configurable threshold.

```python
from ovos_plugin_manager.templates.agents import AgentContextManager, AgentMessage

# Abstract interface
ctx = manager.build_conversation_context(utterance, session_id)  # List[AgentMessage]
manager.update_history([user_msg, assistant_msg], session_id)

```

Compression config (`ClaudeContextManager`):

```json
{
  "ovos-memory-claude-plugin": {
    "api_key": "sk-ant-...",
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

Implementation: `ClaudeMultimodalChatEngine`.

---

## Deprecated [Solver](agent-plugins.md) Types

The legacy `opm.solver.*` entry points are deprecated and will be removed in the next major
release. Migrate existing plugins to the corresponding `opm.agents.*` types.

| Deprecated entry point | Replacement |
|---|---|
| `opm.solver.question` (`QuestionSolver`) | `opm.agents.chat` (`ChatEngine`) |
| `opm.solver.chat` (`ChatMessageSolver`) | `opm.agents.chat` (`ChatEngine`) |
| `opm.solver.summarization` (`TldrSolver`) | `opm.agents.summarizer` (`SummarizerEngine`) |
| `opm.solver.reading_comprehension` (`EvidenceSolver`) | `opm.agents.extractive_qa` (`ExtractiveQAEngine`) |
| `opm.solver.multiple_choice` (`MultipleChoiceSolver`) | `opm.agents.reranker` (`ReRankerEngine`) |
| `opm.solver.entailment` (`EntailmentSolver`) | `opm.agents.nli` (`NaturalLanguageInferenceEngine`) |
| `opm.coreference` | `opm.agents.coref` |

The deprecated classes remain in `ovos_plugin_manager.templates.solvers` and are still loaded
by `PersonaService` and `QuestionSolversService` for backwards compatibility — but no new
plugins should use them.

---

## Cross-References

- [Agent Plugins](agent-plugins.md) — complete engine configuration reference


- [Mixture of Solvers](mos-plugin.md) — compose multiple engines for higher accuracy


- [Claude Plugin](claude-plugin.md) — all ten Claude-backed engine implementations


- [OpenAI Plugin](openai-plugin.md) — OpenAI-compatible engine implementations


- [GGUF Plugin](gguf-plugin.md) — local offline engine implementations


- [OPM Plugin Types](https://openvoiceos.github.io/ovos-technical-manual/360-solver_plugins/) — full solver plugin reference

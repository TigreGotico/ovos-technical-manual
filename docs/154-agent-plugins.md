# OPM Agent Engine Types — Complete Reference

OVOS uses OPM (ovos-plugin-manager) to discover and load AI agent backends at runtime. Each
engine type is registered under a dedicated entry point group. Plugins are independent: a single
package (e.g. `ovos-claude-plugin`) can provide implementations for several groups simultaneously.

This page documents every `opm.agents.*` engine type, its contract, and config examples from
the three main backend families: **Claude** (Anthropic API), **OpenAI** (OpenAI-compatible API),
and **GGUF** (local model via `llama-cpp-python`).

---

## Common Base: `AbstractSolver` / `AbstractAgentEngine`

All agent engines ultimately derive from `AbstractSolver`
(`ovos_plugin_manager.thirdparty.solvers.AbstractSolver`).

Constructor parameters shared by all engines:

| Parameter | Description |
|---|---|
| `config` | Plugin-specific config dict |
| `priority` | Solver priority (lower = higher priority). Default 50. |
| `enable_tx` | Auto-translate inputs/outputs for language support |
| `enable_cache` | Cache results on disk via `JsonStorageXDG` |
| `internal_lang` | Internal language (BCP-47) for auto-translation |

---

## Chat Engine — `opm.agents.chat`

**Base class:** `ChatEngine`

Multi-turn conversational LLM. The core engine type used by [personas](150-personas.md).

### Key methods

| Method | Description |
|---|---|
| `continue_chat(messages, session_id, lang, units) → AgentMessage` | Single blocking response |
| `stream_tokens(messages, ...) → Iterable[str]` | Raw token stream (not suitable for direct TTS) |
| `stream_sentences(messages, ...) → Iterable[str]` | Sentence-buffered stream, TTS-ready |
| `get_response(utterance, ...) → str` | Convenience single-turn wrapper |

### Claude — `ovos-chat-claude-plugin`

```json
{
  "ovos-chat-claude-plugin": {
    "api_key": "sk-ant-...",
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 200,
    "temperature": 0.7,
    "system_prompt": "You are a helpful voice assistant. Be concise.",
    "allow_system_prompts": false
  }
}
```

Available models: `claude-haiku-4-5-20251001` (fastest/cheapest), `claude-sonnet-4-6` (general
purpose), `claude-opus-4-6` (most capable).

### OpenAI — `ovos-chat-openai-plugin`

Works with any OpenAI-compatible endpoint including Ollama, llama.cpp, and
`ovos-persona-server`:

```json
{
  "ovos-chat-openai-plugin": {
    "api_url": "https://api.openai.com/v1",
    "key": "sk-...",
    "model": "gpt-4o-mini",
    "max_tokens": 150,
    "temperature": 0.5,
    "system_prompt": "You are a concise assistant."
  }
}
```

Local Ollama example:

```json
{
  "ovos-chat-openai-plugin": {
    "api_url": "http://localhost:11434/v1",
    "key": "sk-nokey",
    "model": "llama3.1:8b",
    "system_prompt": "You are a helpful assistant."
  }
}
```

### GGUF — `ovos-gguf-plugin` (chat)

```json
{
  "ovos-gguf-chat-plugin": {
    "model": "microsoft/Phi-3-mini-4k-instruct-gguf",
    "remote_filename": "*Q4_K_M.gguf",
    "n_gpu_layers": 0,
    "system_prompt": "You are a helpful assistant."
  }
}
```

Set `"model"` to an absolute `.gguf` file path for fully offline use.

---

## Multimodal Chat — `opm.agents.chat.multimodal`

Extends `ChatEngine` with image support. Images are passed as base64 strings in
`MultimodalAgentMessage.image_content`.

### Claude — `ovos-chat-multimodal-claude-plugin`

```json
{
  "ovos-chat-multimodal-claude-plugin": {
    "api_key": "sk-ant-...",
    "model": "claude-sonnet-4-6"
  }
}
```

---

## Summarizer — `opm.agents.summarizer`

**Base class:** `SummarizerEngine`

Condenses a plain-text document into 1–3 sentences.

### Claude — `ovos-summarizer-claude-plugin`

```json
{
  "ovos-summarizer-claude-plugin": {
    "api_key": "sk-ant-...",
    "model": "claude-haiku-4-5-20251001",
    "prompt_template": "Summarize the following text in 1-3 sentences.\n\n{content}"
  }
}
```

### OpenAI — `ovos-summarizer-openai-plugin`

```json
{
  "ovos-summarizer-openai-plugin": {
    "api_url": "https://api.openai.com/v1",
    "key": "sk-...",
    "model": "gpt-4o-mini",
    "system_prompt": "Your task is to summarize text in a couple paragraphs."
  }
}
```

### GGUF — `ovos-gguf-summarizer-plugin`

```json
{
  "ovos-gguf-summarizer-plugin": {
    "model": "/path/to/model.gguf"
  }
}
```

---

## Chat Summarizer — `opm.agents.summarizer.chat`

Converts a structured `List[AgentMessage]` chat history into a concise narrative summary.
Used internally by memory plugins for history compression.

```json
{
  "ovos-chat-summarizer-claude-plugin": {
    "api_key": "sk-ant-...",
    "model": "claude-haiku-4-5-20251001"
  }
}
```

---

## ReRanker — `opm.agents.reranker`

**Base class:** `ReRankerEngine`

Scores candidate answers 0.0–1.0 and returns them sorted descending. Used by the Common Query
pipeline, OCP media search, and [Mixture of Solvers](155-mos-plugin.md) as judge/king/referee.

| Method | Description |
|---|---|
| `rerank(query, options) → List[Tuple[float, str]]` | Score and sort all candidates |
| `select_answer(query, options) → str` | Return the top-scored candidate |

### Claude — `ovos-reranker-claude-plugin`

```json
{
  "ovos-reranker-claude-plugin": {
    "api_key": "sk-ant-...",
    "model": "claude-haiku-4-5-20251001"
  }
}
```

### GGUF — `ovos-gguf-reranker-plugin`

```json
{
  "ovos-gguf-reranker-plugin": {
    "model": "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
    "remote_filename": "*Q4_K_M.gguf"
  }
}
```

Local (non-LLM) alternative: `ovos-flashrank-reranker-plugin` uses a small cross-encoder
transformer model — no API key, runs entirely on CPU.

---

## Extractive QA — `opm.agents.extractive_qa`

**Base class:** `ExtractiveQAEngine`

Given evidence text and a question, returns the exact passage that answers it.

| Method | Description |
|---|---|
| `get_best_passage(evidence, question) → str` | Extract the answering passage |

### Claude — `ovos-extractive-qa-claude-plugin`

```json
{
  "ovos-extractive-qa-claude-plugin": {
    "api_key": "sk-ant-..."
  }
}
```

---

## NLI — `opm.agents.nli`

**Base class:** `NaturalLanguageInferenceEngine`

Predicts whether a premise entails a hypothesis.

| Method | Description |
|---|---|
| `predict_entailment(premise, hypothesis) → bool` | Returns `True` if premise entails hypothesis |

### Claude — `ovos-nli-claude-plugin`

```json
{
  "ovos-nli-claude-plugin": {
    "api_key": "sk-ant-..."
  }
}
```

---

## Yes/No Classifier — `opm.agents.yesno`

Classifies an ambiguous user confirmation as `True` / `False` / `None`.

| Method | Description |
|---|---|
| `yes_or_no(question, answer) → Optional[bool]` | Classify the answer |

### Claude — `ovos-yesno-claude-plugin`

```json
{
  "ovos-yesno-claude-plugin": {
    "api_key": "sk-ant-..."
  }
}
```

---

## Coreference Resolution — `opm.agents.coref`

Resolves pronouns and ambiguous references against recent conversation context.

| Method | Description |
|---|---|
| `resolve(utterance, lang) → str` | Return utterance with references resolved |
| `contains_corefs(utterance, lang) → bool` | Fast check — avoids API call if no pronouns |

### Claude — `ovos-coref-claude-plugin`

```json
{
  "ovos-coref-claude-plugin": {
    "api_key": "sk-ant-...",
    "context_ttl": 120
  }
}
```

---

## Memory / Context Manager — `opm.agents.memory`

**Base class:** `AgentContextManager`

Manages per-session conversation history.

| Method | Description |
|---|---|
| `build_conversation_context(utterance, session_id) → List[AgentMessage]` | Build context for the next LLM call |
| `update_history(messages, session_id)` | Append new messages to history |

### `ovos-agents-short-term-memory-plugin` (default, no LLM)

Built into `ovos-persona`. Stores history in RAM; no API key needed.

```json
{
  "memory_module": "ovos-agents-short-term-memory-plugin"
}
```

### Claude — `ovos-memory-claude-plugin`

Compresses history exceeding `max_history` turns into a SYSTEM summary:

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

### GGUF — `ovos-gguf-memory-plugin`

```json
{
  "ovos-gguf-memory-plugin": {
    "model": "/path/to/model.gguf",
    "system_prompt": "You are a helpful assistant.",
    "max_history": 10,
    "compress": true
  }
}
```

---

## Agent Engines vs Deprecated Solvers

| Engine type | `opm.agents.*` | Deprecated `opm.solver.*` |
|---|---|---|
| Chat | `opm.agents.chat` | `opm.solver.chat`, `opm.solver.question` |
| Summarizer | `opm.agents.summarizer` | `opm.solver.summarization` |
| Extractive QA | `opm.agents.extractive_qa` | `opm.solver.reading_comprehension` |
| ReRanker | `opm.agents.reranker` | `opm.solver.multiple_choice` |
| NLI | `opm.agents.nli` | `opm.solver.entailment` |
| Coref | `opm.agents.coref` | `opm.coreference` |

Do not use the deprecated entry point groups in new plugins. Both are still recognised by OPM for
backwards compatibility but the old classes will be removed in the next major release.

---

## Cross-References

- [Personas & PersonaService](150-personas.md) — how engines are composed into agents
- [Specialized Engine Types](150-advanced_solvers.md) — deep-dives per engine type
- [Claude Plugin](157-claude-plugin.md) — all ten Claude engine implementations
- [OpenAI Plugin](158-openai-plugin.md) — OpenAI-compatible engine implementations
- [GGUF Plugin](159-gguf-plugin.md) — local GGUF engine implementations
- [Mixture of Solvers](155-mos-plugin.md) — orchestrate multiple engines

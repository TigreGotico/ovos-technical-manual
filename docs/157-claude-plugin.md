# Claude Agent Plugin (`ovos-claude-plugin`)

`ovos-claude-plugin` connects OVOS to the [Anthropic Claude](https://anthropic.com) API. It
provides ten OPM agent engine implementations — covering every `opm.agents.*` type — plus two
transformer plugins. All engines share a single `AnthropicClient` wrapper and the same base
configuration keys.

Install: `pip install ovos-claude-plugin`

For the pre-built Claude persona: `pip install ovos-claude-persona`

Repository: `OpenVoiceOS Workspace/Agent Plugins/ovos-claude-plugin`

---

## Plugins Overview

| Entry point | Class | Purpose |
|---|---|---|
| `opm.agents.chat` | `ClaudeChatEngine` | Multi-turn chat for [personas](150-personas.md) |
| `opm.agents.chat.multimodal` | `ClaudeMultimodalChatEngine` | Vision (base64 images) + multi-turn chat |
| `opm.agents.summarizer` | `ClaudeSummarizerEngine` | Condense documents into plain-text summaries |
| `opm.agents.summarizer.chat` | `ClaudeChatSummarizerEngine` | Compress chat history for long sessions |
| `opm.agents.coref` | `ClaudeCoreferenceEngine` | Resolve pronouns and ambiguous references |
| `opm.agents.reranker` | `ClaudeReRankerEngine` | Semantically rank candidate answers |
| `opm.agents.extractive_qa` | `ClaudeExtractiveQAEngine` | Extract the exact passage answering a question |
| `opm.agents.nli` | `ClaudeNLIEngine` | Predict whether a premise entails a hypothesis |
| `opm.agents.yesno` | `ClaudeYesNoEngine` | Classify ambiguous responses as yes / no / unknown |
| `opm.agents.memory` | `ClaudeContextManager` | Per-session memory with automatic history compression |
| `opm.transformer.utterance` | `ClaudeUtteranceTransformer` | Normalise noisy ASR output before intent matching |
| `opm.transformer.dialog` | `ClaudeDialogTransformer` | Rewrite skill responses before TTS synthesis |

---

## Common Configuration Keys

All plugins read from `AnthropicClient.__init__` — `ovos_claude/api.py:AnthropicClient.__init__`.

| Key | Type | Default | Description |
|---|---|---|---|
| `api_key` | `str` | `""` | Anthropic API key. Falls back to `ANTHROPIC_API_KEY` env var if omitted. |
| `model` | `str` | `claude-haiku-4-5-20251001` | Claude model ID (see table below). |
| `max_tokens` | `int` | `512` | Maximum tokens in the completion. |
| `temperature` | `float` | `0.7` | Sampling temperature 0–1. Higher = more creative. |
| `top_p` | `float` | `1.0` | Nucleus sampling probability mass. |

### Model Selection

| Model ID | Speed | Cost | Best for |
|---|---|---|---|
| `claude-haiku-4-5-20251001` | Fastest | Cheapest | Real-time voice (**default**) |
| `claude-sonnet-4-6` | Medium | Medium | General purpose |
| `claude-opus-4-6` | Slowest | Most expensive | Complex reasoning, long documents |

---

## Chat Engine (`opm.agents.chat`)

**Class:** `ClaudeChatEngine` — `ovos_claude/chat.py:ClaudeChatEngine`

**OPM plugin name:** `ovos-chat-claude-plugin`

Multi-turn conversational LLM. The primary engine type used inside [personas](150-personas.md).
Supports synchronous responses, raw token streaming, and sentence-level streaming for TTS.

| Method | Description |
|---|---|
| `continue_chat(messages, session_id, lang, units) → AgentMessage` | Single blocking response |
| `stream_tokens(messages, ...) → Iterable[str]` | Raw token stream — not suitable for direct TTS |
| `stream_sentences(messages, ...) → Iterable[str]` | Sentence-buffered stream via `SentenceBoundaryDetector`, TTS-ready |
| `get_response(utterance, ...) → str` | Convenience single-turn wrapper |

### Plugin-specific keys

| Key | Type | Default | Description |
|---|---|---|---|
| `system_prompt` | `str` | `null` | System instruction prepended to every conversation. |
| `allow_system_prompts` | `bool` | `false` | When `true`, system messages from the caller are merged with the configured prompt. |

### System prompt merging behaviour

| `allow_system_prompts` | Caller sends system message | Result |
|---|---|---|
| `false` (default) | yes | Caller's system message stripped; configured `system_prompt` used |
| `false` | no | Configured `system_prompt` prepended |
| `true` | yes | Both merged: `configured_prompt + "\n" + caller_prompt` |
| `true` | no | Configured `system_prompt` prepended |

### Configuration example

```json
{
  "ovos-chat-claude-plugin": {
    "api_key": "sk-ant-...",
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 200,
    "temperature": 0.7,
    "system_prompt": "You are a helpful voice assistant. Be concise."
  }
}
```

### Usage in a persona

```json
{
  "name": "Claude",
  "handlers": ["ovos-chat-claude-plugin"],
  "ovos-chat-claude-plugin": {
    "api_key": "sk-ant-...",
    "model": "claude-haiku-4-5-20251001",
    "system_prompt": "You are Claude, a helpful voice assistant. Be concise."
  }
}
```

---

## Multimodal Chat Engine (`opm.agents.chat.multimodal`)

**Class:** `ClaudeMultimodalChatEngine` — `ovos_claude/multimodal.py:ClaudeMultimodalChatEngine`

**OPM plugin name:** `ovos-chat-multimodal-claude-plugin`

Extends `ClaudeChatEngine` with vision support. Images are passed as base64-encoded strings in
`MultimodalAgentMessage.image_content`. Data-URI headers (`data:image/png;base64,...`) are
stripped automatically.

```python
from ovos_claude.multimodal import ClaudeMultimodalChatEngine
from ovos_plugin_manager.templates.agents import MultimodalAgentMessage, MessageRole
import base64

engine = ClaudeMultimodalChatEngine({"api_key": "sk-ant-..."})

with open("photo.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

messages = [
    MultimodalAgentMessage(
        role=MessageRole.USER,
        content="What is in this image?",
        image_content=[b64],
    )
]
reply = engine.continue_chat(messages)
```

---

## Summarizer (`opm.agents.summarizer`)

**Class:** `ClaudeSummarizerEngine` — `ovos_claude/summarizer.py:ClaudeSummarizerEngine`

**OPM plugin name:** `ovos-summarizer-claude-plugin`

Condenses a plain-text document into 1–3 sentences. Used by skills (Wikipedia solver, news
reader) before TTS to avoid reading entire articles aloud.

| Key | Type | Default | Description |
|---|---|---|---|
| `system_prompt` | `str` | See source | System instruction for the summarisation model. |
| `prompt_template` | `str` | See source | Template with a `{content}` placeholder. |

```json
{
  "ovos-summarizer-claude-plugin": {
    "api_key": "sk-ant-...",
    "model": "claude-haiku-4-5-20251001",
    "prompt_template": "Summarize the following text in 1-3 sentences.\n\n{content}"
  }
}
```

---

## Chat Summarizer (`opm.agents.summarizer.chat`)

**Class:** `ClaudeChatSummarizerEngine` — `ovos_claude/summarizer.py:ClaudeChatSummarizerEngine`

**OPM plugin name:** `ovos-chat-summarizer-claude-plugin`

Converts a structured `List[AgentMessage]` chat history into a concise narrative summary. Used
internally by `ClaudeContextManager` for memory compression — `memory.py:ClaudeContextManager._compress_history`.

```json
{
  "ovos-chat-summarizer-claude-plugin": {
    "api_key": "sk-ant-...",
    "model": "claude-haiku-4-5-20251001"
  }
}
```

---

## Coreference Engine (`opm.agents.coref`)

**Class:** `ClaudeCoreferenceEngine` — `ovos_claude/coref.py:ClaudeCoreferenceEngine`

**OPM plugin name:** `ovos-coref-claude-plugin`

Resolves pronouns and ambiguous references in voice commands. `contains_corefs()` uses a fast
per-language pronoun wordlist — `api.py:PRONOUN_WORDLISTS` — to avoid calling the API on
utterances that need no resolution.

Supported wordlist languages: English, German, French, Spanish, Portuguese. All other languages
fall back to English. `solve_corefs()` calls Claude which handles many more languages natively.

| Key | Type | Default | Description |
|---|---|---|---|
| `system_prompt` | `str` | See source | Instruction for the pronoun resolution model. |
| `context_ttl` | `int` | `120` | Seconds before a tracked context entry expires. |

```json
{
  "ovos-coref-claude-plugin": {
    "api_key": "sk-ant-...",
    "context_ttl": 120
  }
}
```

```python
from ovos_claude.coref import ClaudeCoreferenceEngine

engine = ClaudeCoreferenceEngine({"api_key": "sk-ant-..."})
# After "Play Bohemian Rhapsody":
result = engine.resolve("Turn it off", lang="en")
print(result)  # "Turn Bohemian Rhapsody off"
```

---

## ReRanker (`opm.agents.reranker`)

**Class:** `ClaudeReRankerEngine` — `ovos_claude/reranker.py:ClaudeReRankerEngine`

**OPM plugin name:** `ovos-reranker-claude-plugin`

Prompts Claude to score each candidate 0.0–1.0 and returns the list sorted descending. Falls
back to equal scores (0.5) on API errors or malformed JSON. Used by the
[Common Query pipeline](cq_pipeline.md), OCP media search, and [Mixture of Solvers](155-mos-plugin.md).

```json
{
  "ovos-reranker-claude-plugin": {
    "api_key": "sk-ant-...",
    "model": "claude-haiku-4-5-20251001"
  }
}
```

### Common Query pipeline integration

```json
{
  "intents": {
    "common_query": {
      "reranker": "ovos-reranker-claude-plugin",
      "ovos-reranker-claude-plugin": {
        "api_key": "sk-ant-...",
        "model": "claude-haiku-4-5-20251001"
      }
    }
  }
}
```

---

## Extractive QA (`opm.agents.extractive_qa`)

**Class:** `ClaudeExtractiveQAEngine` — `ovos_claude/qa.py:ClaudeExtractiveQAEngine`

**OPM plugin name:** `ovos-extractive-qa-claude-plugin`

Given an evidence paragraph and a question, Claude identifies and quotes the relevant
sentence(s). Returns an empty string on API error.

```json
{
  "ovos-extractive-qa-claude-plugin": {
    "api_key": "sk-ant-..."
  }
}
```

```python
from ovos_claude.qa import ClaudeExtractiveQAEngine

engine = ClaudeExtractiveQAEngine({"api_key": "sk-ant-..."})
evidence = "The Eiffel Tower stands 330 metres tall. It was built from 1887 to 1889."
answer = engine.get_best_passage(evidence, "How tall is the Eiffel Tower?")
print(answer)  # "The Eiffel Tower stands 330 metres tall."
```

---

## NLI Engine (`opm.agents.nli`)

**Class:** `ClaudeNLIEngine` — `ovos_claude/nli.py:ClaudeNLIEngine`

**OPM plugin name:** `ovos-nli-claude-plugin`

Determines whether a *premise* logically entails a *hypothesis*. Returns `False` on API error.

```json
{
  "ovos-nli-claude-plugin": {
    "api_key": "sk-ant-..."
  }
}
```

```python
from ovos_claude.nli import ClaudeNLIEngine

engine = ClaudeNLIEngine({"api_key": "sk-ant-..."})
print(engine.predict_entailment("It is raining heavily.", "The weather is wet."))  # True
print(engine.predict_entailment("It is sunny.", "You need an umbrella."))          # False
```

---

## Yes/No Classifier (`opm.agents.yesno`)

**Class:** `ClaudeYesNoEngine` — `ovos_claude/nli.py:ClaudeYesNoEngine`

**OPM plugin name:** `ovos-yesno-claude-plugin`

Classifies a user's response to a yes/no question as `True`, `False`, or `None` (unclear).
Returns `None` on API error. Use in skills when `ask_yesno()` receives uncertain phrasing like
"I guess" or "maybe".

```json
{
  "ovos-yesno-claude-plugin": {
    "api_key": "sk-ant-..."
  }
}
```

```python
from ovos_claude.nli import ClaudeYesNoEngine

engine = ClaudeYesNoEngine({"api_key": "sk-ant-..."})
print(engine.yes_or_no("Do you want me to set a timer?", "sure, go ahead"))  # True
print(engine.yes_or_no("Shall I call John?", "no, not now"))                 # False
print(engine.yes_or_no("Ready?", "what do you mean?"))                       # None
```

---

## Context Manager / Memory (`opm.agents.memory`)

**Class:** `ClaudeContextManager` — `ovos_claude/memory.py:ClaudeContextManager`

**OPM plugin name:** `ovos-memory-claude-plugin`

Manages per-session conversation history. When the history exceeds `max_history` messages, the
oldest half is summarised by Claude and stored as a single SYSTEM message —
`memory.py:ClaudeContextManager._compress_history`.

| Key | Type | Default | Description |
|---|---|---|---|
| `system_prompt` | `str` | `""` | System prompt prepended to every built context. |
| `max_history` | `int` | `20` | Number of user/assistant messages before compression. `0` = disable. |
| `compress` | `bool` | `true` | Enable automatic history compression via Claude. |

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

### Persona with memory

```json
{
  "name": "Claude with Memory",
  "memory_module": "ovos-memory-claude-plugin",
  "handlers": ["ovos-chat-claude-plugin"],
  "ovos-chat-claude-plugin": {
    "api_key": "sk-ant-...",
    "model": "claude-sonnet-4-6",
    "system_prompt": "You are a helpful assistant."
  },
  "ovos-memory-claude-plugin": {
    "api_key": "sk-ant-...",
    "max_history": 30,
    "compress": true
  }
}
```

---

## Utterance Transformer (`opm.transformer.utterance`)

**Class:** `ClaudeUtteranceTransformer` — `ovos_claude/transformers.py:ClaudeUtteranceTransformer`

**OPM plugin name:** `ovos-utterance-transformer-claude-plugin`

Runs after ASR, before intent matching. Normalises informal or noisy speech to standard form.
Falls back to the original utterance on API error. Default priority: `10`.

| Key | Type | Default | Description |
|---|---|---|---|
| `system_prompt` | `str` | See source | Normalisation instruction for the ASR post-processor. |
| `priority` | `int` | `10` | Pipeline priority (lower runs first). |

```json
{
  "utterance_transformers": {
    "ovos-utterance-transformer-claude-plugin": {
      "api_key": "sk-ant-...",
      "model": "claude-haiku-4-5-20251001"
    }
  }
}
```

---

## Dialog Transformer (`opm.transformer.dialog`)

**Class:** `ClaudeDialogTransformer` — `ovos_claude/transformers.py:ClaudeDialogTransformer`

**OPM plugin name:** `ovos-dialog-transformer-claude-plugin`

Runs after skill response generation, before TTS synthesis. Only invokes Claude when a
`rewrite_prompt` is set (via config or `context["prompt"]`). Falls back to the original dialog
on API error. Default priority: `50`.

| Key | Type | Default | Description |
|---|---|---|---|
| `system_prompt` | `str` | See source | High-level rewrite instruction. |
| `rewrite_prompt` | `str` | `null` | Per-call directive appended before the dialog string. Can be passed at call time via `context["prompt"]`. |
| `priority` | `int` | `50` | Pipeline priority. |

```json
{
  "dialog_transformers": {
    "ovos-dialog-transformer-claude-plugin": {
      "api_key": "sk-ant-...",
      "model": "claude-haiku-4-5-20251001",
      "rewrite_prompt": "Rewrite the text so it sounds natural when spoken aloud. Remove any markdown."
    }
  }
}
```

### Rewrite prompt examples

| `rewrite_prompt` | Effect |
|---|---|
| `"Rewrite so it sounds natural when spoken aloud. Remove markdown."` | TTS-safe output |
| `"Rewrite as if explaining to a 5-year-old."` | Simpler vocabulary |
| `"Rewrite in the style of a grumpy old pirate."` | Character voice |
| `"Make it sound enthusiastic and upbeat."` | Tone adjustment |

---

## Persona Examples

### Minimal Claude persona

```json
{
  "name": "My Claude",
  "handlers": ["ovos-chat-claude-plugin"],
  "ovos-chat-claude-plugin": {
    "api_key": "sk-ant-...",
    "model": "claude-sonnet-4-6",
    "system_prompt": "You are a friendly assistant who gives short factual answers."
  }
}
```

### High-capability persona (Opus)

```json
{
  "name": "Claude Opus",
  "handlers": ["ovos-chat-claude-plugin"],
  "ovos-chat-claude-plugin": {
    "api_key": "sk-ant-...",
    "model": "claude-opus-4-6",
    "max_tokens": 400,
    "system_prompt": "You are an expert assistant. Reason carefully before answering."
  }
}
```

Store persona JSON files in `~/.config/ovos_persona/personas/`. Activate by voice:
`"Chat with My Claude"` or `"Ask Claude what the meaning of life is"`.

---

## Cross-References

- [Agent Engine Types](154-agent-plugins.md) — base class contracts and full type reference
- [Personas & PersonaService](150-personas.md) — how to load and activate personas
- [LLM Transformers](151-llm-transformers.md) — utterance and dialog transformer pipeline
- [Mixture of Solvers](155-mos-plugin.md) — using Claude engines as workers or kings
- [OpenAI Plugin](158-openai-plugin.md) — OpenAI-compatible alternative
- [GGUF Plugin](159-gguf-plugin.md) — fully offline local alternative

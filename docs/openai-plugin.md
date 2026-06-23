# OpenAI Agent Plugin (`ovos-openai-plugin`)

!!! abstract "In a nutshell"
    This plugin lets OVOS talk to AI chat services that follow OpenAI's popular format — that includes OpenAI itself, but also many private or locally-run alternatives that copy the same style. So it's the bridge that connects your assistant to a chosen AI "brain", whether that brain lives in the cloud or on your own machine. See [AI Agents & Personas](personas.md) for how this fits in, and the [Glossary](glossary.md) for unfamiliar terms.

`ovos-openai-plugin` connects OVOS to any OpenAI-compatible Chat Completions API — including
OpenAI itself, local models via [Ollama](https://ollama.com) or `llama.cpp`, self-hosted
proxies, and [`ovos-persona-server`](persona-server.md).

Install: `pip install ovos-openai-plugin`

Repository: `OpenVoiceOS Workspace/Agent Plugins/ovos-openai-plugin`

!!! note "Removed legacy solver"
    The old `ovos-solver-openai-plugin` entry point and the `OpenAIChatCompletionsSolver` /
    `OpenAICompletionsSolver` classes no longer exist. Personas that referenced them must
    switch to the `ovos-chat-openai-plugin` agent engine (still listed under a persona's
    `solvers` / `handlers` key, which `ovos-persona` accepts).

---

## Plugins Overview

| Entry point | Plugin name | Class | Purpose |
|---|---|---|---|
| `opm.agents.chat` | `ovos-chat-openai-plugin` | `OpenAIChatEngine` | Multi-turn chat for [personas](personas.md) |
| `opm.agents.memory` | `ovos-openai-rag-memory-plugin` | `PersonaServerRAGMemory` | RAG memory backed by an `ovos-persona-server` vector store |
| `opm.agents.summarizer` | `ovos-summarizer-openai-plugin` | `OpenAISummarizer` | Summarize arbitrary text |
| `opm.transformer.dialog` | `ovos-dialog-transformer-openai-plugin` | `OpenAIDialogTransformer` | Rewrite [TTS](tts-plugins.md) dialog in a different voice or style |
| `opm.lang.translate` | `ovos-translate-openai-plugin` | `OpenAITextTranslator` | Translate text between languages |
| `opm.lang.detect` | `ovos-lang-detect-openai-plugin` | `OpenAITextLangDetector` | Detect the language of text |
| `opm.plugin.persona` | `Remote Llama` | (pre-built persona) | Demo persona pointing at a public ollama/LLama server |

All engines wrap the same `OpenAIChatCompletions` API client, so any OpenAI-compatible Chat
Completions server (OpenAI, ollama, llama.cpp, vLLM, LocalAI, `ovos-persona-server`, …) works
by pointing `api_url` at its `/v1` base.

---

## Common Configuration Keys

All plugins wrap `OpenAIChatCompletions` internally.

| Key | Type | Default | Description |
|---|---|---|---|
| `api_url` | `str` | `https://api.openai.com/v1` | Base URL (the `/v1` root). `/chat/completions` is appended automatically. Change for local/self-hosted servers. |
| `key` | `str` | `""` | API key sent as a Bearer token. Omit (or use `"sk-nokey"`) for servers that don't require auth. |
| `model` | `str` | `gpt-4o-mini` | Model identifier (e.g. `gpt-4o`, `llama3.1:8b`). |
| `max_tokens` | `int` | `300` | Maximum number of tokens in the completion. |
| `temperature` | `float` | `0.5` | Sampling temperature. Higher = more creative. |
| `top_p` | `float` | `0.2` | Nucleus sampling probability mass. |
| `frequency_penalty` | `float` | `0` | Penalise repeated tokens by frequency. |
| `presence_penalty` | `float` | `0` | Penalise tokens that have already appeared. |
| `stop_token` | `str\|list` | `null` | One or more stop sequences that terminate generation. |

---

## Chat Engine (`opm.agents.chat`)

**Class:** `OpenAIChatEngine` — `ovos_openai_plugin/chat.py:OpenAIChatEngine`

**OPM plugin name:** `ovos-chat-openai-plugin`

Multi-turn conversational LLM. The primary engine type used inside [personas](personas.md).
Works with any OpenAI-compatible endpoint.

### Tool / function calling

`OpenAIChatEngine` sets `supports_tools = True`, so it advertises native
function-calling to callers. `continue_chat(messages, …, tools=…)` accepts
`ToolBox` objects and/or raw OpenAI tool dicts; when the model decides to call a
tool, the returned `AgentMessage` carries `tool_calls` (assistant `tool_calls`
turns and `MessageRole.TOOL` results are serialized back to the API on the next
round-trip), letting the caller run a tool loop. This is the same hook the
[agentic loop](agentic-loop.md) engines drive.

!!! note "Memory lives in `ovos-persona`, not this plugin"
    The chat engine is stateless — it only sees the `messages` it is handed each
    turn. Short-term conversational memory is supplied by `ovos-persona` (which
    accumulates the history), not by `ovos-openai-plugin`. The only memory backend
    this package ships is the server-coupled RAG memory described below.

### Plugin-specific keys

| Key | Type | Default | Description |
|---|---|---|---|
| `system_prompt` | `str` | `null` | Instruction prepended to every conversation as a `system` message. |
| `allow_system_prompts` | `bool` | `false` | When `true`, caller system messages are merged with the configured prompt. |

### System prompt merging

| `allow_system_prompts` | Caller sends system message | Result |
|---|---|---|
| `false` (default) | yes | Caller's system message stripped; configured `system_prompt` used |
| `false` | no | Configured `system_prompt` prepended |
| `true` | yes | Both merged: `configured_prompt + "\n" + caller_prompt` |
| `true` | no | Configured `system_prompt` prepended |

### OpenAI configuration example

```json
{
  "ovos-chat-openai-plugin": {
    "api_url": "https://api.openai.com/v1",
    "key": "sk-...",
    "model": "gpt-4o-mini",
    "max_tokens": 150,
    "temperature": 0.5,
    "system_prompt": "You are a concise and helpful voice assistant."
  }
}

```

### Local Ollama configuration

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

### Remote persona server

`ovos-persona-server` exposes any OVOS persona behind an OpenAI-compatible HTTP endpoint.
This lets you keep API keys on a single server and offload LLM computation:

```json
{
  "ovos-chat-openai-plugin": {
    "api_url": "http://my-persona-server:6712/v1",
    "key": "sk-nokey",
    "model": "my-persona-name"
  }
}

```

---

## Persona Configuration

```json
{
  "name": "My Local LLM",
  "handlers": ["ovos-chat-openai-plugin"],
  "ovos-chat-openai-plugin": {
    "api_url": "http://localhost:11434/v1",
    "key": "sk-nokey",
    "model": "llama3.1:8b",
    "system_prompt": "You are a helpful assistant who gives short and factual answers in twenty words or fewer."
  }
}

```

A persona's chat engine can equally be listed under the `solvers` key — `ovos-persona`
accepts either `handlers` or `solvers` and dispatches the same way.

Activate by voice: `"Chat with My Local LLM"`.

---

## RAG Memory (`opm.agents.memory`)

**Class:** `PersonaServerRAGMemory` — `ovos_openai_plugin/rag_memory.py:PersonaServerRAGMemory`

**OPM plugin name:** `ovos-openai-rag-memory-plugin`

A persona `memory_module` (an `AgentContextManager`). Before each turn it queries a vector store
hosted by an [`ovos-persona-server`](persona-server.md) and injects the retrieved chunks into the
conversation context; the persona's normal chat engine still generates the answer, so RAG
composes with any chat backend. This is the server/OpenAI-coupled memory backend — local-only
memory plugins live in `ovos-memory-plugins` instead.

| Key | Type | Default | Description |
|---|---|---|---|
| `api_url` | `str` | `null` | Base URL of the persona-server's OpenAI-compatible API (e.g. `http://localhost:8337/openai/v1`). |
| `vector_store_id` | `str` | — | Vector store to search. |
| `key` | `str` | `null` | Optional bearer token. |
| `inject_mode` | `str` | `system` | How retrieved context is added: `system` / `system_prompt` / `developer` / `user` / `tool`. |
| `retrieval` | `dict` | — | Sub-block: `max_num_results`, `min_score`, `query_mode` (`utterance`/`history`), `query_history_turns`. |
| `context` | `dict` | — | Sub-block: `header`, `chunk_prefix`, `chunk_separator`, `include_sources`, `tool_name`. |
| `system_prompt` | `str` | `null` | Base system prompt (kept stable for caching when `inject_mode="system"`). |
| `max_history` | `int` | `10` | Conversation turns retained. |

```json
{
  "name": "kb-assistant",
  "solvers": ["ovos-chat-openai-plugin"],
  "memory_module": "ovos-openai-rag-memory-plugin",
  "ovos-openai-rag-memory-plugin": {
    "api_url": "http://localhost:8337/openai/v1",
    "vector_store_id": "vs_...",
    "inject_mode": "system",
    "retrieval": {"max_num_results": 5, "query_mode": "utterance"}
  }
}

```

---

## Dialog [Transformer](transformer-plugins.md) (`opm.transformer.dialog`)

**Class:** `OpenAIDialogTransformer` — `ovos_openai_plugin/dialog_transformers.py:OpenAIDialogTransformer`

**OPM plugin name:** `ovos-dialog-transformer-openai-plugin`

Intercepts OVOS TTS dialog just before it is spoken and rewrites it using an LLM. Useful for
giving the assistant a distinct personality or adapting the reading level. Default priority: `10`.

| Key | Type | Default | Description |
|---|---|---|---|
| `system_prompt` | `str` | `"Your task is to rewrite text as if it was spoken by a different character"` | High-level instruction for the rewrite model. |
| `rewrite_prompt` | `str` | `null` | Per-call directive appended before each dialog string. Can also be passed at call time via `context["prompt"]`. |

```json
{
  "dialog_transformers": {
    "ovos-dialog-transformer-openai-plugin": {
      "api_url": "https://api.openai.com/v1",
      "key": "sk-...",
      "model": "gpt-4o-mini",
      "rewrite_prompt": "rewrite the text as if you were explaining it to a 5-year-old"
    }
  }
}

```

### Rewrite prompt examples

| `rewrite_prompt` | Effect |
|---|---|
| `"rewrite the text as if you were explaining it to a 5-year-old"` | Simpler vocabulary |
| `"rewrite the text as if it was an angry old man speaking"` | Grumpy character voice |
| `"Add more 'dude'ness to it"` | Casual/surfer tone |
| `"Explain it like you're a Shakespearean actor"` | Archaic dramatic style |

The `rewrite_prompt` can also be passed per-call via the `context` dict:

```python
text, ctx = transformer.transform(dialog, context={"prompt": "make it sound pirate-y"})

```

---

## Summarizer (`opm.agents.summarizer`)

**Class:** `OpenAISummarizer` — `ovos_openai_plugin/summarizer.py:OpenAISummarizer`

**OPM plugin name:** `ovos-summarizer-openai-plugin`

Condenses long documents into a short plain-text summary (2 paragraphs by default). Intended
for consumption by skills before TTS, not directly by end-users.

| Key | Type | Default | Description |
|---|---|---|---|
| `system_prompt` | `str` | `"Your task is to summarize text in a couple paragraphs."` | Instruction for the summarization model. |
| `prompt_template` | `str` | See below | Template with a `{content}` placeholder. |

Default `prompt_template`:

```
Your task is to summarize the text into a suitable format.
Answer in plaintext with no formatting, 2 paragraphs long at most.
Focus on the most important information.
---------------------
{content}

```

```json
{
  "ovos-summarizer-openai-plugin": {
    "api_url": "https://api.openai.com/v1",
    "key": "sk-...",
    "model": "gpt-4o-mini"
  }
}

```

---

## Translator (`opm.lang.translate`)

**Class:** `OpenAITextTranslator` — `ovos_openai_plugin/translate.py:OpenAITextTranslator`

**OPM plugin name:** `ovos-translate-openai-plugin`

Translates text between languages using an LLM. Language codes follow BCP-47 (e.g. `en-us`,
`pt-pt`, `es-es`). Supports translating OVOS `.intent` files while preserving `{variables}`,
`[optional]`, and `(alt|ernatives)` syntax.

```json
{
  "language": {
    "translation_module": "ovos-translate-openai-plugin",
    "ovos-translate-openai-plugin": {
      "api_url": "https://api.openai.com/v1",
      "key": "sk-...",
      "model": "gpt-4o-mini"
    }
  }
}

```

```python
from ovos_openai_plugin.translate import OpenAITextTranslator

translator = OpenAITextTranslator({"key": "sk-...", "model": "gpt-4o-mini"})
result = translator.translate("Hello, world!", target="pt-pt", source="en-us")
print(result)  # "Olá, mundo!"

```

---

## Language Detector (`opm.lang.detect`)

**Class:** `OpenAITextLangDetector` — `ovos_openai_plugin/translate.py:OpenAITextLangDetector`

**OPM plugin name:** `ovos-lang-detect-openai-plugin`

Detects the BCP-47 language code of a given text using an LLM.

```json
{
  "language": {
    "detection_module": "ovos-lang-detect-openai-plugin",
    "ovos-lang-detect-openai-plugin": {
      "api_url": "https://api.openai.com/v1",
      "key": "sk-...",
      "model": "gpt-4o-mini"
    }
  }
}

```

```python
from ovos_openai_plugin.translate import OpenAITextLangDetector

detector = OpenAITextLangDetector({"key": "sk-...", "model": "gpt-4o-mini"})
lang = detector.detect("The quick brown fox jumps over the lazy dog")
print(lang)  # "en"

```

---

## Full mycroft.conf Example

```json
{
  "dialog_transformers": {
    "ovos-dialog-transformer-openai-plugin": {
      "api_url": "https://api.openai.com/v1",
      "key": "sk-...",
      "model": "gpt-4o-mini",
      "rewrite_prompt": "Rewrite for natural spoken delivery. Remove markdown."
    }
  },
  "language": {
    "detection_module": "ovos-lang-detect-openai-plugin",
    "translation_module": "ovos-translate-openai-plugin",
    "ovos-lang-detect-openai-plugin": {
      "api_url": "https://api.openai.com/v1",
      "key": "sk-...",
      "model": "gpt-4o-mini"
    },
    "ovos-translate-openai-plugin": {
      "api_url": "https://api.openai.com/v1",
      "key": "sk-...",
      "model": "gpt-4o-mini"
    }
  }
}

```

---

## Cross-References

- [Agent Engine Types](agent-plugins.md) — base class contracts and full type reference


- [Personas & PersonaService](personas.md) — how to load and activate personas


- [LLM Transformers](llm-transformers.md) — utterance and dialog transformer pipeline


- [Persona Server](persona-server.md) — expose a persona via OpenAI-compatible HTTP API


- [GGUF Plugin](gguf-plugin.md) — fully offline local alternative

---

*Source code: [OpenVoiceOS/ovos-openai-plugin](https://github.com/OpenVoiceOS/ovos-openai-plugin).*

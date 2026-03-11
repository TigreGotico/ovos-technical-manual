# OpenAI Agent Plugin (`ovos-openai-plugin`)

`ovos-openai-plugin` connects OVOS to any OpenAI-compatible Chat Completions API — including
OpenAI itself, local models via [Ollama](https://ollama.com) or `llama.cpp`, self-hosted
proxies, and [`ovos-persona-server`](202-persona_server.md).

Install: `pip install ovos-openai-plugin`

Repository: `OpenVoiceOS Workspace/Agent Plugins/ovos-openai-plugin`

!!! note "Version compatibility"
    `ovos-persona >= 1.0.0` is required for `ovos-chat-openai-plugin`. If you cannot upgrade
    `ovos-persona`, pin `ovos-openai-plugin <= 2.0.6` which ships the legacy
    `ovos-solver-openai-plugin` entry point instead.

---

## Plugins Overview

| Entry point | Class | Purpose |
|---|---|---|
| `opm.agents.chat` | `OpenAIChatEngine` | Multi-turn chat for [personas](150-personas.md) |
| `opm.transformer.dialog` | `OpenAIDialogTransformer` | Rewrite TTS dialog in a different voice or style |
| `opm.agents.summarizer` | `OpenAISummarizer` | Summarize arbitrary text |
| `opm.lang.translate` | `OpenAITextTranslator` | Translate text between languages |
| `opm.lang.detect` | `OpenAITextLangDetector` | Detect the language of text |

---

## Common Configuration Keys

All plugins wrap `OpenAIChatCompletions` internally.

| Key | Type | Default | Description |
|---|---|---|---|
| `api_url` | `str` | `https://api.openai.com/v1` | Base URL of the Chat Completions endpoint. Change this for local or self-hosted models. |
| `key` | `str` | `""` | API key sent as a Bearer token. Use `"sk-nokey"` for servers that don't require auth. |
| `model` | `str` | `""` | Model identifier (e.g. `gpt-4o`, `llama3.1:8b`). Required by most backends. |
| `max_tokens` | `int` | `100` | Maximum number of tokens in the completion. |
| `temperature` | `float` | `0.5` | Sampling temperature. Higher = more creative. |
| `top_p` | `float` | `0.2` | Nucleus sampling probability mass. |
| `frequency_penalty` | `float` | `0` | Penalise repeated tokens by frequency. |
| `presence_penalty` | `float` | `0` | Penalise tokens that have already appeared. |
| `stop_token` | `str\|list` | `null` | One or more stop sequences that terminate generation. |

---

## Chat Engine (`opm.agents.chat`)

**Class:** `OpenAIChatEngine` — `ovos_openai_plugin/chat.py:OpenAIChatEngine`

**OPM plugin name:** `ovos-chat-openai-plugin`

Multi-turn conversational LLM. The primary engine type used inside [personas](150-personas.md).
Works with any OpenAI-compatible endpoint.

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

### Standard persona (ovos-persona >= 1.0.0)

```json
{
  "name": "My Local LLM",
  "memory_module": "ovos-agents-short-term-memory-plugin",
  "handlers": ["ovos-chat-openai-plugin"],
  "ovos-chat-openai-plugin": {
    "api_url": "http://localhost:11434/v1",
    "key": "sk-nokey",
    "model": "llama3.1:8b",
    "system_prompt": "You are a helpful assistant who gives short and factual answers in twenty words or fewer."
  }
}
```

### Legacy persona (ovos-persona < 1.0.0)

```json
{
  "name": "My Local LLM",
  "solvers": ["ovos-solver-openai-plugin"],
  "ovos-solver-openai-plugin": {
    "api_url": "http://localhost:11434/v1",
    "key": "sk-nokey",
    "model": "llama3.1:8b",
    "system_prompt": "You are a helpful assistant."
  }
}
```

Activate by voice: `"Chat with My Local LLM"`.

---

## Dialog Transformer (`opm.transformer.dialog`)

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

- [Agent Engine Types](154-agent-plugins.md) — base class contracts and full type reference
- [Personas & PersonaService](150-personas.md) — how to load and activate personas
- [LLM Transformers](151-llm-transformers.md) — utterance and dialog transformer pipeline
- [Persona Server](202-persona_server.md) — expose a persona via OpenAI-compatible HTTP API
- [Mixture of Solvers](155-mos-plugin.md) — using OpenAI engines as workers or kings
- [Claude Plugin](157-claude-plugin.md) — Anthropic Claude alternative with more engine types
- [GGUF Plugin](159-gguf-plugin.md) — fully offline local alternative

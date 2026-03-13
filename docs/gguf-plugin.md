# GGUF / Local LLM Agent Plugin (`ovos-gguf-plugin`)

`ovos-gguf-plugin` provides feature-parity with [ovos-claude-plugin](claude-plugin.md) using
locally-running GGUF models powered by [`llama-cpp-python`](https://github.com/abetlen/llama-cpp-python).
No API keys, no network access, no cloud dependency — suitable for offline, air-gapped, or
privacy-sensitive deployments.

GGUF models can be loaded from a [Hugging Face Hub](https://huggingface.co) repository (downloaded
on first use) or from a local `.gguf` file path.

Install: `pip install ovos-gguf-plugin`

Repository: `OpenVoiceOS Workspace/Agent Plugins/ovos-gguf-plugin`

---

## Plugins Overview

| Entry point | Class | Source |
|---|---|---|
| `opm.agents.chat` | `GGUFChatEngine` | `ovos_gguf_solver/chat.py` |
| `opm.agents.summarizer` | `GGUFSummarizerEngine` | `ovos_gguf_solver/summarizer.py` |
| `opm.agents.summarizer.chat` | `GGUFChatSummarizerEngine` | `ovos_gguf_solver/summarizer.py` |
| `opm.agents.coref` | `GGUFCoreferenceEngine` | `ovos_gguf_solver/coref.py` |
| `opm.agents.reranker` | `GGUFReRankerEngine` | `ovos_gguf_solver/reranker.py` |
| `opm.agents.extractive_qa` | `GGUFExtractiveQAEngine` | `ovos_gguf_solver/qa.py` |
| `opm.agents.nli` | `GGUFNLIEngine` | `ovos_gguf_solver/nli.py` |
| `opm.agents.yesno` | `GGUFYesNoEngine` | `ovos_gguf_solver/nli.py` |
| `opm.agents.memory` | `GGUFContextManager` | `ovos_gguf_solver/memory.py` |
| `opm.transformer.text` | `GGUFUtteranceTransformer` | `ovos_gguf_solver/transformers.py` |
| `opm.transformer.dialog` | `GGUFDialogTransformer` | `ovos_gguf_solver/transformers.py` |

A legacy `GGUFSolver` entry point (`neon.plugin.solver`) is also provided for backwards
compatibility with older `ovos-persona` versions.

---

## Shared Client: `GGUFClient`

All engines delegate to `GGUFClient` — `ovos_gguf_solver/api.py:GGUFClient`.

**The model is lazy-loaded on the first API call.** Construction is always cheap — no model is
loaded until a request is made. This means OVOS startup is not delayed even when multiple GGUF
engines are configured.

---

## Common Configuration Keys

| Key | Type | Default | Description |
|---|---|---|---|
| `model` | `str` | required | Hugging Face repo ID (`"owner/repo-name-GGUF"`) or absolute path to a `.gguf` file. |
| `remote_filename` | `str` | `null` | Glob pattern to select a specific GGUF file from the repo (e.g. `"*Q4_K_M.gguf"`). Required when using a Hub repo. |
| `n_gpu_layers` | `int` | `0` | Number of layers to offload to GPU. `0` = CPU only. `-1` = all layers on GPU. |
| `n_ctx` | `int` | `2048` | Context window size in tokens. |
| `temperature` | `float` | `0.7` | Sampling temperature. |
| `max_tokens` | `int` | `512` | Maximum tokens in the completion. |

### Minimal configuration (Hub model)

```json
{
  "model": "microsoft/Phi-3-mini-4k-instruct-gguf",
  "remote_filename": "*Q4_K_M.gguf",
  "n_gpu_layers": 0
}

```

### Local file configuration

```json
{
  "model": "/home/user/models/llama-3.1-8b.gguf",
  "n_gpu_layers": 20,
  "n_ctx": 4096
}

```

---

## Chat Engine (`opm.agents.chat`)

**Class:** `GGUFChatEngine` — `ovos_gguf_solver/chat.py:GGUFChatEngine`

**OPM plugin name:** `ovos-gguf-chat-plugin`

Multi-turn conversational LLM using a local GGUF model. API-compatible with `ClaudeChatEngine`
and `OpenAIChatEngine` — drop-in replacement for offline use.

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

### Offline persona example

```json
{
  "name": "Local Phi-3",
  "handlers": ["ovos-gguf-chat-plugin"],
  "ovos-gguf-chat-plugin": {
    "model": "microsoft/Phi-3-mini-4k-instruct-gguf",
    "remote_filename": "*Q4_K_M.gguf",
    "n_gpu_layers": 0,
    "system_prompt": "You are a concise, helpful voice assistant."
  }
}

```

Activate by voice: `"Chat with Local Phi-3"`.

---

## Summarizer (`opm.agents.summarizer`)

**Class:** `GGUFSummarizerEngine` — `ovos_gguf_solver/summarizer.py:GGUFSummarizerEngine`

**OPM plugin name:** `ovos-gguf-summarizer-plugin`

Condenses a plain-text document into 1–3 sentences using a local GGUF model.

```json
{
  "ovos-gguf-summarizer-plugin": {
    "model": "/path/to/model.gguf",
    "max_tokens": 256
  }
}

```

---

## Chat Summarizer (`opm.agents.summarizer.chat`)

**Class:** `GGUFChatSummarizerEngine` — `ovos_gguf_solver/summarizer.py:GGUFChatSummarizerEngine`

**OPM plugin name:** `ovos-gguf-chat-summarizer-plugin`

Converts a structured `List[AgentMessage]` chat history into a concise narrative summary. Used
internally by `GGUFContextManager` for memory compression.

```json
{
  "ovos-gguf-chat-summarizer-plugin": {
    "model": "/path/to/model.gguf"
  }
}

```

---

## Coreference Engine (`opm.agents.coref`)

**Class:** `GGUFCoreferenceEngine` — `ovos_gguf_solver/coref.py:GGUFCoreferenceEngine`

**OPM plugin name:** `ovos-gguf-coref-plugin`

Resolves pronouns and ambiguous references in voice commands. Uses the same fast pronoun
wordlist check as `ClaudeCoreferenceEngine` to avoid model inference on utterances with no
pronouns.

```json
{
  "ovos-gguf-coref-plugin": {
    "model": "/path/to/model.gguf",
    "context_ttl": 120
  }
}

```

---

## ReRanker (`opm.agents.reranker`)

**Class:** `GGUFReRankerEngine` — `ovos_gguf_solver/reranker.py:GGUFReRankerEngine`

**OPM plugin name:** `ovos-gguf-reranker-plugin`

Scores candidate answers 0.0–1.0 using a local GGUF model and returns them sorted descending.
Used by the [Common Query pipeline](cq-pipeline.md), [OCP](ocp-pipeline.md) media search, and
[Mixture of Solvers](mos-plugin.md) as judge/king/referee.

```json
{
  "ovos-gguf-reranker-plugin": {
    "model": "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
    "remote_filename": "*Q4_K_M.gguf"
  }
}

```

For a non-LLM local reranker with no model download required, consider
`ovos-flashrank-reranker-plugin` (cross-encoder transformer, CPU-only).

---

## Extractive QA (`opm.agents.extractive_qa`)

**Class:** `GGUFExtractiveQAEngine` — `ovos_gguf_solver/qa.py:GGUFExtractiveQAEngine`

**OPM plugin name:** `ovos-gguf-extractive-qa-plugin`

Given evidence text and a question, extracts and returns the exact passage that answers it.

```json
{
  "ovos-gguf-extractive-qa-plugin": {
    "model": "/path/to/model.gguf"
  }
}

```

---

## NLI Engine (`opm.agents.nli`)

**Class:** `GGUFNLIEngine` — `ovos_gguf_solver/nli.py:GGUFNLIEngine`

**OPM plugin name:** `ovos-gguf-nli-plugin`

Determines whether a *premise* logically entails a *hypothesis* using a local GGUF model.

```json
{
  "ovos-gguf-nli-plugin": {
    "model": "/path/to/model.gguf"
  }
}

```

---

## Yes/No Classifier (`opm.agents.yesno`)

**Class:** `GGUFYesNoEngine` — `ovos_gguf_solver/nli.py:GGUFYesNoEngine`

**OPM plugin name:** `ovos-gguf-yesno-plugin`

Classifies a user's ambiguous confirmation as `True` (yes), `False` (no), or `None` (unclear).

```json
{
  "ovos-gguf-yesno-plugin": {
    "model": "/path/to/model.gguf"
  }
}

```

---

## Context Manager / Memory (`opm.agents.memory`)

**Class:** `GGUFContextManager` — `ovos_gguf_solver/memory.py:GGUFContextManager`

**OPM plugin name:** `ovos-gguf-memory-plugin`

Manages per-session conversation history with optional automatic compression via the local GGUF
model when history exceeds `max_history` messages.

| Key | Type | Default | Description |
|---|---|---|---|
| `system_prompt` | `str` | `""` | System prompt prepended to every built context. |
| `max_history` | `int` | `20` | Number of user/assistant messages before compression. `0` = disable. |
| `compress` | `bool` | `true` | Enable automatic history compression via the local model. |

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

### Offline persona with memory

```json
{
  "name": "Offline Assistant",
  "memory_module": "ovos-gguf-memory-plugin",
  "handlers": ["ovos-gguf-chat-plugin"],
  "ovos-gguf-chat-plugin": {
    "model": "/path/to/model.gguf",
    "system_prompt": "You are a helpful assistant."
  },
  "ovos-gguf-memory-plugin": {
    "model": "/path/to/model.gguf",
    "max_history": 10,
    "compress": true
  }
}

```

---

## Utterance [Transformer](transformer-plugins.md) (`opm.transformer.text`)

**Class:** `GGUFUtteranceTransformer` — `ovos_gguf_solver/transformers.py:GGUFUtteranceTransformer`

**OPM plugin name:** `ovos-utterance-transformer-gguf-plugin`

Runs after ASR, before intent matching. Normalises informal or noisy speech to standard form
using a local GGUF model. Falls back to the original utterance on inference error.

```json
{
  "utterance_transformers": {
    "ovos-utterance-transformer-gguf-plugin": {
      "model": "microsoft/Phi-3-mini-4k-instruct-gguf",
      "remote_filename": "*Q4_K_M.gguf",
      "n_gpu_layers": 0
    }
  }
}

```

---

## Dialog Transformer (`opm.transformer.dialog`)

**Class:** `GGUFDialogTransformer` — `ovos_gguf_solver/transformers.py:GGUFDialogTransformer`

**OPM plugin name:** `ovos-dialog-transformer-gguf-plugin`

Runs after skill response generation, before [TTS](tts-plugins.md) synthesis. Rewrites skill responses using a
local GGUF model. Only invoked when a `rewrite_prompt` is configured. Falls back to the original
dialog on inference error.

```json
{
  "dialog_transformers": {
    "ovos-dialog-transformer-gguf-plugin": {
      "model": "/path/to/model.gguf",
      "rewrite_prompt": "Rewrite in a warm, friendly tone. Remove markdown.",
      "n_gpu_layers": 20
    }
  }
}

```

---

## Model Selection Guide

| Use case | Recommended model size | Example |
|---|---|---|
| Real-time voice (low latency) | 1B–3B parameters | `Phi-3-mini` Q4_K_M |
| General purpose | 7B–8B parameters | `Llama-3.1-8B` Q4_K_M |
| Complex reasoning | 13B+ parameters | `Llama-3.1-13B` Q4_K_M |
| Memory-constrained devices | 1B parameters | `Qwen2.5-1.5B` Q4_K_M |

Quantization level guide:

- `Q4_K_M` — good balance of quality and speed (recommended default)


- `Q8_0` — higher quality, roughly 2× the memory of Q4


- `Q2_K` — smallest/fastest, lowest quality

---

## GPU Acceleration

Set `n_gpu_layers` to offload transformer layers to a CUDA or Metal GPU:

```json
{
  "model": "/path/to/llama-3.1-8b.gguf",
  "n_gpu_layers": -1
}

```

`-1` offloads all layers (full GPU inference). Values > 0 offload that many layers (partial
offload for limited VRAM). `0` = CPU only.

Requires `llama-cpp-python` to be compiled with CUDA or Metal support:

```bash
CMAKE_ARGS="-DLLGGML_CUDA=on" pip install llama-cpp-python --force-reinstall

```

---

## Cross-References

- [Agent Engine Types](agent-plugins.md) — base class contracts and full type reference


- [Personas & PersonaService](personas.md) — how to load and activate personas


- [LLM Transformers](llm-transformers.md) — utterance and dialog transformer pipeline


- [Mixture of Solvers](mos-plugin.md) — using GGUF engines as offline workers in MoS


- [Claude Plugin](claude-plugin.md) — Anthropic Claude cloud alternative


- [OpenAI Plugin](openai-plugin.md) — OpenAI-compatible API alternative

# GGUF / Local LLM Agent Plugin (`ovos-gguf-plugin`)

`ovos-gguf-plugin` runs local GGUF models through
[`llama-cpp-python`](https://github.com/abetlen/llama-cpp-python) — no API keys, no network,
suitable for offline, air-gapped, or privacy-sensitive deployments. It provides a chat engine,
a summarizer, translation / language-detection, a text-embeddings plugin, and a dialog
transformer.

Models load from a [Hugging Face Hub](https://huggingface.co) repository (downloaded on first
use) or from a local `.gguf` file path. Each engine loads its own `llama_cpp.Llama` instance;
one `Llama` can be shared between engines by passing `gguf_engine=` in code.

Install: `pip install ovos-gguf-plugin`

Repository: `OpenVoiceOS Workspace/Agent Plugins/ovos-gguf-plugin`

---

## Plugins Overview

| Entry point | Plugin name | Class | Source |
|---|---|---|---|
| `opm.agents.chat` | `ovos-chat-gguf-plugin` | `GGUFChatEngine` | `ovos_gguf_plugin/chat.py` |
| `opm.agents.summarizer` | `ovos-summarizer-gguf-plugin` | `GGUFSummarizer` | `ovos_gguf_plugin/summarizer.py` |
| `opm.lang.translate` | `ovos-translate-gguf-plugin` | `GGUFTextTranslator` | `ovos_gguf_plugin/translate.py` |
| `opm.lang.detect` | `ovos-lang-detect-gguf-plugin` | `GGUFTextLangDetector` | `ovos_gguf_plugin/translate.py` |
| `opm.transformer.dialog` | `ovos-dialog-transformer-gguf-plugin` | `GGUFDialogTransformer` | `ovos_gguf_plugin/dialog_transformers.py` |

!!! note "Scope"
    This plugin does **not** ship coref / reranker / extractive-QA / NLI / yes-no / memory
    engines, a chat-summarizer, or an utterance transformer. For reranking, install any
    `opm.agents.reranker` plugin (see [Agent Plugins](agent-plugins.md)).

---

## Common Configuration Keys

Model loading happens in `GGUFChatEngine`, which the other engines delegate to.

| Key | Type | Default | Description |
|---|---|---|---|
| `model` | `str` | required | Hugging Face repo id (`"owner/repo-name-GGUF"`) or absolute path to a `.gguf` file. |
| `remote_filename` | `str` | `*Q4_K_M.gguf` | Glob selecting the GGUF file from a Hub repo (ignored for local-file `model`). |
| `n_gpu_layers` | `int` | `0` | Layers offloaded to GPU. `0` = CPU only; `-1` = all layers on GPU. |
| `chat_format` | `str` | `null` | `llama-cpp-python` chat template name (auto-detected if unset). |
| `max_tokens` | `int` | `null` | Maximum tokens in the completion (`null` = model/llama.cpp default). |
| `verbose` | `bool` | `true` | Pass-through to `llama_cpp.Llama`. |
| `system_prompt` | `str` | `null` | Default system prompt. |
| `allow_system_prompts` | `bool` | `false` | When `true`, caller system messages are merged with the configured prompt; when `false`, stripped. |

A `model` value that is an existing file path is loaded with `Llama(model_path=...)`; otherwise
it is treated as a Hub repo id and loaded with `Llama.from_pretrained(repo_id=..., filename=...)`.

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
  "n_gpu_layers": 20
}

```

---

## Chat Engine (`opm.agents.chat`)

**Class:** `GGUFChatEngine` — `ovos_gguf_plugin/chat.py:GGUFChatEngine`

**OPM plugin name:** `ovos-chat-gguf-plugin`

Multi-turn conversational LLM using a local GGUF model. Implements `continue_chat`,
`stream_tokens`, and `stream_sentences` — API-compatible with `OpenAIChatEngine` for offline use.

```json
{
  "ovos-chat-gguf-plugin": {
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
  "handlers": ["ovos-chat-gguf-plugin"],
  "ovos-chat-gguf-plugin": {
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

**Class:** `GGUFSummarizer` — `ovos_gguf_plugin/summarizer.py:GGUFSummarizer`

**OPM plugin name:** `ovos-summarizer-gguf-plugin`

Condenses a document into a short summary using a local GGUF model. Delegates generation to a
`GGUFChatEngine`. The system prompt and user prompt default to the plugin's localized
`.prompt` files; override with `system_prompt` and `prompt_template` (a template with a
`{content}` placeholder).

| Key | Type | Default | Description |
|---|---|---|---|
| `system_prompt` | `str` | localized `summarize_system` prompt | Instruction for the summarisation model. |
| `prompt_template` | `str` | localized `summarize_user` prompt | Template with a `{content}` placeholder. |

```json
{
  "ovos-summarizer-gguf-plugin": {
    "model": "/path/to/model.gguf",
    "max_tokens": 256
  }
}

```

---

## Translation & Language Detection (`opm.lang.translate`, `opm.lang.detect`)

**Classes:** `GGUFTextTranslator` / `GGUFTextLangDetector` — `ovos_gguf_plugin/translate.py`

**OPM plugin names:** `ovos-translate-gguf-plugin` / `ovos-lang-detect-gguf-plugin`

Translate text between languages or detect a text's language using a local GGUF model.

```json
{
  "language": {
    "translation_module": "ovos-translate-gguf-plugin",
    "detection_module": "ovos-lang-detect-gguf-plugin",
    "ovos-translate-gguf-plugin": {
      "model": "/path/to/model.gguf"
    },
    "ovos-lang-detect-gguf-plugin": {
      "model": "/path/to/model.gguf"
    }
  }
}

```

---

## Dialog Transformer (`opm.transformer.dialog`)

**Class:** `GGUFDialogTransformer` — `ovos_gguf_plugin/dialog_transformers.py:GGUFDialogTransformer`

**OPM plugin name:** `ovos-dialog-transformer-gguf-plugin`

Runs after skill response generation, before [TTS](tts-plugins.md) synthesis. Rewrites skill
responses with a local GGUF model. Only invoked when a `rewrite_prompt` is configured (via
config or `context["prompt"]`); falls back to the original dialog otherwise. Default priority:
`10`. The system prompt defaults to the localized `dialog_transform_system` prompt.

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
| Memory-constrained devices | 1B–1.5B parameters | `Qwen2.5-1.5B` Q4_K_M |

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
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall

```

---

## Cross-References

- [Agent Engine Types](agent-plugins.md) — base class contracts and full type reference


- [Personas & PersonaService](personas.md) — how to load and activate personas


- [LLM Transformers](llm-transformers.md) — dialog transformer pipeline


- [OpenAI Plugin](openai-plugin.md) — OpenAI-compatible API alternative

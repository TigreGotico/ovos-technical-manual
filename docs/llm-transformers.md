# Generative AI [Transformer](transformer-plugins.md) Plugins

**Transformer plugins** intercept the OVOS processing pipeline at two points — before intent
matching (utterance transformers) and before [TTS](tts-plugins.md) synthesis (dialog transformers). They operate
independently of the persona system but can use the same LLM backends.

- **[Utterance](life-of-an-utterance.md) transformers** (`opm.transformer.text`) — run after [STT](stt-plugins.md), before NLP.


- **Dialog transformers** (`opm.transformer.dialog`) — run after skill response generation, before TTS.

LLM-backed implementations are provided by `ovos-claude-plugin` (utterance + dialog) and
`ovos-openai-plugin` / `ovos-gguf-plugin` (dialog only).

Multiple transformers of each type can be stacked. The `priority` config key controls
execution order (lower number = runs earlier).

---

## Utterance Transformers

Utterance transformers normalise or validate ASR output before it reaches the intent pipeline.
They receive a list of candidate utterances and return a (possibly modified) list plus a context
dict.

### Claude Utterance Transformer

`ClaudeUtteranceTransformer` — `ovos_claude/transformers.py:ClaudeUtteranceTransformer`

Entry point: `opm.transformer.text` (`ovos-utterance-transformer-claude-plugin`)

Normalises informal or noisy speech to standard form. Falls back to the original utterance on
API error.

```json
{
  "utterance_transformers": {
    "ovos-utterance-transformer-claude-plugin": {
      "api_key": "sk-ant-...",
      "model": "claude-haiku-4-5-20251001",
      "priority": 10
    }
  }
}

```

```python
t = ClaudeUtteranceTransformer(config={"api_key": "sk-ant-..."})
result, ctx = t.transform(["whats 2 plus 2 ya know"])
print(result)  # ["What is 2 plus 2?"]

```

Default priority is `10` — runs early in the transformer chain before other plugins.
`ovos-claude-plugin` is the only LLM agent plugin that ships an utterance transformer;
`ovos-gguf-plugin` and `ovos-openai-plugin` provide dialog transformers only.

### OVOS Transcription Validator

`ovos-transcription-validator-plugin` calls an OpenAI-compatible chat endpoint (any local or
remote server exposing `/chat/completions`, e.g. Ollama, llama.cpp, vLLM) to classify ASR output
as valid or invalid *before* it reaches intent matching. Invalid transcriptions are discarded,
preventing skills from firing on garbled speech like `"Potato stop green light now yes."`. The
default `api_url` is the public `https://llama.smartgic.io/v1` demo endpoint.

```json
{
  "utterance_transformers": {
    "ovos-transcription-validator-plugin": {
      "model": "qwen2.5:7b",
      "api_url": "https://llama.smartgic.io/v1",
      "api_key": "sk-xxxx",
      "mode": "reprompt"
    }
  }
}

```

---

## Dialog Transformers

Dialog transformers receive the final response string from the skill and return a rewritten
version. Only invoked when a `rewrite_prompt` is configured (via config or per-call context).
Falls back to the original dialog on API error.

### Claude Dialog Transformer

`ClaudeDialogTransformer` — `ovos_claude/transformers.py:ClaudeDialogTransformer`

Entry point: `opm.transformer.dialog` (`ovos-dialog-transformer-claude-plugin`)

```json
{
  "dialog_transformers": {
    "ovos-dialog-transformer-claude-plugin": {
      "api_key": "sk-ant-...",
      "model": "claude-haiku-4-5-20251001",
      "rewrite_prompt": "Rewrite the text so it sounds natural when spoken aloud. Remove any markdown.",
      "priority": 50
    }
  }
}

```

The `rewrite_prompt` can also be passed per-call via `context["prompt"]`.

```python
from ovos_claude.transformers import ClaudeDialogTransformer

t = ClaudeDialogTransformer(config={
    "api_key": "sk-ant-...",
    "rewrite_prompt": "Rewrite in a cheerful, enthusiastic tone.",
})
result, ctx = t.transform("The forecast shows rain tomorrow.")

# "Oh wow, rain is coming tomorrow — how exciting for the plants!"

```

### OpenAI Dialog Transformer

`OpenAIDialogTransformer` — `ovos_openai_plugin/dialog_transformers.py:OpenAIDialogTransformer`

Entry point: `opm.transformer.dialog` (`ovos-dialog-transformer-openai-plugin`)

Works with any OpenAI-compatible endpoint — OpenAI, Ollama, llama.cpp, or
`ovos-persona-server`:

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

### GGUF Dialog Transformer

`GGUFDialogTransformer` — `ovos_gguf_plugin/dialog_transformers.py:GGUFDialogTransformer`

Fully offline alternative using a local GGUF model:

```json
{
  "dialog_transformers": {
    "ovos-dialog-transformer-gguf-plugin": {
      "model": "/path/to/model.gguf",
      "rewrite_prompt": "Rewrite in a warm, friendly tone.",
      "n_gpu_layers": 20
    }
  }
}

```

---

## Rewrite Prompt Examples

The `rewrite_prompt` value is the most important lever. Examples across all transformer
implementations:

| Prompt | Effect |
|---|---|
| `"Rewrite so it sounds natural when spoken aloud. Remove markdown."` | TTS-safe output |
| `"Rewrite as if explaining to a 5-year-old."` | Simpler vocabulary |
| `"Rewrite in the style of a grumpy old pirate."` | Character voice |
| `"Make it sound enthusiastic and upbeat."` | Tone adjustment |
| `"Remove all technical jargon."` | Plain language |
| `"Explain it like you're a Shakespearean actor."` | Archaic dramatic style |

---

## Stacking Transformers

Multiple transformers can be active simultaneously. Priority controls order:

```json
{
  "utterance_transformers": {
    "ovos-transcription-validator-plugin": {"priority": 5},
    "ovos-utterance-transformer-claude-plugin": {"api_key": "sk-ant-...", "priority": 10}
  },
  "dialog_transformers": {
    "ovos-dialog-transformer-openai-plugin": {
      "key": "sk-...", "model": "gpt-4o-mini",
      "rewrite_prompt": "Rewrite for TTS.",
      "priority": 50
    }
  }
}

```

The validator runs first (priority 5), discarding invalid ASR. The normaliser runs next
(priority 10), cleaning valid utterances before intent matching. The dialog transformer
rewrites skill responses (priority 50) before TTS.

---

## Cross-References

- [Utterance Transformers — ovos-core pipeline](core.md)


- [Dialog Transformers — audio service](audio-service.md)


- [Claude Plugin](claude-plugin.md) — full Claude transformer configuration reference


- [OpenAI Plugin](openai-plugin.md) — OpenAI transformer configuration reference


- [GGUF Plugin](gguf-plugin.md) — local GGUF transformer configuration reference

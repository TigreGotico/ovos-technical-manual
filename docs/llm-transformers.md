# Generative AI [Transformer](transformer-plugins.md) Plugins

**Transformer plugins** intercept the OVOS processing pipeline at two points — before intent
matching (utterance transformers) and before [TTS](tts-plugins.md) synthesis (dialog transformers). They operate
independently of the persona system but can use the same LLM backends.

- **[Utterance](life-of-an-utterance.md) transformers** (`opm.transformer.text`) — run after [STT](stt-plugins.md), before NLP.


- **Dialog transformers** (`opm.transformer.dialog`) — run after skill response generation, before TTS.

LLM-backed implementations are provided by `ovos-openai-plugin` / `ovos-gguf-plugin`
(dialog transformers).

Multiple transformers of each type can be stacked. The `priority` config key controls
execution order (lower number = runs earlier).

---

## Utterance Transformers

Utterance transformers normalise or validate ASR output before it reaches the intent pipeline.
They receive a list of candidate utterances and return a (possibly modified) list plus a context
dict.

A typical utterance transformer normalises informal or noisy speech to standard form, or
classifies ASR output as valid or invalid *before* it reaches intent matching so that garbled
speech like `"Potato stop green light now yes."` is discarded. The `priority` config key
controls where each runs in the chain (lower number = earlier).

---

## Dialog Transformers

Dialog transformers receive the final response string from the skill and return a rewritten
version. Only invoked when a `rewrite_prompt` is configured (via config or per-call context).
Falls back to the original dialog on API error.

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
  "dialog_transformers": {
    "ovos-dialog-transformer-openai-plugin": {
      "key": "sk-...", "model": "gpt-4o-mini",
      "rewrite_prompt": "Rewrite for TTS.",
      "priority": 50
    }
  }
}

```

Utterance transformers run first (lowest priority first), cleaning or validating ASR output
before intent matching. The dialog transformer rewrites skill responses (priority 50) before TTS.

---

## Cross-References

- [Utterance Transformers — ovos-core pipeline](core.md)


- [Dialog Transformers — audio service](audio-service.md)


- [OpenAI Plugin](openai-plugin.md) — OpenAI transformer configuration reference


- [GGUF Plugin](gguf-plugin.md) — local GGUF transformer configuration reference

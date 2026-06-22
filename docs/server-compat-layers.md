# Server Compatibility Layers

!!! abstract "In a nutshell"
    The OVOS servers (for speech-to-text, text-to-speech, translation, and chat personas) can *impersonate* the popular commercial services people already build software for — OpenAI, Google, DeepL, ElevenLabs, Anthropic, and many more. This page lists which imitations each server offers. The benefit: an app written to talk to one of those big-name services can be pointed at your own OVOS server instead, with no code changes, like a power adapter that lets the same plug fit a different socket. See the [STT Server](stt-server.md), [TTS Server](tts-server.md), [Translate Server](translate-server.md), and [Persona Server](persona-server.md) pages, or the [Glossary](glossary.md).

Each OVOS service server exposes vendor-prefixed routers so existing clients and integrations can connect without modification. Every router accepts the vendor's original request format and translates it to the native OVOS plugin call.

---

## Pattern

Each compat router is a self-contained FastAPI `APIRouter` mounted under a fixed vendor prefix. The router:

1. Accepts the vendor's HTTP contract (paths, query params, request/response bodies).
2. Translates to the server's internal `process()` call.
3. Returns the vendor's expected response format.

All compat routers are always loaded; no feature flag is needed.

---

## STT Server Compat Routes

`pip install ovos-stt-http-server`

| Prefix | Vendor |
|--------|--------|
| `/openai` | OpenAI Whisper (`/openai/v1/audio/transcriptions`) |
| `/deepgram` | Deepgram |
| `/google` | Google Cloud Speech |
| `/assemblyai` | AssemblyAI |
| `/speechmatics` | Speechmatics |
| `/azure-stt` | Microsoft Azure Speech |
| `/aws` | AWS Transcribe |
| `/watson/speech-to-text` | IBM Watson STT |
| `/wit` | Wit.ai |
| `/vosk` | Vosk-server WebSocket |
| `/vosk-webrtc` | Vosk WebRTC variant |
| `/whisper-cpp` | whisper.cpp HTTP server |
| `/gladia` | Gladia |
| `/groq` | Groq Whisper |
| `/elevenlabs` | ElevenLabs Scribe |
| `/speech-api` | Chromium/Google `speech-api` |
| `/client` | Kaldi GStreamer Server |

---

## TTS Server Compat Routes

`pip install ovos-tts-server`

| Prefix | Vendor |
|--------|--------|
| `/elevenlabs` | ElevenLabs |
| `/openai` | OpenAI TTS |
| `/coqui` | Coqui TTS |
| `/google-tts` | Google Cloud TTS |
| `/amazon-polly` | Amazon Polly |
| `/azure-tts` | Microsoft Azure TTS |
| `/cartesia` | Cartesia |
| `/deepgram` | Deepgram Aura |
| `/playht` | PlayHT |
| `/marytts` | MaryTTS (`/marytts/process`, `/voices`, `/locales`) |

---

## Translate Server Compat Routes

`pip install ovos-translate-server`

| Prefix | Vendor |
|--------|--------|
| `/libretranslate` | LibreTranslate |
| `/deepl` | DeepL v2 |
| `/deeplx` | DeepLX |
| `/google` | Google Translate v2 |
| `/azure` | Azure Translator v3 |
| `/amazon` | Amazon Translate |
| `/lingva` | Lingva Translate |

---

## Persona Server Compat Routes

`pip install ovos-persona-server`

The persona server baseline is an OpenAI-compatible chat API at **`/openai/v1/chat/completions`**. (The unprefixed `/v1/...` path is also mounted but is **deprecated legacy** — it returns a `Deprecation` header; a bare-root base URL 404s, so always include the `/openai/v1` prefix.) Additional vendor routers are layered on top:

| Prefix | Vendor |
|--------|--------|
| `/openai/v1`, `/ollama/api` | OpenAI + Ollama |
| `/anthropic/v1` | Anthropic Claude |
| `/gemini/v1beta/models` | Google Gemini |
| `/cohere/v1` | Cohere |
| `/tgi` | HuggingFace TGI |
| `/bedrock/model` | AWS Bedrock |

### OpenAI-compatible example (existing, stable)

```python
import openai

client = openai.OpenAI(api_key="", base_url="http://localhost:8337/openai/v1")
response = client.chat.completions.create(
    model="",
    messages=[{"role": "user", "content": "tell me a joke"}]
)
print(response.choices[0].message.content)
```

### Anthropic-compatible example

```python
import anthropic

client = anthropic.Anthropic(
    api_key="sk-fake",
    base_url="http://localhost:8337/anthropic/v1"
)
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=256,
    messages=[{"role": "user", "content": "Hello!"}]
)
print(message.content[0].text)
```

---

## Related Pages

- [STT Server](stt-server.md)
- [TTS Server](tts-server.md)
- [Translate Server](translate-server.md)
- [Persona Server](persona-server.md)
- [Agent Interoperability](agent-interop.md) — MCP/UTCP endpoints on these same servers

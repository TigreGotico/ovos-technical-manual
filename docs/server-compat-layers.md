# Server Compatibility Layers

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

Status: PRs [#53–#69](https://github.com/OpenVoiceOS/ovos-stt-http-server/pulls) (open/draft).

| Prefix | Vendor | PR |
|--------|--------|----|
| `/openai` | OpenAI Whisper (`/openai/v1/audio/transcriptions`) | #53 |
| `/deepgram` | Deepgram (`/deepgram/v1/listen`) | #54 |
| `/google` | Google Cloud Speech (`/google/speech:recognize`) | #55 |
| `/assemblyai` | AssemblyAI | #56 |
| `/speechmatics` | Speechmatics | #57 |
| `/azure-stt` | Microsoft Azure Speech | #58 |
| `/aws` | AWS Transcribe | #60 |
| `/watson/speech-to-text` | IBM Watson STT | #61 |
| `/wit` | Wit.ai | #62 |
| `/vosk` | Vosk-server WebSocket | #63 |
| `/whisper-cpp` | whisper.cpp HTTP server | #64 |
| `/vosk-grpc` | Vosk gRPC variant | #65 |
| `/vosk-webrtc` | Vosk WebRTC variant | #66 |
| `/vosk-mqtt` | Vosk MQTT variant | #67 |
| `/client` | Kaldi GStreamer Server | #69 |

---

## TTS Server Compat Routes

`pip install ovos-tts-server`

Status: PRs [#87–#94](https://github.com/OpenVoiceOS/ovos-tts-server/pulls) (open/draft).

| Prefix | Vendor | PR |
|--------|--------|----|
| `/elevenlabs` | ElevenLabs | #87 |
| `/openai` | OpenAI TTS | #88 |
| `/coqui` | Coqui TTS | #89 |
| `/google-tts` | Google Cloud TTS | #90 |
| `/amazon-polly` | Amazon Polly | #91 |
| `/azure-tts` | Microsoft Azure TTS | #92 |
| `/piper` | Piper TTS | #93 |
| `/process` | MaryTTS (`/process`, `/voices`, `/locales`) | #94 |

---

## Translate Server Compat Routes

`pip install ovos-translate-server`

Status: PRs [#17–#22](https://github.com/OpenVoiceOS/ovos-translate-server/pulls) (draft).

| Prefix | Vendor | PR |
|--------|--------|----|
| Base | FastAPI migration (replaces Flask) | #17 |
| `/libretranslate` | LibreTranslate | #18 |
| `/deepl` | DeepL v2 | #19 |
| `/google` | Google Translate v2 | #20 |
| `/azure` | Azure Translator v3 | #21 |
| `/amazon` | Amazon Translate | #22 |

---

## Persona Server Compat Routes

`pip install ovos-persona-server`

Status: PRs [#29–#34](https://github.com/OpenVoiceOS/ovos-persona-server/pulls) (draft).

The persona server baseline is an OpenAI-compatible chat API (`/v1/chat/completions`). Additional vendor routers are layered on top:

| Prefix | Vendor | PR |
|--------|--------|----|
| `/openai`, `/ollama` | OpenAI + Ollama (refactored) | #29 |
| `/anthropic/v1` | Anthropic Claude | #30 |
| `/gemini/v1beta` | Google Gemini | #31 |
| `/cohere/v1` | Cohere | #32 |
| `/tgi` | HuggingFace TGI | #33 |
| `/bedrock/model` | AWS Bedrock | #34 |

### OpenAI-compatible example (existing, stable)

```python
import openai

client = openai.OpenAI(api_key="", base_url="http://localhost:8337")
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

# OpenVoiceOS [STT](stt-plugins.md) HTTP Server

**Lightweight HTTP microservice for any OVOS speech‑to‑text plugin, with optional Gradio UI.**

The OpenVoiceOS STT HTTP Server wraps your chosen OVOS STT plugin inside a FastAPI service (complete with automatic language detection), making it easy to deploy on your local machine, in Docker, or behind a load balancer.

---

## Usage Guide

**Install the server** 

```bash
pip install ovos-stt-http-server

```

**Configure your STT plugin**  

In your `mycroft.conf` (or equivalent) under the `stt` section:  

```json
{
 "stt": {
   "module": "ovos-stt-plugin-xxx",
   "ovos-stt-plugin-xxx": {
     "model": "xxx"
   }
 }
}

```

**Launch the server**  

```bash
ovos-stt-server \
 --engine ovos-stt-plugin-xxx \
 --host 0.0.0.0 \
 --port 9666

```

**Verify it’s running**  

Visit [http://localhost:9666/status](http://localhost:9666/status) in your browser or run:  

```bash
curl http://localhost:9666/status

```

---

## Command‑Line Options

```bash
$ ovos-stt-server --help
usage: ovos-stt-server [-h] --engine ENGINE [--lang-engine LANG_ENGINE] [--port PORT] [--host HOST] [--multi]

options:
  -h, --help            show this help message and exit
  --engine ENGINE       stt plugin to be used (required)
  --lang-engine LANG_ENGINE
                        audio language detection plugin to be used
  --port PORT           port number (default: 8080)
  --host HOST           host (default: 0.0.0.0)
  --multi               Load a plugin instance per language (force lang support)

```
---

## Technical Explanation

- **FastAPI core**  
  The server is a FastAPI app served by `uvicorn`, exposing REST endpoints.

- **Plugin wrapping**  
  `--engine` names any `opm.stt` plugin entry point (Whisper, Deepgram, etc.); it is loaded dynamically via the OVOS Plugin Manager. Plugin config is read from the `stt` section of your `mycroft.conf`.

- **Language detection**  
  `--lang-engine` names an `opm.transformer.audio` plugin implementing `AudioLanguageDetector`. When a `/stt` request passes `lang=auto`, audio is routed through it before transcription.

- **Multi-model mode**  
  `--multi` loads one engine instance per language on demand (one model per `lang`), instead of a single shared model.

- **Compatibility routers**  
  Beyond the native endpoints, the app mounts drop-in compatible routers so existing cloud-STT clients work unchanged, e.g. Wit.ai (`POST /wit/speech`, override the SDK host with the `WIT_URL` env var), Chromium speech-api (`POST /speech-api/v2/recognize`), and routers for OpenAI Whisper, Deepgram, Google, AssemblyAI, Azure, IBM Watson, AWS, Vosk, Kaldi, Gladia, ElevenLabs, Groq and Speechmatics. A `GET /utcp` manual advertises the endpoints to UTCP agents, and an MCP server mounts when `pip install 'ovos-stt-http-server[mcp]'` is present.

- **Scalability**  
  Stateless design lets you run multiple instances behind a load balancer or in Kubernetes.

---

## HTTP API Endpoints

Native endpoints:

| Endpoint       | Method | Description                                                |
| -------------- | ------ | ---------------------------------------------------------- |
| `/status`      | GET    | Returns `{status, plugin, lang_plugin}`.                  |
| `/stt`         | POST   | Raw audio bytes in the body (query: `lang`, `sample_rate`, `sample_width`) → plain‑text transcript. With `lang=auto`, language is detected first. |
| `/lang_detect` | POST   | Raw audio bytes (query: `valid_langs`) → JSON `{ "lang": "en", "conf": 0.83 }`. |
| `/utcp`        | GET    | UTCP tool-discovery manual (JSON).                        |
| `/docs`        | GET    | Interactive FastAPI OpenAPI docs.                         |

Compatibility routers (selection): `POST /wit/speech` (Wit.ai), `POST /speech-api/v2/recognize` (Chromium), plus OpenAI/Deepgram/Google/etc. See `/docs` for the full list.

---

## Companion Plugin

To point a OpenVoiceOS (or compatible project) to a STT server you can use the companion plugin

**Install**  

```bash
pip install ovos-stt-plugin-server

```

**Configure**  

```json
  "stt": {
    "module": "ovos-stt-plugin-server",
    "ovos-stt-plugin-server": {
      "urls": ["https://0.0.0.0:8080/stt"],
      "verify_ssl": true
    },
 }

```

for audio language detection

```json
  "listener": {
    "audio_transformers": {
        "ovos-audio-lang-server-plugin": {
          "urls": ["https://0.0.0.0:8080/lang_detect"],
          "verify_ssl": true
        }
    }
  }

```

---

## Docker Deployment

**Create a Dockerfile**

```dockerfile
FROM python:3.11-slim
RUN pip install ovos-stt-http-server
RUN pip install {YOUR_STT_PLUGIN}
ENTRYPOINT ["ovos-stt-server", "--engine", "{YOUR_STT_PLUGIN}"]

```

The console script is `ovos-stt-server` (not `ovos-stt-http-server`, which is the PyPI package name).

**Build & Run**

```bash
docker build -t my-ovos-stt .
docker run -p 8080:8080 my-ovos-stt

```

Pre-built containers are also available via the [ovos-docker-stt](https://github.com/OpenVoiceOS/ovos-docker-stt) repository.

---

## Tips & Caveats

- **`/stt` takes raw audio bytes, not a multipart upload.** Send the PCM/WAV bytes as the request body (`curl --data-binary @audio.wav`), and pass `sample_rate`/`sample_width` as query params if they differ from the 16000/2 defaults — those defaults are assumed when reading the raw body.

- **Audio Formats**: Ensure client sends PCM‑compatible formats (`.wav`, `.mp3` recommended).


- **Securing Endpoints**: Consider putting a reverse proxy (NGINX, Traefik) in front for SSL or API keys.


- **Plugin Dependencies**: Some STT engines require heavy native libraries—bake them into your Docker image.

---

## Links & References

- OVOS STT HTTP Server GitHub: https://github.com/OpenVoiceOS/ovos-stt-http-server


- Companion Plugin: https://github.com/OpenVoiceOS/ovos-stt-server-plugin


- Docker Images: https://github.com/OpenVoiceOS/ovos-docker-stt


- OVOS Plugin Manager: https://github.com/OpenVoiceOS/ovos-plugin-manager
# OpenVoiceOS [STT](stt-plugins.md) HTTP Server

!!! abstract "In a nutshell"
    This is a small standalone program that turns any OVOS speech-to-text engine — the part that converts spoken audio into written text — into a web service. Once it's running, other devices on your network (or the internet) can send it audio over a simple web request and get back the transcribed text, so one capable machine can do the listening for many lightweight devices. It can even pretend to be popular cloud services (like OpenAI Whisper or Google), so software written for those works against your own server unchanged. See [STT plugins](stt-plugins.md) and the [Glossary](glossary.md).

**Lightweight HTTP microservice for any OVOS speech‑to‑text plugin.**

The OpenVoiceOS STT HTTP Server wraps your chosen OVOS STT plugin inside a FastAPI service (complete with automatic language detection), making it easy to deploy on your local machine, in Docker, or behind a load balancer.

---

## Usage Guide

**Install the server** 

```bash
pip install ovos-stt-http-server

```

**Choose your STT plugin**

You name the plugin to serve with the `--engine` flag (below). Note that — unlike a full OVOS
install — the standalone server instantiates the plugin with an **empty config**, so it runs
with the plugin's **built-in defaults**; it does **not** read the `stt` section of
`mycroft.conf`. Pick a plugin whose defaults suit you, or one that loads its own configuration.

A normal OVOS install (not this server) selects its STT plugin under the `stt` section instead:

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

**Verify it's running**  

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
  `--engine` names any `opm.stt` plugin entry point (Whisper, Deepgram, etc.); it is loaded dynamically via the OVOS Plugin Manager. The server instantiates it with an empty config (built-in defaults), not the `stt` section of `mycroft.conf`.

- **Language detection**  
  `--lang-engine` names an `opm.transformer.audio` plugin implementing `AudioLanguageDetector`. When a `/stt` request passes `lang=auto`, audio is routed through it before transcription.

- **Multi-model mode**  
  `--multi` loads one engine instance per language on demand (one model per `lang`), instead of a single shared model.

- **Compatibility routers**  
  Beyond the native endpoints, the app mounts drop-in compatible routers so existing cloud-STT clients work unchanged, e.g. Wit.ai (`POST /wit/speech`, override the SDK host with the `WIT_URL` env var), Chromium speech-api (`POST /speech-api/v2/recognize`), and routers for OpenAI Whisper, Whisper.cpp server, Deepgram, Google, AssemblyAI, Azure, IBM Watson, AWS Transcribe, Vosk and Speechmatics. A `GET /utcp` manual advertises the endpoints to UTCP agents, and an MCP server mounts when `pip install 'ovos-stt-http-server[mcp]'` is present.

- **Scalability**  
  Stateless design lets you run multiple instances behind a load balancer or in Kubernetes.

---

## HTTP API Endpoints

Native endpoints:

| Endpoint       | Method | Description                                                |
| -------------- | ------ | ---------------------------------------------------------- |
| `/status`      | GET    | Returns `{status, plugin, lang_plugin}`.                  |
| `/stt`         | POST   | Raw audio bytes in the body (query: `lang`, `sample_rate` default `16000`, `sample_width` default `2`) → plain‑text transcript. With `lang=auto`, language is detected first. |
| `/lang_detect` | POST   | Raw audio bytes (query: `valid_langs`) → JSON `{ "lang": "en", "conf": 0.83 }`. |
| `/utcp`        | GET    | UTCP tool-discovery manual (JSON).                        |
| `/docs`        | GET    | Interactive FastAPI OpenAPI docs.                         |

Compatibility routers (selection): `POST /wit/speech` (Wit.ai), `POST /speech-api/v2/recognize` (Chromium), plus OpenAI/Deepgram/Google/etc. See `/docs` for the full list.

### OpenAI-Compatible Translation Endpoint

`POST /openai/v1/audio/translations` mirrors OpenAI's Whisper translations endpoint. OpenAI's
contract for this endpoint always returns **English**, regardless of the spoken language, so
after transcribing the request runs an extra translate step using the configured OVOS
translate plugin. If no translate plugin is configured, the endpoint falls back to returning
the untranslated transcript instead of failing.

```jsonc
{
  "language": {
    "translation_module": "ovos-translate-plugin-server"
  }
}

```

---

## Transformer Pipelines

The server can run OVOS transformer plugins around transcription. Both hooks live in the
model containers, so **every** surface gets them: the native `/stt` endpoint, all
vendor-compat routers, the websocket streaming routes, MCP, and UTCP.

- **Audio transformers** run *before* the STT stage. When the chain includes an
  `AudioLanguageDetector` (like the `--lang-engine` mentioned above), its detected language
  resolves `lang=auto` (an explicitly requested language always wins).
- **Utterance transformers** rewrite the *transcript* after ASR, before it is returned.

Loading is config-gated and opt-in via the standard `mycroft.conf` sections; with no config
the server behaves exactly as before:

```json
{
  "audio_transformers": {
    "ovos-audio-transformer-plugin-speechbrain-langdetect": {}
  },
  "utterance_transformers": {
    "ovos-utterance-corrections-plugin": {}
  }
}

```

Chains run in ascending priority order; an explicit `"order"` list in a section wins over
priorities. In multi-model mode (`--multi`) one set of transformer instances is shared
across the per-language engines. See the
[transformer plugins reference](transformer-plugins.md) for the full contract.

!!! tip "Server-side transforms are a client-invisible change"
    An utterance transformer on the server means clients receive a **different transcript**
    than what the STT engine actually heard. Use it deliberately — fleet-wide vocabulary
    corrections, language routing via an `AudioLanguageDetector`, or server-side audio
    cleanup for thin clients — and never enable the same plugin on both the server and a
    downstream OVOS stack that also runs transformers, or it will run twice.

---

## Companion Plugin

To point a OpenVoiceOS (or compatible project) to a STT server you can use the companion plugin.

!!! note "Package name vs. repository name"
    The PyPI package is `ovos-stt-plugin-server`, but its source repository is named
    `OpenVoiceOS/ovos-stt-server-plugin` (the words are swapped). Both names refer to the same
    plugin — use the pip name to install, the repo name to find the source.

**Install**  

```bash
pip install ovos-stt-plugin-server

```

!!! note "Upcoming — universal server adapter"
    A `server_type` option is planned for this companion plugin, so a single config shape can
    target different self-hosted or cloud STT server APIs without a dedicated plugin per vendor.

**Configure**

Point it at your own server (localhost, or wherever you run the container above):

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-server",
    "ovos-stt-plugin-server": {
      "urls": ["http://localhost:8080/stt"],
      "verify_ssl": true,
      "timeout": 5
    },
 }

```

for audio language detection

```jsonc
  "listener": {
    "audio_transformers": {
        "ovos-audio-lang-server-plugin": {
          "urls": ["http://localhost:8080/lang_detect"],
          "verify_ssl": true
        }
    }
  }

```

!!! warning "No `urls` configured → public servers, not local failure"
    If you omit `urls` entirely, the plugin does **not** fail — it silently falls back to a
    small built-in list of **public** OVOS STT servers (shuffled, tried in order) run by
    community members. That's convenient for a quick test, but it means your audio leaves your
    network by default unless you set `urls` yourself. Always set `urls` explicitly for any
    real deployment.

--8<-- "snippets/community-servers.md"

See [STT plugins](stt-plugins.md) for fully offline engines if you'd rather not depend on any server.

`urls` semantics:

- **List, tried in order until one succeeds** — if you list more than one server, the plugin
  tries each in turn (each attempt bounded by `timeout`, default 5 seconds) and returns the
  first successful transcription; it does not race them in parallel.
- **`timeout`** is per-attempt, in seconds, not a total budget across the whole list.
- A request that exhausts every URL without success raises no exception from the plugin call
  itself — the caller (the listener, below) just gets no transcript back.

### Listener-side fallback: a second STT engine, not just a second URL

Independent of this plugin's own multi-URL retry, `ovos-dinkum-listener` supports a completely
separate **fallback STT engine** — a different plugin entirely, used only if the primary
engine returns no utterance. Configure it under the `stt` section:

```jsonc
{
  "stt": {
    "module": "ovos-stt-plugin-fasterwhisper",  // primary, offline
    "fallback_module": "ovos-stt-plugin-server", // used only if the primary returns nothing
    "ovos-stt-plugin-server": {
      "urls": ["http://localhost:8080/stt"]
    }
  }
}

```

This is useful the other way around too — a fast/light primary engine locally, with a heavier
server-backed engine as the fallback for when the light one comes back empty.

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


- **Plugin Dependencies**: Some STT engines require heavy native libraries — bake them into your Docker image.

---

## Links & References

- OVOS STT HTTP Server GitHub: https://github.com/OpenVoiceOS/ovos-stt-http-server


- Companion Plugin: https://github.com/OpenVoiceOS/ovos-stt-server-plugin


- Docker Images: https://github.com/OpenVoiceOS/ovos-docker-stt


- OVOS Plugin Manager: https://github.com/OpenVoiceOS/ovos-plugin-manager
# OpenVoiceOS [TTS](tts-plugins.md) Server

!!! abstract "In a nutshell"
    This is a small standalone program that turns any OVOS text-to-speech voice — the part that reads written text aloud — into a web service. You send it some text over a simple web request and it sends back the spoken audio, so one capable machine can do the talking for many lightweight devices. It can also imitate popular cloud voice services (like ElevenLabs or OpenAI), letting software built for those use your own server instead. See [TTS plugins](tts-plugins.md) and the [Glossary](glossary.md).

**Lightweight HTTP microservice for any OVOS text‑to‑speech plugin, with optional caching.**

Wrap your favorite OVOS TTS engine in a FastAPI service—ready to deploy locally, in Docker, or behind a load balancer.

The OpenVoiceOS TTS HTTP Server exposes any OVOS TTS plugin over a simple HTTP API. Send text, receive audio—no extra
glue code required.

---

## Usage Guide

**Install the server**

```bash
pip install ovos-tts-server

```

**Configure your TTS plugin**

In your `mycroft.conf` (or equivalent) under the `tts` section:

```json
{
 "tts": {
   "module": "ovos-tts-plugin-xxx",
   "ovos-tts-plugin-xxx": {
     "voice": "xxx"
   }
 }
}

```

**Launch the server**  

```bash
ovos-tts-server \
 --engine ovos-tts-plugin-xxx \
 --host 0.0.0.0 \
 --port 9666

```

**Verify it’s running**  

Visit http://localhost:9666/status in your browser or run:

```bash
curl http://localhost:9666/status

```

---

## Command‑Line Options

```bash
$ ovos-tts-server --help
usage: ovos-tts-server [-h] [--engine ENGINE] [--port PORT] [--host HOST] [--cache] [--lang LANG] [--mcp]

options:
  -h, --help            show this help message and exit
  --engine ENGINE       tts plugin to be used
  --port PORT           port number (default: 9666)
  --host HOST           host (default: 0.0.0.0)
  --cache               save every synth to disk
  --lang LANG           accepted for compatibility but currently ignored; the default
                        language comes from config (`lang`) or falls back to "mul"
  --mcp                 mount MCP server at /mcp (requires ovos-tts-server[mcp])

```

---

## Technical Explanation

- **FastAPI Core**  
  Spins up a FastAPI application exposing RESTful endpoints for synthesis and status checks.

- **Plugin Loading**  
  `--engine` names any `opm.tts` plugin entry point; it is loaded dynamically via the OVOS Plugin Manager—no code changes needed when adding new voices. Plugin config is read from the `tts` section of your `mycroft.conf`.

- **Caching**  
  When `--cache` is enabled, every synthesis request is stored on disk for debugging or reuse.

- **Compatibility routers**  
  The app also mounts drop-in compatible routers so existing cloud-TTS clients work unchanged: ElevenLabs, OpenAI, Coqui, Google, Amazon Polly, Azure, MaryTTS, Cartesia, Deepgram Aura, and PlayHT. A `GET /utcp` manual advertises the endpoints to UTCP agents, and `--mcp` mounts an MCP server at `/mcp` (requires the `mcp` extra).

- **Scalability**  
  Stateless by design—run multiple instances behind NGINX, Traefik, or Kubernetes with round‑robin or load‑based
  routing.

---

## HTTP API Endpoints

| Endpoint                  | Method | Description                                                          |
|---------------------------|--------|---------------------------------------------------------------------|
| `/status`                 | GET    | Returns loaded plugin name, supported `langs`, and `default_lang` / `default_model` / `default_voice`. |
| `/synthesize/{utterance}` | GET    | Legacy: URL‑encoded text in the path → synthesized audio file.      |
| `/v2/synthesize`          | GET    | `utterance` (required) plus optional query params → synthesized audio file. |
| `/utcp`                   | GET    | UTCP tool-discovery manual (JSON).                                  |
| `/docs`                   | GET    | Interactive OpenAPI (Swagger) docs.                                 |

> Both synthesis endpoints respond with a `FileResponse` (the audio file written by the plugin, WAV by default).
> Any extra query parameters on `/v2/synthesize` (besides `utterance`) are forwarded to the plugin's `get_tts` method as kwargs.
> 💡 This allows `"voice"` and `"lang"` to be set per-request at runtime rather than only by plugin config at load time (for plugins that support it). A missing `utterance` returns HTTP 400.

---

## Companion Plugin

Point your OVOS instance at this TTS server with the companion client plugin
(repo `ovos-tts-server-plugin`, class `OVOSServerTTS`, entry point and PyPI package
`ovos-tts-plugin-server`):

```bash
pip install ovos-tts-plugin-server

```

**Configuration** `mycroft.conf`:

```json
{
  "tts": {
    "module": "ovos-tts-plugin-server",
    "ovos-tts-plugin-server": {
        "host": "http://localhost:9666",
        "voice": "xxx",
        "v2": true,
        "verify_ssl": true,
        "tts_timeout": 5
     }
 } 
}

```

!!! warning "No `host` configured → public servers, not local failure"
    If you omit `host`, the plugin does **not** fail — it silently falls back to a built-in
    list of **public** OVOS TTS servers run by community members, shuffled and tried in order.
    That's fine for a quick test, but every sentence your assistant speaks is sent to a
    third-party server by default until you set `host` yourself. Always set `host` explicitly
    (as in the localhost example above) for any real deployment.

--8<-- "snippets/community-servers.md"

See [TTS plugins](tts-plugins.md) for fully offline voices if you'd rather not depend on any server.

Config keys:

| Key | Default | Description |
|-----|---------|-------------|
| `host` | public servers | Server base URL, or a list of URLs to try in order. If unset, a built-in list of public OVOS TTS servers is shuffled and used. |
| `v2` | `true` | Use `/v2/synthesize` (utterance as a query param); set `false` to use the legacy `/synthesize/{utterance}` path. |
| `voice` | plugin default | Voice name forwarded as a query param (omitted when unset or `"default"`). |
| `verify_ssl` | `true` | Verify the server's TLS certificate. |
| `tts_timeout` | `5` | Per-request timeout in seconds. |

---

## Docker Deployment

**Create a Dockerfile**

```dockerfile
FROM python:3.11-slim
RUN pip install ovos-tts-server
RUN pip install {YOUR_TTS_PLUGIN}
ENTRYPOINT ["ovos-tts-server", "--engine", "{YOUR_TTS_PLUGIN}"]

```

**Build & Run**

```bash
docker build -t my-ovos-tts .
docker run -p 9666:9666 my-ovos-tts

```

Pre-built containers are also available via the [ovos-docker-tts](https://github.com/OpenVoiceOS/ovos-docker-tts)
repository.

---

## Tips & Caveats

- **Default port is 9666, not 8080.** The companion plugin defaults to `/v2/synthesize`; if you point an old client at the legacy `/synthesize/{utterance}` path, set `"v2": false` in its config.

- **Audio Formats**: By default, outputs WAV (PCM). If you need MP3 or OGG, wrap with an external converter or check
  plugin support.

- **Disk Usage**: `--cache` saves every synthesis to disk; that directory grows unbounded. Omit the flag to disable caching (there is no `--no-cache` flag — caching is simply off by default).


- **Security**: Consider adding API keys or putting a reverse proxy (NGINX, Traefik) in front for SSL termination and
  rate limiting.

- **Plugin Dependencies**: Some voices require native libraries (e.g., TensorFlow). Bake them into your Docker image to
  avoid runtime surprises.

---

## Links & References

- **TTS Server GitHub**: https://github.com/OpenVoiceOS/ovos-tts-server


- **Companion Plugin**: https://github.com/OpenVoiceOS/ovos-tts-server-plugin


- **Docker Images**: https://github.com/OpenVoiceOS/ovos-docker-tts


- **OVOS Plugin Manager**: https://github.com/OpenVoiceOS/ovos-plugin-manager
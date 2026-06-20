
# `ovos-translate-server` — HTTP Translation Server

## What it Does

`ovos-translate-server` wraps any OVOS translation plugin and language-detection plugin and exposes them as a FastAPI HTTP service (served by `uvicorn`). It is the standard way to make OVOS language plugins available to remote clients or to use them as a microservice in a Docker-based deployment.

The companion client plugin `ovos-translate-server-plugin` can point an OVOS device at this server so that translation and language detection are offloaded from the device.

---

## Installation

```bash
pip install ovos-translate-server
```

Also install the translation plugin(s) you intend to serve:

```bash
pip install ovos-translate-plugin-nllb
pip install ovos-lang-detector-classics-plugin
```

---

## Running the Server

### Command Line

```bash
ovos-translate-server \
  --tx-engine ovos-translate-plugin-nllb \
  --detect-engine ovos-lang-detector-classics-plugin \
  --host 0.0.0.0 \
  --port 9686
```

CLI arguments:

| Argument | Default | Description |
|----------|---------|-------------|
| `--tx-engine` | required | OPM translation plugin (`opm.lang.translate`) entry-point name |
| `--detect-engine` | `None` | OPM language detection plugin (`opm.lang.detect`) entry-point name (optional) |
| `--host` | `0.0.0.0` | Host to bind |
| `--port` | `9686` | TCP port |

If `--detect-engine` is omitted, no dedicated detection plugin is loaded; `/detect` and `/classify` fall back to the translation plugin's own `detect()` / `detect_probs()` methods.

### Python API

```python
import uvicorn
from ovos_translate_server import start_translate_server

app, engine = start_translate_server(
    tx_engine="ovos-translate-plugin-nllb",
    detect_engine="ovos-lang-detector-classics-plugin",
)
uvicorn.run(app, host="0.0.0.0", port=9686)
```

`start_translate_server()` loads the plugins and returns `(app, engine)` where `app` is a FastAPI application; you run it with `uvicorn` (the `ovos-translate-server` CLI does exactly this). Plugin configs are read from `Configuration().get("language", {})` using the plugin name as key.

---

## HTTP API Endpoints

All endpoints accept `GET` requests. There is no authentication.

### `GET /status`

Health check. Returns the translation plugin name and its supported languages.

Response (JSON):
```json
{
  "plugin": "ovos-translate-plugin-nllb",
  "langs": ["en", "pt", "fr", ...]
}
```

---

### `GET /detect/{utterance}`

Detect the language of the given text.

| Path parameter | Description |
|----------------|-------------|
| `utterance` | The text string to classify |

Response: a language code string (e.g. `"pt"`, `"en"`, `"fr"`), returned directly from `LanguageDetector.detect()`.

Example:
```
GET /detect/o meu nome é Casimiro
→ "pt"
```

---

### `GET /classify/{utterance}`

Return per-language confidence scores for the given text.

| Path parameter | Description |
|----------------|-------------|
| `utterance` | The text string to classify |

Response: a JSON object mapping language codes to confidence floats, returned from `LanguageDetector.detect_probs()`.

Example:
```
GET /classify/hello world
→ {"en": 0.95, "de": 0.03, ...}
```

---

### `GET /translate/{tgt_lang}/{utterance}`

Translate text to the target language, auto-detecting the source language.

| Path parameter | Description |
|----------------|-------------|
| `tgt_lang` | Target language code (e.g. `"en"`, `"pt"`) |
| `utterance` | Text to translate |

Response: translated string, returned directly from `LanguageTranslator.translate(utterance, target=lang)`.

Example:
```
GET /translate/en/o meu nome é Casimiro
→ "my name is Casimiro"
```

---

### `GET /translate/{src_lang}/{tgt_lang}/{utterance}`

Translate text with an explicit source language.

| Path parameter | Description |
|----------------|-------------|
| `src_lang` | Source language code (e.g. `"pt"`) |
| `tgt_lang` | Target language code (e.g. `"en"`) |
| `utterance` | Text to translate |

Response: translated string, returned from `LanguageTranslator.translate(utterance, target=lang, source=src)`.

Example:
```
GET /translate/pt/en/o meu nome é Casimiro
→ "my name is Casimiro"
```

---

### `GET /utcp`

Returns the UTCP (Universal Tool Calling Protocol) manual describing every HTTP endpoint, so UTCP-compatible agents can discover and invoke the translation tools. No extra dependency required.

---

## Vendor-Compatible Routers

Beyond the native endpoints above, the app mounts drop-in compatible routers so clients written for hosted translation APIs can talk to this server unchanged: DeepL, DeepLX, LibreTranslate, Lingva, Amazon Translate, Google Translate and Azure Translator. See the server's `/docs` (OpenAPI) for their exact paths.

---

## MCP Server

A separate Model Context Protocol server exposes the translate/detect tools to MCP clients. It is a distinct process from the HTTP server and requires the `mcp` extra (`pip install 'ovos-translate-server[mcp]'`):

```bash
python -m ovos_translate_server.mcp_server \
  --tx-engine ovos-translate-plugin-nllb \
  --host 127.0.0.1 \
  --port 9687
```

It defaults to host `127.0.0.1` and port `9687` (note: different default host/port from the HTTP server's `0.0.0.0:9686`). The `FastMCP` instance can also be embedded into an existing FastAPI app.

---

## How It Wraps OVOS Translation Plugins

`start_translate_server()` uses two `ovos-plugin-manager` loader functions:

```python
from ovos_plugin_manager.language import load_lang_detect_plugin, load_tx_plugin
```

- `load_tx_plugin(name)` — looks up the `opm.lang.translate` entry-point group for the named plugin
- `load_lang_detect_plugin(name)` — looks up the `opm.lang.detect` entry-point group

Both return the plugin class. Each class is instantiated with an empty config:

```python
self.tx = tx_cls(config={})
self.detect = detect_cls(config={})   # only when --detect-engine is given
```

The translator (`engine.tx`) and optional detector (`engine.detect`) are held on a `TranslateEngineWrapper` and used by all FastAPI route handlers. When no detection plugin is configured, `/detect` and `/classify` call the translator's own `detect()` / `detect_probs()`.

---

## Plugin Interface

Translation plugins must implement `LanguageTranslator` from `ovos_plugin_manager.templates.language`:

```python
class LanguageTranslator:
    def translate(self, text, target="en", source="auto") -> str: ...
```

Detection plugins must implement `LanguageDetector`:

```python
class LanguageDetector:
    def detect(self, text) -> str: ...          # returns language code
    def detect_probs(self, text) -> dict: ...   # returns {lang: confidence}
```

---

## Docker

A minimal Dockerfile for serving a single plugin:

```dockerfile
FROM python:3.11

RUN pip install ovos-translate-server
RUN pip install <plugin-package>

ENTRYPOINT ovos-translate-server --tx-engine <plugin-name>
```

Build and run:

```bash
docker build . -t my-translate-server
docker run -p 9686:9686 my-translate-server
```

---

## Gotchas

- **All endpoints are `GET` with the text in the URL path.** Long or special-character utterances must be URL-encoded by the client; there is no request body and no authentication. Don't expose this server directly to untrusted networks — front it with a reverse proxy.
- The HTTP server (`9686`) and the optional MCP server (`9687`) are **separate processes** with different default hosts; running one does not start the other.

---

## Cross-References

- `ovos-plugin-manager` — `load_tx_plugin()` (`opm.lang.translate`), `load_lang_detect_plugin()` (`opm.lang.detect`), `LanguageTranslator`, `LanguageDetector`
- `ovos-google-translate-plugin` — `GoogleTranslatePlugin` (implements `LanguageTranslator`), `GoogleLangDetectPlugin` (implements `LanguageDetector`)
- `ovos-translate-server-plugin` — companion client plugin that points an OVOS device at this server
- `ovos-translate-plugin-nllb` — example translation plugin (Meta NLLB model)
- `ovos-lang-detector-classics-plugin` — example detection plugin (ensemble of classical methods)

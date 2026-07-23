# OVOS Persona Server

!!! abstract "In a nutshell"
    A "persona" is an OVOS chat character — a configured AI personality that answers questions. This server puts a persona online and makes it *look and behave like* the well-known AI chat services (such as OpenAI, Ollama, or Anthropic Claude). The practical upshot: any app or tool that already knows how to talk to one of those services can be pointed at your persona instead, with no changes — handy for plugging an OVOS persona into other software (like Home Assistant). Note it has no built-in password protection, so keep it on a trusted network. See [OVOS Personas](personas.md) and the [Glossary](glossary.md).

The OVOS Persona Server exposes any OVOS [persona](personas.md) over HTTP using the APIs of
major LLM vendors, so an OVOS persona becomes a drop-in replacement for an LLM backend in
third-party tools. Today the running server actually serves **OpenAI-** and
**Ollama-compatible** chat endpoints plus a UTCP tool surface (and MCP, if installed); modules
for Anthropic, Gemini, Cohere, AWS Bedrock and HuggingFace TGI compatibility already exist in
the package but are not yet mounted on the app the CLI starts — see the note below.

It is a FastAPI app served by `uvicorn`. A persona is loaded from a JSON file at startup; the persona's `solvers` do the actual work (anything from a local rule-based bot to a remote LLM).

---

## Install

```bash
pip install ovos-persona-server
```

Install the solver plugin(s) your persona references, e.g.:

```bash
pip install ovos-solver-openai-plugin
```

---

## Run

```bash
ovos-persona-server --persona my_persona.json --host 0.0.0.0 --port 8337
```

| Argument | Default | Description |
|----------|---------|-------------|
| `--persona` | `None` | Path to the persona `.json` file to load |
| `--host` | `0.0.0.0` | Host to bind |
| `--port` | `8337` | TCP port |

The console script is `ovos-persona-server` (module `ovos_persona_server.__main__:main`).

!!! warning "Upcoming — Agent-to-Agent (A2A) surface"
    The package ships an `ovos_persona_server.a2a` module (`create_a2a_application()`) that
    exposes a persona as an [A2A](https://google.github.io/A2A/) agent, and it is unit-tested —
    but it is **not yet wired into the CLI or the running FastAPI app**: there is no
    `--a2a-base-url` flag and no `a2a` installable extra today. Treat the A2A surface as a
    library building block, not a currently reachable endpoint.

---

## The Persona File

A persona is a JSON object whose `solvers` list names the plugins that answer queries. Per-solver config is keyed by the plugin name. Example pointing at an OpenAI-compatible LLM:

```json
{
  "name": "kb-assistant",
  "solvers": ["ovos-solver-openai-plugin"],
  "ovos-solver-openai-plugin": {
    "api_url": "https://llama.smartgic.io/v1",
    "model": "llama3.1:8b",
    "key": "sk-xxx"
  }
}
```

Solvers are tried in order; the first that returns an answer wins. Some solvers are **not** LLMs and keep no chat history — in that case only the last user message is processed.

---

## HTTP API Endpoints

| Endpoint | Method | Compatible with |
|----------|--------|-----------------|
| `/v1/chat/completions` | POST | OpenAI chat (streaming + tool calls) |
| `/v1/completions` | POST | OpenAI legacy completions |
| `/api/chat` | POST | Ollama chat |
| `/api/generate` | POST | Ollama generate |
| `/api/tags` | GET | Ollama model listing |
| `/tools/manual` | GET | UTCP tool-discovery manual |
| `/tools/{name}` | POST | UTCP tool invocation |
| `/mcp` | * | MCP streamable-HTTP transport (mounted when the `mcp` extra is installed) |

There is no authentication; put the server behind a reverse proxy if it is exposed.

!!! note "Vendor-prefixed and additional routes exist but are not mounted"
    The package also ships router modules for **Anthropic** (`/anthropic/v1/...`), **Gemini**
    (`/gemini/v1beta/models/...`), **Cohere** (`/cohere/v1/...`), **AWS Bedrock**
    (`/bedrock/model/...`), and **HuggingFace TGI** (`/tgi/...`), plus vendor-prefixed
    `/openai/v1/...` / `/ollama/api/...` aliases for the OpenAI/Ollama routes above (intended
    as the canonical paths, with `/v1`/`/api` becoming the deprecated aliases). None of these
    are actually included on the FastAPI app the `ovos-persona-server` CLI starts today — only
    the bare `/v1` and `/api` paths in the table above are reachable. Treat the vendor-prefixed
    paths, and the Anthropic/Gemini/Cohere/Bedrock/TGI compatibility surfaces, as not yet wired
    up rather than as something you can point a client at.

---

## OpenAI-Compatible Example

Point the `openai` SDK at the `/v1` path:

```python
from openai import OpenAI

client = OpenAI(
    api_key="not-needed",                       # no key required for local use
    base_url="http://localhost:8337/v1",
)

resp = client.chat.completions.create(
    model="",                                    # ignored; the persona decides
    messages=[{"role": "user", "content": "tell me a joke"}],
)
print(resp.choices[0].message.content)
```

---

## Ollama-Compatible Use

The Ollama surface (`/api/chat`, `/api/generate`, `/api/tags`) lets Ollama clients treat the
persona as a local model. For example, the
[Home Assistant Ollama integration](https://www.home-assistant.io/integrations/ollama/) can
connect directly and use the persona as its LLM backend. `/api/tags` reports the model name(s)
from the persona's solver config.

---

## Tips

- **Mind the prefix.** Clients must hit `/v1` (OpenAI) or `/api` (Ollama), not the bare host
  root — pointing a client at `http://localhost:8337` alone will 404. Tool calling is only
  supported with `stream=false`.

- Make sure your persona file's `solvers` and their config are complete; a missing plugin or model means the persona cannot answer.

- Capabilities (chat history, tool use, embeddings) depend entirely on the chosen solver plugins, so behavior varies by persona.

- For production, secure the endpoint (reverse proxy, rate limits) — the server itself is unauthenticated.

---

## Related Links

- [OVOS Personas](personas.md)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Home Assistant Ollama Integration](https://www.home-assistant.io/integrations/ollama/)

---

*Source code: [OpenVoiceOS/ovos-persona-server](https://github.com/OpenVoiceOS/ovos-persona-server).*

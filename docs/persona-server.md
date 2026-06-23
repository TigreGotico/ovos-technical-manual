# OVOS Persona Server

!!! abstract "In a nutshell"
    A "persona" is an OVOS chat character — a configured AI personality that answers questions. This server puts a persona online and makes it *look and behave like* the well-known AI chat services (such as OpenAI, Ollama, or Anthropic Claude). The practical upshot: any app or tool that already knows how to talk to one of those services can be pointed at your persona instead, with no changes — handy for plugging an OVOS persona into other software (like Home Assistant). Note it has no built-in password protection, so keep it on a trusted network. See [OVOS Personas](personas.md) and the [Glossary](glossary.md).

The OVOS Persona Server exposes any OVOS [persona](personas.md) over HTTP using the APIs of the major LLM vendors, so an OVOS persona becomes a drop-in replacement for an LLM backend in third-party tools. A single server simultaneously serves OpenAI-, Ollama-, Anthropic-, Gemini-, Cohere-, AWS Bedrock- and HuggingFace TGI-compatible endpoints, plus embeddings, MCP, UTCP and A2A surfaces.

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
| `--a2a-base-url` | `None` | Enable the A2A endpoint at `/a2a` and set its public base URL (e.g. `http://myhost:8337/a2a`). Requires the `a2a` extra. |

The console script is `ovos-persona-server` (module `ovos_persona_server.__main__:main`).

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

Endpoints are mounted under vendor-specific prefixes. Legacy unprefixed paths (`/v1/...` for OpenAI, `/api/...` for Ollama) are also mounted for backward compatibility and return a deprecation header.

| Endpoint | Method | Compatible with |
|----------|--------|-----------------|
| `/openai/v1/chat/completions` | POST | OpenAI chat (streaming + tool calls) |
| `/openai/v1/completions` | POST | OpenAI legacy completions |
| `/ollama/api/chat` | POST | Ollama chat |
| `/ollama/api/generate` | POST | Ollama generate |
| `/ollama/api/tags`, `/show`, `/ps`, `/pull`, `/push`, `/embeddings` | GET/POST | Ollama model listing + embeddings |
| `/anthropic/v1/...` | POST | Anthropic Messages |
| `/gemini/v1beta/models/...` | POST | Google Gemini |
| `/cohere/v1/...` | POST | Cohere |
| `/bedrock/model/...` | POST | AWS Bedrock |
| `/tgi/...` | POST | HuggingFace Text Generation Inference |
| `/tools/manual` | GET | UTCP tool-discovery manual |
| `/tools/{name}` | POST | UTCP tool invocation |
| `/a2a` | * | Agent-to-Agent (only when `--a2a-base-url` is set; requires the `a2a` extra) |
| `/mcp` | * | MCP streamable-HTTP transport (mounted when the `mcp` extra is installed) |

There is no authentication; put the server behind a reverse proxy if it is exposed.

---

## OpenAI-Compatible Example

Point the `openai` SDK at the OpenAI prefix (`/openai/v1`, or the legacy `/v1`):

```python
from openai import OpenAI

client = OpenAI(
    api_key="not-needed",                       # no key required for local use
    base_url="http://localhost:8337/openai/v1",
)

resp = client.chat.completions.create(
    model="",                                    # ignored; the persona decides
    messages=[{"role": "user", "content": "tell me a joke"}],
)
print(resp.choices[0].message.content)
```

---

## Ollama-Compatible Use

The Ollama surface (`/ollama/api/...`, legacy `/api/...`) lets Ollama clients treat the persona as a local model. For example, the [Home Assistant Ollama integration](https://www.home-assistant.io/integrations/ollama/) can connect directly and use the persona as its LLM backend. `/ollama/api/tags` reports the model name(s) from the persona's solver config.

---

## Tips

- **Mind the prefix.** Clients must hit `/openai/v1` (or legacy `/v1`), not the bare host root — pointing a client at `http://localhost:8337` alone will 404. Tool calling is only supported with `stream=false`.

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

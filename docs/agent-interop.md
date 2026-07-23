# Agent Interoperability: MCP, UTCP, and A2A

!!! abstract "In a nutshell"
    This page is about letting OVOS work *together with other AI systems*. OVOS can offer its abilities — like speech, translation, and reasoning — to outside AI tools, and can also call on them, using a few shared "languages" (the protocols MCP, UTCP, and A2A) so different systems can find and use each other. Think of it as agents agreeing on a common plug and socket so they can cooperate. See the [Glossary](glossary.md) for unfamiliar terms.

OVOS exposes its speech, translation, and reasoning services as first-class agent tools via two discovery/calling protocols — **MCP** (Model Context Protocol) and **UTCP** (Universal Tool Calling Protocol) — and implements bidirectional **A2A** (Agent-to-Agent) bridging.

---

## Protocol Overview

| Protocol | Discovery | Invocation | Deps |
|----------|-----------|------------|------|
| **UTCP** | `GET /utcp` → UTCP 1.0 JSON manifest | `POST /utcp/{tool}` or native HTTP endpoints | None (always on) |
| **MCP** | MCP `initialize` + `list_tools` | `call_tool` over Streamable HTTP / SSE | `pip install …[mcp]` |
| **A2A** | `GET /.well-known/agent.json` (agent card) | JSON-RPC 2.0 `tasks/send` / `tasks/sendSubscribe` | `pip install …[a2a]` |

---

## MCP + UTCP on the Service Servers

### STT Server

```bash
pip install "ovos-stt-http-server[mcp]"
ovos-stt-server --engine ovos-stt-plugin-whisper --port 9666 --mcp
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/utcp` | GET | UTCP manifest (always on, no extra package required) |
| `/mcp` | Streamable HTTP | MCP server (requires `[mcp]` extra and `--mcp` flag) |

UTCP tools exposed: `stt_status`, `stt_transcribe_v1`, `stt_transcribe_v2`.

Claude Desktop config:

```json
{
  "mcpServers": {
    "ovos-stt": {
      "transport": "http",
      "url": "http://localhost:9666/mcp"
    }
  }
}
```

### TTS Server

```bash
pip install "ovos-tts-server[mcp]"
ovos-tts-server --engine ovos-tts-plugin-piper --port 9667 --mcp
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/utcp` | GET | UTCP manifest (always on) |
| `/mcp` | Streamable HTTP | MCP server (requires `[mcp]` extra and `--mcp` flag) |

UTCP tools exposed: `tts_status`, `tts_synthesize_v2`, `tts_synthesize_legacy`.

MCP tool: `synthesize` — parameters: `text` (str), `voice` (str, optional), `lang` (str, optional). Returns base64 WAV.

```bash
# Discover all TTS tools via UTCP
curl -s http://localhost:9667/utcp | jq '.tools[].name'

# Synthesize via HTTP
curl -s 'http://localhost:9667/v2/synthesize?utterance=hello%20world' -o out.wav
```

### Translate Server

```bash
pip install "ovos-translate-server[mcp]"
python -m ovos_translate_server --tx-engine ovos-google-translate-plugin --port 9669
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/utcp` | GET | UTCP manifest (always on) |
| `/mcp` | Streamable HTTP | MCP server (requires `[mcp]` extra) |

UTCP tools: `ovos_translate.translate`, `ovos_translate.detect_language`, and the native HTTP REST endpoints.

MCP tools: `translate` (params: `text`, `target_lang`, optional `source_lang`), `detect_language` (param: `text`).

### Persona Server — Tool Plugins via MCP + UTCP

The persona server surfaces every installed OPM `ToolBox` plugin as both a UTCP tool and an MCP tool.

```bash
pip install "ovos-persona-server[mcp]"
ovos-persona-server --persona my_persona.json
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tools/manual` | GET | UTCP 1.0 manifest of all installed tool plugins |
| `/tools/{name}` | POST | Direct HTTP invocation of a tool |
| `/mcp` | SSE | MCP server (one tool per OPM ToolBox tool) |
| `/mcp` (stdio) | — | Console script `ovos-persona-tools-mcp` |

---

## A2A (Agent-to-Agent Protocol)

A2A is the [Google A2A open protocol](https://google.github.io/A2A/). An A2A server publishes a discovery document (agent card) and accepts tasks via JSON-RPC 2.0.

### Persona Server as A2A Server

```bash
pip install "ovos-persona-server[a2a]"
ovos-persona-server --persona my_persona.json --a2a-base-url http://localhost:8337
```

The `OVOSPersonaAgentExecutor` wraps the active persona and exposes it at `/a2a`. The agent card at `/a2a/.well-known/agent.json` advertises the persona's skills and capabilities. Both blocking (`tasks/send`) and streaming (`tasks/sendSubscribe`) modes are supported when the persona solver supports streaming.

### OVOS as A2A Consumer

[OpenVoiceOS/ovos-a2a-agent-plugin](https://github.com/OpenVoiceOS/ovos-a2a-agent-plugin) (pip: `ovos-a2a-solver-plugin`) is an `A2AChatEngine` `ChatEngine` plugin (OPM group `opm.agents.chat`, entry point `ovos-a2a-solver`) that delegates persona reasoning to any external A2A server.

```yaml
# persona YAML
name: my-a2a-persona
engine: ovos-a2a-solver
engine_config:
  agent_url: "https://my-a2a-agent.example.com"
  auth_header: "Bearer <token>"
  timeout: 60
  streaming: false
```

Config keys:

| Key | Default | Description |
|-----|---------|-------------|
| `agent_url` | — | Base URL of the A2A server (**required**) |
| `auth_header` | — | `Authorization` header value, e.g. `Bearer <token>` |
| `timeout` | `60` | Seconds per call |
| `streaming` | `false` | Use the SSE streaming endpoint when `true` |

---

## ovos-tool-adapters — Consuming MCP/UTCP from the Agentic Loop

[OpenVoiceOS/ovos-tool-adapters](https://github.com/OpenVoiceOS/ovos-tool-adapters) bridges external MCP and UTCP servers into the OVOS agentic loop as standard `ToolBox` plugins.

```bash
pip install ovos-tool-adapters[mcp]     # MCP support
pip install ovos-tool-adapters[utcp]    # UTCP support
```

Add to a persona JSON:

```json
{
  "name": "researcher",
  "solvers": ["ovos-react-loop"],
  "ovos-react-loop": {
    "brain": "ovos-chat-openai-plugin",
    "toolboxes": ["ovos-mcp-toolbox"],
    "ovos-mcp-toolbox": {
      "transport": "stdio",
      "command": "uvx",
      "args": ["mcp-server-fetch"],
      "timeout": 30
    }
  }
}
```

> `ovos-persona` selects its engine via `solvers` (or the legacy alias `handlers`); the agentic loop names its inner LLM with `brain` and loads adapters via `toolboxes`. The `chat_module` key seen in some READMEs is not consumed by either `ovos-persona` or `ovos-tool-adapters`.

### MCP transports (`ovos-mcp-toolbox`)

| Transport | Config |
|-----------|--------|
| stdio (subprocess) | `"transport": "stdio", "command": "uvx", "args": [...]` |
| SSE | `"transport": "sse", "url": "http://..."` |
| Streamable HTTP | `"transport": "http", "url": "http://..."` |

### UTCP (`ovos-utcp-toolbox`)

```json
{
  "toolboxes": ["ovos-utcp-toolbox"],
  "ovos-utcp-toolbox": {
    "utcp_config": {
      "tool_providers": [
        {"name": "stt", "provider_type": "http", "url": "http://localhost:9666/utcp"}
      ]
    }
  }
}
```

A background asyncio event loop keeps sessions alive between tool calls. Each server's JSON Schema is translated to a Pydantic model at discovery time so the LLM receives the actual input schema.

!!! note "`ovos-tool-adapters` and the Persona Server's own MCP/UTCP bridge"
    Both `MCPToolBox` and `UTCPToolBox` (from `ovos-tool-adapters`) and the Persona Server's tool
    surface (`/tools/manual`, `/mcp`) are `ToolBox` plugins under the same `opm.agents.toolbox`
    entry-point group, so installing `ovos-tool-adapters` alongside `ovos-persona-server` also
    exposes the bridged external tools through the Persona Server's own MCP/UTCP endpoints.
    Every shipped `ToolBox` implementation (`DuckDuckGoToolbox`, `WikipediaToolbox`, `MCPToolBox`,
    `UTCPToolBox`, ...) takes a single optional `config` dict and derives its own `toolbox_id`
    internally, rather than the literal `toolbox_id` keyword declared by the abstract `ToolBox`
    template — the Persona Server tries the no-argument/config-based convention first, since it
    matches every real-world plugin, and only falls back to the template's `toolbox_id` kwarg for
    a class that still inherits the base `__init__` unchanged.

## Further reading

- [Building an Open and Interoperable Voice Ecosystem (MCP / UTCP / A2A)](https://blog.openvoiceos.org/posts/2025-10-24-protocol_interoperability) — OVOS blog

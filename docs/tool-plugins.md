# Agent Tool Plugins

The OPM `ToolBox` framework provides a standardized mechanism for exposing discoverable, schema-validated functions to OVOS agents (persona solvers, agentic loops, MCP/UTCP clients).

This page covers the plugin ecosystem, the PHAL bus provider, and integration with agentic loops. For full authoring documentation see the [upstream OpenVoiceOS technical manual](https://openvoiceos.github.io/ovos-technical-manual/tools.html).

---

## OPM ToolBox Interface

Source: [OpenVoiceOS/ovos-plugin-manager#340](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/340) (merged).

Every `ToolBox` plugin:

1. Declares its tools via `discover_tools()`, returning a list of `AgentTool` instances.
2. Each `AgentTool` carries Pydantic `argument_schema` and `output_schema` models — these are converted to JSON Schema for LLM tool-use / function-calling.
3. Registers MessageBus handlers automatically when a bus is injected.

### Plugin entry point

```python
# pyproject.toml
[project.entry-points."opm.agents.toolbox"]
my-toolbox = "my_package:MyToolBox"
```

### Authoring a ToolBox plugin

The full authoring guide with `AgentTool`, `ToolArguments`, and `ToolOutput` examples is embedded in the [tools.md page in the upstream OpenVoiceOS manual](https://openvoiceos.github.io/ovos-technical-manual/tools.html) and mirrors the [OPM PR #340 docs](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/340).

---

## PHAL Bus Provider

[TigreGotico/ovos-PHAL-plugin-tools](https://github.com/TigreGotico/ovos-PHAL-plugin-tools) is a PHAL plugin that loads all installed `ToolBox` plugins and registers them on the MessageBus, making them available to any component that can send bus messages.

```bash
pip install ovos-PHAL-plugin-tools
```

Entry point: `ovos.plugin.phal` / `ovos-phal-plugin-tools`.

### MessageBus event table

| Message type | Direction | Description |
|---|---|---|
| `ovos.tools.discover` | → PHAL | Request list of all registered tools and their schemas |
| `ovos.tools.discover.response` | PHAL → | Response with JSON Schema list of all tools |
| `ovos.tools.<toolbox_id>.call` | → PHAL | Invoke a named tool in a specific toolbox |
| `ovos.tools.<toolbox_id>.call.response` | PHAL → | Tool result or error |

### Discovery payload

```json
{
  "type": "ovos.tools.discover.response",
  "data": {
    "tools": [
      {
        "name": "web_search",
        "description": "Searches the web for information...",
        "toolbox_id": "ovos-web-search-tools",
        "argument_schema": { "type": "object", "properties": {...}, "required": [...] },
        "output_schema": { "type": "object", "properties": {...} }
      }
    ]
  }
}
```

### Tool call payload

```json
{
  "type": "ovos.tools.ovos-web-search-tools.call",
  "data": { "name": "web_search", "kwargs": {"query": "OVOS voice assistant"} }
}
```

---

## ovos-agentic-loop Toolboxes

[ovos-agentic-loop](agentic-loop.md) bundles five ready-to-use toolboxes:

| Entry point | Key tools |
|---|---|
| `ovos-math-tools` | `evaluate_expression`, `unit_convert`, `statistics_summary` |
| `ovos-filesystem-tools` | `read_file`, `write_file`, `list_directory`, `find_files` |
| `ovos-shell-tools` | `run_command` (disabled by default) |
| `ovos-web-search-tools` | `web_search` |
| `ovos-clock-tools` | `get_current_datetime` |
| `ovos-skill-md-toolbox` | One tool per installed `SKILL.md` |

Wire them into a persona:

```json
{
  "name": "researcher",
  "solvers": ["ovos-react-loop"],
  "ovos-react-loop": {
    "brain": "ovos-chat-openai-plugin",
    "toolboxes": ["ovos-math-tools", "ovos-web-search-tools"]
  }
}
```

---

## Exposing Tools over MCP / UTCP

The Persona Server can bridge any installed ToolBox plugin to MCP and UTCP clients. See [agent-interop.md#persona-server-tool-plugins-via-mcp-utcp](agent-interop.md#persona-server-tool-plugins-via-mcp-utcp).

---

## Related Pages

- [agentic-loop.md](agentic-loop.md) — loop architectures
- [agent-interop.md](agent-interop.md) — MCP/UTCP/A2A integration

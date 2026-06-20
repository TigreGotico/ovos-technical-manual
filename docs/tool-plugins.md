# Agent Tool Plugins

The OPM `ToolBox` framework provides a standardized mechanism for exposing discoverable, schema-validated functions to OVOS agents (persona solvers, agentic loops, MCP/UTCP clients).

This page covers the plugin ecosystem, the PHAL bus provider, and integration with agentic loops. For full authoring documentation see the [Plugin Manager reference](plugin-manager.md).

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

The full authoring guide with `AgentTool`, `ToolArguments`, and `ToolOutput` examples is embedded in the [Plugin Manager reference](plugin-manager.md) and mirrors the [OPM PR #340 docs](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/340).

---

## PHAL Bus Provider

[TigreGotico/ovos-PHAL-plugin-tools](https://github.com/TigreGotico/ovos-PHAL-plugin-tools) is a PHAL plugin that loads all installed `ToolBox` plugins and registers them on the MessageBus, making them available to any component that can send bus messages.

```bash
pip install ovos-PHAL-plugin-tools
```

Entry point group: `opm.phal`; plugin name `ovos-phal-plugin-tools`.

### MessageBus event table

| Message type | Direction | Payload |
|---|---|---|
| `ovos.tools.list` | → plugin | *(none)* |
| `ovos.tools.list.response` | plugin → | `{tools: [{name, description, argument_schema, output_schema, toolbox_id}]}` |
| `ovos.tools.get` | → plugin | `{name: str}` |
| `ovos.tools.get.response` | plugin → | Full schema dict or `{error: str}` |
| `ovos.tools.invoke` | → plugin | `{name: str, args: dict}` |
| `ovos.tools.invoke.response` | plugin → | `{name, result: dict}` or `{name, error: str}` |
| `ovos.tools.reload` | → plugin | *(none)* |
| `ovos.tools.reload.response` | plugin → | `{loaded: [str, ...], total_tools: int}` |

Every request is answered — unknown tools, bad arguments, and tool exceptions
come back as an `error` field, never silence.

### Third-party usage

```python
from ovos_bus_client import MessageBusClient
from ovos_bus_client.message import Message

bus = MessageBusClient()
bus.run_in_thread()

tools = bus.wait_for_response(Message("ovos.tools.list"))
schema = bus.wait_for_response(Message("ovos.tools.get", {"name": "add"}))
result = bus.wait_for_response(Message("ovos.tools.invoke",
                                       {"name": "add", "args": {"a": 1, "b": 2}}))
```

---

## ovos-agentic-loop Toolboxes

[ovos-agentic-loop](agentic-loop.md) bundles six ready-to-use toolboxes:

| Entry point | Key tools |
|---|---|
| `ovos-math-tools` | `evaluate_expression`, `unit_convert`, `statistics_summary`, `solve_equation` |
| `ovos-filesystem-tools` | `read_file`, `write_file`, `list_directory`, `search_in_files`, `find_files` |
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

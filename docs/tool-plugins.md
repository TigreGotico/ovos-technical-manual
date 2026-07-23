# Agent Tool Plugins

!!! abstract "In a nutshell"
    These plugins give an AI assistant real *abilities* it can reach for — like fetching information or performing an action — rather than only talking. Each "tool" is described in a standard way so the AI knows what it does and what information it needs, much like labeled buttons on a control panel. See [Agentic Loops](agentic-loop.md) for how an assistant decides to use them, and the [Glossary](glossary.md) for unfamiliar terms.

The OPM `ToolBox` framework provides a standardized mechanism for exposing discoverable, schema-validated functions to OVOS agents (persona solvers, agentic loops, MCP/UTCP clients). For full authoring documentation see the [Plugin Manager reference](plugin-manager.md).

---

## OPM ToolBox Interface

Every `ToolBox` plugin:

1. Declares its tools via `discover_tools()`, returning a list of `AgentTool` instances.
2. Each `AgentTool` carries Pydantic `argument_schema` and `output_schema` models — these are converted to JSON Schema for LLM tool-use / function-calling.
3. Registers messagebus handlers automatically when a bus is injected.

### Plugin entry point

```python
# pyproject.toml
[project.entry-points."opm.agents.toolbox"]
my-toolbox = "my_package:MyToolBox"
```

### Authoring a ToolBox plugin

A minimal `ToolBox` implementing a single `add` tool:

```python
from typing import List
from ovos_plugin_manager.templates.agent_tools import ToolBox, AgentTool, ToolArguments, ToolOutput

class AddArgs(ToolArguments):
    a: float
    b: float

class AddResult(ToolOutput):
    sum: float

def add(args: AddArgs) -> AddResult:
    return AddResult(sum=args.a + args.b)

class MathToolBox(ToolBox):
    def discover_tools(self) -> List[AgentTool]:
        return [
            AgentTool(
                name="add",
                description="Add two numbers together.",
                argument_schema=AddArgs,
                output_schema=AddResult,
                tool_call=add,
            )
        ]
```

`ToolBox.__init__` calls `discover_tools()` immediately to populate `self.tools`, and `bind(bus)`
registers the messagebus handlers described below. The full authoring guide with more
`AgentTool`, `ToolArguments`, and `ToolOutput` examples is embedded in the
[Plugin Manager reference](plugin-manager.md).

---

## PHAL Bus Provider

[OpenVoiceOS/ovos-PHAL-plugin-tools](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-tools) is a PHAL plugin that loads all installed `ToolBox` plugins and registers them on the messagebus, making them available to any component that can emit bus messages.

```bash
pip install ovos-PHAL-plugin-tools
```

Entry point group: `opm.phal`; plugin name `ovos-phal-plugin-tools`.

### messagebus event table

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

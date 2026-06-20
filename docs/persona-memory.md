# Persona Memory Plugins

**What this is:** a pluggable way to control what an OVOS persona "remembers". Instead of a fixed conversation buffer, a memory plugin decides which past messages (and any summaries or retrieved snippets) get prepended to the LLM call on each turn, and how that history is persisted across turns and sessions.

Persona memory is managed through the `AgentContextManager` interface (OPM `opm.agents.memory`), introduced in [OpenVoiceOS/ovos-plugin-manager#363](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/363) (merged). Integration into `ovos-persona` landed in [OpenVoiceOS/ovos-persona#143](https://github.com/OpenVoiceOS/ovos-persona/pull/143) (merged).

---

## Interface

```python
from ovos_plugin_manager.templates.agents import AgentContextManager, AgentMessage

class MyMemory(AgentContextManager):  # all three methods are abstract
    def build_conversation_context(self, utterance: str, session_id: str) -> List[AgentMessage]:
        """Messages to prepend before the current utterance (system prompt,
        summaries, retrieved history, tool definitions)."""
        ...

    def get_history(self, session_id: str) -> List[AgentMessage]:
        """Return the stored history for a session (plugins may trim/summarize here)."""
        ...

    def update_history(self, new_messages: List[AgentMessage], session_id: str) -> None:
        """Append new turns after each interaction. Takes a list of messages,
        not a single exchange tuple."""
        ...
```

`AgentMessage` (`role`, `content`, optional `tool_calls` / `tool_call_id` / `name`) is the canonical message type. The short-term memory previously hard-coded in `ovos-persona` is now a plugin under this interface, so all memory strategies are composable.

---

## Per-Session Persona Tracking

[OpenVoiceOS/ovos-persona#140](https://github.com/OpenVoiceOS/ovos-persona/pull/140) (merged, built on ovos-bus-client#192) adds session isolation to persona management:

- Each `Session` can activate a different persona.
- Conversation history is tracked per session, not globally.
- Enables: different persona per wake word, different TTS voice per persona, distinct persona for each HiveMind satellite.

Configure via the session `active_persona` field or the `ovos.persona.set` bus message.

---

## Plugin Wiring

In a persona JSON or YAML file, set `memory_module` to the plugin entry point:

```json
{
  "name": "MyAssistant",
  "handlers": ["ovos-solver-openai-plugin"],
  "memory_module": "ovos-memory-plugin-longterm",
  "ovos-memory-plugin-longterm": {
    "api_url": "http://localhost:8000/v1",
    "summarize_every": 8,
    "recent_window": 4
  }
}
```

---

## Available Plugins (ovos-memory-plugins)

[TigreGotico/ovos-memory-plugins](https://github.com/TigreGotico/ovos-memory-plugins) packages two `AgentContextManager` implementations.

```bash
pip install ovos-memory-plugins
```

### ovos-memory-plugin-longterm

Rolling summarization with a verbatim recent window. Older turns are compressed by a local LLM; the summary + the most recent exchanges are injected as context.

| Key | Default | Description |
|-----|---------|-------------|
| `api_url` | `http://192.168.1.200:8000/v1` | OpenAI-compatible chat endpoint for summarization |
| `model` | auto-detected | Model name |
| `summarize_every` | `6` | Exchanges before triggering summarization |
| `max_summary_tokens` | `256` | `max_tokens` for the summarization request |
| `recent_window` | `4` | Verbatim exchanges kept after summarization |
| `backend` | `"json"` | `"json"` or `"sqlite"` |
| `db_path` | `~/.local/share/ovos/longterm_memory.{json,db}` | Persistence path |
| `system_prompt` | `""` | Persona system prompt prepended to every context |
| `request_timeout` | `30` | HTTP timeout in seconds |

### ovos-memory-plugin-rag

Stores every exchange as a vector-indexed document using an OpenAI-compatible files/embeddings API, then retrieves the top-k semantically similar past turns at query time.

| Key | Default | Description |
|-----|---------|-------------|
| `api_url` | `http://192.168.1.200:8000/v1` | OpenAI-compatible endpoint (embeddings + vector stores) |
| `top_k` | `3` | Number of retrieved documents to inject |
| `collection` | `"ovos_memory"` | Vector store collection name |
| `min_score` | `0.0` | Minimum similarity to inject a retrieved turn |
| `request_timeout` | `30` | HTTP timeout in seconds |
| `inject_as_system` | `false` | Inject retrieved turns into the system message instead of as prior turns |

Fallback: if the vector store endpoint is unavailable, in-process cosine similarity is used.

!!! warning "Upcoming — unreleased"
    [OpenVoiceOS/ovos-memory-plugins#9](https://github.com/OpenVoiceOS/ovos-memory-plugins/pull/9) (`feat!`, open) makes this plugin **fully local**: it replaces the server-coupled `ovos-memory-plugin-rag` / `RAGMemory` with `ovos-memory-plugin-local-rag` / `LocalRAGMemory`, which embeds and stores exchanges in-process via OVOS embeddings plugins (`opm.embeddings.text` + `EmbeddingsDB`) — no network, no cloud key. `ovos-memory-plugins` is local-first only; any server- or OpenAI-coupled RAG lives in `ovos-openai-plugin` instead. After that PR lands, the entry point above and its `api_url`-based config no longer apply.

---

## Plugin Entry Points

| Entry point | Class |
|---|---|
| `ovos-memory-plugin-longterm` | `LongTermMemory` |
| `ovos-memory-plugin-rag` | `RAGMemory` |

---

## Related Pages

- [Personas](personas.md)
- [Agent Tool Plugins](tool-plugins.md)
- [Agent Interoperability](agent-interop.md)

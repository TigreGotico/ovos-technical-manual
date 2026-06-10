# Persona Memory Plugins

Persona memory is managed through the `AgentContextManager` interface (OPM `opm.agents.memory`), introduced in [OpenVoiceOS/ovos-plugin-manager#363](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/363) (merged). Plugins build the conversation context — the list of messages sent to the LLM before each turn — and persist history between turns and sessions.

Integration into `ovos-persona` is tracked in [OpenVoiceOS/ovos-persona#143](https://github.com/OpenVoiceOS/ovos-persona/pull/143) (open).

---

## Interface

```python
class AgentContextManager:
    def build_conversation_context(
        self,
        utterance: str,
        session_id: str = "default",
    ) -> list[AgentMessage]:
        """Return messages to prepend before the current utterance."""
        ...

    def update_history(
        self,
        exchange: tuple[AgentMessage, AgentMessage],
        session_id: str = "default",
    ) -> None:
        """Called after each completed user/assistant exchange."""
        ...
```

The short-term memory that was previously hard-coded in `ovos-persona` is packaged as a plugin under the same interface, so all memory strategies are composable.

---

## Per-Session Persona Tracking

[OpenVoiceOS/ovos-persona#140](https://github.com/OpenVoiceOS/ovos-persona/pull/140) (open, depends on ovos-bus-client#192) adds session isolation to persona management:

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

Fallback: if the vector store endpoint is unavailable, in-process cosine similarity is used.

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

# Persona Memory Plugins

!!! abstract "In a nutshell"
    This controls what your assistant's persona *remembers* from earlier in a conversation. Rather than always carrying the whole chat along, a memory plugin decides which past messages — or short summaries of them — to bring back into the next reply, like a notepad that keeps the bits worth keeping. It also decides whether those notes survive between separate conversations. See [AI Agents & Personas](personas.md) for the bigger picture and the [Glossary](glossary.md) for unfamiliar terms.

**What this is:** a pluggable way to control what an OVOS persona "remembers". Instead of a fixed conversation buffer, a memory plugin decides which past messages (and any summaries or retrieved snippets) get prepended to the LLM call on each turn, and how that history is persisted across turns and sessions.

Persona memory is managed through the `AgentContextManager` interface (OPM `opm.agents.memory`), which `ovos-persona` loads for each persona. The persona owns the chat engine and tools; the memory plugin owns **conversation state and context assembly**, composing with any chat backend instead of generating answers itself.

`ovos-memory-plugins` is **local-first**: most backends need no external service at all. Only `longterm` and `entity` call an OpenAI-compatible chat endpoint — and that endpoint can be your own local LLM, never a hosted provider.

```bash
pip install ovos-memory-plugins
```

---

## Interface

```python
from ovos_plugin_manager.templates.agents import AgentContextManager, AgentMessage

class MyMemory(AgentContextManager):  # all three methods are abstract
    def get_history(self, session_id: str) -> List[AgentMessage]:
        """Return the stored history for a session (plugins may trim/summarize here)."""
        ...

    def update_history(self, new_messages: List[AgentMessage], session_id: str) -> None:
        """Append new turns after each interaction. Takes a list of messages,
        not a single exchange tuple."""
        ...

    def build_conversation_context(self, utterance: str, session_id: str) -> List[AgentMessage]:
        """Messages to prepend before the current utterance (system prompt,
        summaries, retrieved history, tool definitions)."""
        ...
```

`AgentMessage` (`role`, `content`, optional `tool_calls` / `tool_call_id` / `name`) is the canonical message type, from `ovos_plugin_manager.templates.agents`. The persona calls `build_conversation_context` before each turn and `update_history` after each exchange.

Two rules hold for every backend in this package:

- the **first** message MAY be a `system` message carrying the persona's `system_prompt`;
- the **last** message is ALWAYS the current user utterance.

The short-term memory previously hard-coded in `ovos-persona` is now a plugin under this interface, so all memory strategies are composable.

---

## Per-Session Persona Tracking

Persona management is session-isolated:

- Each `Session` can activate a different persona.
- Conversation history is tracked per session, not globally.
- Enables: different persona per wake word, different TTS voice per persona, distinct persona for each HiveMind satellite.

Configure via the session `active_persona` field or the `ovos.persona.set` bus message.

---

## Plugin Wiring

In a persona JSON or YAML file, set `memory_module` to the plugin entry point, and give that entry point its own config block:

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

A persona selects exactly **one** backend — but that one may be `ovos-memory-plugin-composite`, which loads and consolidates several of the others.

---

## Choosing a backend

| | longterm | local-rag | lexical | recency | entity | composite |
|---|---|---|---|---|---|---|
| Entry point | `…-longterm` | `…-local-rag` | `…-lexical` | `…-recency` | `…-entity` | `…-composite` |
| Recall style | rolling **summary** | **semantic** top-k | **keyword** (BM25) | recent window | durable **facts** | **ensemble** of members |
| External service | chat endpoint | none | none | none | chat endpoint | members' |
| Extra deps | none | embeddings + vector DB | **none** (stdlib) | **none** | none | members' |
| Runs fully offline | if LLM is local | yes | yes | yes | if LLM is local | if members do |
| Persistence | JSON / SQLite | vector DB | SQLite | optional JSON | JSON | members' |
| Best for | gist of long chats | exact semantic recall | exact-term recall | plain short-term | user preferences | hybrid / combine all |

Rules of thumb:

- Private/offline assistant needing specifics → **local-rag** (semantic) and/or **lexical** (keywords); combine them with **composite** for hybrid recall.
- Remember *who the user is* across sessions → **entity**.
- Just the last few turns → **recency**.
- A running gist of very long chats and you have an LLM endpoint → **longterm**.

---

## Shared retrieval mechanics

The retrieval backends (`local-rag`, `lexical`) and the `composite` share a `BaseRetrievalMemory` that folds recalled context into the conversation via a configurable `inject_mode`.

### Inject modes

| `inject_mode` | What it does | When to use |
|---|---|---|
| `system` (default) | Retrieved context goes in a **separate** `system` message; the persona's `system_prompt` stays its own message | Keeps the base prompt stable/cacheable; safe default |
| `developer` | Same, but a `developer`-role message | Providers that distinguish developer from system instructions |
| `system_prompt` | Context folded into the persona's system prompt (one combined `system` message) | Backends that only honour a single system message |
| `user` | Context prepended to the final user message | Backends that ignore system/developer roles |
| `tool` | A synthetic assistant `tool_calls` turn + its `tool` result carry the context, just before the user turn | Tool-calling brains; presents recall as a search-tool result. Needs the `ovos-plugin-manager` TOOL contract |

### Retrieval knobs

Set under the backend's `retrieval` block:

- `max_num_results` (default `5`) — top-k documents per query.
- `min_score` (default `null`) — drop hits below this score; `null` keeps all. Scale is backend specific: `local-rag` is `1 - cosine_distance` (~0..1), `lexical` is `-bm25`.
- `query_mode` (default `utterance`) — `utterance` searches on the current turn; `history` folds the last `query_history_turns` (default `3`) user turns into the search query for follow-up questions.

---

## Backends

### ovos-memory-plugin-longterm

Class `LongTermMemory`. Keeps a compact **rolling summary** of a long conversation with a verbatim recent window. Every `summarize_every` exchanges it sends the oldest turns to an OpenAI-compatible chat endpoint, replaces them with the returned summary, and keeps only `recent_window` exchanges verbatim. The summary plus the recent window are persisted per session (JSON or SQLite).

**Use it when** a *gist* of the conversation is enough and you already have an LLM endpoint — it trades exact recall for a bounded, cheap-to-carry context.

| Key | Default | Description |
|-----|---------|-------------|
| `api_url` | `http://localhost:8000/v1` | OpenAI-compatible chat endpoint for summarization |
| `model` | auto-detected (`""`) | Model name; resolved from the server when empty |
| `summarize_every` | `6` | Exchanges before triggering summarization |
| `max_summary_tokens` | `256` | `max_tokens` for the summarization request |
| `recent_window` | `4` | Verbatim exchanges kept after summarization |
| `backend` | `"json"` | `"json"` or `"sqlite"` |
| `db_path` | `~/.local/share/ovos/longterm_memory.{json,db}` | Persistence path |
| `system_prompt` | `""` | Persona system prompt prepended to every context |
| `request_timeout` | `30` | HTTP timeout in seconds |

### ovos-memory-plugin-local-rag

Class `LocalRAGMemory`. Runs Retrieval-Augmented Generation **entirely in-process**: it loads an OVOS text-embeddings plugin (`opm.embeddings.text`) and an `EmbeddingsDB` plugin directly — no HTTP, no cloud key — embedding every exchange and retrieving the top-k **semantically** similar past turns at query time. This is the local-first replacement for any server- or OpenAI-coupled RAG; server-coupled RAG lives in [`ovos-openai-plugin`](openai-plugin.md) instead.

**Use it when** a private/offline assistant needs exact semantic recall of past detail.

Install the known-good offline stack with the extra:

```bash
pip install 'ovos-memory-plugins[local-rag]'
```

which pulls `ovos-gguf-embeddings-plugin` (labse gguf embeddings) + `ovos-chromadb-embeddings-plugin` (persistent local vector store). Any embeddings + `EmbeddingsDB` pair works (e.g. point `embeddings_db_plugin` at `ovos-qdrant-embeddings-plugin`).

| Key | Default | Notes |
|---|---|---|
| `embeddings_plugin` | `ovos-gguf-embeddings-plugin` | any `opm.embeddings.text` entry point |
| `embeddings_config` | `{}` | forwarded to the embeddings plugin constructor |
| `embeddings_db_plugin` | `ovos-chromadb-embeddings-plugin` | any `opm.embeddings` (`EmbeddingsDB`) entry point |
| `embeddings_db_config` | `{}` | forwarded to the DB constructor (chromadb takes `path`) |
| `collection` | `ovos_local_rag` | collection name (chromadb: 3-512 chars from `[a-zA-Z0-9._-]`) |
| `retrieval.max_num_results` | `5` | top-k |
| `retrieval.min_score` | `null` | similarity threshold in `[0, 1]` (`score = 1 - distance`); `null` keeps all |
| `retrieval.query_mode` / `query_history_turns` | `utterance` / `3` | fold recent user turns into the query |
| `context.*` | — | rendering of the retrieved chunk block |
| `inject_mode` | `system` | see the inject-modes table above |
| `system_prompt` | `""` | persona base prompt |
| `max_history` | `10` | recent verbatim messages retained per session |

Document ids are stable and deterministic (`"<session_id>_<n>"`), so storage and tests are reproducible.

### ovos-memory-plugin-lexical

Class `LexicalMemory`. Recalls prior exchanges by **keyword** match using SQLite's built-in FTS5 full-text index and its `bm25()` ranking. It needs **no extra dependencies** (`sqlite3` is stdlib, FTS5 ships with CPython's bundled SQLite), runs fully offline, and persists to a single `.db` file. It is a retriever (exposes `search()`), so it works standalone *and* as a composite member.

**Use it when** you need exact-term recall — names, codes, IDs, rare words — that dense embeddings blur. Pair it with `local-rag` through the composite for hybrid recall.

| Key | Default | Description |
|---|---|---|
| `db_path` | `~/.local/share/ovos/lexical_memory.db` | SQLite file. Use `":memory:"` for an ephemeral store |
| `table` | `lexical_memory` | FTS5 virtual-table name |
| `retrieval.max_num_results` | `5` | Max documents per query |
| `retrieval.min_score` | `null` | Drop hits below this BM25-derived score (`score = -bm25`) |
| `retrieval.query_mode` / `query_history_turns` | `utterance` / `3` | Fold recent user turns into the query |
| `context.*` | — | Chunk rendering (shared with the other retrievers) |
| `inject_mode` | `system` | `system` \| `developer` \| `system_prompt` \| `user` \| `tool` |
| `system_prompt` | `""` | Persona system prompt |
| `max_history` | `10` | Recent verbatim messages kept per session |

!!! note "Score scale"
    Lexical `score = -bm25` is **not** on the 0..1 cosine scale of `local-rag`. Set `min_score` accordingly, and when combining retrievers prefer the composite's rank-based `rrf` fusion rather than comparing raw scores.

### ovos-memory-plugin-recency

Class `RecencyMemory`. Keeps a sliding window of the most **recent** turns, bounded by a message count and optionally by age (time decay). It is the lightest possible memory: no LLM, no embeddings, **no extra dependencies**, fully local.

**Use it when** plain short-term context is all you need, or as the `primary` (history-providing) member inside a composite alongside heavier recall backends.

| Key | Default | Description |
|---|---|---|
| `max_history` | `10` | Messages kept verbatim. `0` = unbounded |
| `max_age` | `null` | If set, drop messages older than this many seconds (decay) |
| `system_prompt` | `""` | Persona system prompt |
| `db_path` | `null` | Optional JSON file; when set, the window persists across restarts |

`build_conversation_context` returns `[system?] + recent window + [USER utterance]`. JSON persistence stores message role and content; tool-call structure (`tool_calls`, `tool_call_id`) is not persisted across restarts.

### ovos-memory-plugin-entity

Class `EntityMemory`. Distills **durable facts** about the user — name, preferences, relationships, constraints, goals — and re-injects them into every turn. After each exchange it asks a **local** OpenAI-compatible endpoint to extract short fact lines, then merges them (deduplicated) into a per-session fact store. Local-first, same kind of endpoint `longterm` uses. If the endpoint is unreachable, extraction simply no-ops and the turn proceeds.

**Use it when** you want the assistant to remember *who the user is* across sessions, no matter how long ago a fact was said — without embeddings or a vector store.

| Key | Default | Description |
|---|---|---|
| `api_url` | `http://localhost:8000/v1` | OpenAI-compatible endpoint |
| `model` | auto-detected (`""`) | Model name; pulled from the server when empty |
| `max_facts` | `50` | Cap per session (oldest dropped past the cap) |
| `max_extract_tokens` | `128` | `max_tokens` for the extraction call |
| `request_timeout` | `30` | HTTP timeout in seconds |
| `backend` | `"json"` | `"json"` (persisted) or `"memory"` (ephemeral) |
| `db_path` | `~/.local/share/ovos/entity_memory.json` | JSON store path |
| `extraction_prompt` | built-in | Override the extraction template (must contain `{exchange}`) |
| `facts_header` | `Known facts about the user:` | Heading for the injected block |
| `system_prompt` | `""` | Persona system prompt |

### ovos-memory-plugin-composite

Class `CompositeMemory`. A **pure ensemble orchestrator**: it loads several member memory plugins by name (via `ovos-plugin-manager`) and consolidates them, so a persona's single `memory_module` slot can combine many memories. It stores and retrieves nothing itself — every contribution comes from a member.

How it consolidates:

- **Retriever members** (anything exposing `search() -> List[MemoryHit]`, e.g. `local-rag`, `lexical`) have their hits **fused** into one ranked, deduplicated list (RRF by default), rendered once and injected per the composite's own `inject_mode`.
- **Plain members** (`longterm`, `entity`, `recency`, …) contribute their leading `system`/`developer` block(s) — a rolling summary, known facts, etc. Their own history and user turn are ignored.
- **History** comes from the designated `primary` member (default: the first).
- **`update_history` is written through to every member**, so each advances its own state.
- **Fault tolerance:** members that fail to load, or raise at runtime, are skipped — the composite keeps working with whatever remains. With zero members it is a harmless passthrough.

**Use it when** you want hybrid recall (e.g. semantic + lexical) or to layer durable facts on top of recall — combining several backends behind one slot.

| Key | Default | Description |
|---|---|---|
| `members` | `[]` | Ordered list of `{module, config, weight}`. Each member gets **only** its own `config` block |
| `primary` | first member | Member whose `get_history` provides the verbatim history |
| `fusion` | `rrf` | `rrf` \| `weighted` \| `merge` \| `priority` \| `interleave` |
| `rrf_k` | `60` | RRF constant |
| `max_num_results` | `5` | Size of the final fused list |
| `member_fetch_k` | `2×max_num_results` | Candidates pulled from each member before fusing |
| `dedup` | `true` | Deduplicate by content (for `merge` / `interleave`) |
| `inject_mode` | `system` | How the fused context is injected (same modes as the retrievers) |
| `system_prompt` | `""` | Persona system prompt |

```jsonc
{
  "memory_module": "ovos-memory-plugin-composite",
  "ovos-memory-plugin-composite": {
    "members": [
      {"module": "ovos-memory-plugin-local-rag", "weight": 1.0, "config": { /* its block */ }},
      {"module": "ovos-memory-plugin-lexical",   "weight": 1.0, "config": { /* its block */ }},
      {"module": "ovos-memory-plugin-entity",    "config": { /* its block */ }}
    ],
    "primary": "ovos-memory-plugin-local-rag",
    "fusion": "rrf",
    "max_num_results": 5,
    "inject_mode": "system"
  }
}
```

**Why RRF is the default.** Different retrievers score on incompatible scales: semantic cosine similarity is ~0..1, lexical BM25 is unbounded. Summing raw scores would let the larger-magnitude scale dominate. RRF (`score(d) = Σ weight · 1/(k + rank)`) throws magnitudes away and fuses on **rank position** only, so a semantic top-1 and a lexical top-1 count equally — the standard hybrid-search fusion. Give each retriever member a **distinct** storage path/collection so they don't collide, and leave `system_prompt` to the composite.

---

## Plugin Entry Points

All six backends are registered under the `opm.agents.memory` group.

| Entry point | Class |
|---|---|
| `ovos-memory-plugin-longterm` | `LongTermMemory` |
| `ovos-memory-plugin-local-rag` | `LocalRAGMemory` |
| `ovos-memory-plugin-lexical` | `LexicalMemory` |
| `ovos-memory-plugin-recency` | `RecencyMemory` |
| `ovos-memory-plugin-entity` | `EntityMemory` |
| `ovos-memory-plugin-composite` | `CompositeMemory` |

---

## Writing your own backend

A memory backend is an `AgentContextManager`. There are two starting points:

- **A retrieval backend** (stores items, recalls them by search): subclass `BaseRetrievalMemory` and implement `_store_document` and `_query_backend` (returning ranked `MemoryHit`s). You inherit history handling, the five inject modes, the context renderer, and a `search()` that lets the composite fuse you with other retrievers.
- **Anything else** (a summary, a fact store, a custom rule): subclass `AgentContextManager` and implement the three contract methods directly. Add a `search()` method to also be fusable as a composite retriever.

Register the class under the `opm.agents.memory` entry-point group in your package's `pyproject.toml`, then select it from a persona with `memory_module`.

---

## Related Pages

- [Personas](personas.md)
- [Agent Tool Plugins](tool-plugins.md)
- [Agent Interoperability](agent-interop.md)

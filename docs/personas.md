# AI Agents & Personas in OpenVoiceOS

OpenVoiceOS (OVOS) provides a flexible, modular system for integrating AI agents into voice-first
environments. The architecture is built in layers: low-level **agent engine plugins** registered
through OPM, named **personas** that combine one or more engines into a conversational identity,
and the **PersonaService** pipeline plugin that routes live utterances to the right persona at
runtime.

---

## Agent Engine Plugins (OPM `opm.agents.*`)

Agent engines are the building blocks. Each engine type solves one well-defined sub-problem. They
are discovered and loaded by `ovos-plugin-manager` at runtime using Python entry points.

| Entry point group | Base class | Purpose |
|---|---|---|
| `opm.agents.chat` | `ChatEngine` | Multi-turn conversational LLM |
| `opm.agents.chat.multimodal` | `MultimodalChatEngine` | Chat + vision/audio/files (base64) |
| `opm.agents.multimodal_adapter` | `MultimodalAdapter` | Describe non-text content as text |
| `opm.agents.summarizer` | `SummarizerEngine` | Condense long text to a few sentences |
| `opm.agents.summarizer.chat` | `ChatSummarizerEngine` | Compress structured chat history |
| `opm.agents.reranker` | `ReRankerEngine` | Score and rank candidate answers |
| `opm.agents.option_matcher` | `OptionMatcherEngine` | Match an utterance to a fixed option set |
| `opm.agents.extractive_qa` | `ExtractiveQAEngine` | Extract the best passage from evidence |
| `opm.agents.nli` | `NaturalLanguageInferenceEngine` | Entailment prediction (premise → hypothesis) |
| `opm.agents.yesno` | `YesNoEngine` | Classify ambiguous responses as yes / no / unknown |
| `opm.agents.coref` | `CoreferenceEngine` | Pronoun / coreference resolution |
| `opm.agents.memory` | `AgentContextManager` | Per-session conversation history management |
| `opm.agents.retrieval` | `RetrievalEngine` | Retrieval-augmented generation |
| `opm.agents.retrieval.documents` | `DocumentIndexerEngine` | Index + retrieve over a document corpus |
| `opm.agents.retrieval.qa` | `QAIndexerEngine` | Index + retrieve over a Q/A corpus |
| `opm.agents.toolbox` | — | Tool/function-calling registry |

Each group has a parallel `*.config` group for plugin config metadata. All base classes live in
`ovos_plugin_manager.templates.agents`. The `AgentMessage` dataclass carries messages between
engines:

```python
from ovos_plugin_manager.templates.agents import AgentMessage, MessageRole

msg = AgentMessage(role=MessageRole.USER, content="What is the speed of light?")

```

`MessageRole` values: `SYSTEM`, `DEVELOPER`, `USER`, `ASSISTANT`, `TOOL`.

See [Agent Plugins](agent-plugins.md) for the full engine-type reference and configuration
examples for Claude, OpenAI, and local GGUF models.

---

## Personas (Named Agent Identities)

A **persona** is a named conversational identity defined by a JSON file (or an OPM plugin entry
point). It lists one or more agent engine plugin IDs in priority order and carries per-plugin
configuration inline.

```json
{
  "name": "My Assistant",
  "handlers": ["ovos-chat-openai-plugin"],
  "ovos-chat-openai-plugin": {
    "api_url": "https://api.openai.com/v1",
    "key": "sk-...",
    "model": "gpt-4o-mini",
    "system_prompt": "You are a helpful voice assistant. Be concise."
  }
}

```

The `"solvers"` key is an alias for `"handlers"` (legacy compat). Plugins are tried in order;
the first non-`None` response wins.

### Persona with session memory

Pair any chat engine with an `opm.agents.memory` plugin to persist per-session conversation
history across turns:

```json
{
  "name": "Assistant with Memory",
  "memory_module": "ovos-memory-plugin-longterm",
  "handlers": ["ovos-chat-openai-plugin"],
  "ovos-chat-openai-plugin": {
    "api_url": "https://api.openai.com/v1",
    "key": "sk-...",
    "model": "gpt-4o-mini",
    "system_prompt": "You are a helpful assistant."
  },
  "ovos-memory-plugin-longterm": {
    "max_history": 30,
    "compress": true
  }
}

```

The `memory_module` key names an `opm.agents.memory` plugin. The default when omitted is
`"ovos-agents-short-term-memory-plugin"` — `BasicShortTermMemory` from `ovos-persona`.

#### Memory backends

| Plugin / entry point | Package | Backend |
|---|---|---|
| `ovos-agents-short-term-memory-plugin` (`BasicShortTermMemory`) | `ovos-persona` | In-RAM short-term history, no API key |
| `ovos-memory-plugin-longterm` (`LongTermMemory`) | `ovos-memory-plugins` | Local JSON/SQLite store (uses an OpenAI-compatible endpoint only for LLM summarization) |

`ovos-memory-plugins` is **local-first**: server- / cloud-coupled RAG memory lives in
`ovos-openai-plugin` as `PersonaServerRAGMemory` (`ovos-openai-rag-memory-plugin`), not here.

> **Upcoming:** [OpenVoiceOS/ovos-memory-plugins#9](https://github.com/OpenVoiceOS/ovos-memory-plugins/pull/9)
> (draft) makes the package purely local-first: it adds `LocalRAGMemory`
> (`ovos-memory-plugin-local-rag`), a fully in-process RAG backend using local OVOS embeddings +
> an `EmbeddingsDB` plugin (no HTTP, no cloud key), and removes the current server-coupled HTTP
> `RAGMemory` (`ovos-memory-plugin-rag`) in favour of `ovos-openai-plugin`'s server RAG.

### Non-LLM personas

Personas do not require LLMs. Any installed OPM solver plugin can serve as a handler, enabling
fully local, privacy-preserving conversational agents:

```json
{
  "name": "OldSchoolBot",
  "solvers": [
    "ovos-wikipedia-plugin",
    "ovos-ddg-plugin",
    "ovos-wolfram-alpha-plugin",
    "ovos-wordnet-plugin",
    "ovos-solver-failure-plugin"
  ],
  "ovos-wolfram-alpha-plugin": {"appid": "Y7353-XXX"}
}

```

---

## PersonaService — Pipeline Plugin

`PersonaService` (`ovos_persona.PersonaService`) is the runtime component. It registers as an
`opm.pipeline` plugin and integrates directly with the OVOS intent pipeline.

Entry point: `opm.pipeline = ovos-persona-pipeline-plugin`

### Pipeline placement

```json
{
  "intents": {
    "pipeline": [
      "stop_high",
      "converse",
      "padatious_high",
      "adapt_high",
      "ovos-persona-pipeline-plugin-high",
      "ocp_medium",
      "fallback_medium",
      "ovos-persona-pipeline-plugin-low",
      "fallback_low"
    ]
  }
}

```

### Confidence levels

| Level | Method | Behaviour |
|---|---|---|
| High | `match_high()` | Matches persona management intents (summon, release, list, check, ask). If a persona is active and no management intent matched, delegates to `match_low()`. |
| Medium | `match_medium()` | Keyword fallback for summon/ask when padatious confidence was too low. |
| Low | `match_low()` | If `handle_fallback: true` and a `default_persona` is set, routes every unhandled utterance to the default persona. |

### Configuration

All keys live under `"intents": { "persona": { ... } }` in `mycroft.conf`:

```json
{
  "intents": {
    "persona": {
      "handle_fallback": true,
      "default_persona": "My Assistant",
      "personas_path": "~/.config/ovos_persona",
      "memory_module": "ovos-agents-short-term-memory-plugin"
    }
  }
}

```

| Key | Default | Description |
|---|---|---|
| `personas_path` | `~/.config/ovos_persona` | Directory for user JSON persona files |
| `default_persona` | first loaded | Persona used when `handle_fallback` is active |
| `handle_fallback` | `false` | Route all unhandled utterances to `default_persona` |
| `persona_blacklist` | `[]` | Persona names to skip when loading |
| `ignore_plugin_personas` | `false` | Skip OPM-registered plugin personas |
| `min_intent_confidence` | `0.6` | Minimum padatious confidence for persona intents |
| `memory_module` | `"ovos-agents-short-term-memory-plugin"` | Memory plugin (`null` to disable) |

### Voice intents

| Intent | Example utterances |
|---|---|
| Summon | "Connect me to Claude", "Let me chat with My Assistant" |
| Ask | "Ask Claude what the meaning of life is" |
| List | "What personas are available?" |
| Check | "Who am I talking to right now?" |
| Release | "Stop the interaction", "Go dormant" |

---

## Persona Loading

`PersonaService.load_personas()` loads from two sources:

1. **User JSON files** in `~/.config/ovos_persona/` — each `.json` file becomes a `Persona`. The
   `"name"` field inside the JSON overrides the filename.

2. **OPM plugin personas** — packages that register via the `opm.plugin.persona` entry point
   group (unless `ignore_plugin_personas: true`).

User-defined personas take precedence: a plugin persona with the same name as a loaded file is
silently skipped. Both sources respect `persona_blacklist`.

---

## OVOS Core as a Chat Engine

`ovos-messagebus-chat-plugin` (entry point `ovos-messagebus`, class `OVOSMessagebusChatAgent`,
group `opm.agents.chat`) exposes a running `ovos-core` instance as a persona handler. This
enables OVOS to act as an agent inside another system — for example a Docker network or a
[HiveMind](hivemind-agents.md) satellite — without exposing the [MessageBus](bus-service.md) directly.

```json
{
  "name": "Open Voice OS",
  "handlers": ["ovos-messagebus", "ovos-solver-failure-plugin"],
  "ovos-messagebus": {
    "autoconnect": true,
    "host": "127.0.0.1",
    "port": 8181
  }
}

```

This plugin replaces the removed `OVOSMessagebusSolver` / `ovos-solver-bus-plugin`, which lived
under the deprecated `neon.plugin.solver` group; install
[`ovos-messagebus-chat-plugin`](https://github.com/OpenVoiceOS/ovos-messagebus-chat-plugin) and
migrate any persona that referenced the old solver to the `ovos-messagebus` chat engine.

**Note:** routing OVOS back through itself creates an infinite loop if this engine is used inside
a persona that is *already* loaded by the same running `ovos-core`. It is intended for
cross-instance bridging, not local routing. For secure remote access see
[HiveMind Agents](hivemind-agents.md).

---

## Summary

| Component | Role |
|---|---|
| `ChatEngine` / `ReRankerEngine` / etc. | Low-level OPM agent engine plugins (`opm.agents.*`) |
| Persona JSON | Named agent identity: ordered engine list + per-engine config |
| `PersonaService` | Pipeline plugin: loads personas, routes utterances, manages sessions |
| `BasicShortTermMemory` | Default in-memory session history manager |
| `ovos-persona-server` | Expose a persona via OpenAI-compatible HTTP API |

Cross-references:

- [Agent Plugins](agent-plugins.md) — full engine-type reference with config examples


- [OpenAI Plugin](openai-plugin.md) — OpenAI-compatible engine implementations and translation plugins


- [GGUF Plugin](gguf-plugin.md) — fully offline local GGUF engine implementations


- [HiveMind Agents](hivemind-agents.md) — remote satellite-to-persona connections


- [Persona Pipeline](persona-pipeline.md) — detailed pipeline matching logic


- [Persona Server](persona-server.md) — expose a persona via OpenAI-compatible HTTP API

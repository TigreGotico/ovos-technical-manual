# Agent Plugins

!!! abstract "In a nutshell"
    Agent plugins are the swappable "brains" your assistant can use to do thinking work: holding a conversation, answering a factual question, summarizing a document, picking the best of several answers, remembering what was said earlier, or figuring out who "she" refers to. You don't run them yourself — you list the ones you want in a [persona](personas.md), and OVOS loads them. Think of it like choosing which browser extensions to install, except each "extension" is a different reasoning skill. See [Agents & Personas](personas.md) or the [Glossary](glossary.md) for related terms.

**For beginners:** agent plugins are the installable building blocks that let a persona think,
answer, rank, summarize, remember, or resolve pronouns. You don't call them directly — you list
them in a [persona](personas.md) and the [PersonaService](personas.md#personaservice-pipeline-plugin)
loads them. Each plugin advertises itself to OVOS through an OPM entry-point group.

!!! note "Version requirement"
    The agent plugin system (`opm.agents.*` entry-point groups) requires
    **`ovos-plugin-manager >= 2.3.0a1`** (cap below `<3.0.0`). Older OPM releases don't
    know these groups.

**For advanced users:** every agent engine subclasses an abstract base in
`ovos_plugin_manager.templates.agents` and registers under one `opm.agents.*` group (each with a
parallel `*.config` group for config metadata). The discovery helpers live in
`ovos_plugin_manager.agents`. The authoritative group/base-class mapping:

| Entry-point group | Base class | Purpose |
|---|---|---|
| `opm.agents.chat` | `ChatEngine` | Multi-turn conversational LLM |
| `opm.agents.chat.multimodal` | `MultimodalChatEngine` | Chat with image/audio/file input |
| `opm.agents.multimodal_adapter` | `MultimodalAdapter` | Render non-text content as text |
| `opm.agents.summarizer` | `SummarizerEngine` | Condense a document |
| `opm.agents.summarizer.chat` | `ChatSummarizerEngine` | Compress a chat history |
| `opm.agents.reranker` | `ReRankerEngine` | Score/rank candidate answers |
| `opm.agents.option_matcher` | `OptionMatcherEngine` | Match an utterance to a fixed option set |
| `opm.agents.extractive_qa` | `ExtractiveQAEngine` | Extract the answering passage from evidence |
| `opm.agents.nli` | `NaturalLanguageInferenceEngine` | Premise → hypothesis entailment |
| `opm.agents.yesno` | `YesNoEngine` | Classify a response as yes / no / unknown |
| `opm.agents.coref` | `CoreferenceEngine` | Pronoun / coreference resolution |
| `opm.agents.memory` | `AgentContextManager` | Per-session conversation history |
| `opm.agents.retrieval` | `RetrievalEngine` | Retrieval-augmented generation |
| `opm.agents.retrieval.documents` | `DocumentIndexerEngine` | Index + retrieve over a document corpus |
| `opm.agents.retrieval.qa` | `QAIndexerEngine` | Index + retrieve over a Q/A corpus |
| `opm.agents.toolbox` | — | Tool / function-calling registry |

The legacy `opm.solver.*` groups (and the `QuestionSolver` family in
`ovos_plugin_manager.templates.solvers`) are deprecated — see [Specialized Agent Engine
Types](advanced-solvers.md) for the migration map. For per-engine method contracts and config
examples, see [Agents & Personas](personas.md) and [Advanced Solvers](advanced-solvers.md).

---

## Plugin catalog

| Plugin | Description |
|--------|-------------|
| [ovos-qdrant-embeddings-plugin](#ovos-qdrant-embeddings-plugin) | The `QdrantEmbeddingsDB` plugin integrates with the [qdrant](https://qdrant.tech/) database to provide a robust solution for managing and querying embeddings. This plugin extends the abstract `EmbeddingsDB` class, allowing you to store, retrieve, and query embeddings efficiently using qdrant's capabilities. |
| [ovos-solver-plugin-aiml](#ovos-solver-plugin-aiml) | A rule-based chatbot answer engine for OVOS, using AIML pattern matching. |
| [ovos-persona](#ovos-persona) | The **`PersonaPipeline`** brings multi-persona management to OpenVoiceOS (OVOS), enabling interactive conversations with virtual assistants. 🎙️ With personas, you can customize how queries are handled by assigning specific solvers to each persona. |
| [ovos-openai-plugin](#ovos-openai-plugin) | Leverages the [OpenAI Completions API](https://platform.openai.com/docs/api-reference/completions/create) to provide a chat engine, a dialog-rewriting transformer, and a summarizer, all pointed at any OpenAI-compatible endpoint. |
| [ovos-messagebus-chat-plugin](#ovos-messagebus-chat-plugin) | `OVOSMessagebusChatAgent` — a `ChatEngine` (`opm.agents.chat`, entry point `ovos-messagebus`) that proxies each turn through a connected OVOS messagebus pipeline. |
| [ovos-wikipedia-solver](#ovos-wikipedia-solver) | Answers factual questions by querying Wikipedia. |
| [ovos-chromadb-embeddings-plugin](#ovos-chromadb-embeddings-plugin) | The `ChromaEmbeddingsDB` plugin integrates with the [ChromaDB](https://www.trychroma.com/) database to provide a robust solution for managing and querying embeddings. This plugin extends the abstract `EmbeddingsDB` class, allowing you to store, retrieve, and query embeddings efficiently using ChromaDB's capabilities. |
| [ovos-wolfram-alpha-solver](#ovos-wolfram-alpha-solver) | Answers computational and factual questions via the Wolfram Alpha API. |
| [ovos-ddg-solver-plugin](#ovos-ddg-solver-plugin) | Answers questions using DuckDuckGo instant-answer results. |
| [ovos-solver-YesNo-plugin](#ovos-solver-yesno-plugin) | A simple tool to indicate whether a user answered "yes" or "no" to a yes/no prompt. |
| [ovos-solver-failure-plugin](#ovos-solver-failure-plugin) | Extreme fallback, just complains it does not have a brain |
| [ovos-gguf-plugin](#ovos-gguf-plugin) | Unified GGUF wrapper — chat, summarization, dialog rewriting, translation, language detection, and text embeddings, all backed by quantized GGUF models via `llama-cpp-python`. |
| [ovos-persona-server](#ovos-persona-server) | Standalone server that exposes an OVOS persona over an HTTP API. |
| [ovos-solver-plugin-rivescript](#ovos-solver-plugin-rivescript) | A rule-based chatbot answer engine for OVOS, using RiveScript pattern matching. |

## ovos-qdrant-embeddings-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-qdrant-embeddings-plugin](https://github.com/OpenVoiceOS/ovos-qdrant-embeddings-plugin)


- **Description**: The `QdrantEmbeddingsDB` plugin integrates with the [qdrant](https://qdrant.tech/) database to provide a robust solution for managing and querying embeddings. This plugin extends the abstract `EmbeddingsDB` class, allowing you to store, retrieve, and query embeddings efficiently using qdrant's capabilities.

- **Entry point group**: `opm.embeddings` (the `EmbeddingsDB` backends register here, not under `opm.agents.*`).

- **Config keys**:

| Key | Default | Notes |
|---|---|---|
| `vector_size` | — | **Required.** Dimension of the stored embedding vectors. |
| `distance_metric` | `cosine` | One of `cosine`, `euclidean`, `dot`. |
| `host` | — | When set, connects to a remote Qdrant server (otherwise a persistent local client is used). |
| `port` | `6333` | HTTP port for the remote client. |
| `grpc_port` | `6334` | gRPC port for the remote client. |

---

## ovos-solver-plugin-aiml

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-solver-plugin-aiml](https://github.com/OpenVoiceOS/ovos-solver-plugin-aiml)


- **Description**: A rule-based chatbot answer engine for OVOS, using AIML pattern matching.

---

## ovos-persona

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-persona](https://github.com/OpenVoiceOS/ovos-persona)


- **Description**: The **`PersonaPipeline`** brings multi-persona management to OpenVoiceOS (OVOS), enabling interactive conversations with virtual assistants. 🎙️ With personas, you can customize how queries are handled by assigning specific solvers to each persona.

---

## ovos-openai-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-openai-plugin](https://github.com/OpenVoiceOS/ovos-openai-plugin)


- **Description**: An OpenAI-compatible engine family — chat, dialog-rewriting, and summarization — usable with any OpenAI-compatible endpoint. See [OpenAI Plugin](openai-plugin.md) for the full entry-point table, config keys, and examples.

---

## ovos-messagebus-chat-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-messagebus-chat-plugin](https://github.com/OpenVoiceOS/ovos-messagebus-chat-plugin)

- **Entry point**: `ovos-messagebus` → `OVOSMessagebusChatAgent` (group `opm.agents.chat`).

- **Description**: A `ChatEngine` that proxies each turn through a connected OVOS messagebus pipeline, letting a persona answer via the full skills/intent stack rather than an LLM.

---

## ovos-wikipedia-solver

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-wikipedia-solver](https://github.com/OpenVoiceOS/ovos-wikipedia-solver)


- **Description**: Answers factual questions by querying Wikipedia.

---

## ovos-chromadb-embeddings-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-chromadb-embeddings-plugin](https://github.com/OpenVoiceOS/ovos-chromadb-embeddings-plugin)


- **Description**: The `ChromaEmbeddingsDB` plugin integrates with the [ChromaDB](https://www.trychroma.com/) database to provide a robust solution for managing and querying embeddings. This plugin extends the abstract `EmbeddingsDB` class, allowing you to store, retrieve, and query embeddings efficiently using ChromaDB's capabilities.

- **Entry point group**: `opm.embeddings` (the `EmbeddingsDB` backends register here, not under `opm.agents.*`).

- **Config keys**:

| Key | Default | Notes |
|---|---|---|
| `path` | `./chromadb_storage` | Storage path for the persistent local client. |
| `host` | — | When set, connects to a remote ChromaDB HTTP server instead of the local persistent client. |
| `port` | `8000` | Port for the remote HTTP client. |

Per-collection metadata defaults `hnsw:space` to `cosine` when not specified.

---

## ovos-wolfram-alpha-solver

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-wolfram-alpha-solver](https://github.com/OpenVoiceOS/ovos-wolfram-alpha-solver)


- **Description**: Answers computational and factual questions via the Wolfram Alpha API.

---

## ovos-ddg-solver-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ddg-solver-plugin](https://github.com/OpenVoiceOS/ovos-ddg-solver-plugin)


- **Description**: Answers questions using DuckDuckGo instant-answer results.

---

## ovos-solver-YesNo-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-solver-YesNo-plugin](https://github.com/OpenVoiceOS/ovos-solver-YesNo-plugin)


- **Description**: A simple tool to indicate whether a user answered "yes" or "no" to a yes/no prompt.

---

## ovos-solver-failure-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-solver-failure-plugin](https://github.com/OpenVoiceOS/ovos-solver-failure-plugin)


- **Description**: Extreme fallback, just complains it does not have a brain

---

## ovos-gguf-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-gguf-plugin](https://github.com/OpenVoiceOS/ovos-gguf-plugin)


- **Description**: A unified GGUF wrapper providing chat, summarization, dialog rewriting, translation, language detection, and text-embedding engines, all backed by quantized GGUF models loaded through `llama-cpp-python`. See [GGUF Plugin](gguf-plugin.md) for the full entry-point table.

---

## ovos-persona-server

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-persona-server](https://github.com/OpenVoiceOS/ovos-persona-server)


- **Description**: Standalone server that exposes an OVOS persona over an HTTP API (e.g. `ovos-persona-server --persona rivescript_bot.json`).

---

## ovos-solver-plugin-rivescript

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-solver-plugin-rivescript](https://github.com/OpenVoiceOS/ovos-solver-plugin-rivescript)


- **Description**: A rule-based chatbot answer engine for OVOS, using RiveScript pattern matching.

---

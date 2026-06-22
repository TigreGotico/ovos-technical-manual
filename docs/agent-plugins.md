# Agent Plugins

**For beginners:** agent plugins are the installable building blocks that let a persona think,
answer, rank, summarize, remember, or resolve pronouns. You don't call them directly — you list
them in a [persona](personas.md) and the [PersonaService](personas.md#personaservice-pipeline-plugin)
loads them. Each plugin advertises itself to OVOS through an OPM entry-point group.

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
| [ovos-qdrant-embeddings-plugin](#ovos-qdrant-embeddings-plugin) | The `QdrantEmbeddingsDB` plugin integrates with the [qdrant](https://www.tryQdrant.com/) database to provide a robust solution for managing and querying embeddings. This plugin extends the abstract `EmbeddingsDB` class, allowing you to store, retrieve, and query embeddings efficiently using qdrant’s capabilities. |
| [ovos-solver-plugin-aiml](#ovos-solver-plugin-aiml) | Give Mycroft some sass with AIML! |
| [ovos-persona](#ovos-persona) | The **`PersonaPipeline`** brings multi-persona management to OpenVoiceOS (OVOS), enabling interactive conversations with virtual assistants. 🎙️ With personas, you can customize how queries are handled by assigning specific solvers to each persona. |
| [ovos-openai-plugin](#ovos-openai-plugin) | Leverages [OpenAI Completions API](https://platform.openai.com/docs/api-reference/completions/create) to provide the following ovos plugins: |
| [ovos-wikipedia-solver](#ovos-wikipedia-solver) | Answers factual questions by querying Wikipedia. |
| [ovos-chromadb-embeddings-plugin](#ovos-chromadb-embeddings-plugin) | The `ChromaEmbeddingsDB` plugin integrates with the [ChromaDB](https://www.trychroma.com/) database to provide a robust solution for managing and querying embeddings. This plugin extends the abstract `EmbeddingsDB` class, allowing you to store, retrieve, and query embeddings efficiently using ChromaDB’s capabilities. |
| [ovos-wolfram-alpha-solver](#ovos-wolfram-alpha-solver) | Answers computational and factual questions via the Wolfram Alpha API. |
| [ovos-ddg-solver-plugin](#ovos-ddg-solver-plugin) | Answers questions using DuckDuckGo instant-answer results. |
| [ovos-solver-YesNo-plugin](#ovos-solver-yesno-plugin) | A simple tool to indicate whether a user answered "yes" or "no" to a yes/no prompt. |
| [ovos-solver-failure-plugin](#ovos-solver-failure-plugin) | Extreme fallback, just complains it does not have a brain |
| [ovos-gguf-plugin](#ovos-gguf-plugin) | `GGUFSolver` is a question-answering module that utilizes GGUF models to provide responses to user queries. This solver |
| [ovos-persona-server](#ovos-persona-server) | Standalone server that exposes an OVOS persona over an HTTP API. |
| [ovos-solver-plugin-rivescript](#ovos-solver-plugin-rivescript) | Give Mycroft some sass with Rivescript! |

## ovos-qdrant-embeddings-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-qdrant-embeddings-plugin](https://github.com/OpenVoiceOS/ovos-qdrant-embeddings-plugin)


- **Description**: The `QdrantEmbeddingsDB` plugin integrates with the [qdrant](https://www.tryQdrant.com/) database to provide a robust solution for managing and querying embeddings. This plugin extends the abstract `EmbeddingsDB` class, allowing you to store, retrieve, and query embeddings efficiently using qdrant’s capabilities.

---

## ovos-solver-plugin-aiml

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-solver-plugin-aiml](https://github.com/OpenVoiceOS/ovos-solver-plugin-aiml)


- **Description**: Give Mycroft some sass with AIML!

---

## ovos-persona

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-persona](https://github.com/OpenVoiceOS/ovos-persona)


- **Description**: The **`PersonaPipeline`** brings multi-persona management to OpenVoiceOS (OVOS), enabling interactive conversations with virtual assistants. 🎙️ With personas, you can customize how queries are handled by assigning specific solvers to each persona.

---

## ovos-openai-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-openai-plugin](https://github.com/OpenVoiceOS/ovos-openai-plugin)


- **Description**: Leverages [OpenAI Completions API](https://platform.openai.com/docs/api-reference/completions/create) to provide the following ovos plugins:

---

## ovos-wikipedia-solver

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-wikipedia-solver](https://github.com/OpenVoiceOS/ovos-wikipedia-solver)


- **Description**: Answers factual questions by querying Wikipedia.

---

## ovos-chromadb-embeddings-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-chromadb-embeddings-plugin](https://github.com/OpenVoiceOS/ovos-chromadb-embeddings-plugin)


- **Description**: The `ChromaEmbeddingsDB` plugin integrates with the [ChromaDB](https://www.trychroma.com/) database to provide a robust solution for managing and querying embeddings. This plugin extends the abstract `EmbeddingsDB` class, allowing you to store, retrieve, and query embeddings efficiently using ChromaDB’s capabilities.

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


- **Description**: `GGUFSolver` is a question-answering module that utilizes GGUF models to provide responses to user queries. This solver

---

## ovos-persona-server

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-persona-server](https://github.com/OpenVoiceOS/ovos-persona-server)


- **Description**: Standalone server that exposes an OVOS persona over an HTTP API (e.g. `ovos-persona-server --persona rivescript_bot.json`).

---

## ovos-solver-plugin-rivescript

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-solver-plugin-rivescript](https://github.com/OpenVoiceOS/ovos-solver-plugin-rivescript)


- **Description**: Give Mycroft some sass with Rivescript!

---

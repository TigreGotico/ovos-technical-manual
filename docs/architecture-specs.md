# Formal Specifications

!!! abstract "In a nutshell"
    OVOS is not only an implementation — its component contracts are written
    down as a set of **formal, implementation-agnostic specifications**. They
    define *exactly* how the parts talk to each other: the bus messages, the
    session, the intent pipeline, and each plugin role. If you are new, treat
    them as the authoritative "how it really works." If you are building
    plugins, skills, or a whole new orchestrator, they are the **source of
    truth** — where this manual or the current code diverges from a spec, the
    spec wins.

The specifications live in the
[**OpenVoiceOS/architecture**](https://github.com/OpenVoiceOS/architecture)
repository. They are **prescriptive, not descriptive**: they describe the
intended architecture, not a transcript of any one codebase. That is what lets
a skill written against the intent stack run on *any* conformant orchestrator,
in any language, under any pipeline configuration — and what lets a second
project adopt the same formats and bus contracts without buying into OVOS as a
whole.

Throughout this manual you will see a callout like this on the page for each
subsystem:

??? info "📐 Formal specification"
    This subsystem is specified by **[OVOS-EXAMPLE-1 — Example](https://github.com/OpenVoiceOS/architecture)**.

Follow it to the precise wire format, field-by-field, with conformance
requirements.

---

## The voice operating system model

The specifications are organized around one idea: OVOS is a **voice operating
system**, not a voice assistant. A voice assistant is a product that answers
questions; a voice OS is a *platform* that defines the boundary between user
input and computation, arbitrates which application handles each utterance, and
provides a stable ABI that arbitrary third-party applications run against
without knowing anything about each other. The analogy to a general-purpose OS
is direct:

| OS concept | Voice OS equivalent |
|---|---|
| IPC / message passing | The bus and the **[Message](https://github.com/OpenVoiceOS/architecture/blob/dev/msg-1.md)** envelope |
| Shared memory | The **[Session](https://github.com/OpenVoiceOS/architecture/blob/dev/session-1.md)** carrier |
| Process scheduler | **[Pipeline](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)** plugin ordering |
| Loadable kernel modules | Pipeline plugins and transformer plugins |
| Process supervision | The handler-lifecycle events |
| System-call ABI | The `match(utterances, lang, session) → Match` contract |

---

## The specifications

### Intent stack — what a skill defines

| Spec | What it covers |
|------|----------------|
| [**OVOS-INTENT-1** — Sentence Template Grammar](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-1.md) | The `(a\|b)` / `[optional]` / `{slot}` / `<vocab>` grammar shared by `.intent`, `.voc`, `.dialog`, `.entity` resource files. |
| [**OVOS-INTENT-2** — Locale Resource Formats](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-2.md) | The `locale/` folder layout and the plain-text resource file formats (`.intent`, `.dialog`, `.voc`, `.entity`, `.prompt`). |
| [**OVOS-INTENT-3** — Intent Definition](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-3.md) | What an intent *is* — keyword vs template definition, skill/intent identity, and the match-result shape. |
| [**OVOS-INTENT-4** — Intent & Entity Registration](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-4.md) | The broadcast bus messages a skill uses to declare its intents and entities, and the orchestrator's introspection manifest. |

### Bus stack — how components talk

| Spec | What it covers |
|------|----------------|
| [**OVOS-MSG-1** — Bus Message](https://github.com/OpenVoiceOS/architecture/blob/dev/msg-1.md) | The JSON `{type, data, context}` envelope, `source`/`destination` routing, and the `forward` / `reply` / `response` derivations every message obeys. |
| [**OVOS-SESSION-1** — Session Carrier Wire Shape](https://github.com/OpenVoiceOS/architecture/blob/dev/session-1.md) | The wire shape of the session — the per-conversation state that rides in every message — and the field registry other specs extend. |
| [**OVOS-SESSION-2** — Session Lifecycle & State Ownership](https://github.com/OpenVoiceOS/architecture/blob/dev/session-2.md) | Who owns session state, when it may be mutated, the reserved `"default"` device session, and out-of-band sync. |
| [**OVOS-BRIDGE-1** — Bus Bridge & Opaque Relay](https://github.com/OpenVoiceOS/architecture/blob/dev/bridge-1.md) | How a satellite / remote deployment relays messages and preserves sessions across a [HiveMind](https://github.com/JarbasHiveMind) mesh. |

### Orchestrator stack — what processes utterances

| Spec | What it covers |
|------|----------------|
| [**OVOS-PIPELINE-1** — Utterance Lifecycle & Pipeline](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md) | The foundational input/output spec: the `match(utterances, lang, session) → Match` contract, **first-match-wins** ordering, dispatch, and the handler-lifecycle events. |
| [**OVOS-TRANSFORM-1** — Transformer Plugins](https://github.com/OpenVoiceOS/architecture/blob/dev/transformer.md) | The six ordered chains (audio / utterance / metadata / intent / dialog / tts) that enrich or rewrite artifacts at fixed points in the lifecycle. |
| [**OVOS-CONTEXT-1** — Intent Context](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-context.md) | The decaying, per-session key/value store that **gates** which intents may match across conversational turns. |
| [**OVOS-CONVERSE-1** — Active Handlers & Interactive Response](https://github.com/OpenVoiceOS/architecture/blob/dev/converse.md) | How a skill stays "active" to intercept follow-ups, and the response window that collects a single follow-up reply. |
| [**OVOS-STOP-1** — Stop Pipeline Plugin](https://github.com/OpenVoiceOS/architecture/blob/dev/stop-1.md) | How "stop" cascades to the most recently active handler, or triggers a global stop. |
| [**OVOS-PERSONA-1** — Persona Pipeline Plugin](https://github.com/OpenVoiceOS/architecture/blob/dev/persona.md) | A complete conversational agent (e.g. an LLM) as a first-class, summonable pipeline stage. |
| [**OVOS-FALLBACK-1** — Fallback Pipeline Plugin](https://github.com/OpenVoiceOS/architecture/blob/dev/fallback.md) | The priority-ordered handlers that catch utterances no earlier stage claimed. |
| [**OVOS-COMMON-QUERY-1** — Common Query Pipeline Plugin](https://github.com/OpenVoiceOS/architecture/blob/dev/common-query.md) | The scatter-gather question-answering contest across every skill that can answer. |

### I/O stack — input and output surfaces

| Spec | What it covers |
|------|----------------|
| [**OVOS-AUDIO-IN-1** — Audio Input Service](https://github.com/OpenVoiceOS/architecture/blob/dev/audio-in.md) | Capture → audio-transformer chain → STT → utterance, plus the listening-lifecycle signals. |
| [**OVOS-AUDIO-1** — Audio Output Service](https://github.com/OpenVoiceOS/architecture/blob/dev/audio-out.md) | Dialog-transformer chain → TTS → tts-transformer chain → playback queue, plus remote-client rendering. |
| [**OVOS-GUI-1** — GUI Display Subsystem](https://github.com/OpenVoiceOS/architecture/blob/dev/gui-1.md) | The closed `SYSTEM_*` template vocabulary and the interchangeable render backends that draw it. |

### Media stack — playback and transport

| Spec | What it covers |
|------|----------------|
| [**OVOS-OCP-1** — OVOS Common Playback](https://github.com/OpenVoiceOS/architecture/blob/dev/ocp-1.md) | The per-session **virtual media player** and its MPRIS-style search / play / pause / resume control surface. |

---

## How to read a spec

Each spec is a standalone document with a scope statement, the normative wire
format, and a conformance section. The key words **MUST**, **SHOULD**, and
**MAY** are used as in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

- **Newcomers:** read the scope and the worked examples; skip the conformance
  tables until you need them. Start with
  [OVOS-MSG-1](https://github.com/OpenVoiceOS/architecture/blob/dev/msg-1.md)
  (the message), then
  [OVOS-PIPELINE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)
  (how an utterance is handled).
- **Skill authors:** OVOS-INTENT-1 → INTENT-2 → INTENT-3 cover everything you
  declare; add INTENT-4 only if you need the registration wire format.
- **Plugin / orchestrator builders:** the conformance sections are your test
  checklist; the
  [README registry](https://github.com/OpenVoiceOS/architecture/blob/dev/README.md)
  lists every spec and its compatibility class.

The repository also ships a non-normative
[appendix](https://github.com/OpenVoiceOS/architecture/tree/dev/appendix) with
design rationale, comparisons to other voice systems, and the catalog of
deliberate divergences from current OVOS code.

!!! tip "Citing a spec stably"
    Links to `dev` (as used throughout this manual) always show the latest wording, which is
    what you want while reading. If you need to **cite** a specific clause elsewhere — in an
    issue, a commit message, or another project's own documentation — link to the file at a
    specific commit hash instead of `dev`, so the cited text cannot shift under the link later.
    On GitHub, press <kbd>y</kbd> while viewing the file to swap the URL's `dev` for the exact
    commit it resolved to.

---

## Building on the specs

You rarely need to implement a spec from scratch. The
[**Specification Tooling**](spec-tooling.md) page covers the reference
implementation ([`ovos-spec-tools`](https://github.com/OpenVoiceOS/ovos-spec-tools)),
the executable conformance suite
([`ovos-test-harness`](https://github.com/OpenVoiceOS/ovos-test-harness)), and the
[bus-client namespace migration](bus-service.md#namespace-migration) that lets the
ecosystem adopt the new `ovos.*` topics without a flag day.

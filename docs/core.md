# ovos-core

!!! abstract "In a nutshell"
    `ovos-core` is the "brain" of your assistant. It does not listen through the microphone or talk through the speaker — those are separate helpers — but it is the part in the middle that loads your skills, takes the words you said, decides which skill should answer, and hands back the reply. Think of it as the dispatcher in a control room: it does not do the talking or listening itself, it just routes each request to the right place. Everything it does travels over the [MessageBus](bus-service.md); see also the [Glossary](glossary.md).

!!! info "📐 Formal specification"
    `ovos-core` is the reference **orchestrator** — the logical role that runs the pipeline, routes matches to handlers, and emits the handler-lifecycle events. That role is specified by **[OVOS-PIPELINE-1 — Utterance Lifecycle & Pipeline](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)**; the transformer chains it hosts by **[OVOS-TRANSFORM-1 — Transformer Plugins](https://github.com/OpenVoiceOS/architecture/blob/dev/transformer.md)**; and the intent/entity registration it ingests by **[OVOS-INTENT-4 — Intent & Entity Registration](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-4.md)**. See also the [spec index](architecture-specs.md). The specs are implementation-agnostic: any conformant orchestrator can replace `ovos-core` and run the same skills.

`ovos-core` is the central intelligence of OpenVoiceOS. It acts as the orchestrator, managing the lifecycle of skills, coordinating the intent pipeline, and ensuring smooth communication between all parts of the system.

**In plain terms:** `ovos-core` is the "brain" service. It does not capture audio or speak — those are separate services. Its job is to load your skills, take the transcribed text off the bus, decide which skill handles it, and hand off the reply. Everything it does flows over the [MessageBus](bus-service.md).

## Role in the System

Every user utterance, whether captured from a microphone or received via a remote client, flows through `ovos-core`. It performs the heavy lifting of:

- **Discovering and loading skill plugins.**


- **Routing utterances** through various NLP and intent-matching stages.


- **Managing sessions** and their associated states.


- **Coordinating system-wide events** via the [MessageBus](bus-service.md).

## Architecture

The diagram below shows the key components within `ovos-core` and how they interact with other services:

```
ovos-messagebus  (WebSocket pub/sub)
      │
      ├── ovos-core  (this service)
      │     ├── [Skill Manager](skill-manager.md)   – loads/unloads skill plugins
      │     ├── [Intent Service](intent-service.md) – routes utterances through the pipeline
      │     │     ├── Utterance Transformers
      │     │     ├── Metadata Transformers
      │     │     ├── Intent Transformers
      │     │     └── Pipeline plugins (Adapt, Padatious, Converse, Fallback, …)
      │     ├── [Skill Installer](skill-installer.md) – runtime pip install/uninstall
      │     └── Event Scheduler – timed bus events
      │
      ├── ovos-dinkum-listener  – STT / wake-word → ovos.utterance.handle
      │                            (legacy: recognizer_loop:utterance)
      ├── ovos-audio            – TTS playback
      ├── ovos-gui              – GUI layer
      └── ovos-phal             – hardware/platform plugins

```

## Key Components

For a deeper dive into each subsystem, refer to the following pages:

### Skill Manager
Learn how `ovos-core` finds, loads, and manages the lifecycle of your skills. It also handles connectivity gating, ensuring skills are only loaded when their requirements (like internet access) are met.

### Intent Service
Discover how utterances are processed and matched to skills. This section covers the utterance handling flow, language disambiguation, and the query API.

### Intent Pipeline
The pipeline is the ordered sequence of **pipeline plugins** OVOS uses to understand what the user wants. Each plugin exposes a single `match(utterances, lang, session) → Match | None` contract and they are tried in order, **first-match-wins** — there is no cross-plugin confidence scoring (OVOS-PIPELINE-1 §4, §6.2). You can learn about specific matchers like [Adapt](adapt-pipeline.md), [Padatious](padatious-pipeline.md), and the [Common Query](cq-pipeline.md) framework.

### Transformer Plugins
Transformers allow you to modify utterances, metadata, or intent matches as they move through the system.

### Skill Installer
The built-in system for installing and managing skills and Python packages dynamically at runtime.

---

## Entry Points

If you are running OVOS manually, you can use these commands:

| Command | Module |
|---|---|
| `ovos-core` | `ovos_core.__main__:main` |
| `ovos-intent-service` | `ovos_core.intent_services.service:launch_standalone` |
| `ovos-skill-installer` | `ovos_core.skill_installer:launch_standalone` |

## Subsystem Enable Flags

You can customize which parts of `ovos-core` start by using flags in the CLI or settings in your configuration:

| Flag | Subsystem |
|---|---|
| `enable_intent_service` | `IntentService` |
| `enable_installer` | `SkillsStore` |
| `enable_event_scheduler` | `EventScheduler` |
| `enable_skill_api` | `SkillApi.connect_bus` |
| `enable_file_watcher` | Skill settings file watcher |

CLI equivalents are the `--disable-*` forms: `--disable-intent-service`, `--disable-installer`, `--disable-file-watcher`, etc.

---

*Source code: [OpenVoiceOS/ovos-core](https://github.com/OpenVoiceOS/ovos-core).*

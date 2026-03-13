# ovos-core

`ovos-core` is the central intelligence of OpenVoiceOS. It acts as the orchestrator, managing the lifecycle of skills, coordinating the intent pipeline, and ensuring smooth communication between all parts of the system.

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
      ├── ovos-dinkum-listener  – STT / wake-word → recognizer_loop:utterance
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
The pipeline is the sequence of matchers that OVOS uses to understand what the user wants. You can learn about specific matchers like [Adapt](adapt-pipeline.md), [Padatious](padatious-pipeline.md), and the [Common Query](cq-pipeline.md) framework.

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

CLI equivalents include `--disable-intent-service`, `--disable-installer`, etc.

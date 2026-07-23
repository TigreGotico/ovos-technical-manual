# Persona Pipeline

!!! abstract "In a nutshell"
    A "persona" is a configurable AI character — often powered by a chatbot-style language model — that the assistant can hand your request to. This pipeline decides when to let that persona answer you instead of the usual command-matching skills, which is useful for open-ended chat or questions that no specific skill covers. You can set it to handle everything, or only step in when nothing else fits. See the [Glossary](glossary.md) for terms, or [Solver/Agent plugins](agent-plugins.md) for the components a persona uses to come up with answers.

!!! info "📐 Formal specification"
    The persona plugin is specified by **[OVOS-PERSONA-1 — Persona Pipeline Plugin](https://github.com/OpenVoiceOS/architecture/blob/dev/persona.md)**, built on **[OVOS-PIPELINE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)**. See the [spec index](architecture-specs.md).

The **`ovos-persona-pipeline-plugin`** provides a dynamic way to integrate persona-based conversational behavior into the OVOS pipeline system. It allows you to route user utterances to AI personas instead of skill matchers, depending on context and configuration.

!!! note "How the spec frames it"
    A persona is a **complete conversational agent** that, when active, claims *every* utterance reaching its pipeline stage (PERSONA-1 §2). The active persona is held in one session field, **`session.persona_id`** (PERSONA-1 §3) — absent means no-persona mode (deterministic skills only); set means that persona's plugin catches everything that reaches it. The plugin is a self-matching pipeline plugin (PIPELINE-1 §7.0): its `Match.skill_id` equals its own `pipeline_id`. **Summon** sets `persona_id` (via `Match.updated_session`, a client, or a session sync); **dismiss** clears it — and the stop cascade (OVOS-STOP-1) clears it too, which is how "stop" returns control to the skills. The "full control / hybrid / fallback" strategies below are just different positions for the `persona` stage (route 2, active-persona catch-all) and an optional `persona_fallback` stage (route 3) in `session.pipeline` (PERSONA-1 §10).

---

## Overview

The `persona-pipeline` is a plugin for the OVOS pipeline architecture, shipped in the separate **`ovos-persona`** package (not part of `ovos-core`). It dynamically delegates user utterances to a configured **Persona**, which attempts to resolve the intent using a sequence of **[Solver](agent-plugins.md) Plugins** (e.g., LLMs, search tools, knowledge bases).

You can configure it to:

- Intercept all utterances and give full control to the persona.


- Fall back to the persona only if skills don't match.


- Operate based on confidence tiers (high/medium/low).

---

## Plugin Structure

Persona ships as the external `ovos-persona` package, which registers a single `opm.pipeline` entry point:

```ini
[project.entry-points."opm.pipeline"]
ovos-persona-pipeline-plugin = "ovos_persona:PersonaService"
```

`PersonaService` is a `ConfidenceMatcherPipeline` (and an `OVOSAbstractApplication`), so the single base ID auto-expands into three confidence-tier matchers you can place in the pipeline:

| Pipeline ID                            | Tier   | Usage                            |
|----------------------------------------|--------|----------------------------------|
| `ovos-persona-pipeline-plugin-high`    | high   | Active persona interactions and persona-control intents |
| `ovos-persona-pipeline-plugin-medium`  | medium | Keyword-gated persona queries |
| `ovos-persona-pipeline-plugin-low`     | low    | [Fallback](fallback-pipeline.md) persona handling |

Insert the tier IDs you need into your `mycroft.conf` under the `intents.pipeline` key to activate persona handling at the appropriate stage.

---

## Configuration

```jsonc
{
  "intents": {
    "persona": {
      "handle_fallback": true,
      "default_persona": "Remote Llama",
      "min_intent_confidence": 0.6,
      "personas_path": "~/.config/ovos_persona"
    },
    "pipeline": [
      // depending on strategy, insert the persona stage(s) here — see below
    ]
  }
}
```

### `persona` section options:

| Key                      | Description                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| `handle_fallback`        | When `true`, the low tier routes unmatched utterances to the default persona |
| `default_persona`        | Persona used by default (e.g., after boot or reset)                         |
| `min_intent_confidence`  | Confidence floor for the high-tier persona-control intents (summon/list/active/ask; default `0.6`) |
| `personas_path`          | Directory to load persona JSON files from (defaults to the XDG persona dir) |
| `persona_blacklist`      | Persona names to exclude                                                     |
| `ignore_plugin_personas` | When `true`, skip personas provided by installed plugins                     |

> Conversation memory is configured **per persona** (the `memory_module` / `max_history` keys inside each persona's JSON), not in this pipeline section.

---

## Pipeline Strategies

### 1. **Full Control (Persona-First)**

In this mode, **personas override** all skills. The persona handles every utterance unless explicitly deactivated.

```jsonc
{
  "pipeline": [
    "ovos-persona-pipeline-plugin-high",
    "ovos-stop-pipeline-plugin-high",
    "ovos-converse-pipeline-plugin",
    "ovos-padatious-pipeline-plugin-high",
    "ovos-adapt-pipeline-plugin-high"
    // ...remaining stages as needed
  ]
}
```

- Best for immersive chatbot experiences


- Skills like music, alarms, and weather will not trigger unless persona is disabled

---

### 2. **Hybrid Mode (Skills First)**

Only unmatched or low-confidence utterances are routed to the persona.

```jsonc
{
  "pipeline": [
    "ovos-stop-pipeline-plugin-high",
    "ovos-converse-pipeline-plugin",
    "ovos-padatious-pipeline-plugin-high",
    "ovos-adapt-pipeline-plugin-high",
    "ovos-persona-pipeline-plugin-high",
    "ovos-fallback-pipeline-plugin-medium"
    // ...remaining stages as needed
  ]
}
```

- Preserves traditional voice assistant behavior


- Persona fills in where skills fall short

---

### 3. **Fallback Mode Only**

Even when no persona is active, this mode allows the pipeline to fall back to a **default persona** for unmatched utterances.

```jsonc
{
  "pipeline": [
    // ...earlier stages as needed
    "ovos-fallback-pipeline-plugin-medium",
    "ovos-persona-pipeline-plugin-low",
    "ovos-fallback-pipeline-plugin-low"
  ]
}
```

- Replaces `skill-ovos-fallback-chatgpt`


- Fallbacks to a default persona response for a consistent assistant feel

---

## Persona Resolution Flow

1. **[Utterance](life-of-an-utterance.md) Received**


2. Pipeline matchers are checked in order.


3. If `persona-pipeline` is reached:


    - If a persona is **active**, send utterance to that persona.


    - If no persona is active and `handle_fallback` is enabled, use the **default_persona**.


4. The persona delegates to its configured **handlers** (solver plugins) until one returns a response.


5. The pipeline returns the matched response back to the user.

---

## Persona Configuration

Personas are loaded from the XDG persona config directory (typically `~/.config/ovos_persona/`, overridable via the `personas_path` config key). Each `*.json` file in that directory defines one persona (its name is the `"name"` field, or the filename without `.json`). Plugin-provided personas are also discovered unless `ignore_plugin_personas` is set.

### Example:

```json
{
  "name": "Remote Llama",
  "handlers": [
    "ovos-solver-openai-plugin",
    "ovos-solver-failure-plugin"
  ],
  "ovos-solver-openai-plugin": {
    "api_url": "https://llama.smartgic.io/v1",
    "key": "sk-xxx",
    "persona": "friendly and concise assistant"
  }
}

```

Each persona defines a `handlers` list (the older key `solvers` is still accepted as a fallback).

- Handlers are attempted **in order**.


- The first handler to return a valid result ends the search.


- Include a `"ovos-solver-failure-plugin"` as a final fallback for graceful error handling.

---

## Persona Intents

`"ovos-persona-pipeline-plugin-high"` supports a set of core voice intents to manage persona interactions seamlessly. 

These intents provide **out-of-the-box functionality** for controlling the Persona Service, ensuring smooth integration with the conversational pipeline and enhancing user experience. The backing intent/vocab files are `list_personas.intent`, `active_persona.intent`, `summon.intent` (activate), `ask.intent` (single-shot), and `Release.voc` (stop).

### **List Personas**

**Example Utterances**:

- "What personas are available?"


- "Can you list the personas?"


- "What personas can I use?"

### **Check Active Persona**

**Example Utterances**:

- "Who am I talking to right now?"


- "Is there an active persona?"


- "Which persona is in use?"

### **Activate a Persona**

**Example Utterances**:

- "Connect me to {persona}"


- "Enable {persona}"


- "Awaken the {persona} assistant"


- "Start a conversation with {persona}"


- "Let me chat with {persona}"


### **Single-Shot Persona Questions**

Enables users to query a persona directly without entering an interactive session.

**Example Utterances**:

- "Ask {persona} what they think about {utterance}"


- "What does {persona} say about {utterance}?"


- "Query {persona} for insights on {utterance}"


- "Ask {persona} for their perspective on {utterance}"


### **Stop Conversation**

**Example Utterances**:

- "Stop the interaction"


- "Terminate persona"


- "Deactivate the chatbot"


- "Go dormant"


- "Enough talking"


- "Shut up"

Releasing a persona (via the `Release.voc` keyword match) ends the active session: the service marks the session inactive so any in-flight streaming response stops and subsequent utterances flow back through the normal pipeline. Persona uses `skill_id` `persona.openvoiceos`.

---

## Related Pages

- [Agent / Solver Plugins](agent-plugins.md) — the handler plugins a persona delegates to


- [Fallback Pipeline](fallback-pipeline.md) — the low-tier fallback persona routing complements


- [Life of an Utterance](life-of-an-utterance.md) — where the persona stages sit in the pipeline

---

---

*Source code: [OpenVoiceOS/ovos-persona](https://github.com/OpenVoiceOS/ovos-persona).*

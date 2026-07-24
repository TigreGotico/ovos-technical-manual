# Stop Pipeline

!!! abstract "In a nutshell"
    This is the part of OVOS that listens for "stop", "cancel", or the same word in your language and makes the assistant quit whatever it is doing — interrupting a spoken reply, ending a question, or halting a task a skill started. Because being able to stop is so essential to a voice assistant, OVOS treats it as a built-in, always-on feature rather than an optional add-on, and it works in any language that ships the right word list. For the wider system this fits into, see the [Fallback Pipeline](fallback-pipeline.md) or the [Glossary](glossary.md).

??? info "📐 Formal specification"
    The stop plugin is specified by **[OVOS-STOP-1 — Stop Pipeline Plugin](https://github.com/OpenVoiceOS/architecture/blob/dev/stop-1.md)**, built on **[OVOS-PIPELINE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)**. See the [spec index](architecture-specs.md).

The **stop pipeline** is a core component of the OpenVoiceOS (OVOS) pipeline architecture. It defines the logic responsible for stopping ongoing interactions with active skills. This includes aborting responses, halting speech, and terminating background tasks that skills may be performing. 

Because stopping is a **fundamental feature of a voice assistant**, it is implemented as a **dedicated pipeline plugin**, not just a fallback or intent handler. STOP-1 is emphatic that stop is a **pipeline plugin and not a skill** — `skill-ovos-stop` is superseded. Stop only works because PIPELINE-1's first-match-wins lets a high-confidence stop stage placed *first* in `session.pipeline` (STOP-1 §7) intercept "stop" before any other pipeline plugin claims the bare word.

!!! note "Spec model and topic names"
    STOP-1 distinguishes two outcomes, both via reserved `intent_name`s. A generic **stop** cascades to the *most recently active* handler: the plugin reads `session.active_handlers` (the recency record, PIPELINE-1 §7.1), pings them with `ovos.stop.ping`, collects `ovos.stop.pong` (`can_handle`) within a recommended 0.5s ceiling, and returns a `Match` on the reserved `stop` name targeting the highest-`activated_at` positive responder — dispatched on `<skill_id>:stop`. A handler that does not answer within the timeout counts as `can_handle: false`.

    `global_stop` covers the three cases where there is nothing to target (STOP-1 §5.1): explicit "stop everything" vocabulary, an empty `active_handlers` list, or a ping round that produced **no positive responder**. Its `Match` clears `active_handlers`, `converse_handlers` and `response_mode` atomically, and its handler broadcasts `ovos.stop`, which every active component subscribes to.

    | Spec topic (STOP-1 §8) | Legacy name |
    |---|---|
    | `ovos.stop.ping` / `ovos.stop.pong` | `{skill_id}.stop.ping` / `skill.stop.pong` |
    | `<skill_id>:stop` — targeted-stop dispatch (reserved name) | `stop:skill` → `{skill_id}.stop` |
    | `<pipeline_id>:global_stop` — global-stop dispatch | `stop:global` |
    | `ovos.stop` — global-stop broadcast | `mycroft.stop` |
    | `session.active_handlers` — recency input to the cascade | `Session.active_skills` |

---

## Implementation

**Module:** `ovos_core.intent_services.stop_service.StopService`
**Pipeline plugin ID:** `ovos-stop-pipeline-plugin`
**Stage names:** `ovos-stop-pipeline-plugin-high`, `ovos-stop-pipeline-plugin-medium`, `ovos-stop-pipeline-plugin-low` (deprecated aliases: `stop_high`, `stop_medium`, `stop_low`)

`StopService` subclasses both `ConfidenceMatcherPipeline` and `OVOSAbstractApplication` (its `skill_id` is `stop.openvoiceos`). Because it is a `ConfidenceMatcherPipeline`, the single base plugin ID auto-expands into three confidence-tier matchers — `match_high`, `match_medium` and `match_low` — which you reference in the pipeline as `ovos-stop-pipeline-plugin-high`, `-medium`, and `-low`. It ships inside `ovos-core`:

```ini
[project.entry-points."opm.pipeline"]
ovos-stop-pipeline-plugin = "ovos_core.intent_services.stop_service:StopService"
```

---

## Purpose

A voice assistant must always be capable of responding to a "stop" command. Whether the user says *"stop," "cancel,"* or another localized phrase, OVOS must quickly:

* Determine if a skill is actively responding


* Allow skills to confirm whether they can be stopped


* Abort conversations, questions, or spoken responses

The `stop` pipeline guarantees this behavior through a flexible plugin system and localized vocab matching.

---

## How it works

The stop pipeline exposes three confidence tiers.

### High-confidence (`stop_high`)

Triggered when a user says an **exact** match (`voc_match(..., exact=True)`) for the `stop` or `global_stop` vocab, e.g.:

* "Stop"


* "Cancel"


* "Parar" (in Portuguese)


* "Stopp" (in German)

The plugin:

1. Collects the session's **active skills** (skipping session-blacklisted ones).


2. Pings them via `ovos.stop.ping` (legacy: `{skill_id}.stop.ping`) and waits up to `0.5s` for `ovos.stop.pong` (legacy: `skill.stop.pong`) replies carrying `can_handle`.


3. Dispatches `<skill_id>:stop` (legacy: `{skill_id}.stop`) to the most recently activated positive responder.


4. If no skill is active, no responder answered positively, or the utterance matched `global_stop`, emits a **global stop**: `ovos.stop` (legacy: `mycroft.stop`).

### Medium-confidence (`stop_medium`)

A fuzzy (`exact=False`) match of the same `stop` / `global_stop` vocab, for phrases that contain a stop command but are not exact. When it matches, it delegates to `match_low` to compute a confidence score.

### Low-confidence (`stop_low`)

Scores the utterance against the `stop` vocab list via fuzzy matching (`match_one`), adds a small bonus when active skills are present, and rejects anything below `min_conf` (default `0.5`). Used as a permissive catch-all so phrases like "can you stop now?" still reach the stop logic.

---

## Localization

The plugin supports stop commands in multiple languages using `.voc` files bundled in `ovos-core` under `ovos_core/intent_services/locale/<lang>/`:

```text
ovos_core/intent_services/locale/
  en-us/
    stop.voc
    global_stop.voc
  pt-pt/
    stop.voc
    global_stop.voc

```

`match_high`/`match_medium` look up the `stop` and `global_stop` vocab groups; `match_low` uses the `stop` list only. Not every language ships both files (some provide only `stop.voc`).

---

## Session Integration

The stop plugin interfaces with the OVOS session system:

* Skills that respond to `stop` will be removed from **active skill list**


* Session blacklists are respected, blacklisted skills will not be pinged


* Session state is updated after each successful stop

---

## Bus Events

| Event | Direction | Purpose |
|---|---|---|
| `<pipeline_id>:global_stop` (legacy: `stop:global`) | in | Global-stop dispatch — its handler emits the `ovos.stop` broadcast (and `ovos.utterance.handled`) |
| `<skill_id>:stop` (legacy: `stop:skill` → `{skill_id}.stop`) | out | Targeted stop dispatch to one skill |
| `ovos.stop.ping` (legacy: `{skill_id}.stop.ping`) | out | Asks the active handlers whether they can stop |
| `ovos.stop.pong` (legacy: `skill.stop.pong`) | in | Handler's `can_handle` reply |
| `ovos.stop` (legacy: `mycroft.stop`) | out | Universal stop broadcast |

`<skill_id>:stop` and `<pipeline_id>:global_stop` are dispatch topics and fire the handler-lifecycle trio; the `ovos.stop.*` topics and `ovos.stop` do not.

## Configuration

The service reads its config from `mycroft.conf` under `skills.stop`. The only key it consults is `min_conf` (default `0.5`), the floor used by the low-confidence matcher:

```json
{
  "skills": {
    "stop": {
      "min_conf": 0.5
    }
  }
}
```

## Design Philosophy

* **Low latency**: skills are pinged with a 0.5s wait, so stop resolves quickly


* **Extensible**: other plugins can extend or override this pipeline


* **Localized**: matching is language-aware via per-language vocab


* **Resilient**: falls back to a global `ovos.stop` broadcast if no handler responds positively

---

## Summary

The `stop` pipeline ensures that OVOS is always in control. Whether a user needs to quickly interrupt a skill, cancel a conversation, or shut down all interactions, the `StopService` plugin provides the robust, language-aware foundation to make that possible.

It is **not considered optional**, all OVOS installations should include this pipeline by default.

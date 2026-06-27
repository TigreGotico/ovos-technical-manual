# Intent Service

!!! abstract "In a nutshell"
    The Intent Service is the part of OpenVoiceOS that figures out what you actually meant. Once the [Speech Service](speech-service.md) has turned your words into text, this service reads that text and decides which skill should handle it — much like a receptionist hearing your request and directing you to the right desk. It tries a series of matchers in order and stops at the first one confident enough to respond. New to the terms? See the [Glossary](glossary.md).

**Module:** `ovos_core.intent_services.service.IntentService` — [`ovos_core/intent_services/service.py`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/intent_services/service.py)

!!! info "📐 Formal specification"
    The utterance lifecycle, the `match(utterances, lang, session) → Match` contract, **first-match-wins** ordering, and the dispatch/handler-lifecycle events are specified by **[OVOS-PIPELINE-1 — Utterance Lifecycle & Pipeline](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)**; what an intent *is* (keyword vs template) and the match-result shape by **[OVOS-INTENT-3 — Intent Definition](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-3.md)**; and how skills declare intents/entities on the bus by **[OVOS-INTENT-4 — Intent & Entity Registration](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-4.md)**. See also the [spec index](architecture-specs.md). `IntentService` is the reference **orchestrator** of this lifecycle; the spec topic names below are canonical.

`IntentService` is the component of `ovos-core` responsible for routing user utterances through the configured **Intent Pipeline** until a match is found.

**In plain terms:** this is the part that takes the words you said and figures out *which* skill should answer. It runs each matcher in your pipeline in order (e.g. stop, converse, padatious, adapt, …) and stops at the first one confident enough to handle the request.

---

??? abstract "Technical Reference"

    - `IntentService.handle_utterance()` — [`ovos_core/intent_services/service.py:415`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/intent_services/service.py) — Main entry point for processing utterances.


    - `IntentService._emit_match_message()` — [`ovos_core/intent_services/service.py:275`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/intent_services/service.py) — logic for emitting match messages and activating skills.


    - `OVOSPipelineFactory.load_plugin()` — [`ovos_plugin_manager/pipeline.py`](https://github.com/OpenVoiceOS/ovos-plugin-manager/blob/dev/ovos_plugin_manager/pipeline.py) — factory that builds matcher pipeline plugins from config (`get_installed_pipeline_ids()` lists them).
    

## Utterance Handling Flow

When an `ovos.utterance.handle` message (legacy: `recognizer_loop:utterance`) arrives on the bus — the lifecycle entry point of [OVOS-PIPELINE-1 §9.1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md):

```
ovos.utterance.handle  (legacy: recognizer_loop:utterance)   §9.1
  │
  ├── UtteranceTransformersService.transform()   # utterance-transformer chain   TRANSFORM-1 §3.2
  ├── MetadataTransformersService.transform()    # metadata-transformer chain    TRANSFORM-1 §3.3
  ├── disambiguate_lang()                        # pick the best language
  ├── _validate_session()                        # get/create Session
  │
  └── for each pipeline plugin (in order, first-match-wins):    §6.2
        match(utterances, lang, session) → Match | None         §4
          ├── match found → ovos.intent.matched (§9.2) → dispatch → handler trio (§8)
          └── no match   → next plugin
              (no plugin matched) → ovos.intent.unmatched (§9.3, legacy: complete_intent_failure)

```

Every lifecycle terminates with exactly one `ovos.utterance.handled` (§9.5), the universal end-marker, whether or not anything matched.

## Language Disambiguation

The language for an utterance is chosen based on a priority list from message context keys:

1. `stt_lang` — language used by [STT](stt-plugins.md) to transcribe.


2. `request_lang` — volunteered by the source (e.g. wake word).


3. `detected_lang` — detected by a transformer plugin.


4. Config default / `message.data["lang"]`.

The chosen language is validated against `valid_langs` from config using `closest_lang()` (from `ovos_spec_tools`), which tolerates near-matches such as `en` vs `en-us`.

## Multilingual Matching

When `intents.multilingual_matching` is enabled, if the primary language produces no match, OVOS will try all other configured languages in order.

## Session Management

Each utterance is associated with a `Session`.

- The **default session** expires and is reset automatically.


- **Non-default sessions** (e.g., from [HiveMind](hivemind-agents.md) clients) are updated but not reset.


- Session state (active skills, pipeline, blacklists) is serialised into every reply message under `context.session`.

## Intent Match Emission

When a pipeline plugin returns a match:

1. `IntentTransformersService.transform(match)` — the **intent-transformer chain** post-processes the match (OVOS-TRANSFORM-1 §3.4).


2. Emit `ovos.intent.matched` (§9.2) — a notification that a plugin claimed the utterance.


3. Build the dispatch message with `match.match_type` as the message type.


4. Activate the skill in the session (`sess.activate_skill(skill_id)`) and emit `{skill_id}.activate` for the skill's callback.


5. Wrap the dispatch in the **handler-lifecycle trio** — the orchestrator (not the skill) emits `ovos.intent.handler.start`, then exactly one of `ovos.intent.handler.complete` / `ovos.intent.handler.error` (§8, legacy: `mycroft.skill.handler.*`). The skill's intent handler runs between them.

## Intent Query API

External tools can query the pipeline without triggering a skill action:

```
intent.service.intent.get  {utterance: "...", lang: "..."}
  → intent.service.intent.reply  {intent: {...} | null, utterance: "..."}

```

## Bus Events Handled

| Event | Handler |
|---|---|
| `ovos.utterance.handle` (legacy: `recognizer_loop:utterance`) | `handle_utterance` |
| `add_context` | `handle_add_context` |
| `remove_context` | `handle_remove_context` |
| `clear_context` | `handle_clear_context` |

The `*_context` events mutate the per-session intent context (`session.intent_context`) specified by [OVOS-CONTEXT-1](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-context.md) — see [Session Aware Skills](session.md).
| `intent.service.intent.get` | `handle_get_intent` |
| `intent.service.skills.deactivate` | `_handle_deactivate` |
| `intent.service.pipelines.reload` | `handle_reload_pipelines` |

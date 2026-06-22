# Intent Service

!!! abstract "In a nutshell"
    The Intent Service is the part of OpenVoiceOS that figures out what you actually meant. Once the [Speech Service](speech-service.md) has turned your words into text, this service reads that text and decides which skill should handle it — much like a receptionist hearing your request and directing you to the right desk. It tries a series of matchers in order and stops at the first one confident enough to respond. New to the terms? See the [Glossary](glossary.md).

**Module:** `ovos_core.intent_services.service.IntentService` — [`ovos_core/intent_services/service.py`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/intent_services/service.py)

> Specification: intent/entity registration follows [OVOS-INTENT-4: Intent and Entity Registration Bus Contract](https://github.com/OpenVoiceOS/architecture/blob/dev/ovos-intent-4.md); pipeline ordering follows [OVOS-PIPELINE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/ovos-pipeline-1.md).

`IntentService` is the component of `ovos-core` responsible for routing user utterances through the configured **Intent Pipeline** until a match is found.

**In plain terms:** this is the part that takes the words you said and figures out *which* skill should answer. It runs each matcher in your pipeline in order (e.g. stop, converse, padatious, adapt, …) and stops at the first one confident enough to handle the request.

---

??? abstract "Technical Reference"

    - `IntentService.handle_utterance()` — [`ovos_core/intent_services/service.py:415`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/intent_services/service.py) — Main entry point for processing utterances.


    - `IntentService._emit_match_message()` — [`ovos_core/intent_services/service.py:275`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/intent_services/service.py) — logic for emitting match messages and activating skills.


    - `OVOSPipelineFactory.load_plugin()` — [`ovos_plugin_manager/pipeline.py`](https://github.com/OpenVoiceOS/ovos-plugin-manager/blob/dev/ovos_plugin_manager/pipeline.py) — factory that builds matcher pipeline plugins from config (`get_installed_pipeline_ids()` lists them).
    

## Utterance Handling Flow

When a `recognizer_loop:utterance` message arrives on the bus:

```
recognizer_loop:utterance
  │
  ├── UtteranceTransformersService.transform()   # may rewrite utterance text
  ├── MetadataTransformersService.transform()    # may enrich context
  ├── disambiguate_lang()                        # pick the best language
  ├── _validate_session()                        # get/create Session
  │
  └── for each pipeline stage (in order):
        match_func(utterances, lang, message)
          ├── match found → _emit_match_message() → skill intent handler
          └── no match   → next stage
              (all stages fail) → send_complete_intent_failure()

```

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

When a pipeline stage returns a match:

1. `IntentTransformersService.transform(match)` — post-process the match.


2. Build a reply message with `match.match_type` as the message type.


3. Activate the skill in the session (`sess.activate_skill(skill_id)`).


4. Emit `{skill_id}.activate` for the skill's callback.


5. Emit the reply — the skill's intent handler receives it.

## Intent Query API

External tools can query the pipeline without triggering a skill action:

```
intent.service.intent.get  {utterance: "...", lang: "..."}
  → intent.service.intent.reply  {intent: {...} | null, utterance: "..."}

```

## Bus Events Handled

| Event | Handler |
|---|---|
| `recognizer_loop:utterance` | `handle_utterance` |
| `add_context` | `handle_add_context` |
| `remove_context` | `handle_remove_context` |
| `clear_context` | `handle_clear_context` |
| `intent.service.intent.get` | `handle_get_intent` |
| `intent.service.skills.deactivate` | `_handle_deactivate` |
| `intent.service.pipelines.reload` | `handle_reload_pipelines` |

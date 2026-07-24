# Intent Service

!!! abstract "In a nutshell"
    The Intent Service is the part of OpenVoiceOS that figures out what you actually meant. Once the [Speech Service](speech-service.md) has turned your words into text, this service reads that text and decides which skill should handle it — much like a receptionist hearing your request and directing you to the right desk. It tries a series of matchers in order and stops at the first one confident enough to respond. New to the terms? See the [Glossary](glossary.md).

**Module:** `ovos_core.intent_services.service.IntentService` — [`ovos_core/intent_services/service.py`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/intent_services/service.py)

??? info "📐 Formal specification"
    The utterance lifecycle, the `match(utterances, lang, session) → Match` contract, **first-match-wins** ordering, and the dispatch/handler-lifecycle events are specified by **[OVOS-PIPELINE-1 — Utterance Lifecycle & Pipeline](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)**; what an intent *is* (keyword vs template) and the match-result shape by **[OVOS-INTENT-3 — Intent Definition](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-3.md)**; and how skills declare intents/entities on the bus by **[OVOS-INTENT-4 — Intent & Entity Registration](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-4.md)**. See also the [spec index](architecture-specs.md). `IntentService` is the reference **orchestrator** of this lifecycle; the spec topic names below are canonical.

`IntentService` is the component of `ovos-core` responsible for routing user utterances through the configured **Intent Pipeline** until a match is found.

**In plain terms:** this is the part that takes the words you said and figures out *which* skill should answer. It runs each matcher in your pipeline in order (e.g. stop, converse, padatious, adapt, …) and stops at the first one confident enough to handle the request.

---

??? abstract "Technical Reference"

    - `IntentService.handle_utterance()` — [`ovos_core/intent_services/service.py`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/intent_services/service.py) — Main entry point for processing utterances.


    - `IntentService._emit_utterance_handled()` — [`ovos_core/intent_services/service.py`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/intent_services/service.py) — terminal callback that emits the handled/complete message once a matcher's handler chain finishes.


    - `OVOSPipelineFactory.load_plugin()` — [`ovos_plugin_manager/pipeline.py`](https://github.com/OpenVoiceOS/ovos-plugin-manager/blob/dev/ovos_plugin_manager/pipeline.py) — factory that builds matcher pipeline plugins from config (`get_installed_pipeline_ids()` lists them).
    

## Utterance Handling Flow

When an `ovos.utterance.handle` message (legacy: `recognizer_loop:utterance`) arrives on the bus — the lifecycle entry point of [OVOS-PIPELINE-1 §9.1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md):

```text
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

Reading top to bottom: an incoming utterance is first reshaped by the utterance- and
metadata-transformer chains, then the best language and a `Session` are resolved once, up front —
every pipeline plugin after that point sees the same already-prepared utterance, language, and
session. The plugins themselves are then tried strictly in configured order; the first one to
return a match wins and short-circuits the rest, and if none of them do, the lifecycle ends in
`ovos.intent.unmatched` instead of a dispatch.

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


- Session state (active skills, pipeline, blacklists) is serialized into every reply message under `context.session`.

## Intent Match Emission

When a pipeline plugin returns a match:

1. `IntentTransformersService.transform(match)` — the **intent-transformer chain** post-processes the match (OVOS-TRANSFORM-1 §3.4).


2. Emit `ovos.intent.matched` (§9.2) — a notification that a plugin claimed the utterance.


3. Build the dispatch message with `match.match_type` as the message type.


4. Activate the skill in the session (`sess.activate_skill(skill_id)`) and emit `{skill_id}.activate` for the skill's callback.


5. Wrap the dispatch in the **handler-lifecycle trio** — the orchestrator emits `ovos.intent.handler.start`, then exactly one of `ovos.intent.handler.complete` / `ovos.intent.handler.error` (§8). The skill's intent handler runs between them.

    !!! note "The trio is orchestrator-owned"
        The handler — skill or plugin-bundled — is a black box, and third-party handler code
        carries no obligation here (PIPELINE-1 §8). The wrapper around the invocation emits
        `start` before the call and exactly one of `complete` (normal return) or `error`
        (exception) after it, each `forward`-derived from the dispatch message so `context`
        and `session` are preserved. The payload is `{skill_id, intent_name}`, plus
        `exception` on the `error` leg. A handler bounded by a deployment-defined timeout that
        overruns produces an `error` leg carrying a timeout `exception`; the dispatch is never
        re-emitted.

## Threading and Failure Model

Skills run **in the same process** as `ovos-core` — loaded and supervised by the `SkillManager`
thread, not a separate process per skill. Each skill talks to the bus either through
`ovos-core`'s single shared connection (`websocket.shared_connection: true`, the default) or,
if set to `false`, through its own private connection — see
[messagebus Configuration](bus-service.md#configuration).

Each skill's handlers (intents, converse, events) run synchronously inside `create_wrapper()`, on
whichever thread delivers the message to that skill's bus subscription — there is no per-handler
thread pool. This means: two skills that each own a bus connection can handle messages
concurrently, but a single slow handler blocks only its own skill's subsequent messages, not
other skills'. `create_wrapper()` runs the handler inside a `try`/`except`/`finally`: an
uncaught exception is caught, logged, reported via the handler's `.error` message (and, unless
`speak_errors=False`, spoken back to the user as a generic "I ran into an error" style dialog) —
it never crashes `ovos-core` or the offending skill's process. A handler can also raise
`AbortEvent` to end the current handler run early and skip the `.error` path, treating it as a
normal (early) completion instead of a failure.

## Intent Query API

External tools can query the pipeline without triggering a skill action:

```text
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
| `intent.service.intent.get` | `handle_get_intent` |
| `intent.service.skills.deactivate` | `_handle_deactivate` |
| `intent.service.pipelines.reload` | `handle_reload_pipelines` |

The `*_context` events (`add_context` / `remove_context` / `clear_context`) mutate the per-session
intent context (`session.intent_context`) specified by
[OVOS-CONTEXT-1](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-context.md) — see
[Session Aware Skills](session.md).

!!! note "INTENT-4 registration topics"
    Skills broadcast their intent and entity registrations on the canonical
    [OVOS-INTENT-4](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-4.md) topics —
    `ovos.intent.register.keyword`, `ovos.intent.register.template`, `ovos.intent.deregister`,
    `ovos.intent.enable` / `.disable` — alongside the legacy `register_intent` /
    `register_vocab` events, so pipeline plugins can consume the spec topics while skills on
    the legacy events keep working. Registrations are broadcast, not addressed: every
    interested plugin indexes them in parallel, and the orchestrator keeps a passive manifest
    it serves through `ovos.intent.list` and `ovos.intent.describe`.

!!! note "Reserved `intent_name` values"
    [OVOS-PIPELINE-1 §7.3](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)
    keeps a registry of `intent_name` values leased to a pipeline-plugin role: `converse`,
    `response`, `stop`, `fallback` and `common_query`. A skill or pipeline **must not** register
    a reserved name under INTENT-4 — such a registration is malformed, logged at WARN and not
    indexed; a skill subscribes to the reserved dispatch topic by framework convention instead.
    A reservation is a namespace lease, not a dispatch change: reserved-name dispatches fire
    context stamping, routing and the handler trio like any other, except that the
    `session.active_handlers` push is suppressed, since a reserved name continues or terminates
    an already-active skill's participation rather than starting a fresh one. See
    [Converse](converse.md) for how reserved names interact with converse/context handling.

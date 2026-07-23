# Bus Events Reference

!!! abstract "In a nutshell"
    Every OVOS component talks to every other one by sending small named messages over the
    shared [messagebus](bus-service.md) — a bit like a group chat where each service watches
    for the message types it cares about. This page collects the message types documented
    elsewhere in the manual into one place, grouped by which stage of the
    [utterance lifecycle](life-of-an-utterance.md) they belong to, so you don't have to hunt
    through six different pages to find one event name. Each row links back to the page that
    documents that event in context; this page does not introduce anything new.

!!! note
    Many events have a legacy `mycroft.*`/bare name alongside a newer `ovos.*` name. Both are
    emitted by default (see [Bus Service: legacy/modern topic pairs](bus-service.md#namespace-migration));
    the tables below show both where applicable.

## Listener / wake word

Emitted by `ovos-dinkum-listener` as the audio pipeline runs. See
[Speech Service](speech-service.md) for the full lifecycle.

| Event | Data | Meaning |
|---|---|---|
| `ovos.listener.record.started` (legacy: `recognizer_loop:record_begin`) | none | Command recording started |
| `ovos.listener.record.ended` (legacy: `recognizer_loop:record_end`) | none | Command recording ended |
| `recognizer_loop:wakeword` | `{"utterance", "lang"}` | Wake word fired |
| `recognizer_loop:speech.recognition.unknown` | none | STT returned nothing (silence / failure) |
| `ovos.listener.awoken` (legacy: `mycroft.awoken`) | none | Listener woke from sleep |

## STT / utterance entry point

| Event | Data | Meaning |
|---|---|---|
| `ovos.utterance.handle` (legacy: `recognizer_loop:utterance`) | `{"utterances": [str], "lang"}` | Transcribed command enters the pipeline — see [Life of an Utterance](life-of-an-utterance.md) and [Intent Service](intent-service.md#bus-events-handled) |
| `ovos.utterance.handled` | — | Universal utterance-lifecycle end-marker; see [Bus Service](bus-service.md#core-intent-pipeline) |

## Intent matching & context

Handled by `ovos-core`'s `IntentService`; see [Intent Service](intent-service.md#bus-events-handled).

| Event | Handler | Meaning |
|---|---|---|
| `ovos.utterance.handle` (legacy: `recognizer_loop:utterance`) | `handle_utterance` | Run an utterance through the pipeline |
| `add_context` / `remove_context` / `clear_context` | `handle_add_context` / `handle_remove_context` / `handle_clear_context` | Manage [intent context](context.md) |
| `intent.service.intent.get` | `handle_get_intent` | Query the best-matching intent without dispatching it |
| `intent.service.skills.deactivate` | `_handle_deactivate` | Remove a skill from active/converse consideration |
| `intent.service.pipelines.reload` | `handle_reload_pipelines` | Reload the configured pipeline plugin stack |
| `ovos.intent.unmatched` (legacy: `complete_intent_failure`) | — | No pipeline plugin claimed the utterance; routed to [Fallback](fallback-pipeline.md) |

### Converse

See [Converse Pipeline](converse-pipeline.md#bus-events-handled) for the full picture.

| Event | Handler | Meaning |
|---|---|---|
| `intent.service.skills.activate` | `handle_activate_skill_request` | Add a skill to the converse-eligible list |
| `intent.service.skills.deactivate` | `handle_deactivate_skill_request` | Remove a skill from the converse-eligible list |
| `intent.service.active_skills.get` | `handle_get_active_skills` | Query the current converse-eligible list |
| `skill.converse.get_response.enable` / `.disable` | `handle_get_response_enable` / `handle_get_response_disable` | Toggle the `get_response` window for a skill |
| `converse:skill` | `handle_converse` | Dispatch an utterance to an active skill's `converse` |
| `{skill_id}.converse.get_response` | — | Feed the user's reply back into a pending `get_response` (see [OVOSSkill API](ovos-skill.md#system-bus-events-handled-per-skill)) |

### Common Query

See [Common Query Pipeline](cq-pipeline.md).

| Event | Meaning |
|---|---|
| `question:query` | Common query pipeline request broadcast to all skills |
| `ovos.common_query.ping` | Common query service discovery |
| `question:action.{skill_id}` | Callback: this skill's answer was selected |
| `question:action` | Callback: some skill's answer was selected (generic) |

### Fallback

See [Fallback Pipeline](fallback-pipeline.md#bus-events-handled).

| Event | Handler | Meaning |
|---|---|---|
| `ovos.skills.fallback.register` | `handle_register_fallback` | Register a skill as a fallback handler |
| `ovos.skills.fallback.deregister` | `handle_deregister_fallback` | Remove a fallback handler |

## Skill lifecycle

Handled by every `OVOSSkill` instance; see [OVOSSkill API](ovos-skill.md#system-bus-events-handled-per-skill).

| Event | Meaning |
|---|---|
| `mycroft.stop` | Trigger the skill's stop flow (also the global stop broadcast, see below) |
| `{skill_id}.stop` | Skill-specific stop |
| `{skill_id}.stop.ping` | Check whether this skill can stop |
| `mycroft.skill.enable_intent` / `mycroft.skill.disable_intent` | Enable/disable one of the skill's intents |
| `mycroft.skill.set_cross_context` / `mycroft.skill.remove_cross_context` | Manage cross-skill context |
| `mycroft.skills.settings.changed` | Remote settings update |
| `ovos.skills.settings_changed` | Local settings file changed |
| `homescreen.metadata.get` | Homescreen requesting metadata |
| `{skill_id}.public_api` | Skill API introspection (see [Skill API — Inter-Skill RPC](ovos-skill.md#skill-api-inter-skill-rpc)) |

### Stop pipeline

`mycroft.stop` and the per-skill stop handshake above are driven by the dedicated
[Stop Pipeline](stop-pipeline.md#bus-events) plugin, not by a generic intent match:

| Event | Direction | Meaning |
|---|---|---|
| `stop:global` | in | Handled by `handle_global_stop` — emits `mycroft.stop` (and `ovos.utterance.handled`) |
| `stop:skill` | in | Handled by `handle_skill_stop` — forwards `{skill_id}.stop` |
| `{skill_id}.stop.ping` | out | Asks a skill whether it can stop |
| `skill.stop.pong` | in | Skill's reply |
| `{skill_id}.stop` | out | Tells a specific skill to stop |
| `{skill_id}.stop.response` | in | Skill's stop confirmation |
| `mycroft.stop` | out | Global stop signal when no skill handles it |

## TTS / audio playback

Handled by `ovos-audio`; see [Audio Service](audio-service.md).

| Event | Meaning |
|---|---|
| `ovos.utterance.speak` (legacy: `speak`) | Natural-language response to synthesize and play — the exit point of the utterance lifecycle |
| `mycroft.audio.queue` | Queue a sound effect / audio file for playback (see [`play_audio`](ovos-skill.md#playing-audio-files)) |
| `mycroft.audio.play_sound` | Play a sound effect / audio file instantly |
| `mycroft.audio.speech.stop` | Interrupt in-progress TTS speech (emitted by the [`@intent_handler(..., stop_tts=True)`](decorators.md) decorator, among others) |
| `mycroft.audio.service.play` | Legacy media audioservice: play a track (only relevant when `enable_old_audioservice` is on) |

## GUI forwarding

Handled by `ovos-gui`; see [GUI Service](gui-service.md).

| Event | Meaning |
|---|---|
| `gui.value.set` | Write session variables into a skill's GUI namespace |
| `gui.page.show` | Request one or more QML/HTML pages be shown |
| `gui.page.delete` / `gui.page.delete.all` | Remove page(s) from the namespace |
| `gui.event.send` | Send a custom event into the namespace |
| `gui.clear.namespace` | Remove a skill's namespace from the active GUI stack |

## Session & skill management

See [Bus Service: common message types](bus-service.md#key-message-categories).

| Event | From | To |
|---|---|---|
| `mycroft.skills.initialized` | `ovos-core` | GUI clients, tools |
| `skillmanager.list` | any client | `ovos-core` |
| `ovos.skills.install` | any client | `ovos-core` |
| `ovos.session.sync` | new client | `ovos-core` |
| `ovos.session.update_default` | `ovos-core` | all clients |
| `mycroft.network.connected` / `mycroft.internet.connected` | `ovos-PHAL` | `ovos-core`, skills |

## Related pages

- [Bus Service](bus-service.md) — the messagebus itself, connection details, legacy/modern topic pairs
- [Life of an Utterance](life-of-an-utterance.md) — the full request/response journey these events trace
- [Intent Service](intent-service.md), [Converse Pipeline](converse-pipeline.md), [Stop Pipeline](stop-pipeline.md), [Fallback Pipeline](fallback-pipeline.md), [Common Query Pipeline](cq-pipeline.md) — per-pipeline detail
- [Audio Service](audio-service.md), [GUI Service](gui-service.md) — output-side detail
- [OVOSSkill API](ovos-skill.md) — the skill-side handlers for these events

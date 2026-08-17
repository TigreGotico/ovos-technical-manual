# Upcoming Changes

!!! abstract "In a nutshell"
    This page tracks open pull requests across the OVOS repositories that will
    change behavior once merged. It is written for **skill, plugin, and fleet
    maintainers** planning ahead. Just curious what shipped recently? The
    [project timeline](timeline.md) is the readable what's-new list, and
    [checking what you have installed](release-channels.md#checking-what-you-have-installed)
    tells you which of it is already on your machine. Everything on this page is **unreleased and
    subject to change**: PR scope, target version, and even whether a PR lands
    at all can shift before release. Once a PR merges or closes, its content
    graduates to [Updating from Older OVOS](updating-from-older-ovos.md), which
    tracks shipped history. If a PR number below is already merged or closed by
    the time you read this, treat this page as stale for that entry and check
    the linked PR directly.

Swept: 2026-08-01. Before relying on an entry, open its PR link: if the
PR is merged or closed, the entry has already graduated to
[Updating from Older OVOS](updating-from-older-ovos.md) or been dropped.

## The new GUI

[OVOS-GUI-1](architecture-specs.md) is a ground-up rework of how OVOS renders a
screen: interchangeable render-backend plugins instead of one built-in
WebSocket/QML renderer. See [Screens on OVOS Today](gui-status.md) for the full
picture. Until this work lands, the current GUI stack (`ovos-gui` +
`ovos-shell` + `mycroft-gui-qt5`) stays **deprecated but shipped**, since it is
the only screen stack that runs today.

| PR | What it changes | Audience | Breaking | Version |
|---|---|---|---|---|
| [ovos-gui#112](https://github.com/OpenVoiceOS/ovos-gui/pull/112) | State/dispatch hub, no built-in renderer, routes by `session_id` (blocked on `opm#377`) | deployers, GUI-adapter authors, `site_id` skill authors | Yes | 2.0.0 |
| [ovos-gui#117](https://github.com/OpenVoiceOS/ovos-gui/pull/117) | Adds `SYSTEM_` template-name gate, partitions display state per session | skill authors emitting GUI pages, GUI-adapter authors | No | 1.5.0 |
| [opm#377](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/377) | Adds `AbstractGUIPlugin` framework (text, image, video, audio, weather, map, interactive) | GUI-adapter plugin authors, OVOS-GUI integrators | No | 2.12.0 |
| [opm#406](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/406) | Drops legacy Mark-1 `enclosure.*` wiring from `PHALPlugin` | PHAL/enclosure plugin authors, GUI integration maintainers | Yes | 3.0.0 |
| [ovos-bus-client#238](https://github.com/OpenVoiceOS/ovos-bus-client/pull/238) | Stops emitting null GUI keys, base64-encodes local image paths | GUI render-backend implementers, GUI wire-protocol consumers | No | 2.7.3 |
| [ovos-bus-client#197](https://github.com/OpenVoiceOS/ovos-bus-client/pull/197) | Deprecates `EnclosureAPI`, adds `PageTemplates` constants | consumers of `EnclosureAPI` and `GUIInterface` | Yes | 3.0.0 |
| [ovos-workshop#420](https://github.com/OpenVoiceOS/ovos-workshop/pull/420) | Binds `OVOSSkill.gui` to `ovos-gui-api-client`, drops `ui_directories` | skill authors | Yes | 10.0.0 |
| [ovos-workshop#421](https://github.com/OpenVoiceOS/ovos-workshop/pull/421) | Deletes the skill-side resting-screen API | skill authors, plus downstream skills listed below | Yes | 10.0.0 |

`ovos-workshop#421` also touches `ovos-ocp-audio-plugin`, `ovos-skill-iss-location`,
`ovos-pydantic-models`, and `ovos-skill-homescreen`.

## ovos-media

`ovos-media` is **not officially released** — [Media Service](ovos-media.md) rates it proof-of-concept on the [maturity scale](maturity.md). `ovos-audio` remains
the production audio service, and stock installs keep
`enable_old_audioservice: true` (the default). See
[Media Service (ovos-media)](ovos-media.md) for its maturity status. Two
things are changing on top of that baseline: the legacy audio service is
starting to shed its OCP integration, and the intended role of an OCP skill is
shifting.

MediaProvider plugins (`opm.media.provider`) are meant to own catalog search
once `ovos-media` loads them in-process. OCP skills stay fully supported, but
their intended role narrows: a skill whose job is "answer catalog search
queries" (a station list, a podcast feed) is expected to become a
MediaProvider plugin over time, while a skill where **the skill itself is the
playable media** (a voice game, an ebook reader) stays an OCP skill. See
[OCP Skills](ocp-skills.md) for the full split.

| PR | What it changes | Audience | Breaking | Version |
|---|---|---|---|---|
| [ovos-workshop#423](https://github.com/OpenVoiceOS/ovos-workshop/pull/423) | Deprecates `OVOSCommonPlaybackSkill` toward `opm.media.provider` | OCP skill authors | No | 9.4.0 |
| [ovos-workshop#428](https://github.com/OpenVoiceOS/ovos-workshop/pull/428) | Makes OCP playback state per-session (stacked on #427) | OCP/game-skill authors, HiveMind/remote deployers | No | 9.4.0 |
| [ovos-audio#115](https://github.com/OpenVoiceOS/ovos-audio/pull/115) | Drops OCP integration and `disable_ocp` from `ovos-audio` | skill authors/deployers using OCP in `ovos-audio` | Yes | 3.0.0 |
| [ovos-ocp-pipeline-plugin#156](https://github.com/OpenVoiceOS/ovos-ocp-pipeline-plugin/pull/156) | Dispatches search in-process to installed MediaProvider plugins, merged with the existing bus-only OCP-skill search rather than replacing it (dedup only drops a provider entry whose URI a legacy result already covers). No bus message types change. Enabled by default, with an explicit `media_providers.enabled: false` off-switch under the OCP pipeline config; with no MediaProvider plugins installed, behavior is byte-identical to today | deployers running MediaProvider plugins, OCP pipeline config authors | No | not yet released |

## Official spec adoption

Repositories across the org are being brought into conformance with the
[Formal Specifications](architecture-specs.md), largely OVOS-STOP-1,
OVOS-CONTEXT-1, OVOS-TRANSFORM-1, and OVOS-PIPELINE-1. A related but separate
effort, the legacy bus-namespace migration, has not removed anything yet:
`ovos-bus-client`'s namespace bridge is still live on `dev`, with `modernize` and
`emit_legacy` both defaulting to on, and its kill-switch
([ovos-bus-client#272](https://github.com/OpenVoiceOS/ovos-bus-client/pull/272)) is still an
open draft. See [Bus Namespace Migration](bus-namespace-migration.md). The PRs below carry
that migration the rest of the way (rows marked **merged** have already landed
and ship on current `dev` prereleases; the rest are still open): a set of coordinated kill-switches that
drop the last hardcoded legacy topic literals from `ovos-core`, `ovos-workshop`,
and the `ovos-utils` test double. Each is explicitly gated to merge only once
fleets no longer run legacy-namespace consumers.

| PR | What it changes | Audience | Breaking | Version |
|---|---|---|---|---|
| [ovos-core#802](https://github.com/OpenVoiceOS/ovos-core/pull/802) | Reworks stop dispatch onto one spec path (requires `opm>=2.9.0a1`, supersedes #777) | skill authors, deployers of legacy skills, remote/HiveMind stop consumers | Yes | 3.0.0a1 (merged, on `dev`) |
| [ovos-core#777 (closed)](https://github.com/OpenVoiceOS/ovos-core/pull/777) | OVOS-STOP-1 bus surface bridged to legacy topics (superseded by #802) | n/a | No | 2.6.0 |
| [ovos-core#786](https://github.com/OpenVoiceOS/ovos-core/pull/786) | Core-resident OVOS-CONTEXT-1 store, additive | skill authors declaring context, remote session-sync consumers | No | 3.0.0a1 (merged, on `dev`) |
| [ovos-core#785](https://github.com/OpenVoiceOS/ovos-core/pull/785) | Conforms transformer chains to OVOS-TRANSFORM-1 | transformer plugin authors | No | 2.5.10a1 (merged, on `dev`) |
| [ovos-workshop#500](https://github.com/OpenVoiceOS/ovos-workshop/pull/500) | Drops the `.intent`-topic dual-bind for canonical intent topics | skill authors on `.intent` topics, mixed-container deployers | Not marked breaking, but drops the dual bind | 9.3.11a2 (merged, on `dev`) |
| [ovos-workshop#414](https://github.com/OpenVoiceOS/ovos-workshop/pull/414) | Routes resource loading through `ovos-spec-tools`, back-compat mixin | skill authors on the legacy resource API | No | 9.3.3 |
| [ovos-persona#192](https://github.com/OpenVoiceOS/ovos-persona/pull/192) | Fixes persona's PIPELINE-1 done-signal timing | skill/pipeline authors on `ovos-core>=2.3.0a1` | No | 0.9.1 |
| [ovos-bus-client#271](https://github.com/OpenVoiceOS/ovos-bus-client/pull/271) | Adds a version-skew bridge for `.intent` topics (removed later by #272) | deployers running mixed-version fleets | No | 2.8.0a1 (merged, on `dev`) |
| [ovos-utils#411](https://github.com/OpenVoiceOS/ovos-utils/pull/411) | Mirrors the #271 bridge in `FakeBus`/`AsyncFakeBus` — **shipped** via the superseding [#417](https://github.com/OpenVoiceOS/ovos-utils/pull/417) in 0.13.10a1; #411 itself stays open as a duplicate | test-harness authors (ovoscope, skill test suites) | No | shipped (0.13.10a1) |
| [ovos-bus-client#272](https://github.com/OpenVoiceOS/ovos-bus-client/pull/272) | Kill-switch: drops the namespace bridge from `MessageBusClient` (blocked on #271) | deployers with legacy-namespace consumers | Yes | 3.0.0 |
| [ovos-core#837](https://github.com/OpenVoiceOS/ovos-core/pull/837) | Kill-switch: drops the last legacy-topic literals from `ovos-core` | deployers/plugin authors on legacy topic spellings | Yes | 3.0.0 |
| [ovos-workshop#501](https://github.com/OpenVoiceOS/ovos-workshop/pull/501) | Kill-switch: drops legacy-topic literals from `ovos-workshop` (blocked on #500) | deployers/skill authors on legacy topic spellings | Yes | 10.0.0 |
| [ovos-utils#412](https://github.com/OpenVoiceOS/ovos-utils/pull/412) | Kill-switch: drops the bridge from `FakeBus` (its prerequisite bridge shipped via #417) | test-harness authors on legacy-compat flags | Yes | 1.0.0 |

The four kill-switch PRs above (`ovos-bus-client#272`, `ovos-core#837`,
`ovos-workshop#501`, `ovos-utils#412`) must merge together. `ovos-bus-client#272`
is explicit: "do not merge until then." `ovos-utils#412` would also be that
package's first stable 1.0 release.

## Other changes by repository

Entries here are PRs that change behavior but don't fit the three
headline efforts above. Most are still open; rows marked **merged** have
already landed on that repo's `dev`.

### ovos-audio

| PR | What it changes | Audience | Breaking | Version |
|---|---|---|---|---|
| [#146](https://github.com/OpenVoiceOS/ovos-audio/pull/146) | Adds duration to the `utterance_start` recognizer event | skill authors, remote bus consumers, analytics tooling | No | 2.2.0 |

### ovos-bus-client

| PR | What it changes | Audience | Breaking | Version |
|---|---|---|---|---|
| [#222](https://github.com/OpenVoiceOS/ovos-bus-client/pull/222) | Fixes `EventsAPI` to emit the right scheduler topic | callers of `EventsAPI.update_scheduled_event()` | No | 2.7.3 |
| [#200](https://github.com/OpenVoiceOS/ovos-bus-client/pull/200) | Adds `AsyncMessageBusClient`, an async-native client | bus-client consumers, plugin authors wanting async I/O | No | 2.8.0 |

### ovos-config

| PR | What it changes | Audience | Breaking | Version |
|---|---|---|---|---|
| [#194](https://github.com/OpenVoiceOS/ovos-config/pull/194) | Adds `AssistantConfig` runtime-write layer, deprecates `RemoteConf` | skill/plugin authors writing config, deployers | No | 2.4.0 |
| [#282](https://github.com/OpenVoiceOS/ovos-config/pull/282) | Adds offline STT/TTS recommends for 49 languages | deployers running `autoconfigure --offline`, langpack maintainers | No | 2.4.0 |
| [#274](https://github.com/OpenVoiceOS/ovos-config/pull/274) | Moves the `--gpu` STT tier onto `onnx-asr` with `use_cuda` | deployers running the `--gpu` autoconfigure tier | No | 2.4.0 |
| [#278](https://github.com/OpenVoiceOS/ovos-config/pull/278) | Documents `ww_urls`/`stt_urls` `open_data` config keys | deployers opting into `open_data`, listener users | No | 2.4.0 |
| [#267](https://github.com/OpenVoiceOS/ovos-config/pull/267) | Fixes a wrong fasterwhisper model id in the GPU-tier recommend | deployers on the GPU-tier `en-us` recommend | No | 2.3.7 |
| [#82](https://github.com/OpenVoiceOS/ovos-config/pull/82) | Turns on audio ducking by default | end users/deployers of the legacy `ovos-audio` service | Not breaking, but changes default audio behavior | 2.3.7 |

### ovos-core

| PR | What it changes | Audience | Breaking | Version |
|---|---|---|---|---|
| [#832](https://github.com/OpenVoiceOS/ovos-core/pull/832) | Adds pipeline blacklisting at load time and per session | deployers tuning boot cost and per-session policy | No | 2.6.0a1 (merged, on `dev`) |
| [#689](https://github.com/OpenVoiceOS/ovos-core/pull/689) | Adds pipeline id and core version to intent metrics | consumers of the intent-metrics telemetry event | No | 2.6.0 |

### ovos-dinkum-listener

| PR | What it changes | Audience | Breaking | Version |
|---|---|---|---|---|
| [#243](https://github.com/OpenVoiceOS/ovos-dinkum-listener/pull/243) | Adds opt-in upload of wake word/STT samples (pairs with ovos-config#278) | deployers who opt in to data-sharing | No | 0.8.3 |
| [#215](https://github.com/OpenVoiceOS/ovos-dinkum-listener/pull/215) | Adds a `duration` field to the utterance bus message | skill/plugin authors, remote bus consumers | No | 0.8.3 |

### ovos-gui

| PR | What it changes | Audience | Breaking | Version |
|---|---|---|---|---|
| [#73](https://github.com/OpenVoiceOS/ovos-gui/pull/73) | Adds PyHTMX GUI client support (likely stale, predates the adapter rework) | developers of PyHTMX-based GUI clients | No | 1.5.0 |
| [#26](https://github.com/OpenVoiceOS/ovos-gui/pull/26) | Adds initial React GUI support (likely superseded, inactive since 2024) | developers of a React-based GUI client | No | 1.5.0 |

### ovos-persona-server

| PR | What it changes | Audience | Breaking | Version |
|---|---|---|---|---|
| [#60](https://github.com/OpenVoiceOS/ovos-persona-server/pull/60) | Fixes the `toolbox_id` loader, plugins own their id now | OPM `ToolBox` plugin authors | Framed as a fix, but breaks the constructor contract | 0.13.4a1 (merged, on `dev`) |
| [#38](https://github.com/OpenVoiceOS/ovos-persona-server/pull/38) | Adds an OpenAI-proxy Docker Compose config and docs | deployers wanting a containerized OpenAI-compatible endpoint | No | 0.14.0 |

### ovos-plugin-manager

| PR | What it changes | Audience | Breaking | Version |
|---|---|---|---|---|
| [#385](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/385) | Adds a triples semantic pipeline, fixes a discovery bug | plugin authors building semantic/knowledge-graph plugins | No | 2.12.0 |
| [#295](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/295) | Modernizes `importlib`, deprecates `normalize_lang()` | plugin authors, deployers on older Python | No, no public symbol removed | 2.11.2 |

### ovos-workshop

| PR | What it changes | Audience | Breaking | Version |
|---|---|---|---|---|
| [#372](https://github.com/OpenVoiceOS/ovos-workshop/pull/372) | Adds Pydantic models and structured errors to the Skill API | skill API consumers, plugin authors calling skill APIs | Backward compatible except structured errors replace silence | 9.4.0 |

---
**Read next:** [Server Compatibility Layers](server-compat-layers.md)
**Related:** [Updating from Older OVOS](updating-from-older-ovos.md) · [Version Compatibility Guide](version-compat-guide.md) · [Screens on OVOS Today](gui-status.md) · [Formal Specifications](architecture-specs.md)

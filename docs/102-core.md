# ovos-core

`ovos-core` contains the central intelligence of OpenVoiceOS. It manages skill loading, intent routing, and coordinates all NLP components. Every user utterance flows through this service.

## Architecture

```
ovos-messagebus  (WebSocket pub/sub)
      │
      ├── ovos-core  (this service)
      │     ├── SkillManager          – loads/unloads skill plugins
      │     ├── IntentService         – routes utterances through the pipeline
      │     │     ├── UtteranceTransformersService
      │     │     ├── MetadataTransformersService
      │     │     ├── IntentTransformersService
      │     │     └── Pipeline plugins (Adapt, Padatious, Converse, Fallback, …)
      │     ├── SkillsStore           – runtime pip install/uninstall
      │     └── EventScheduler        – timed bus events
      │
      ├── ovos-dinkum-listener  – STT / wake-word → recognizer_loop:utterance
      ├── ovos-audio            – TTS playback
      ├── ovos-gui              – GUI layer
      └── ovos-PHAL             – hardware/platform plugins
```

## Entry Points

| Command | Module |
|---|---|
| `ovos-core` | `ovos_core.__main__:main` |
| `ovos-intent-service` | `ovos_core.intent_services.service:launch_standalone` |
| `ovos-skill-installer` | `ovos_core.skill_installer:launch_standalone` |

## Quick Start

```bash
pip install ovos-core
ovos-core           # starts SkillManager + IntentService + installer + scheduler
```

Run only the intent service (no skills):
```bash
ovos-intent-service
```

## Subsystem Enable Flags

`SkillManager.__init__` and `main()` accept boolean flags to opt out of subsystems:

| Flag | Subsystem |
|---|---|
| `enable_intent_service` | `IntentService` |
| `enable_installer` | `SkillsStore` |
| `enable_event_scheduler` | `EventScheduler` |
| `enable_skill_api` | `SkillApi.connect_bus` |
| `enable_file_watcher` | Settings file watcher |

CLI equivalents: `--disable-intent-service`, `--disable-installer`, etc.

## Process Status States

Each subsystem publishes its state to the bus via `ProcessStatus`:

```
started → alive → ready → stopping
```

`IntentService` emits `mycroft.intents.is_ready` when it reaches the `ready` state.

## Startup Flow

1. Connect to MessageBus (`MessageBusClient.run_in_thread`)
2. Instantiate `SkillManager` (daemon thread)
   - Optionally starts `IntentService`, `SkillsStore`, `EventScheduler`
3. `SkillManager.run()`:
   a. Wait for `IntentService` to report ready (`mycroft.intents.is_ready`)
   b. Load offline skills (`_load_on_startup`)
   c. Query PHAL for network/internet status → load network/internet skills
   d. Emit `mycroft.skills.initialized`
   e. Loop every 30 s: scan for newly installed skills, call watchdog
4. On exit: unload all skills gracefully, shutdown subsystems

---

## SkillManager

**Module:** `ovos_core.skill_manager.SkillManager`

`SkillManager` is a daemon `Thread` that owns the full lifecycle of skill plugins: discovery, loading, connectivity-gating, and graceful shutdown.

### Skill Discovery

Skills are Python packages that register themselves via the `opm.skills` entry point group. `ovos-plugin-manager` discovers them with `find_skill_plugins()`, which returns a `{skill_id: SkillClass}` dict.

```python
from ovos_plugin_manager.skills import find_skill_plugins
plugins = find_skill_plugins()
```

### Connectivity Gating

Skills declare their runtime requirements (`network_before_load`, `internet_before_load`, `requires_gui`) in `RuntimeRequirements`. The skill manager only loads a skill when those requirements are met:

| Event | Action |
|---|---|
| Startup (offline) | Load skills with no network/internet requirement |
| `mycroft.network.connected` | Load skills requiring network |
| `mycroft.internet.connected` | Load skills requiring internet |
| `mycroft.gui.available` | Load skills requiring GUI |

Network/internet state is queried from PHAL at startup via `ovos.PHAL.internet_check`; falls back to a direct HTTP check if PHAL is unavailable.

### Loading a Skill

```
find_skill_plugins()
  → _get_plugin_skill_loader(skill_id, skill_class)
    → PluginSkillLoader.load(skill_class)
      → mycroft.skill.loaded (bus event)
```

Each skill gets its own bus connection when `websocket.shared_connection` is `false` in config (isolation from BusBricker-style attacks).

### Blacklisting

Skills listed in `skills.blacklisted_skills` in `mycroft.conf` are skipped at load time. The recommended approach is to uninstall unwanted skills rather than blacklist them.

### Intent Training

After new skills are loaded, the manager requests pipeline re-training:

```
mycroft.skills.train  →  (pipeline plugins train)  →  mycroft.skills.trained
```

Training has a 60-second timeout. On failure, an error is logged but the manager continues.

### Settings File Watcher

When enabled, a `FileWatcher` monitors `~/.config/ovos/skills/*/settings.json`. Any change emits:

```
ovos.skills.settings_changed  {skill_id: "..."}
```

### Bus Events Handled

| Event | Handler |
|---|---|
| `skillmanager.list` | `send_skill_list` |
| `skillmanager.activate` | `activate_skill` |
| `skillmanager.deactivate` | `deactivate_skill` |
| `skillmanager.keep` | `deactivate_except` |
| `mycroft.network.connected` | `handle_network_connected` |
| `mycroft.internet.connected` | `handle_internet_connected` |
| `mycroft.gui.available` | `handle_gui_connected` |
| `mycroft.network.disconnected` | `handle_network_disconnected` |
| `mycroft.internet.disconnected` | `handle_internet_disconnected` |
| `mycroft.gui.unavailable` | `handle_gui_disconnected` |

---

## IntentService

**Module:** `ovos_core.intent_services.service.IntentService`

`IntentService` receives `recognizer_loop:utterance` messages from the listener and walks the configured pipeline until a skill claims the utterance.

### Utterance Handling Flow

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

### Language Disambiguation

Language is chosen by priority from message context keys:

1. `stt_lang` — language used by STT to transcribe
2. `request_lang` — volunteered by the source (e.g. wake word)
3. `detected_lang` — detected by a transformer plugin
4. Config default / `message.data["lang"]`

The chosen language is validated against `valid_langs` from config using `langcodes.closest_match` (max distance 10).

### Multilingual Matching

When `intents.multilingual_matching` is `true` in config, if the primary language produces no match, all other configured languages are tried in order.

### Session Management

Each utterance is associated with a `Session`. The default session expires and is reset automatically. Non-default sessions (e.g. from HiveMind clients) are updated but not reset. Session state (active skills, pipeline, blacklists) is serialised into every reply message under `context.session`.

### Intent Match Emission

When a pipeline stage returns a match (`IntentHandlerMatch`):

1. `IntentTransformersService.transform(match)` — post-process the match
2. Build a reply message with `match.match_type` as the message type
3. Activate the skill in the session (`sess.activate_skill(skill_id)`)
4. Emit `{skill_id}.activate` for the skill's callback
5. Emit the reply — the skill's intent handler receives it

### Intent Query API

External tools can query the pipeline without triggering a skill:

```
intent.service.intent.get  {utterance: "...", lang: "..."}
  → intent.service.intent.reply  {intent: {...} | null, utterance: "..."}
```

### Bus Events Handled

| Event | Handler |
|---|---|
| `recognizer_loop:utterance` | `handle_utterance` |
| `add_context` | `handle_add_context` |
| `remove_context` | `handle_remove_context` |
| `clear_context` | `handle_clear_context` |
| `intent.service.intent.get` | `handle_get_intent` |
| `intent.service.skills.deactivate` | `_handle_deactivate` |
| `intent.service.pipelines.reload` | `handle_reload_pipelines` |

---

## Intent Pipeline

The pipeline is an ordered list of matchers configured per-session. The default comes from `mycroft.conf`:

```json
{
  "intents": {
    "pipeline": [
      "stop_high",
      "converse",
      "ocp_high",
      "padatious_high",
      "adapt_high",
      "ocp_medium",
      "fallback_high",
      "stop_medium",
      "adapt_medium",
      "padatious_medium",
      "adapt_low",
      "common_qa",
      "fallback_medium",
      "fallback_low"
    ]
  }
}
```

Pipeline stages are also configurable per-`Session`, allowing HiveMind clients or individual users to have different pipelines.

### Pipeline Plugin IDs

Pipeline plugins are loaded by `OVOSPipelineFactory` from the `opm.pipeline` entry point group. Each plugin ID maps to one or more stage names:

| Stage name(s) | Plugin ID | Matcher type |
|---|---|---|
| `converse` | `ovos-converse-pipeline-plugin` | `PipelinePlugin` |
| `common_qa` | `ovos-common-query-pipeline-plugin` | `PipelinePlugin` |
| `fallback_high/medium/low` | `ovos-fallback-pipeline-plugin` | `ConfidenceMatcherPipeline` |
| `stop_high/medium/low` | `ovos-stop-pipeline-plugin` | `ConfidenceMatcherPipeline` |
| `adapt_high/medium/low` | `ovos-adapt-pipeline-plugin` | `ConfidenceMatcherPipeline` |
| `padatious_high/medium/low` | `ovos-padatious-pipeline-plugin` | `ConfidenceMatcherPipeline` |
| `padacioso_high/medium/low` | `ovos-padacioso-pipeline-plugin` | `ConfidenceMatcherPipeline` |
| `ocp_high/medium/low/legacy` | `ovos-ocp-pipeline-plugin` | `ConfidenceMatcherPipeline` |

`ovos-core` ships three built-in pipeline plugins via its own entry points:
- `ovos-converse-pipeline-plugin` → `ConverseService` (see [Converse Pipeline](converse_pipeline.md))
- `ovos-fallback-pipeline-plugin` → `FallbackService` (high/medium/low)
- `ovos-stop-pipeline-plugin` → `StopService` (high/medium/low)

### Plugin Resolution

`IntentService.get_pipeline_matcher(matcher_id)` resolves a stage name:

1. Apply legacy name migration map
2. Strip `-high`/`-medium`/`-low` suffix to get the plugin base ID
3. Look up the loaded plugin in `self.pipeline_plugins`
4. Return the appropriate method (`match`, `match_high`, `match_medium`, or `match_low`)

Unloaded or unknown plugins are skipped with a warning — they do not cause startup failures.

---

## Transformer Plugins

Three transformer stages run before pipeline matching on every utterance.

### UtteranceTransformersService

**Entry point group:** `opm.utterance_transformer` | **Config key:** `utterance_transformers`

Receives the raw utterance list and may rewrite it. Changes are logged as `utterances transformed: X -> Y`. Use cases: spelling correction, canonicalisation, language normalisation.

```python
utterances, context = utterance_transformers.transform(utterances, context)
```

### MetadataTransformersService

**Entry point group:** `opm.metadata_transformer` | **Config key:** `metadata_transformers`

Receives only `message.context` and may enrich it with additional metadata. Does not alter the utterance text. Use cases: speaker identification, emotion detection, tagging detected language.

```python
context = metadata_transformers.transform(context)
```

### IntentTransformersService

**Entry point group:** `opm.intent_transformer` | **Config key:** `intent_transformers`

Runs after a pipeline match is found. Receives and may modify the `IntentHandlerMatch` object before the reply is emitted. Use cases: entity normalisation, confidence adjustment.

```python
match = intent_transformers.transform(match)
```

### Plugin Priority

All transformer services load plugins ordered by `priority` (higher number = called first). Enable/disable each plugin in `mycroft.conf`:

```json
{
  "utterance_transformers": {
    "ovos-utterance-normalizer": {"active": true},
    "ovos-utterance-plugin-cancel": {},
    "ovos-utterance-corrections-plugin": {}
  },
  "metadata_transformers": {},
  "intent_transformers": {}
}
```

A plugin not listed in config is not loaded even if installed.

---

## Converse Service

**Module:** `ovos_core.intent_services.converse_service.ConverseService`
**Pipeline plugin ID:** `ovos-converse-pipeline-plugin`

Converse allows active skills (recently used) to intercept utterances before general intent matching. Active skills are stored in the `Session` object.

### How It Works

1. `converse` stage is hit in the pipeline
2. `ConverseService.match()` iterates active skills in priority order
3. For each skill, emits `{skill_id}.converse.request` and waits for a response
4. If the skill returns `True`, the utterance is consumed
5. If not, the next active skill is tried

### Configuration

```json
{
  "skills": {
    "converse": {
      "timeout": 300,
      "converse_mode": "accept_all",
      "converse_activation": "accept_all",
      "converse_whitelist": [],
      "converse_blacklist": [],
      "max_activations": -1,
      "cross_activation": true,
      "max_skill_runtime": 10
    }
  }
}
```

| Config Key | Description |
|---|---|
| `timeout` | Seconds before an idle skill is removed from converse mode (default 300) |
| `converse_mode` | `"accept_all"` / `"whitelist"` / `"blacklist"` |
| `converse_activation` | `"accept_all"` / `"priority"` / `"whitelist"` / `"blacklist"` |
| `max_activations` | Max consecutive self-activations per minute (`-1` = unlimited) |
| `cross_activation` | Whether any skill can activate any other skill |
| `max_skill_runtime` | Maximum seconds to wait for a skill's `converse()` response |

See [Converse Pipeline](converse_pipeline.md) for full documentation.

---

## Fallback Service

**Module:** `ovos_core.intent_services.fallback_service.FallbackService`
**Pipeline plugin ID:** `ovos-fallback-pipeline-plugin`

Fallback skills handle utterances that nothing else could match. They register with a priority number (lower = higher priority).

| Stage | Priority range |
|---|---|
| `fallback_high` | 0–49 |
| `fallback_medium` | 50–89 |
| `fallback_low` | 90–100+ |

```json
{
  "skills": {
    "fallbacks": {
      "fallback_priorities": {"my-skill-id": 10},
      "fallback_mode": "accept_all",
      "fallback_whitelist": [],
      "fallback_blacklist": []
    }
  }
}
```

See [Fallback Pipeline](fallback_pipeline.md) for full documentation.

---

## Skill Installer (SkillsStore)

**Module:** `ovos_core.skill_installer.SkillsStore`

`SkillsStore` provides runtime skill and package management via the MessageBus. Uses `uv pip` if `uv` is on `$PATH`; otherwise falls back to `pip`. A named lock (`ovos_pip.lock`) prevents concurrent installs.

```json
{
  "skills": {
    "installer": {
      "constraints": "https://raw.githubusercontent.com/OpenVoiceOS/ovos-releases/refs/heads/main/constraints-stable.txt",
      "sounds": {
        "pip_error": "snd/error.mp3",
        "pip_success": "snd/acknowledge.mp3"
      }
    }
  }
}
```

### Install/Uninstall Events

```
ovos.skills.install        data: {"packages": ["ovos-skill-foo"]}
  → ovos.skills.install.complete  (success)
  → ovos.skills.install.failed    (error)

ovos.skills.uninstall      data: {"packages": ["ovos-skill-foo"]}
  → ovos.skills.uninstall.complete
  → ovos.skills.uninstall.failed

ovos.pip.install           data: {"packages": ["some-lib>=1.0"]}
ovos.pip.uninstall         data: {"packages": ["some-lib"]}
```

After a successful skill install, `ovos-plugin-manager`'s entry point cache is reloaded so the new skill is discovered on the next `SkillManager` scan cycle (every 30 s).

### InstallError Types

| `InstallError` | Meaning |
|---|---|
| `DISABLED` | pip disabled in config |
| `PIP_ERROR` | subprocess returned non-zero |
| `BAD_URL` | URL validation failed |
| `NO_PKGS` | empty package list |

---

## MessageBus Events Reference

Key events emitted or handled by `ovos-core`:

### Utterance / Intent Flow

| Event | Direction | Description |
|---|---|---|
| `recognizer_loop:utterance` | listener → core | User utterance, triggers intent pipeline |
| `add_context` / `remove_context` / `clear_context` | skill → core | Manage session context entities |
| `ovos.utterance.handled` | core → * | Utterance processing complete |
| `complete_intent_failure` | core → * | No pipeline stage could handle the utterance |

### Intent Service API

| Event | Direction | Description |
|---|---|---|
| `intent.service.intent.get` | * → core | Query the pipeline without triggering a skill |
| `intent.service.intent.reply` | core → * | Response to the query |
| `intent.service.pipelines.reload` | * → core | Reload all pipeline plugins |
| `mycroft.intents.is_ready` | * → core | Health-check: is IntentService ready? |

### Skill Manager

| Event | Direction | Description |
|---|---|---|
| `mycroft.skills.initialized` | core → * | All startup skills loaded, manager ready |
| `mycroft.skills.train` | core → * | Request pipeline intent training |
| `mycroft.skill.loaded` | core → * | A skill was successfully loaded |
| `ovos.skills.settings_changed` | core → * | A skill's `settings.json` file changed |

### Converse & Fallback

| Event | Direction | Description |
|---|---|---|
| `{skill_id}.converse.request` | core → skill | Ask a skill to handle converse |
| `skill.converse.get_response.enable` | skill → core | Lock converse to this skill (during `get_response`) |
| `ovos.skills.fallback.register` | skill → core | Register as a fallback skill with a priority |

### Skill Installer

| Event | Direction | Description |
|---|---|---|
| `ovos.skills.install` | * → core | Install skill packages via pip |
| `ovos.skills.install.complete` | core → * | Install succeeded |
| `ovos.skills.install.failed` | core → * | Install failed |
| `ovos.pip.install` / `ovos.pip.uninstall` | * → core | Install/uninstall arbitrary pip packages |

---

## Integration Testing

End-to-end tests live at `test/end2end/` and use **ovoscope** — the OVOS E2E testing framework. Each test spins up a `MiniCroft` (a `SkillManager` subclass backed by `FakeBus`) with specific skill plugins and asserts on the full bus message sequence.

```
ovos-core/test/end2end/
├── test_adapt.py         # Adapt intent pipeline: match, blacklist, intent blacklist
└── ...                   # additional pipeline tests
```

See [ovoscope documentation](451-ovoscope-usage.md) for the full tutorial.

---

## Related Pages

- [Bus Service](100-bus_service.md) — MessageBus WebSocket server
- [Bus Client](900-bus_client.md) — `MessageBusClient`, `Message`, `Session`
- [Bus Session](901-bus-session.md) — `Session`, `SessionManager`, per-session pipeline
- [Configuration](110-config.md) — `mycroft.conf` configuration
- [Converse Pipeline](converse_pipeline.md) — converse pipeline details
- [Fallback Pipeline](fallback_pipeline.md) — fallback pipeline details
- [Skill Development](400-skill-design-guidelines.md) — writing skills for OVOS
- [Skill Classes](412-skill-classes.md) — `OVOSSkill`, `FallbackSkill`, and all base classes

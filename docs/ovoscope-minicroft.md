# MiniCroft

!!! abstract "In a nutshell"
    To check that a skill behaves correctly, you would normally need to run the whole assistant — microphone, speakers, network and all. `MiniCroft` is a stripped-down stand-in: a tiny, self-contained version of OVOS that loads just the skills you care about and pretends to be the real thing, so automated tests can talk to it and check the answers. It is the test-bench that powers OvoScope, the OVOS skill-testing tool. This is a developer page; see the [Glossary](glossary.md) for unfamiliar terms.

`MiniCroft` is a minimal, in-process OVOS Core that loads real skill plugins and runs the full intent pipeline on a `FakeBus`. It is the execution engine behind every OvoScope test.

!!! tip "New here? You rarely build `MiniCroft` directly"
    For most tests you never touch this class — `End2EndTest` creates and tears
    down a `MiniCroft` for you. Reach for `get_minicroft()` only when you want to
    drive the bus by hand (see [CaptureSession](capture-session.md)) or reuse one
    runtime across several tests to avoid re-training intent models each time.

## Class: `MiniCroft`

```python
from ovoscope import MiniCroft

```
Subclass of `ovos_core.skill_manager.SkillManager`. The `get_minicroft()` factory
replaces the real WebSocket bus with `FakeBus`, disables components not needed for
testing, and only loads the skills you specify.

### Constructor

```python
MiniCroft(
    skill_ids: list[str],
    enable_installer: bool = False,
    enable_intent_service: bool = True,
    enable_event_scheduler: bool = False,
    enable_file_watcher: bool = False,
    enable_skill_api: bool = True,
    extra_skills: dict[str, OVOSSkill] | None = None,
    isolate_config: bool = True,
    default_pipeline: list[str] | None = ...,  # sentinel: auto-selected (see below)
    lang: str | None = None,
    secondary_langs: list[str] | None = None,
    pipeline_config: dict[str, dict] | None = None,
    *args, **kwargs,
)

```

| Parameter | Default | Description |
|---|---|---|
| `skill_ids` | required | [Skill](skill-design-guidelines.md) plugin IDs to load (from installed entry points) |
| `enable_installer` | `False` | Enable the runtime pip installer service |
| `enable_intent_service` | `True` | Enable intent matching pipeline |
| `enable_event_scheduler` | `False` | Enable scheduled event service |
| `enable_file_watcher` | `False` | Enable settings file watcher |
| `enable_skill_api` | `True` | Enable skill API exposure |
| `extra_skills` | `None` | Inject skill instances directly (useful for testing a skill class before packaging) |
| `isolate_config` | `True` | Clear user XDG configs so tests are reproducible |
| `default_pipeline` | *auto* | Override the session pipeline for deterministic intent matching. When left unset it auto-selects `DEFAULT_TEST_PIPELINE` if those stages are installed, otherwise `LIGHT_TEST_PIPELINE` (which avoids C-extension engines like Padatious). Pass an explicit list to pin it, or `None` to use the system config. |
| `lang` | `None` | Override the system default language (`Configuration()["lang"]`). Patched before [Adapt](adapt-pipeline.md)/[Padatious](padatious-pipeline.md) init so vocab is registered for this language. |
| `secondary_langs` | `None` | Set `Configuration()["secondary_langs"]`. Adapt and Padatious create per-language engines for each language in this list, enabling multilingual intent matching. |
| `pipeline_config` | `None` | Per-pipeline plugin config overrides. A `dict` keyed by the plugin's config key under `Configuration()["intents"]` (e.g. `"ovos_m2v_pipeline"`). Patched before `super().__init__()` so pipeline plugins read overridden values during their `__init__`. Restored in `stop()`. |

### Key attributes

| Attribute | Type | Description |
|---|---|---|
| `bus` | `FakeBus` | The in-process message bus |
| `boot_messages` | `list[Message]` | All messages captured during startup |
| `pipeline` | property → `list[str]` | The active pipeline stage IDs |
| `skill_ids` | `list[str]` | The skill IDs this runtime loaded |
| `status` | process-status object | Lifecycle tracker; `status.state` is a `ProcessState` (e.g. `ProcessState.READY`) |

### `MiniCroft.run()`
Loads plugins and marks the runtime as ready. Called internally by `start()`. Does not block — returns after all skills are loaded.

### `MiniCroft.inject_message(msg)`
Emit a `Message` onto the in-process `FakeBus` as if it came from a client. Useful
for driving an interaction by hand instead of through `End2EndTest`.

### `MiniCroft.stop()`
Shuts down skills, restores any patched config/pipeline (when `isolate_config=True`),
and closes the bus.
---

## Factory: `get_minicroft()`

```python
from ovoscope import get_minicroft
croft = get_minicroft(
    skill_ids: list[str] | str,
    *args,
    max_wait: float = 60,   # seconds to wait for READY before TimeoutError
    **kwargs,               # forwarded to the MiniCroft constructor
)

```
Builds, starts, and blocks until the `MiniCroft` reaches `ProcessState.READY`, then
returns the ready instance. If it does not become ready within `max_wait` seconds it
raises `TimeoutError` (and stops the croft on any exception during startup).

```python
croft = get_minicroft(["skill-weather.openvoiceos", "skill-timer.openvoiceos"])

# croft.status.state == ProcessState.READY

```
---

## Injecting Skills Under Test
To test a skill class that isn't installed as a plugin, inject it directly via `extra_skills`:

```python
from my_skill import MySkill
croft = get_minicroft(
    skill_ids=[],
    extra_skills={"my-skill.test": MySkill},
)

```
The skill ID key must match what the skill would normally register under.
---

## Multilingual Testing
By default, Adapt and Padatious only register vocab/intents for the system's configured default language. To test skills in other languages, pass `secondary_langs`:

```python
croft = get_minicroft(
    ["my-skill.openvoiceos"],
    secondary_langs=["pt-PT", "de-DE", "es-ES"],
)

```
This patches `Configuration()["secondary_langs"]` before `IntentService` initializes, so Adapt creates per-language engines and registers vocab from all locale directories.
To also change the primary language:

```python
croft = get_minicroft(
    ["my-skill.openvoiceos"],
    lang="pt-PT",
    secondary_langs=["en-US", "de-DE"],
)

```
---

## Pipeline Plugin Config Overrides
Use `pipeline_config` to override per-plugin configuration under `Configuration()["intents"]` before pipeline plugins initialize. This ensures tests are reproducible regardless of the user's local `mycroft.conf`.

The key must match the plugin's config key (the key it reads under `Configuration()["intents"]`):

```python

# Force M2V to use the multilingual model regardless of mycroft.conf
croft = get_minicroft(
    ["my-skill.openvoiceos"],
    default_pipeline=M2V_PIPELINE,
    pipeline_config={
        "ovos_m2v_pipeline": {
            "model": "Jarbas/ovos-model2vec-intents-distiluse-base-multilingual-cased-v2",
        }
    },
)

```

All overrides are restored to their original values in `MiniCroft.stop()`.

---

## Boot Sequence
On startup, MiniCroft captures all messages emitted during skill loading into `boot_messages`. These can be asserted in `End2EndTest.expected_boot_sequence`. The typical boot sequence includes:

1. `mycroft.skills.train` — intent pipeline training request


2. `mycroft.skills.initialized` — skills initialized


3. `mycroft.skills.ready` — skills service ready


4. `mycroft.ready` — all core services ready
Skills that participate in `converse` or `fallback` registration also emit messages during boot (e.g. `ovos.skills.fallback.register`).

---

*Source code: [OpenVoiceOS/ovoscope](https://github.com/OpenVoiceOS/ovoscope).*

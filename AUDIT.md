# ovos-technical-manual — Audit Report

## Documentation status

Every nav page validated against the real source code of the repo it documents
(`origin/dev`) and, where applicable, the formal specifications in
`OpenVoiceOS/architecture` (OVOS-MSG-1, SESSION-1/2, INTENT-1–4, PIPELINE-1,
STOP-1, AUDIO-IN-1, GUI-1). Content describing unreleased work is marked
**Upcoming** and linked to the open PR rather than presented as shipped.

## Source bugs found during the audit (candidates for upstream issues)

These are defects in the **documented repos** (not in the manual), surfaced while
reading source. None filed yet.

| Repo | Bug | Status |
|---|---|---|
| ovos-number-parser | `__init__.py:332` — `is_fractional` `nl` branch returns `is_fractional_pl` (Polish) instead of `is_fractional_nl` (copy-paste) | |
| ovos-bus-client | `update_scheduled_event` is a silent no-op: `apis/events.py` emits `mycroft.schedule.update_event` but the scheduler listens on `mycroft.scheduler.update_event` | |
| ovoscope | `cli.py cmd_record` (non-`--live`) passes `pipeline=` into `SkillManager` (no such kwarg) and a `MiniCroft` where `from_message` expects `skill_ids` → `TypeError` | |
| ovos-MoS | `AbstractDuopolyMoS.__init__` reads `self.founders` before assignment; `ReRankerDuopolyMoS.discuss_answers` calls `select_answer` without the required `options` arg | |
| ovos-PHAL | `AdminPHAL.load_plugins` calls `validator.validate()` unguarded (vs `PHAL`'s try/except) — a raising validator crashes admin loading instead of skipping the plugin | |
| ovos-gguf-plugin | `GGUFDialogTransformer.__init__` defaults `name="ovos-dialog-transformer-openai-plugin"` (copy-pasted from the OpenAI plugin) | |
| ovos-legacy-mycroft-gui-plugin | class name misspelled `LegacyMycoftGuiPlugin` (entry-point depends on it; needs a deliberate breaking rename) | |
| ovos-workshop | `ovos.py` `default_shutdown()` (~line 1203) docstring claims step 5 calls `self.shutdown()`, but the method body never calls it — it goes straight from event-scheduler cleanup to emitting `detach_skill` | draft PR opened |
| ovos-core | `skill_manager.py` (~535–545) `_unload_on_internet_disconnect` / `_unload_on_network_disconnect` / `_unload_on_gui_disconnect` are `# TODO - implementation missing` stubs, even though the `RuntimeRequirements` docs promise skills get unloaded on disconnect | draft PR opened |
| ovos-persona-server | The Anthropic/Gemini/Cohere/AWS Bedrock/HuggingFace TGI vendor routers and `deprecated_routers` module are implemented and unit-tested but never mounted in `create_persona_app()`; only `chat_router`/`ollama_router`/`utcp_router` are included. The deprecated-router comment claims `chat_router` has prefix `/openai/v1`, but `chat.py` actually defines it as `/v1`. There is no `--a2a-base-url` CLI flag and no `a2a` installable extra | draft PR opened |
| ovos-shell | `ListenerAnimation.qml` listens for the legacy `recognizer_loop:record_end` bus message to hide the listening animation, but per AUDIO-IN-1 the spec name `ovos.listener.record.ended` is what current listeners actually emit and what `ovos-gui` forwards to GUI clients — the animation's stop condition can no longer fire | draft PR opened |
| ovos-plugin-manager | `PluginTypes.GUI = "opm.gui"` is the only GUI member in the enum, but the package's own `docs/plugin-types.md` also documents a `GUI_ADAPTER = "opm.gui_adapter"` value, and `ovos-legacy-mycroft-gui-plugin`'s entry point registers under `opm.gui_adapter` — a namespace the enum doesn't define | draft PR opened |
| ovos-color-parser | `models.py` (~line 323) `as_spectral_color`/`_hue_to_wavelength` raises `ValueError("Hue is out of the defined spectral color palette.")` for hues that fall in a gap between defined hue-bands (e.g. orange, ~39°) | draft PR opened |
| ovos-date-parser | `extract_duration` leaves a dangling "and" in the remainder text once the duration phrase is consumed, e.g. `"remind me in 1 hour and turn off the lights"` → remainder `"remind me in and turn off the lights"` | draft PR opened |

## Documentation toolchain

- Fixed: the GitHub Pages deploy was failing because `pygments` was unpinned;
  `pymdown-extensions==10.11.2` crashes on `pygments>=2.19`. Pinned `pygments==2.18.0`
  in `build.yml`.

Full page→source validation map: `~/wiki/pages/projects/ovos-technical-manual.md`.

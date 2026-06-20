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

| Repo | Bug |
|---|---|
| ovos-color-parser | `matching.py` strips the region subtag (`lang.split("-")[0]`) but `res/` ships full locale dirs (`en-US`…); only `it` has a bare dir, so every non-Italian lookup raises `FileNotFoundError` |
| ovos-number-parser | `__init__.py:332` — `is_fractional` `nl` branch returns `is_fractional_pl` (Polish) instead of `is_fractional_nl` (copy-paste) |
| ovos-bus-client | `update_scheduled_event` is a silent no-op: `apis/events.py` emits `mycroft.schedule.update_event` but the scheduler listens on `mycroft.scheduler.update_event` |
| ovoscope | `cli.py cmd_record` (non-`--live`) passes `pipeline=` into `SkillManager` (no such kwarg) and a `MiniCroft` where `from_message` expects `skill_ids` → `TypeError` |
| ovos-MoS | `AbstractDuopolyMoS.__init__` reads `self.founders` before assignment; `ReRankerDuopolyMoS.discuss_answers` calls `select_answer` without the required `options` arg |
| ovos-PHAL | `AdminPHAL.load_plugins` calls `validator.validate()` unguarded (vs `PHAL`'s try/except) — a raising validator crashes admin loading instead of skipping the plugin |
| ovos-gguf-plugin | `GGUFDialogTransformer.__init__` defaults `name="ovos-dialog-transformer-openai-plugin"` (copy-pasted from the OpenAI plugin) |
| ovos-workshop | `set_cross_skill_context` emits `mycroft.skill.set_cross_context` with no ovos-core consumer on dev (dead path) |
| ovos-legacy-mycroft-gui-plugin | class name misspelled `LegacyMycoftGuiPlugin` (entry-point depends on it; needs a deliberate breaking rename) |

## Documentation toolchain

- Fixed: the GitHub Pages deploy was failing because `pygments` was unpinned;
  `pymdown-extensions==10.11.2` crashes on `pygments>=2.19`. Pinned `pygments==2.18.0`
  in `build.yml`.

Full page→source validation map: `~/wiki/pages/projects/ovos-technical-manual.md`.

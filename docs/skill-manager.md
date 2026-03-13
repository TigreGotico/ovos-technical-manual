# Skill Manager

**Module:** `ovos_core.skill_manager.SkillManager` — [`ovos_core/skill_manager.py`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/skill_manager.py)

The `SkillManager` is a core component of `ovos-core`. It is a daemon `Thread` that owns the full lifecycle of skill plugins: discovery, loading, connectivity-gating, and graceful shutdown.

---

??? abstract "Technical Reference"

    - `SkillManager.run()` — [`ovos_core/skill_manager.py:204`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/skill_manager.py) — Main loop handling skill loading and periodic scans.


    - `SkillManager.load_plugin()` — [`ovos_core/skill_manager.py:301`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/skill_manager.py) — logic for loading a specific skill via `PluginSkillLoader`.


    - `SkillManager._check_connectivity()` — [`ovos_core/skill_manager.py:450`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/skill_manager.py) — connectivity gating based on `RuntimeRequirements`.
    

## Skill Discovery

Skills are Python packages that register themselves via the `opm.skills` entry point group. `ovos-plugin-manager` discovers them with `find_skill_plugins()`, which returns a `{skill_id: SkillClass}` dict.

```python
from ovos_plugin_manager.skills import find_skill_plugins
plugins = find_skill_plugins()

```

## Connectivity Gating

Skills declare their runtime requirements (`network_before_load`, `internet_before_load`, `requires_gui`) in `RuntimeRequirements`. The skill manager only loads a skill when those requirements are met:

| Event | Action |
|---|---|
| Startup (offline) | Load skills with no network/internet requirement |
| `mycroft.network.connected` | Load skills requiring network |
| `mycroft.internet.connected` | Load skills requiring internet |
| `mycroft.gui.available` | Load skills requiring GUI |

Network/internet state is queried from [PHAL](ovoscope-phal.md) at startup via `ovos.PHAL.internet_check`; falls back to a direct HTTP check if PHAL is unavailable.

## Loading a Skill

The loading process follows this flow:

```
find_skill_plugins()
  → _get_plugin_skill_loader(skill_id, skill_class)
    → PluginSkillLoader.load(skill_class)
      → mycroft.skill.loaded (bus event)

```

Each skill gets its own bus connection when `websocket.shared_connection` is `false` in config (providing isolation from "BusBricker" style attacks).

## Blacklisting

Skills listed in `skills.blacklisted_skills` in `mycroft.conf` are skipped at load time. The recommended approach is to uninstall unwanted skills rather than blacklist them.

## Intent Training

After new skills are loaded, the manager requests pipeline re-training:

```
mycroft.skills.train  →  (pipeline plugins train)  →  mycroft.skills.trained

```

Training has a 60-second timeout. On failure, an error is logged but the manager continues.

## Settings File Watcher

When enabled, a `FileWatcher` monitors `~/.config/ovos/skills/*/settings.json`. Any change emits:

```
ovos.skills.settings_changed  {skill_id: "..."}

```

## Bus Events Handled

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

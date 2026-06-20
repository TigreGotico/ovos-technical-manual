# Skill Manager

**Module:** `ovos_core.skill_manager.SkillManager` — [`ovos_core/skill_manager.py`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/skill_manager.py)

The `SkillManager` is a core component of `ovos-core`. It is a daemon `Thread` that owns the full lifecycle of skill plugins: discovery, loading, connectivity-gating, and graceful shutdown.

**In plain terms:** when OVOS starts, the SkillManager finds every installed skill, decides which ones are allowed to load right now (some need the network or a screen first), starts them, and re-scans periodically so newly installed skills show up without a restart.

---

??? abstract "Technical Reference"

    - `SkillManager.run()` — [`ovos_core/skill_manager.py:476`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/skill_manager.py) — Main loop; re-scans for new skills every 30 s via `self._stop_event.wait(30)`.


    - `SkillManager.load_plugin_skills()` — [`ovos_core/skill_manager.py:347`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/skill_manager.py) — loads discovered skills via `PluginSkillLoader` (from `ovos_workshop.skill_launcher`).


    - `SkillManager._sync_skill_loading_state()` — [`ovos_core/skill_manager.py:181`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/skill_manager.py) — connectivity gating based on `RuntimeRequirements`.
    

## Skill Discovery

Skills are Python packages that register themselves via the `opm.skill` entry point group (the older `ovos.plugin.skill` group is still accepted as a deprecated alias). `ovos-plugin-manager` discovers them with `find_skill_plugins()`, which returns a `{skill_id: SkillClass}` dict.

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

Network/internet state is queried from [PHAL](phal.md) at startup via `ovos.PHAL.internet_check`; falls back to a direct HTTP check if PHAL is unavailable.

## Loading a Skill

The loading process follows this flow:

```
load_plugin_skills()
  → find_skill_plugins()                              # {skill_id: SkillClass}
    → _get_plugin_skill_loader(skill_id, skill_class) # build a PluginSkillLoader
      → _load_plugin_skill(skill_id, skill_class)     # instantiate & start the skill

```

Each skill gets its own bus connection when `websocket.shared_connection` is `false` in config (see `_get_internal_skill_bus()`), providing isolation from "BusBricker" style attacks.

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

# Skill Installer (SkillsStore)

**Module:** `ovos_core.skill_installer.SkillsStore` — [`ovos_core/skill_installer.py`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/skill_installer.py)

The `SkillsStore` is a built-in subsystem of `ovos-core` that provides runtime skill and package management via the [MessageBus](bus-service.md).

---

??? abstract "Technical Reference"

    - `SkillsStore.install_package()` — [`ovos_core/skill_installer.py:315`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/skill_installer.py) — Core logic for calling `pip` or `uv`.


    - `SkillsStore.handle_install()` — [`ovos_core/skill_installer.py:120`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/skill_installer.py) — Bus event handler for `ovos.skills.install`.


    - `ovos_plugin_manager.utils.plugin_utils.reload_plugins()` — [`ovos_plugin_manager/utils/plugin_utils.py`](https://github.com/OpenVoiceOS/ovos-plugin-manager/blob/dev/ovos_plugin_manager/utils/plugin_utils.py) — entry point cache invalidation after install.
    
    ---
    

## Overview

The skill installer allows for dynamic installation and uninstallation of skills and other Python packages. It uses `uv pip` if `uv` is available on the system's `$PATH`; otherwise, it falls back to standard `pip`.

To prevent issues with concurrent package management, a named lock (`ovos_pip.lock`) is used during all install and uninstall operations.

## Configuration

The installer can be configured in `mycroft.conf`:

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

## Install/Uninstall Events

You can trigger installation and uninstallation by emitting messages on the MessageBus:

### Installation

```
ovos.skills.install        data: {"packages": ["ovos-skill-foo"]}
  → ovos.skills.install.complete  (success)
  → ovos.skills.install.failed    (error)

```

### Uninstallation

```
ovos.skills.uninstall      data: {"packages": ["ovos-skill-foo"]}
  → ovos.skills.uninstall.complete
  → ovos.skills.uninstall.failed

```

### General pip management

```
ovos.pip.install           data: {"packages": ["some-lib>=1.0"]}
ovos.pip.uninstall         data: {"packages": ["some-lib"]}

```

## Post-Install Discovery

After a successful skill installation, `ovos-plugin-manager`'s entry point cache is reloaded. This ensures the new skill is discovered on the next `SkillManager` scan cycle (which occurs every 30 seconds by default).

## InstallError Types

If an installation fails, an error message is emitted. Possible errors include:

| Error Code | Meaning |
|---|---|
| `DISABLED` | The installer is disabled in the configuration. |
| `PIP_ERROR` | The underlying pip/uv process returned a non-zero exit code. |
| `BAD_URL` | A provided URL failed validation. |
| `NO_PKGS` | The package list was empty. |

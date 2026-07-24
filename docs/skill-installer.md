# Skill Installer (SkillsStore)

!!! abstract "In a nutshell"
    This is the built-in part of OVOS that can add or remove [skills](skill-examples.md) (and other software packages) while the assistant is running — no need to open a terminal or restart anything. Think of it as an app-store back end: something asks "install this skill," and OVOS downloads and wires it in on the fly. It is switched off unless explicitly enabled, for safety. See [Skill Manager](skill-manager.md) for how skills then get loaded, or the [Glossary](glossary.md) for terms.

**Module:** `ovos_core.skill_installer.SkillsStore` — [`ovos_core/skill_installer.py`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/skill_installer.py)

The `SkillsStore` is a built-in subsystem of `ovos-core` that provides runtime skill and package management via the [messagebus](bus-service.md).

**In plain terms:** other parts of the system (or you, over the bus) can ask OVOS to `pip install` a skill or library while it is running — no shell access or restart needed. It is opt-in and guarded behind the `allow_pip` config flag.

---

??? abstract "Technical Reference"

    - `SkillsStore.pip_install()` — [`ovos_core/skill_installer.py:85`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/skill_installer.py) — Core logic for calling `pip` or `uv`.


    - `SkillsStore.handle_install_skill()` — [`ovos_core/skill_installer.py:288`](https://github.com/OpenVoiceOS/ovos-core/blob/dev/ovos_core/skill_installer.py) — Bus event handler for `ovos.skills.install`.


    - After a successful install, `ovos_core/skill_installer.py` re-imports `ovos_plugin_manager` (Python's `importlib.reload`) so the new entry points are picked up.
    
    ---
    

## Overview

The skill installer allows for dynamic installation and uninstallation of skills and other Python packages. It uses `uv pip` if `uv` is available on the system's `$PATH`; otherwise, it falls back to standard `pip`.

To prevent issues with concurrent package management, a named lock (`ovos_pip.lock`) is used during all install and uninstall operations.

## Configuration

The installer can be configured in `mycroft.conf`. It is **disabled unless `allow_pip` is `true`** — every install/uninstall handler bails out with a `DISABLED` error otherwise:

```json
{
  "skills": {
    "installer": {
      "allow_pip": true,
      "constraints": "https://raw.githubusercontent.com/OpenVoiceOS/ovos-releases/refs/heads/main/constraints-stable.txt",
      "sounds": {
        "pip_error": "snd/error.mp3",
        "pip_success": "snd/acknowledge.mp3"
      }
    }
  }
}

```

The `constraints` file bounds allowed versions — its entries are compatible **ranges**
(`>=x,<y`), not exact pins, so it constrains what may be installed rather than fixing it. The
packages it lists are also treated as **protected**: `ovos.pip.uninstall` refuses to remove a
package named there.

!!! note "Uninstall protection is an accident guard, not a security control"
    The protected list stops a request from removing OVOS's own components by name. It is not a
    privilege boundary — anything that can reach the [messagebus](bus-service.md) already has
    full control of the device, and `allow_pip: true` gives it package-management rights.
    Security comes from keeping the bus local and `allow_pip` off, not from this list.

!!! danger "Skills are not sandboxed — this installs and runs arbitrary code"
    There is no sandbox or permission model. Installing a skill through
    `SkillsStore` means `pip`/`uv install`ing a Python package and loading it —
    it runs with the same access as the rest of OVOS on the OVOS user account.
    Combined with the fact that the [messagebus](bus-service.md) has **no
    authentication**, turning `allow_pip` on while the bus is reachable by
    anyone untrusted is effectively a remote-code-execution switch: anyone who
    can reach the bus can request an install of code they control. See
    [Privacy & Security](privacy-security.md#skills-are-not-sandboxed) for the
    full picture before enabling this in production.

## Install/Uninstall Events

You can trigger installation and uninstallation by emitting messages on the messagebus. Note that the **skill** events and the **pip** events take different payloads: skills are installed from a single GitHub URL, while the generic pip events take a list of package specifiers.

### Skill installation

A skill is installed from a GitHub repo URL (it is validated and then installed as `git+<url>`):

```text
ovos.skills.install        data: {"url": "https://github.com/OpenVoiceOS/skill-foo"}
  → ovos.skills.install.complete  (success)
  → ovos.skills.install.failed    (error)

```

### Skill uninstallation

Uninstall by `skill_id` (or package name); a `skill_id` like `skill-foo.author` is mapped to the package name `skill-foo-author`:

```text
ovos.skills.uninstall      data: {"skill": "skill-foo.author"}
  → ovos.skills.uninstall.complete
  → ovos.skills.uninstall.failed

```

### General pip management

```text
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

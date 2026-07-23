# OVOS Release Channels & Installation Options

!!! abstract "In a nutshell"
    OVOS is built from many small swappable pieces, and this page explains the different ways to install them and how to pick how cutting-edge (or how rock-stable) your version is — a "release channel" is like choosing between a tested, stable edition or an early-preview edition with the newest features but more rough edges. Most people should ignore the details and just use the guided [`ovos-installer`](ovos-installer.md); the manual steps here are for tinkerers who want precise control (see the [Glossary](glossary.md) for terms).

!!! tip "Just want it working? Use the installer."
    Most people should install OVOS with the **[`ovos-installer`](ovos-installer.md)** — a guided
    wizard that handles everything. The manual `pip` commands and version-pinning below are for
    people who want fine-grained control (custom/headless setups). A few terms used on this page:
    **extras** = optional add-on bundles you list in brackets, e.g. `ovos-core[mycroft]`;
    **constraints file** = a version "filter" that pins which package versions get installed;
    **headless** = a device with no monitor/keyboard (e.g. a Raspberry Pi you SSH into).

Open Voice OS (OVOS) is a **modular voice assistant platform** that lets you install only the components you need. Whether you're building a lightweight voice interface or a full-featured smart assistant, OVOS gives you flexibility through modular packages and optional feature sets called **extras**.

---

## Installation Methods

Depending on your experience level and goals, you can choose one of the following methods:

### 1. [The `ovos-installer`](ovos-installer.md) (Recommended)
The easiest way for most users. A guided TUI (Text User Interface) script that handles dependencies, environment setup, and service configuration for you.

### 2. [RaspOVOS](install-raspovos.md) — turnkey Raspberry Pi image
The flagship, actively maintained pre-built image for the Raspberry Pi. Flash it and
boot straight into a working assistant — no manual install steps required.

### 3. Manual Installation (Advanced)
Install individual components via `pip` or `uv`. Best for developers or custom integration (e.g., headless nodes, Docker containers).

---

## Choosing a Release Channel

OVOS follows [**semantic versioning**](https://semver.org/) (SemVer) with a **rolling release model** and supports three release channels — **stable**, **testing**, and **alpha** — so you can pick the right balance between cutting-edge features and system reliability.

These channels are managed via the [constraints files](https://pip.pypa.io/en/stable/user_guide/#constraints-files) hosted in the [ovos-releases](https://github.com/OpenVoiceOS/ovos-releases) repository. **If unsure, choose Testing** — it gets bug fixes and new features without the instability of Alpha.

### 1. Stable Channel (Production-Ready)

- ✅ Bug fixes only
- 🚫 No new features or breaking changes
- ✅ Recommended for production or everyday use

```bash
uv pip install ovos-core[mycroft] -c https://raw.githubusercontent.com/OpenVoiceOS/ovos-releases/refs/heads/main/constraints-stable.txt

```

### 2. Testing Channel (Feature Updates)

- ✅ Bug fixes and new features
- ⚠️ Not as thoroughly tested as stable
- 🧪 Best for early adopters or development environments

```bash
uv pip install ovos-core[mycroft] -c https://raw.githubusercontent.com/OpenVoiceOS/ovos-releases/refs/heads/main/constraints-testing.txt

```

### 3. Alpha Channel (Bleeding Edge)

- 🔬 Experimental features
- ⚠️ May include breaking changes
- 🧪 Not suitable for production use

!!! warning "`--pre` is not scoped to OVOS"
    `--pre` tells `pip`/`uv` to allow pre-release versions of **every** dependency it
    resolves, not just the `ovos-*` packages — a transitive dependency you didn't expect
    can also jump to a pre-release. Use a dedicated virtual environment for alpha testing.

```bash
uv pip install ovos-core[mycroft] --pre -c https://raw.githubusercontent.com/OpenVoiceOS/ovos-releases/refs/heads/main/constraints-alpha.txt

```

---

!!! example "A minimal lab-ready manual install, start to finish"
    Everything below assumes a Python virtual environment is already active and gets you from
    nothing to a talking assistant on one machine, no installer wizard involved:

    ```bash
    # 1. Install the core services on the stable channel
    uv pip install "ovos-core[mycroft]" \
        -c https://raw.githubusercontent.com/OpenVoiceOS/ovos-releases/refs/heads/main/constraints-stable.txt

    # 2. Launch each service (one terminal/tmux pane each, or use the systemd units
    #    in Production Operations for anything long-lived)
    ovos-messagebus &
    ovos_PHAL &
    ovos-dinkum-listener &
    ovos-audio &
    ovos-core &

    # 3. Confirm the bus is up and services are talking to each other
    ovos-busmon
    ```

    Say "Hey Mycroft, what time is it" once everything above has settled — if you get a spoken
    answer, the install is working end to end. See
    [Production Operations](production-operations.md#keep-services-running-systemd-units) to
    turn these into supervised systemd services instead of foreground processes.

---

## OVOS From Scratch: Custom Installation

Rather than using a full distro, you can manually pick which components to install:

- [`ovos-messagebus`](https://github.com/OpenVoiceOS/ovos-messagebus) – internal messaging between services
- [`ovos-core`](https://github.com/OpenVoiceOS/ovos-core) – skill handling
- [`ovos-audio`](https://github.com/OpenVoiceOS/ovos-audio) – text-to-speech ([TTS](tts-plugins.md)), audio playback
- [`ovos-dinkum-listener`](https://github.com/OpenVoiceOS/ovos-dinkum-listener) – wake word, voice activation
- [`ovos-gui`](https://github.com/OpenVoiceOS/ovos-gui) – GUI integration (⚠️ the legacy [GUI](gui-service.md) is deprecated and not usable right now; a replacement is in progress — you can omit this on most setups)
- [`ovos-PHAL`](https://github.com/OpenVoiceOS/ovos-PHAL) – hardware abstraction layer

Media playback (music, podcasts, video) is a separate concern from the components above —
by default it's handled by a bundled backend inside `ovos-audio`
(`enable_old_audioservice: true`); see [ovos-media](ovos-media.md) for the upcoming
standalone player and how to opt into it.

This is useful if you're building something like a **Hivemind node** or **headless device**, where you might not need audio output or a GUI.

---

## What Are OVOS Extras?

OVOS uses Python extras (e.g., `[mycroft]`) to let you install predefined groups of components based on your use case.

| Extra Name           | Purpose                                                                 |
|----------------------|-------------------------------------------------------------------------|
| `mycroft`            | Core services for full voice assistant experience                      |
| `lgpl`               | Adds optional LGPL-licensed tools like [Padatious](padatious-pipeline.md)                       |
| `plugins`            | Includes various plugin interfaces                                     |
| `skills-essential`   | Must-have skills (like system control, clock, weather)                 |
| `skills-audio`       | Audio I/O-based skills                                                  |
| `skills-gui`         | GUI-dependent skills                                                    |
| `skills-internet`    | Skills that require an internet connection                             |
| `skills-media`       | [OCP](ocp-pipeline.md) (OpenVoiceOS [Common Play](ocp-pipeline.md)) media playback skills                    |
| `skills-desktop`     | Desktop environment integrations                                       |

### Full Installation Example

```bash
pip install ovos-core[mycroft,lgpl,plugins,skills-essential,skills-audio,skills-gui,skills-internet,skills-media,skills-desktop]

```

### Minimal Installation Example

```bash
pip install ovos-core[mycroft,plugins,skills-essential]

```


---

## Technical Notes

- OVOS is **fully modularized**, with each major service in its own repository, so you install only what you need.
- All packages follow [Semantic Versioning (SemVer)](https://semver.org/), so you can rely on versioning to understand stability and compatibility.
- Constraints files are a **stable standard** for pinning system versions since the [ovos-releases 1.0.0](https://github.com/OpenVoiceOS/ovos-releases) milestone.

---

## Rolling Back

Constraints files pin a channel's versions, but they don't remember what *you* had installed
before an upgrade. Before upgrading anything you care about, freeze what's currently working:

```bash
uv pip freeze > known-good.txt
```

If an upgrade misbehaves, `pip`/`uv` won't downgrade a package on their own just because a
newer constraints file changed — an ordinary `install` call treats an already-satisfied
requirement as nothing to do. Force the reinstall of the exact frozen versions instead:

```bash
uv pip install --force-reinstall -r known-good.txt
```

See [Production Operations: staged upgrades and rollback](production-operations.md#staged-upgrades-and-rollback)
for the same pattern applied across a fleet of devices rather than one machine.

---

## ⚠️ Tips & Caveats

- Using `--pre` installs pre-releases across all dependencies, not just OVOS-specific ones — so use with caution.
- You can mix and match extras based on your hardware or use case, e.g., omit GUI skills on a headless server.
- When using constraints files, make sure all packages are pinned — it avoids installing incompatible versions.
- After installing you need to launch the individual ovos services, either manually or by creating a systemd service

---

## See Also

- [OVOS Releases repo](https://github.com/OpenVoiceOS/ovos-releases)
- [Constraints files explanation (pip docs)](https://pip.pypa.io/en/stable/user_guide/#constraints-files)
- [Semantic Versioning](https://semver.org/)
- [OVOS Component Repos](https://github.com/OpenVoiceOS)


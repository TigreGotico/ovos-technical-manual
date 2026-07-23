# How to Install Open Voice OS with the `ovos-installer`

!!! abstract "In a nutshell"
    This is the friendly, guided way to get OVOS onto your machine. You run a single command, then a menu-driven wizard walks you through a few choices (your language, where to install, which features you want) and does the rest for you. It works the same on a Raspberry Pi or an everyday Linux laptop, and is the recommended way to install — no programming required. Scripting a fleet instead? See the [non-interactive scenario install](#non-interactive-scenario-install), which skips the wizard entirely. See the [Glossary](glossary.md) for unfamiliar terms.

!!! tip "Privacy first?"
    See [Privacy & Security](privacy-security.md) for what a default install
    actually sends over the network, and how to change it, before you start.

Welcome to the quick-start guide for installing Open Voice OS (OVOS) using the official `ovos-installer`! This guide is suitable for **Raspberry Pi** and **desktop/server** Linux environments. Whether you're running this on a headless Raspberry Pi or your everyday laptop, the steps are mostly the same — only the way you connect to the device differs.

> ⚠️ Note: Some "exotic" hardware (like ReSpeaker microphones or certain audio HATs) may require extra configuration. The installer aims for wide compatibility, but specialized setups might need some manual intervention.

> 💡 The installer is the recommended path on the Raspberry Pi too. The older pre-built
> [RaspOVOS](install-raspovos.md) images are outdated and **not currently recommended** —
> run the `ovos-installer` on Raspberry Pi OS instead.

---

## Step-by-step Installation

### ✅ 1. Connect to Your Device *(if remote)*

If you're installing on a headless device (like a Raspberry Pi), connect via SSH:

```bash
ssh -l your-username <your-device-ip>

```

---

### 🔄 2. Update Package Metadata

Make sure your package manager is up to date:

```bash
sudo apt update

```

---

### 📦 3. Install Prerequisites

Install `git` and `curl`—these are required to run the installer:

```bash
sudo apt install -y git curl

```

---

### 📥 4. Run the OVOS Installer

Now you're ready to kick off the installation process:

```bash
sudo sh -c "$(curl -fsSL https://raw.githubusercontent.com/OpenVoiceOS/ovos-installer/main/installer.sh)"

```

![image](https://gist.github.com/user-attachments/assets/8a87fd01-2570-419b-8154-159b2d5801cb)


---

## What Happens Next?

Once you run the script, the installer will:

- Perform system checks


- Install dependencies (Python, Ansible, etc.)


- Launch a **text-based user interface (TUI)** to guide you through the setup

This can take anywhere from **5 to 20 minutes**, depending on your hardware, internet speed, and storage performance. Now let's walk through the installer screens!

---

## The Installer Wizard

!!! tip "Scripting this instead?"
    Everything below can be answered up front in a
    [scenario file](#non-interactive-scenario-install), so the installer runs
    with no prompts at all — useful for fleets or CI.

Navigation:

- navigation is done via arrow keys


- pressing space selects options in the lists


    - eg. when selecting `virtualenv` or `containers`


- pressing tab will switch between the options and the `<next>`/`<back>` buttons


- pressing enter will execute the highligted `<next>`/`<back>` option

---

### 🌍 Language Selection

The first screen lets you select your preferred language for the installer's own text (not the assistant's spoken language, which is chosen later). Follow the on-screen instructions; use arrow keys and space to pick.

![image](https://gist.github.com/user-attachments/assets/61f9e089-1d54-49e9-8d4a-d5e1f6028ee2)

---

### 🧠 Environment Summary

An informational screen — no action needed. It reports what the installer auto-detected about the machine, including:

`OS`
:   distribution name and version (e.g. Debian, Ubuntu, macOS)

`Kernel`
:   kernel version string

`Raspberry Pi model`
:   detected board, or `N/A` on non-Pi hardware

`Python`
:   detected Python interpreter version

`CPU capability`
:   whether the CPU supports AVX2/SIMD (affects which speech plugins are offered)

`Sound server`
:   PulseAudio or PipeWire, if detected

`Display server`
:   X11, Wayland, or `EGLFS` (used on Mark II/DevKit), if any

If the board looks like a Mycroft Mark II or DevKit (Raspberry Pi 4 plus the
matching audio/I²C hardware), a confirmation prompt asks you to verify that —
some generic HATs expose the same signal without being real Mark II hardware.

![image](https://gist.github.com/user-attachments/assets/1268a703-2007-4bc0-b153-36f33b782b20)

---

### 🧰 Choose Installation Method

A radio-button list with up to two options:

`virtualenv`
:   Python virtual environment. Recommended for most users; supported everywhere, including macOS.

`containers`
:   Docker (or Podman) containers. Installed automatically if Docker is missing. **Not offered** on macOS, on 32-bit CPUs, on Raspberry Pi 3, or on Mark II/DevKit hardware — those are locked to `virtualenv`.

If you're re-running the installer on an existing install, only the method
already in use is offered (you can't switch method in place).

![image](https://gist.github.com/user-attachments/assets/e1b881fc-327d-4e1f-839b-396cffcd354c)

---

### 🌱 Choose Channel

`testing`
:   Recommended for most users; the stable release channel.

`alpha`
:   Bleeding-edge/pre-release packages. **Required** (and the only option offered) on macOS and on Mark II/DevKit hardware.

![image](https://gist.github.com/user-attachments/assets/f782cebe-c86b-4474-93d7-894b712e8fe7)

---

### 🧪 Choose Profile

A radio-button list of installation profiles:

`ovos`
:   The classic, all-in-one experience — voice pipeline, skills, and (optionally) GUI all running locally. The default and the profile the rest of this page assumes.

`satellite`
:   A microphone/speaker endpoint that talks to a separate OVOS core over the network — see [composable deployments](composable-deployments.md). Skips the feature-selection screen (no local skills/GUI/LLM/Home Assistant to configure).

`listener`
:   Runs only the listening/wake-word side of OVOS.

`server`
:   A headless core with no local audio hardware assumptions, meant to serve satellites — also skips GUI/LLM/Home Assistant options.

![image](https://gist.github.com/user-attachments/assets/0ff4279d-69fa-4ab8-b372-0fef263e6d7c)

---

### 🛠️ Feature Selection

A checklist (only shown for the `ovos`/`listener`/`server` profiles, not `satellite`):

`skills`
:   Install the default OVOS skills. **On** by default.

`extra-skills`
:   Install additional community skills beyond the default set. Off by default.

`gui`
:   Enable the OVOS GUI. Only offered on Mark II/DevKit hardware running Debian Trixie (or newer); on those devices it defaults **on**. Not offered on the `server`/`satellite` profiles.

`homeassistant`
:   Enable Home Assistant integration; prompts for a URL and access token. Only offered for the `ovos`/`listener` profiles with the `virtualenv` or `containers` method.

`llm`
:   Enable an LLM-backed fallback answer via the OVOS Persona pipeline; prompts for an OpenAI-compatible API URL, key, model, and persona name. Same availability rule as `homeassistant`.

![image](https://gist.github.com/user-attachments/assets/bdb65ba6-18d6-42fd-aff6-22fab0826870)

> ⚠️ Note: Some features (like the GUI) may be unavailable on lower-end hardware like the Raspberry Pi 3B+.

---

### 🍓 Raspberry Pi Tuning *(if applicable)*

On Raspberry Pi boards only, a yes/no prompt offers system performance tweaks
(including an overclock option on supported boards). It's highly recommended
to enable this on a Pi.

![image](https://gist.github.com/user-attachments/assets/91bb5f18-9c5a-49ef-a0fe-5b0e52b44ee9)

---

### 🧾 Summary

Before the installation begins, you'll see a summary of every option you
selected on the previous screens (method, channel, profile, features, tuning).
This is your last chance to cancel the process.

![image](https://gist.github.com/user-attachments/assets/62a565f3-6871-4dfe-a441-c482199feac0)

---

### 📊 Anonymous Telemetry

There are actually **two separate opt-in prompts** here, and they are easy to
mix up — see [Privacy & Security](privacy-security.md#install-time-telemetry-vs-ongoing-usage-telemetry)
for the full explanation. In short: the first ("Telemetry") is a one-time
install report; the second ("Usage Metrics") configures the *installed
assistant* to keep reporting intent-matching data afterwards, so it is not
purely a "during setup only" choice.

![image](https://gist.github.com/user-attachments/assets/b8015c41-370d-49d3-b783-996887cb421b)

#### Install-time telemetry (`share_telemetry`)

This report is generated and sent **once**, right after installation
completes — nothing else about this specific report is collected afterwards.
Below is the field list _(see the [Ansible template](https://github.com/OpenVoiceOS/ovos-installer/blob/main/ansible/roles/ovos_installer/templates/telemetry.json.j2) used to build it)_.

| Data                   | Description                                              |
| ---------------------- | -------------------------------------------------------- |
| `architecture`         | CPU architecture where OVOS was installed                |
| `channel`              | `testing` or `alpha` channel of OVOS                     |
| `container`            | OVOS installed into containers                           |
| `country`              | Country the machine appeared to be in, derived from a public-IP geolocation lookup (`ip-api.com`) performed by the installer — not something you type in |
| `cpu_capable`          | Is the CPU supports AVX2 or SIMD instructions            |
| `display_server`       | Is X or Wayland are used as display server               |
| `extra_skills_feature` | Extra OVOS's skills enabled during the installation      |
| `gui_feature`          | GUI enabled during the installation                      |
| `hardware`             | Is the device a Mark 1, Mark II or DevKit                |
| `installed_at`         | Date when OVOS has been installed                        |
| `os_kernel`            | Kernel version of the host where OVOS is running         |
| `os_name`              | OS name of the host where OVOS is running                |
| `os_type`              | OS type of the host where OVOS is running                |
| `os_version`           | OS version of the host where OVOS is running             |
| `profile`              | Which profile has been used during the OVOS installation |
| `python_version`       | What Python version was running on the host              |
| `raspberry_pi`         | Does OVOS has been installed on Raspberry Pi             |
| `skills_feature`       | Default OVOS's skills enabled during the installation    |
| `sound_server`         | What PulseAudio or PipeWire used                         |
| `tuning_enabled`       | Whether the Raspberry Pi tuning feature was used         |
| `venv`                 | OVOS installed into a Python virtual environment         |

#### Ongoing usage telemetry (`share_usage_telemetry`)

Accepting this prompt adds an `open_data.intent_urls` entry pointing at a
community metrics endpoint to your installed `mycroft.conf`. That makes the
**running assistant** report anonymous intent-matching data on an ongoing
basis — every time it processes a voice command, not just during setup. If
you want data collection to stop once installation is over, decline this
prompt (declining the first, install-time prompt is not enough on its own).

---

### 🧙‍♂️ Sit Back and Relax

The installation begins! This can take some time, so why not grab a coffee (or maybe a cupcake)? ☕🧁

Here is a demo of how the process should go if everything works as intended.
The recording shows a full run of the wizard on a fresh machine, from launching
`installer.sh` through the summary screen to the final "installation complete"
message.

[![asciicast](https://asciinema.org/a/710286.svg)](https://asciinema.org/a/710286)

---

## Installation Complete!

You've done it! OVOS is now installed and ready to serve you. Try saying things like:

- "What's the weather?"


- "Tell me a joke."


- "Set a timer for 5 minutes."

![image](https://gist.github.com/user-attachments/assets/acbc71ed-46aa-4084-8f4c-82c6a2a19d49)

You're officially part of the Open Voice OS community! 🎤✨

!!! tip "Say the wake word first"
    OVOS only starts listening after it hears its wake word (`hey mycroft` by
    default). Say **"Hey Mycroft"** and wait for the listening sound/prompt
    before speaking your request — a bare "What's the weather?" with no wake
    word first won't be heard. See [Wake Word plugins](wake-word-plugins.md)
    if you want to change it.

---

## Post-install tuning

The installer picks sensible defaults, but the best speech plugins vary by language and hardware. After the initial install, review the selected plugins and run `ovos-config autoconfigure --help` to see the language-aware reconfiguration options. Note that the default STT/TTS plugins talk to public community-run servers rather than running locally — see [Privacy & Security](privacy-security.md#network-surface-of-a-default-install) for exactly what that means and how to switch to an offline or self-hosted plugin.

The recording below shows this post-install tuning step in action.

[![asciicast](https://asciinema.org/a/710295.svg)](https://asciinema.org/a/710295)


---

## Non-interactive (scenario) install

For scripting or fleet deployment, the installer can run without the TUI by reading a
scenario file from `~/.config/ovos-installer/scenario.yaml`. Example (Docker
containers on a Raspberry Pi with default skills):

```yaml
---
uninstall: false
method: containers       # or "virtualenv"
channel: testing         # or "alpha"
profile: ovos
features:
  skills: true
  extra_skills: false
raspberry_pi_tuning: true
share_telemetry: false        # one-time install report — see Privacy & Security
share_usage_telemetry: false  # ongoing intent-matching reports — kept separate on purpose
```

Key options:

| Key | Meaning |
| --- | --- |
| `uninstall` | `true` to uninstall instead of install |
| `method` | `containers` (Docker) or `virtualenv` (Python virtual environment) |
| `channel` | Release channel: `testing` or `alpha` |
| `profile` | Installation profile (e.g. `ovos`) |
| `features.*` | Per-feature toggles (e.g. `skills`, `extra_skills`, `llm`) |
| `raspberry_pi_tuning` | Enable Raspberry Pi performance tuning (includes an overclock prompt) |
| `share_telemetry` | One-time install report, sent once when the install finishes ([details](#anonymous-telemetry)) |
| `share_usage_telemetry` | Configures the *installed, running* assistant to keep reporting intent-matching data afterwards — not a one-time report ([details](#anonymous-telemetry)) |

All of `uninstall`, `method`, `channel`, `profile`, `features`, `raspberry_pi_tuning`,
`share_telemetry`, and `share_usage_telemetry` are **required** — the installer
refuses an incomplete scenario file.

Ready-made example scenarios live in the
[`scenarios/`](https://github.com/OpenVoiceOS/ovos-installer/tree/main/scenarios)
directory of the repository.

> 💡 **LLM and Home Assistant features.** Setting `features.llm: true` enables the OVOS
> Persona LLM fallback and requires the `llm.api_url`, `llm.key`, `llm.model`, and
> `llm.persona` keys (an OpenAI-compatible endpoint). A Home Assistant feature is also
> available. **macOS** is supported with `launchd` service management, but only with the
> `virtualenv` method and the `alpha` channel.

---

## Troubleshooting

> Something went wrong?

Don't panic! If the installer fails, it will generate a log file and upload it to [https://dpaste.com](https://dpaste.com). Please share that link with the community so we can help you out.

OVOS is a community-driven project, maintained by passionate volunteers. Your feedback, bug reports, and patience are truly appreciated.

## Further reading

- [Boring installs, now on macOS (Intel + Apple Silicon)](https://blog.openvoiceos.org/posts/2026-03-05-ovos-installer-macos-intel-apple-silicon) — OVOS blog

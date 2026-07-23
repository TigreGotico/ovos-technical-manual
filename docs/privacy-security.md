# Privacy & Security

!!! abstract "In a nutshell"
    OVOS is designed to run locally and without a cloud account, but a **default
    install still talks to the network** for speech recognition and speech
    synthesis unless you change the plugins, and the [message bus](bus-service.md)
    that skills use to talk to each other has **no authentication** — anything
    that can reach it, or any skill you install, has full control of the
    assistant. This page inventories what a stock install actually sends over
    the network, who you're trusting when you install a skill, and how to
    lock things down. See the [Glossary](glossary.md) for unfamiliar terms.

This page describes the **`ovos` profile installed by the [`ovos-installer`](ovos-installer.md)
with its bundled defaults** — the most common path. Anything below can be
changed by picking different plugins or a different [profile](composable-deployments.md),
so where behavior depends on a choice you made, this page says so instead of
guessing.

---

## Network surface of a default install

| What | Default behavior | Offline? |
| --- | --- | --- |
| Speech-to-text (STT) | `ovos-stt-plugin-server`, which by default talks to a **public whisper server** run by the OVOS community | **No** — your voice audio leaves the device |
| Text-to-speech (TTS) | `ovos-tts-plugin-server`, which by default talks to a **public Piper server** (the "Alan Pope" voice) | **No** — the text you want spoken leaves the device |
| Wake word | `ovos-ww-plugin-precise-onnx` (or `precise-lite`), running fully on-device | **Yes**, once the model file is downloaded on first run |
| Backend / pairing | `mycroft.conf`'s `server.url` ships **empty** — OVOS is "backendless" by default; there is no Mycroft/Selene account and nothing is paired unless you configure a backend yourself | **Yes** |
| Remote config | `disable_remote_config` defaults to `false` (a configured backend is *allowed* to push settings) but this has no effect while no backend is configured | **Yes**, with the default empty backend |
| Update checks | The installer does **not** phone home automatically; you re-run it manually to check for a newer release | **Yes** |
| Install-time telemetry | One-time, opt-in — see below | Depends on your answer |
| Ongoing usage telemetry | Opt-in, continues to run after install — see below | Depends on your answer |

!!! danger "Default STT/TTS send your voice and words to a public server"
    Out of the box, both speech recognition and speech synthesis are configured
    against **public servers operated by the OVOS community**, not services
    running on your device. If you care about audio or text never leaving the
    machine, switch to an offline plugin — see [STT plugins](stt-plugins.md) and
    [TTS plugins](tts-plugins.md) for the offline options (for example
    `onnx-asr`-based STT or `ovos-tts-plugin-piper` running locally), or point
    the server plugins at a server you run yourself
    (see [`stt-server`](stt-server.md) / [`tts-server`](tts-server.md)).

--8<-- "snippets/community-servers.md"

!!! tip "depends on selected profile"
    A `server` or `satellite` install ([composable deployments](composable-deployments.md))
    changes which of these components even run on this particular device — the
    table above describes the all-in-one `ovos` profile.

---

## Install-time telemetry vs. ongoing usage telemetry

The installer asks two separate yes/no questions, and they are easy to
conflate because both are about "sharing anonymous data." They are not the
same thing:

- **Install-time telemetry** (`share_telemetry`) is a **one-time** report sent
  when the installer finishes: things like CPU architecture, OS, the chosen
  channel/profile, and which features were enabled. It is sent once, during
  installation, to a metrics endpoint run by the community, and nothing about
  this is ongoing — see the field table on the
  [installer page](ovos-installer.md#anonymous-telemetry) for the exact list.
- **Ongoing usage telemetry** (`share_usage_telemetry`) is different: saying
  yes here adds an `open_data.intent_urls` entry to your installed
  `mycroft.conf`, which makes the **running assistant** report intent-matching
  data on an ongoing basis, not just during setup. If you want telemetry to
  really stop after installation, decline both prompts, or set both
  `share_telemetry: false` and `share_usage_telemetry: false` if you use a
  [scenario file](ovos-installer.md#non-interactive-scenario-install).

Either way, `country` in the install-time report is derived from a public IP
geolocation lookup performed by the installer at install time (not from any
setting you type in), so it reflects wherever the machine's internet
connection is at that moment.

---

## The message bus is a trust boundary, not a security boundary

Everything inside OVOS — skills, plugins, the voice pipeline — talks over the
local [message bus](bus-service.md). As documented there:

!!! danger "The bus has no authentication and no encryption"
    Any process that can open a WebSocket connection to the bus (default
    `127.0.0.1:8181`) has full control of the assistant: it can trigger any
    skill, read everything crossing the bus, and — through plugins that expose
    subprocess or file access — potentially run arbitrary code. Never bind the
    bus to `0.0.0.0` or port-forward it to the internet. For remote access
    (satellites, phones, other rooms) use [HiveMind](hivemind-agents.md)
    instead, which adds authentication and encryption on top of the same bus
    protocol.

## Skills are not sandboxed

There is no sandbox, permission model, or capability system for skills.
**Installing a skill means running arbitrary Python code as the OVOS user**,
with the same filesystem and network access as the rest of the assistant —
exactly like installing a Python package from PyPI or `pip install`ing
something from GitHub, because that is literally the mechanism (see
[Skill Installer](skill-installer.md)). Only install skills whose source you
trust, the same way you'd vet any other code you run.

### `allow_pip` + the unauthenticated bus is a remote-code-execution chain

The [Skill Installer](skill-installer.md#configuration) is disabled by default,
guarded behind the `skills.installer.allow_pip` config key. If you turn it on
**and** the bus is reachable by someone untrusted (bound to `0.0.0.0`, exposed
through port-forwarding, or reachable on a shared/untrusted network), that is
a remote-code-execution chain: anyone who can speak to the bus can emit
`ovos.skills.install` with a URL of their choosing and have OVOS `pip install`
and load it. Treat `allow_pip: true` as equivalent to giving bus access
root-equivalent power over the device, and only combine it with a bus that is
kept strictly local.

---

## `mycroft.conf` can contain plaintext secrets

Anything you configure for cloud integrations — LLM API keys (`llm.key`), a
Home Assistant long-lived access token, custom STT/TTS server credentials —
is stored **as plaintext** in your user config, typically
`~/.config/mycroft/mycroft.conf` (see [Configuration Management](config.md#file-locations)).
There is no secrets manager or encryption layer.

!!! warning "Treat mycroft.conf like a credentials file"
    - Set restrictive file permissions on it (`chmod 600 ~/.config/mycroft/mycroft.conf`)
      if the account is shared with anyone else.
    - **Don't sync it as part of your dotfiles** to a public repository — a
      GitHub search for `llm.key` or a Home Assistant token is exactly how
      these things leak. If you version-control your dotfiles, exclude this
      file (or template it and inject secrets from an untracked source) instead
      of committing it directly.
    - Anyone with read access to the device's filesystem, or with bus access to
      request the config, can read these values.

---

## Summary checklist

- [ ] Decide whether public STT/TTS servers are acceptable for your use case;
      switch to offline or self-hosted plugins if not ([STT plugins](stt-plugins.md),
      [TTS plugins](tts-plugins.md)).
- [ ] Keep the message bus bound to `127.0.0.1`; never expose port `8181`
      directly to the internet ([Bus Service](bus-service.md)).
- [ ] Leave `allow_pip` off unless you specifically need runtime skill
      installation, and never combine it with a non-local bus
      ([Skill Installer](skill-installer.md)).
- [ ] Only install skills whose source you trust — there is no sandbox.
- [ ] Protect `mycroft.conf`'s file permissions and keep it out of shared
      dotfile repositories.
- [ ] Decide independently on install-time telemetry and ongoing usage
      telemetry — they are separate opt-ins ([installer telemetry](ovos-installer.md#anonymous-telemetry)).
- [ ] For remote/multi-room setups, use [HiveMind](hivemind-agents.md) instead
      of exposing the bus directly.

Found an actual vulnerability rather than a documentation gap? See
[reporting a vulnerability](https://github.com/TigreGotico/ovos-technical-manual/blob/master/SECURITY.md).

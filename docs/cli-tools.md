# Command-line Tools

!!! abstract "In a nutshell"
    Installing OVOS also installs a handful of **terminal commands** — small programs you run from
    a shell to configure the assistant, poke a running system ("say this", "listen now"), read the
    logs, or launch the individual services by hand. This page is a catalogue of the ones the core
    OVOS packages provide, what each does, and which package ships it. (These are the *core* CLIs;
    the [RaspOVOS image](install-raspovos.md) adds its own extra convenience commands on top.) See
    the [Glossary](glossary.md) for unfamiliar terms.

Each command below is a console-script entry point declared by a core OVOS package, so it lands on
your `PATH` when that package is installed. Run any of them with `--help` for the authoritative,
version-correct options.

---

## Configuration — `ovos-config`

Shipped by **[`ovos-config`](config.md)**. Inspect and edit the layered
[configuration](config.md) without hand-editing JSON.

| Command | What it does |
|---|---|
| `ovos-config show` | Print the merged configuration as a table. |
| `ovos-config get <path>` | Read a single value at a dotted config path. |
| `ovos-config set <path> <value>` | Write a value into the user (or system) config. |
| `ovos-config autoconfigure -l <lang>` | Pick sensible default STT/TTS/wake-word plugins for a language and platform. Flags include `--platform {rpi3,rpi4,rpi5,linux,mac,termux}`, `--online` / `--offline` / `--hybrid`, `--gpu`, and `--male` / `--female`. |
| `ovos-config telemetry --enable` / `--disable` | Opt in or out of anonymous intent telemetry. |

`ovos-config autoconfigure --help` is the recommended first stop after an install to set
language-appropriate defaults.

---

## Talking to a running OVOS — `ovos-bus-client`

Shipped by **[`ovos-bus-client`](core-libraries.md#ovos-bus-client)**. These send messages to a *running*
OVOS over the [MessageBus](bus-service.md) — handy for testing, scripting, and debugging.

| Command | What it does |
|---|---|
| `ovos-listen` | Trigger the microphone to start listening, as if the wake word had fired. |
| `ovos-speak "<phrase>"` | Make OVOS speak a phrase out loud. |
| `ovos-say-to "<phrase>"` | Inject an utterance into the pipeline as if the user had said it. |
| `ovos-simple-cli` | Open an interactive terminal chat with the assistant. |

---

## Reading the logs — `ovos-logs`

Shipped by **[`ovos-utils`](core-libraries.md#ovos-utils)**. A helper for slicing and filtering the OVOS
[log files](core-libraries.md#ovos-utils) without wrestling with `grep`/`tail`.

| Command | What it does |
|---|---|
| `ovos-logs slice` | Extract a time-bounded slice across the logs (`--start` / `--until`). |
| `ovos-logs list` | List messages filtered by level — `--error`, `--warning`, `--exception`, `--debug` — and time. |
| `ovos-logs show -l <log>` | Print one named log (e.g. `skills`, `bus`, `audio`). |
| `ovos-logs reduce` | Truncate the logs to a given `--size` or `--date` to reclaim space. |

---

## Running the services by hand

Each core OVOS service is normally started by your service manager (systemd, the
[ovos-installer](ovos-installer.md), or Docker), but every one also has a console script so you
can launch it directly — useful for debugging or minimal/headless setups.

| Command | Service | Package |
|---|---|---|
| `ovos-core` | The skills service ([ovos-core](core.md)) | `ovos-core` |
| `ovos-messagebus` | The [MessageBus](bus-service.md) server | `ovos-messagebus` |
| `ovos-dinkum-listener` | The [speech/listener service](speech-service.md) | `ovos-dinkum-listener` |
| `ovos-audio` | The [audio service](audio-service.md) — TTS & sound playback (and the legacy media audioservice) | `ovos-audio` |
| `ovos-gui-service` | The [GUI service](gui-service.md) | `ovos-gui` |
| `ovos-gui-debug-tui` | A terminal viewer for GUI state, for debugging | `ovos-gui` |
| `ovos-intent-service` | The [intent service](intent-service.md), run standalone | `ovos-core` |
| `ovos-skill-installer` | The [skill installer](skill-installer.md), run standalone | `ovos-core` |
| `ovos-ocp-standalone` | The [OCP media player](ocp-audio-plugin.md#standalone-mode), run standalone | `ovos-plugin-common-play` |

---

## Related Pages

- [ovos-config](config.md) — the configuration system the `ovos-config` CLI edits.
- [ovos-bus-client Overview](core-libraries.md#ovos-bus-client) — the library behind the `ovos-*` bus commands.
- [Logging](core-libraries.md#ovos-utils) — log locations and levels that `ovos-logs` reads.
- [ovos-docs-viewer](docs-viewer.md) — the in-terminal documentation browser.
- [RaspOVOS helper commands](install-raspovos.md#helpful-commands) — extra CLIs added by the RaspOVOS image.

---

*Source code: [OpenVoiceOS/ovos-config](https://github.com/OpenVoiceOS/ovos-config), [OpenVoiceOS/ovos-bus-client](https://github.com/OpenVoiceOS/ovos-bus-client), and [OpenVoiceOS/ovos-utils](https://github.com/OpenVoiceOS/ovos-utils).*

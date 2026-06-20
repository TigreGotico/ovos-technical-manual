
# `ovos-diagnostics` — Documentation Index

`ovos-diagnostics` is a command-line tool for auditing an OVOS installation. It scans installed plugins, checks configuration, inspects skill settings, detects hardware capabilities, and produces actionable recommendations for [STT](stt-plugins.md), [TTS](tts-plugins.md), wake word, audio, pipeline, and platform plugins.

**New to it?** Run a `scan-*` subcommand to list what is installed, or a `recommend-*` subcommand to have the tool suggest plugins for your hardware and language. For example, `ovos-diagnostics listener recommend-stt` tells you which [STT](stt-plugins.md) plugin to use based on detected GPU, platform, and configured language; `ovos-diagnostics core recommend-skills` audits your installed skills for missing API keys, OAuth tokens, and companion plugins. Everything prints plain text to stdout — no daemon, no config changes are made.

The tool is built with [Click](https://click.palletsprojects.com/) and reads live configuration via [ovos-config](https://github.com/OpenVoiceOS/ovos-config). Plugin discovery is performed via [ovos-plugin-manager](https://github.com/OpenVoiceOS/ovos-plugin-manager). [Skill](skill-design-guidelines.md) inspection imports skill base classes from [ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop) and [ovos-core](https://github.com/OpenVoiceOS/ovos-core) (the `mycroft` namespace), so those must be installed for `core` subcommands to import cleanly.

## Installation

```bash
pip install ovos-diagnostics

# or, from source:
git clone https://github.com/OpenVoiceOS/ovos-diagnostics
cd ovos-diagnostics
pip install -e .

```

## Entry Point

```
ovos-diagnostics [OPTIONS] COMMAND [ARGS]...

```

There is one top-level command group (`cli`, exposed as the `ovos-diagnostics` console script) that branches into six subgroups: `core`, `audio`, `listener`, `language`, `phal`, and `gui`. Click converts the underscores in command function names to hyphens, so `scan_stt` is invoked as `scan-stt`. Run any group or subcommand with `--help` for its usage.

## Command Groups

### `ovos-diagnostics core` — Skill pipeline diagnostics

```
ovos-diagnostics core [OPTIONS] COMMAND [ARGS]...

```

| Subcommand | Description |
|---|---|
| `scan-skills` | List all installed skill plugins |
| `scan-pipeline` | List all installed pipeline plugins |
| `scan-reranker` | List all installed CommonQuery reranker plugins |
| `scan-utterance` | List all installed utterance transformer plugins |
| `scan-metadata` | List all installed metadata transformer plugins |
| `recommend-skills` | Check installed skills for missing API keys, missing companion [PHAL](ovoscope-phal.md) plugins, missing [OCP](ocp-pipeline.md) extractor plugins, and OAuth status; recommend missing skills |
| `recommend-pipeline` | Suggest pipeline plugins based on system capabilities |
| `recommend-reranker` | Suggest CommonQuery reranker plugins |
| `recommend-utterance-transformers` | Suggest utterance transformer plugins |
| `recommend-metadata-transformers` | Suggest metadata transformer plugins |

### `ovos-diagnostics audio` — Audio and TTS diagnostics

```
ovos-diagnostics audio [OPTIONS] COMMAND [ARGS]...

```

| Subcommand | Description |
|---|---|
| `scan-tts` | List installed TTS plugins |
| `scan-tts-transformers` | List installed TTS transformer plugins |
| `scan-dialog-transformers` | List installed dialog transformer plugins |
| `scan-wake-words` | List installed wake word plugins |
| `scan-audio-players` | List installed audio player plugins |
| `scan-ocp` | List installed OCP stream extractor plugins |
| `recommend-tts` | Recommend TTS plugins based on language, GPU availability, and online/offline preference |
| `recommend-tts-transformers` | Suggest TTS transformer plugins |
| `recommend-dialog-transformers` | Suggest dialog transformer plugins |
| `recommend-wake-words` | Suggest wake word plugins suited to the platform |
| `recommend-players` | Suggest audio player plugins |
| `recommend-ocp` | Suggest OCP stream extractor plugins |

### `ovos-diagnostics listener` — STT and microphone diagnostics

```
ovos-diagnostics listener [OPTIONS] COMMAND [ARGS]...

```

| Subcommand | Description |
|---|---|
| `scan-stt` | List installed STT plugins |
| `scan-microphone` | List installed microphone plugins |
| `scan-vad` | List installed [Voice Activity Detection](vad-plugins.md) plugins |
| `scan-audio-transformers` | List installed audio transformer plugins |
| `scan-lang-detect` | List installed audio language detector plugins |
| `recommend-stt` | Recommend offline and online STT plugins based on language, GPU, platform |
| `recommend-microphone` | Suggest microphone plugins for the detected hardware |
| `recommend-vad` | Suggest [VAD](vad-plugins.md) plugins |

### `ovos-diagnostics language` — Language plugin diagnostics

```
ovos-diagnostics language [OPTIONS] COMMAND [ARGS]...

```

| Subcommand | Description |
|---|---|
| `scan-detection` | List installed language detection plugins |
| `scan-translation` | List installed translation plugins |
| `recommend-detector` | Recommend language detection plugins |
| `recommend-translator` | Recommend translation plugins |

### `ovos-diagnostics phal` — PHAL platform plugin diagnostics

```
ovos-diagnostics phal [OPTIONS] COMMAND [ARGS]...

```

| Subcommand | Description |
|---|---|
| `recommend-platform` | Suggest platform-specific PHAL plugins for the detected hardware |

### `ovos-diagnostics gui` — GUI plugin diagnostics

```
ovos-diagnostics gui [OPTIONS] COMMAND [ARGS]...

```

| Subcommand | Description |
|---|---|
| `scan-extensions` | List installed GUI extension plugins |
| `recommend-extensions` | Recommend GUI extension plugins for the detected platform |

## Platform Detection

The tool auto-detects the following at startup before generating recommendations:

- **Language** — read from `mycroft.conf` `lang` key (default `en-us`)


- **Homescreen** — `gui.idle_display_skill` from config


- **OVOS Shell / GUI** — whether `ovos-shell` is installed (detected via `ovos_utils.gui.is_installed`); GUI presence also accepts `ovos-gui-app` or `mycroft-gui-app`


- **Raspberry Pi** — presence of `/sys/firmware/devicetree/base/model` containing `"Raspberry Pi"`


- **GPU** — probes `torch.cuda.is_available()`, then `tensorflow`, then `onnxruntime` CUDA providers

## Recommendation Logic

Recommendations are context-aware. For example, `recommend-stt` output:

```
Available plugins:

 - ovos-stt-plugin-dummy


 - ovos-stt-plugin-fasterwhisper


 - ovos-stt-plugin-server
OFFLINE RECOMMENDATION: ovos-stt-plugin-fasterwhisper - multilingual, GPU allows fast inference
ONLINE RECOMMENDATION: ovos-stt-plugin-server - multilingual, self hosted (fasterwhisper)
STT RECOMMENDATION: ovos-stt-plugin-fasterwhisper - recommended offline plugin
FALLBACK STT RECOMMENDATION: None - already offline, no need to reach out to the internet!

```

`recommend-skills` matches each installed skill plugin against built-in tables of known skill requirements and reports:

- **Blacklisted skill** — `UNINSTALL` warning if an installed skill is listed under `skills.blacklisted_skills` in config


- **Missing setting** — checks `<config>/skills/<skill_id>/settings.json` for required keys (e.g. an `api_key`)


- **Missing config key** — checks `mycroft.conf` for required keys some skills need


- **Missing OAuth token** — checks the `OAuthTokenDatabase` (via `ovos-backend-client`); reports the database path and an OAuth helper command when one is known


- **Missing OCP / audio extractor** — checks whether required [OCP](ocp-pipeline.md) stream-extractor or audio-player plugins are installed


- **Missing or recommended PHAL plugin** — checks companion [PHAL](ovoscope-phal.md) requirements; Linux-only PHAL plugins on non-Linux trigger an `UNINSTALL` hint


- **Platform mismatch** — `UNINSTALL` warnings for Linux-only, GPU-only, or Raspberry-Pi-only skills running on unsupported hardware


- **Recommended companion skills** — suggests companion skills for installed solver / audio / PHAL plugins, and recommends the fallback-unknown skill if absent

Example `recommend-skills` output:

```
Listing installed skills...
 0 - skill-ovos-parrot.openvoiceos
 1 - skill-ovos-wolfie.openvoiceos
...
Skill checks ...
ERROR: 'skill-ovos-wolfie.openvoiceos' is installed but 'api_key' not set in '.../skills/skill-ovos-wolfie.openvoiceos/settings.json'
ERROR: 'ovos-skill-spotify.openvoiceos' is installed but OAuth token is missing from '.../ovos_oauth.json'
   INFO: 'ovos-skill-spotify.openvoiceos' OAuth can be performed with the command 'ovos-spotify-oauth'
ERROR: OCP stream extractor plugin missing 'ovos-ocp-youtube-plugin', required by 'ovos-skill-youtube.openvoiceos'
RECOMMENDED PHAL PLUGIN: 'ovos-PHAL-plugin-oauth' is recommended by 'ovos-skill-spotify.openvoiceos'

```

## Output Format

All output is plain text to stdout. Errors are prefixed with `ERROR:`, informational lines with `INFO:`, recommendations with `RECOMMENDATION:` / `RECOMMENDED ...:`, and removal hints with `UNINSTALL:`. At import time the tool calls `LOG.set_level("ERROR")`, so OVOS log output below `ERROR` is suppressed to keep results readable. There is no `--json` or machine-readable output mode; parse the text or import the functions directly if you need structured results.

## Quick Links

| Resource | Path |
|---|---|
| Machine-readable facts | `../QUICK_FACTS.md` |
| Common questions | `../FAQ.md` |
| Known issues | `../AUDIT.md` |

## Cross-References

- [ovos-config](https://github.com/OpenVoiceOS/ovos-config) — configuration access


- [ovos-plugin-manager](https://github.com/OpenVoiceOS/ovos-plugin-manager) — plugin discovery


- [ovos-bus-client](https://github.com/OpenVoiceOS/ovos-bus-client) — not directly used but required by plugins under test


- [ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop) — skill class inspection


- [ovos-backend-client](https://github.com/OpenVoiceOS/ovos-backend-client) — OAuth token database access

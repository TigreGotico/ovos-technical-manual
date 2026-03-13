
# `ovos-diagnostics` — Documentation Index

`ovos-diagnostics` is a command-line tool for auditing an OVOS installation. It scans installed plugins, checks configuration, inspects skill settings, detects hardware capabilities, and produces actionable recommendations for [STT](stt-plugins.md), [TTS](tts-plugins.md), wake word, audio, pipeline, and platform plugins.

The tool is built with [Click](https://click.palletsprojects.com/) and reads live configuration via [ovos-config](https://github.com/OpenVoiceOS/ovos-config). Plugin discovery is performed via [ovos-plugin-manager](https://github.com/OpenVoiceOS/ovos-plugin-manager). [Skill](skill-design-guidelines.md) inspection requires [ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop) and [ovos-core](https://github.com/OpenVoiceOS/ovos-core).

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

There is one top-level command group that branches into six subgroups.

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


- **OVOS Shell** — whether `ovos-shell` is installed (detected via `ovos_utils.gui.is_installed`)


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

`recommend-skills` inspects each installed skill for:

- **Missing API key** — checks `settings.json` for required keys


- **Missing OAuth token** — checks `ovos_oauth.json` (via `ovos-backend-client`)


- **Missing OCP extractor** — checks if required OCP plugins are installed


- **Missing PHAL plugin** — checks companion PHAL requirements


- **Skill type** — detects `FallbackSkill`, `CommonQuerySkill`, `OVOSCommonPlaybackSkill`, `CommonPlaySkill`

Example `recommend-skills` output:

```
Listing installed skills...
 0 - skill-ovos-parrot.openvoiceos
 1 - skill-ovos-wolfie.openvoiceos
...
Skill checks ...
ERROR: 'skill-ovos-wolfie.openvoiceos' is installed but 'api_key' not set
ERROR: 'ovos-skill-spotify.openvoiceos' OAuth token is missing
   INFO: OAuth can be performed with 'ovos-spotify-oauth'
ERROR: OCP stream extractor plugin missing 'ovos-ocp-youtube-plugin'
RECOMMENDED PHAL PLUGIN: 'ovos-PHAL-plugin-oauth' is recommended by 'ovos-skill-spotify.openvoiceos'

```

## Output Format

All output is plain text to stdout. Errors are prefixed with `ERROR:`, informational lines with `INFO:`, and recommendations with `RECOMMENDATION:` or `RECOMMENDED PLUGIN:`. The tool suppresses all OVOS log output below `ERROR` level during execution to reduce noise.

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

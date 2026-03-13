
# `ovos-docs-viewer` — Documentation Index

`ovos-docs-viewer` is a terminal-based documentation browser for OpenVoiceOS. It downloads Markdown documentation from GitHub, then renders it interactively inside the terminal using a [Textual](https://textual.textualize.io/) TUI with a file-tree sidebar and a Markdown viewer panel.

## How It Works

1. On first launch, the tool fetches documentation from a hard-coded set of GitHub sources and caches them under `$XDG_DATA_HOME/ovos_docs/`.


2. A `Documentation` Textual app opens with a split layout: a directory tree on the left (20% width) filtered to `.md` files only, and a `MarkdownViewer` on the right.


3. The user navigates the tree and selects files to render rendered Markdown inline.


4. Press `q` to quit.

Downloaded sources are cached on disk. Subsequent launches skip re-downloading (except `live-status`, which is always refreshed). Pass `--force` (via the code path) to re-download all sources.

## Installation

```bash
pip install ovos-docs-viewer

# or, from source:
git clone https://github.com/OpenVoiceOS/ovos-docs-viewer
cd ovos-docs-viewer
pip install -e .

```

## Entry Point

```
ovos-docs-viewer DOCS

```

`DOCS` must be one of the following string keys:

| Key | Source |
|---|---|
| `technical` | [ovos-technical-manual](https://github.com/OpenVoiceOS/ovos-technical-manual) (zip archive, full `docs/` tree) |
| `messages` | [message_spec](https://github.com/OpenVoiceOS/message_spec) (zip archive) |
| `hivemind` | [HiveMind-community-docs](https://github.com/JarbasHiveMind/HiveMind-community-docs) (zip archive) |
| `live-status` | OVOS status page README (always re-downloaded) |
| `raspOVOS` | raspOVOS README |
| `installer` | ovos-installer README |
| `skills` | README files for ~50 official OVOS skills, one file per skill |

## Usage Examples

```bash

# Browse the OVOS technical manual
ovos-docs-viewer technical

# Browse skill documentation
ovos-docs-viewer skills

# Check live service status
ovos-docs-viewer live-status

# Browse HiveMind documentation
ovos-docs-viewer hivemind

# Browse the OVOS message bus specification
ovos-docs-viewer messages

```

## Cache Location

Documentation is stored under:

```
$XDG_DATA_HOME/ovos_docs/
├── technical/docs/        ← ovos-technical-manual markdown files
├── messages/docs/         ← message spec markdown files
├── hivemind/docs/         ← HiveMind documentation
├── live-status/docs/      ← always refreshed on launch
├── raspOVOS/docs/         ← single README
├── installer/docs/        ← single README
└── skills/docs/           ← one .md per skill (e.g. ovos-skill-alerts.md)

```

`$XDG_DATA_HOME` is resolved via `ovos_utils.xdg_utils.xdg_data_home` (typically `~/.local/share`).

## UI Keybindings

| Key | Action |
|---|---|
| Arrow keys / mouse | Navigate directory tree |
| Enter | Open selected file in Markdown viewer |
| `q` | Quit the application |

## Dependencies

| Package | Role |
|---|---|
| `textual` | TUI framework (App, DirectoryTree, MarkdownViewer) |
| `click` | CLI argument parsing |
| `requests` | HTTP download of documentation |
| `ovos_utils` | XDG path resolution (`xdg_data_home`) |

## Quick Links

| Resource | Path |
|---|---|
| Machine-readable facts | `../QUICK_FACTS.md` |
| Common questions | `../FAQ.md` |
| Change log | `../MAINTENANCE_REPORT.md` |
| Known issues | `../AUDIT.md` |
| Improvement proposals | `../SUGGESTIONS.md` |

## Cross-References

- [ovos-technical-manual](https://github.com/OpenVoiceOS/ovos-technical-manual) — primary documentation source for the `technical` key


- [message_spec](https://github.com/OpenVoiceOS/message_spec) — bus message reference for the `messages` key


- [ovos-utils](https://github.com/OpenVoiceOS/ovos-utils) — XDG path helpers

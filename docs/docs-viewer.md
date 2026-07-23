
# `ovos-docs-viewer` — Documentation Index

!!! abstract "In a nutshell"
    `ovos-docs-viewer` is a little program that lets you read the OVOS documentation right inside your terminal, without opening a web browser. You run `ovos-docs-viewer technical` to open this very manual, then use the arrow keys to browse the pages and press `q` to quit. It downloads the docs the first time and remembers them afterwards, so later visits work even offline. See the [Glossary](glossary.md) for terms.

`ovos-docs-viewer` is a terminal-based documentation browser for OpenVoiceOS. It downloads Markdown documentation from GitHub, then renders it interactively inside the terminal using a [Textual](https://textual.textualize.io/) TUI with a file-tree sidebar and a Markdown viewer panel.

**Minimal use:** `ovos-docs-viewer technical` opens the technical manual in your terminal. Pass one of the documentation keys below as the single argument; the first run downloads and caches the docs, later runs read from the cache. Use the arrow keys to walk the file tree, Enter to open a file, and `q` to quit. It is read-only and needs network access only on first use (and every time for `live-status`).

## How It Works

1. On first launch, the tool fetches documentation from a hard-coded set of GitHub sources and caches them under `$XDG_DATA_HOME/ovos_docs/`.


2. A `Documentation` Textual app opens with a split layout: a directory tree on the left (20% width) filtered to `.md` files only, and a `MarkdownViewer` on the right.


3. The user navigates the tree and selects files to render rendered Markdown inline.


4. Press `q` to quit.

Downloaded sources are cached on disk. Subsequent launches skip re-downloading (except `live-status`, which is always refreshed). There is **no `--force` CLI flag**: forcing a re-download is only possible from Python, by calling `download_docs(force=True)` (or deleting the cache directory before launching).

## Installation

```bash
pip install ovos-docs-viewer

# or, from source:
git clone https://github.com/OpenVoiceOS/ovos-docs-viewer
cd ovos-docs-viewer
pip install -e .

```

## Entry Point

```bash
ovos-docs-viewer DOCS

```

The console script `ovos-docs-viewer` maps to `ovos_docs_viewer.ovos_docs:launch`. `DOCS` is a single required argument and must be one of the following string keys (an unknown key fails with an `AssertionError` before the TUI opens):

| Key | Source |
|---|---|
| `technical` | [ovos-technical-manual](https://github.com/OpenVoiceOS/ovos-technical-manual) (zip archive of the `master` branch, full `docs/` tree) |
| `messages` | [message_spec](https://github.com/OpenVoiceOS/message_spec) (zip archive of `master`) |
| `hivemind` | [HiveMind-community-docs](https://github.com/JarbasHiveMind/HiveMind-community-docs) (zip archive of `master`) |
| `live-status` | OVOS [status](https://github.com/OpenVoiceOS/status) page README (always re-downloaded) |
| `raspOVOS` | the raspOVOS image README |
| `installer` | [ovos-installer](https://github.com/OpenVoiceOS/ovos-installer) README (`main` branch) |
| `skills` | `dev`-branch README files for ~49 official OVOS skills, one `.md` file per skill |

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

```text
$XDG_DATA_HOME/ovos_docs/
├── technical/docs/             ← ovos-technical-manual markdown tree (from zip)
├── messages/docs/              ← message spec markdown tree (from zip)
├── hivemind/docs/              ← HiveMind documentation tree (from zip)
├── live-status/docs/live-status.md  ← single README, always refreshed
├── raspOVOS/docs/raspOVOS.md        ← single README
├── installer/docs/installer.md      ← single README
└── skills/docs/                ← one .md per skill (e.g. ovos-skill-alerts.md)

```

Zip-archive sources (`technical`, `messages`, `hivemind`) keep their full `docs/` tree. Single-README sources (`live-status`, `raspOVOS`, `installer`) are written as `<key>/docs/<key>.md`. `$XDG_DATA_HOME` is resolved via `ovos_utils.xdg_utils.xdg_data_home` (typically `~/.local/share`).

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

## Cross-References

- [ovos-technical-manual](https://github.com/OpenVoiceOS/ovos-technical-manual) — primary documentation source for the `technical` key


- [message_spec](https://github.com/OpenVoiceOS/message_spec) — bus message reference for the `messages` key


- [ovos-utils](https://github.com/OpenVoiceOS/ovos-utils) — XDG path helpers

# Configuration Management

`ovos-config` is the configuration layer for the entire OVOS ecosystem. It provides a layered, merged `Configuration` singleton that all OVOS components read from, plus XDG-aware path helpers, a CLI tool, and meta-config support for custom distributions.

For a detailed list of every available configuration option, see the **[Configuration Reference](config-reference.md)**.

---

## Config Layer Stack

Layers are merged in this priority order (highest wins):

```
MycroftDefaultConfig   (bundled default.conf — read-only)
OvosDistributionConfig (distribution override, e.g. /etc/xdg/mycroft/mycroft.conf)
MycroftSystemConfig    (/etc/mycroft/mycroft.conf — read-only)
RemoteConf             (~/.config/mycroft/web_cache.json)
MycroftUserConfig      (~/.config/mycroft/mycroft.conf — XDG user config)
__patch                (in-memory overlay applied last)

```

All layers are `LocalConf` dict subclasses backed by a file. Only the user config layer (`~/.config/mycroft/mycroft.conf`) should be edited by users.

---

## Usage

```python
from ovos_config import Configuration

config = Configuration()
lang = config["lang"]                         # read a value
tts_module = config["tts"]["module"]          # nested access

# Update the user config layer
from ovos_config.config import update_mycroft_config
update_mycroft_config({"lang": "de-de"})

# Emit configuration.updated on the bus after writing
update_mycroft_config({"lang": "de-de"}, bus=bus)

```

Because `Configuration` is a singleton, all instances share the same merged view. `Configuration.load_all_configs()` is called automatically on first access.

---

## File Locations

All paths respect the `OVOS_CONFIG_BASE_FOLDER` environment variable (default: `"mycroft"`).

| Constant | Default Path | Description |
|---|---|---|
| `DEFAULT_CONFIG` | `<package>/mycroft.conf` | Bundled default config (read-only) |
| `DISTRIBUTION_CONFIG` | `/etc/xdg/mycroft/mycroft.conf` | Distribution-level override |
| `SYSTEM_CONFIG` | `/etc/mycroft/mycroft.conf` | System-level config |
| `USER_CONFIG` | `~/.config/mycroft/mycroft.conf` | XDG user config (primary editable) |
| `WEB_CONFIG_CACHE` | `~/.config/mycroft/web_cache.json` | Remote config cache |
| `OLD_USER_CONFIG` | `~/.mycroft/mycroft.conf` | Legacy pre-XDG location (migration) |

File formats: JSON (`.json` or `.conf`, with C-style `//` comments supported) or YAML (`.yml` or `.yaml`).

---

## Usage Guide

**1. Create or edit your user config:**

```bash
mkdir -p ~/.config/mycroft
nano ~/.config/mycroft/mycroft.conf

```

Add only the keys you want to override — everything else falls back to defaults.

**2. Override via environment variables (optional):**

```bash
export OVOS_CONFIG_BASE_FOLDER="myfolder"
export OVOS_CONFIG_FILENAME="myconfig.yaml"

```

**3. Use the CLI:**

```bash
ovos-config show                        # full merged config
ovos-config get -k lang                 # find all keys containing "lang"
ovos-config get -k /tts/module          # get exact value at tts.module
ovos-config set -k /tts/module -v ovos-tts-plugin-mimic3

```

---

## Protected Keys and System Restrictions

The system config (`/etc/mycroft/mycroft.conf`) can enforce constraints:

| Key in system config | Effect |
|---|---|
| `protected_keys` | Dict of `{layer: [key, ...]}` — keys that cannot be overridden by higher-priority layers |
| `disable_user_config` | If `true`, the user XDG config layer is ignored |
| `disable_remote_config` | If `true`, the remote config layer (`web_cache.json`) is ignored |

Example — prevent users from accidentally exposing the messagebus:

```json
{
  "protected_keys": {
    "user": ["gui_websocket.host", "websocket.host"]
  }
}

```

> Admin [PHAL](ovoscope-phal.md) is a special service that runs as root — it can **only** access `/etc/mycroft/mycroft.conf`.

---

## Patch Mechanism

The `__patch` overlay is an in-memory dict merged on top of all file-backed layers. Used for temporary overrides that should not be persisted to disk.

```python
config.patch({"lang": "fr-fr"})   # apply in-memory patch
config.patch_reset()               # clear the patch

```

Bus event `configuration.patch` triggers `patch()` with the provided `config` data payload.
Bus event `configuration.patch.clear` triggers `patch_reset()`.

---

## Bus Integration

`Configuration.set_config_update_handlers(bus)` registers the following listeners:

| Bus Event | Action |
|---|---|
| `configuration.updated` | Reload all config layers |
| `configuration.patch` | Apply `data["config"]` as an in-memory patch |
| `configuration.patch.clear` | Clear the in-memory patch |

`Configuration.set_config_watcher()` uses `inotify`/`watchdog` to monitor config files on disk and reloads automatically when they change.

---

## Config Models

Each layer is a `LocalConf` instance — a file-backed `dict` subclass.

**Module:** `ovos_config.models`

| Class | Path | Notes |
|---|---|---|
| `LocalConf` | any path | Base class; supports JSON and YAML |
| `ReadOnlyConfig` | any path | Raises `PermissionError` on mutation |
| `MycroftDefaultConfig` | bundled `default.conf` | `ReadOnlyConfig` |
| `OvosDistributionConfig` | `/etc/xdg/mycroft/mycroft.conf` | Distribution-level |
| `MycroftSystemConfig` | `/etc/mycroft/mycroft.conf` | `ReadOnlyConfig` |
| `RemoteConf` | `~/.config/mycroft/web_cache.json` | Cached remote config |
| `MycroftUserConfig` | `~/.config/mycroft/mycroft.conf` | Primary user layer |

```python
from ovos_config.models import LocalConf, MycroftUserConfig

# Direct access to a layer
user = MycroftUserConfig()
user["tts"] = {"module": "ovos-tts-plugin-mimic3"}
user.store()   # write to disk

```

### `LocalConf` Key Methods

| Method | Description |
|---|---|
| `load_config()` | Read from `self.path` and merge into self |
| `store(path=None)` | Write current contents to disk |
| `merge(conf)` | Deep-merge another dict into self |
| `reload()` | Re-read from disk, discarding in-memory changes |

`LocalConf` uses a `NamedLock` (keyed by file path) to coordinate concurrent reads and writes.

### Merge Semantics

- Scalar values: higher-priority layer wins


- Dict values: recursively merged


- List values: higher-priority layer replaces (no deduplication)

---

## Accessing Individual Layers

```python
config = Configuration()
config.system    # MycroftSystemConfig (LocalConf)
config.remote    # RemoteConf (LocalConf)
config.user      # MycroftUserConfig (LocalConf)

```

---

## Environment Variable Overrides

**Module:** `ovos_config.meta`

| Variable | Default | Effect |
|---|---|---|
| `OVOS_CONFIG_BASE_FOLDER` | `"mycroft"` | XDG subdirectory name for all config/data/cache paths |
| `OVOS_CONFIG_FILENAME` | `"mycroft.conf"` | Config filename inside the XDG config directory |
| `OVOS_DEFAULT_CONFIG` | package `mycroft.conf` | Path to the bundled default config |

These are read at import time. Override at runtime:

```python
from ovos_config.meta import set_xdg_base, set_config_filename, set_default_config

set_xdg_base("my_distro")                        # changes ~/.config/my_distro/
set_config_filename("mycroft.conf")                  # changes filename
set_default_config("/opt/my_distro/default.conf") # changes bundled defaults

```

### Distribution Overrides

Distributions can change the default XDG base folder or config filename by setting environment variables:

- `OVOS_CONFIG_BASE_FOLDER`: changes `~/.config/mycroft/` to `~/.config/custom/` (default: `mycroft`).


- `OVOS_CONFIG_FILENAME`: changes `mycroft.conf` to `custom.json` (default: `mycroft.conf`).


- `OVOS_DEFAULT_CONFIG`: provides a full path to a custom default configuration file.

---

## XDG Path Helpers

**Module:** `ovos_config.locations`

```python
from ovos_config.locations import (
    get_xdg_config_save_path,   # e.g. ~/.config/mycroft/
    get_xdg_data_save_path,     # e.g. ~/.local/share/mycroft/
    get_xdg_cache_save_path,    # e.g. ~/.cache/mycroft/
    find_user_config,           # finds user config, with XDG→legacy fallback
    get_config_locations,       # ordered list of all active config paths
)

```

`get_config_locations()` returns the full list of active config file paths — useful for debugging which files are in use.

---

## CLI Reference

**Entry point:** `ovos-config` | **Module:** `ovos_config.__main__`

### `show`

```bash
ovos-config show                        # full merged config
ovos-config show -u --section tts       # user config, tts section only
ovos-config show -s -l                  # list sections of system config
ovos-config show -u --section base      # user config, top-level scalar keys

```

Merge priority displayed: `user > system > remote > default`

### `get`

```bash
ovos-config get -k lang                 # find all keys containing "lang"
ovos-config get -k /tts/module          # get exact value at tts.module (strict path)

```

### `set`

```bash
ovos-config set -k /tts/module -v ovos-tts-plugin-mimic3
ovos-config set -k blacklisted_skills -v my-bad-skill   # append to list
ovos-config set -k gui                  # interactive: choose key and enter value

```

Values are type-cast to match the existing value's type. List targets append rather than replace.

### `autoconfigure`

Automatically configure language, [STT](stt-plugins.md), and [TTS](tts-plugins.md) from a language code:

```bash
ovos-config autoconfigure -l en-us --offline --female
ovos-config autoconfigure -l de-de --online --male -p rpi4
ovos-config autoconfigure -l fr-fr --gpu --female

```

| Option | Description |
|---|---|
| `-l LANG` | BCP-47 language code (required) |
| `-p PLATFORM` | `rpi3`, `rpi4`, `rpi5`, `linux`, `mac`, `termux` |
| `--hybrid` | Offline TTS + online STT (default) |
| `--online` | Online STT and TTS |
| `--offline` | Offline STT and TTS |
| `--gpu` | GPU-optimised offline plugins |
| `--male` / `--female` | Default voice gender |

The `autoconfigure` command uses language-specific STT models and platform-optimized intent pipelines.

### `telemetry`

```bash
ovos-config telemetry --enable    # opt in to intent telemetry upload
ovos-config telemetry --disable   # opt out

```

---

## Tips

- Always edit `~/.config/mycroft/mycroft.conf` (user layer) — never edit system or default files.


- JSON files support C-style `//` comments.


- `get_config_locations()` returns the full list of active config file paths for debugging.


- Use `disable_user_config` or `disable_remote_config` with caution — they silently skip those layers.

---

## Related Pages

- [Bus Service](bus-service.md) — `websocket` config section


- [Bus Client](bus-client-overview.md) — `websocket` and `session` config sections


- [ovos-core](core.md) — `skills`, `intents`, `utterance_transformers` config sections

# ovos-config

`ovos-config` is the configuration layer for the entire OVOS ecosystem. It provides:

- A layered, merged `Configuration` singleton that all OVOS components read from


- File-backed `LocalConf` dict models for each layer in the stack


- XDG-aware path helpers for locating config files


- Environment variable overrides for the XDG base folder, filename, and default config path


- A `ovos-config` CLI tool for inspecting and modifying configuration

---

## Navigation

| Document | Contents |
|---|---|
| [configuration.md](configuration-ref.md) | `Configuration` singleton, config stack, patch mechanism, bus integration |
| [models.md](pydantic-models.md) | `LocalConf`, `ReadOnlyConfig`, concrete layer classes |
| [locations.md](locations-ref.md) | XDG path helpers and path constants |
| [meta.md](config.md) | Environment variable overrides, `get_ovos_config()`, `set_*` helpers |
| [cli.md](config.md) | `ovos-config` CLI: `show`, `get`, `set`, `telemetry`, `autoconfigure` |

---

## Quick Start

```python
from ovos_config import Configuration

config = Configuration()
lang = config["lang"]                         # read a value
tts_module = config["tts"]["module"]          # nested access

# Update the user config layer
from ovos_config.config import update_mycroft_config
update_mycroft_config({"lang": "de-de"})

```

---

## Package Layout

```
ovos_config/
├── config.py       # Configuration singleton
├── models.py       # LocalConf, ReadOnlyConfig, layer classes
├── locations.py    # XDG path helpers and constants
├── meta.py         # Env var overrides (XDG base, filename, default config)
├── locale.py       # Language/timezone helpers
├── utils.py        # init_module_config(), deprecated FileWatcher re-exports
└── __main__.py     # ovos-config CLI (show / get / set / telemetry / autoconfigure)

```

---

## Config Layer Stack

Layers are merged in this priority order (highest wins):

```
MycroftDefaultConfig   (bundled default.conf)
OvosDistributionConfig (distribution override, e.g. /etc/xdg/mycroft/mycroft.conf)
MycroftSystemConfig    (/etc/mycroft/mycroft.conf)
RemoteConf             (~/.config/mycroft/web_cache.json)
MycroftUserConfig      (~/.config/mycroft/mycroft.conf  — XDG user config)
__patch                (in-memory overlay applied last)

```

All layers are `LocalConf` dict subclasses backed by a file. See [models.md](pydantic-models.md) for details.

---

## Entry Points

`ovos-config` registers no plugin entry points of its own. It is consumed by every other OVOS component as a dependency.

The CLI is registered via:

```toml
[project.scripts]
ovos-config = "ovos_config.__main__:config"

```

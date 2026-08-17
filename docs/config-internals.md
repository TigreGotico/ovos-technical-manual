# Configuration Internals

!!! abstract "In a nutshell"
    This page covers how `ovos-config` is built under the hood: the Python classes
    backing each config layer, the in-memory patch overlay, the bus events that keep
    processes in sync, environment-variable overrides, XDG path helpers, and the
    package layout. Most users never need this. If you only want to change a setting,
    see [Configuration Management](config.md). For the settings catalog, see the
    [Configuration Reference](config-reference.md).

---

## Patch Mechanism

The `__patch` overlay is an in-memory dict merged on top of all file-backed layers. It is used for temporary overrides that should not be persisted to disk. Writing a key on the singleton goes into this patch:

```python
config = Configuration()
config["lang"] = "fr-fr"   # stored in the in-memory __patch layer
```

The patch is applied and cleared via `Configuration.patch(message)` and
`Configuration.patch_clear(message)`. Both are `@staticmethod`s that take a bus
`Message` (they read `message.data["config"]`), not a plain dict. In practice they
are driven by the bus handlers below rather than called directly.

---

## Bus Integration

`Configuration.set_config_update_handlers(bus)` registers the following listeners:

| Bus Event | Handler | Action |
|---|---|---|
| `configuration.updated` | `Configuration.updated` | Reload the default, system, remote and XDG layers |
| `configuration.patch` | `Configuration.patch` | Apply `data["config"]` as an in-memory patch |
| `configuration.patch.clear` | `Configuration.patch_clear` | Clear the in-memory patch |
| `configuration.cache.clear` | `Configuration.clear_cache` | **Pending** [`ovos-config#288`](https://github.com/OpenVoiceOS/ovos-config/pull/288), not yet merged: currently a deprecated no-op that only re-emits `configuration.updated` (no cache exists to drop today), but #288 memoizes the merged config stack and makes this handler drop that memo again |
| `mycroft.paired` | `Configuration.handle_remote_update` | Reload the remote/backend config layer |
| `mycroft.internet.connected` | `Configuration.handle_remote_update` | Reload the remote/backend config layer |

`configuration.updated` reloads **every** layer: `reload()` re-reads default, distribution,
system, remote and all the XDG configs from disk (the read-only layers included — their
`reload()` does a real, mtime-checked re-read). A script that edits any layer's file and then
emits this event sees the change immediately, without waiting for the file watcher.

`Configuration.set_config_watcher()` uses `ovos-utils`' `FileWatcher` (watchdog) to monitor
config files on disk, and reloads when a watched file changes.

The watch list is built once, from the files that exist at that moment
(`[p for p in paths if isfile(p)]`), and is never rebuilt. A config file created **after** the
service started is therefore not watched at all. On a fresh install with no
`~/.config/mycroft/mycroft.conf`, creating one later needs a restart before live reload
applies to it.

---

## Config Models

Each layer is a `LocalConf` instance, a file-backed `dict` subclass.

**Module:** `ovos_config.models`

| Class | Path | Notes |
|---|---|---|
| `LocalConf` | any path | Base class; supports JSON and YAML |
| `ReadOnlyConfig` | any path | Raises `PermissionError` on mutation (unless `allow_overwrite=True`) |
| `MycroftDefaultConfig` | bundled `mycroft.conf` | `ReadOnlyConfig` |
| `OvosDistributionConfig` | `/usr/share/mycroft/mycroft.conf` | `ReadOnlyConfig` |
| `MycroftSystemConfig` | `/etc/mycroft/mycroft.conf` | `ReadOnlyConfig` |
| `RemoteConf` | backend / paired-server cache | Optional remote layer (`LocalConf`) |
| `MycroftUserConfig` | `~/.config/mycroft/mycroft.conf` | Primary user layer (`LocalConf`) |

`MycroftUserConfig` is also exported under the alias `MycroftXDGConfig` for backward
compatibility.

```python
from ovos_config.models import LocalConf, MycroftUserConfig

# Direct access to a layer
user = MycroftUserConfig()
user["tts"] = {"module": "ovos-tts-plugin-phoonnx"}
user.store()   # write to disk
```

### `LocalConf` Key Methods

| Method | Description |
|---|---|
| `load_local(path=None)` | Read from `path` (or `self.path`) and merge into self |
| `store(path=None)` | Write current contents to disk |
| `merge(conf)` | Deep-merge another dict into self |
| `reload()` | Re-read from disk if the file changed since last load |

`LocalConf` uses a single shared class-level `NamedLock("ovos_config")` to coordinate concurrent reads and writes across all instances.

### Merge Semantics

- Scalar values: higher-priority layer wins


- Dict values: recursively merged


- List values: higher-priority layer replaces (no deduplication)

---

## Accessing Individual Layers

The individual layers are class attributes on `Configuration` (not per-instance):

```python
Configuration.default       # MycroftDefaultConfig
Configuration.remote        # RemoteConf — backend / paired-server cache (optional)
Configuration.distribution  # OvosDistributionConfig
Configuration.system        # MycroftSystemConfig
Configuration.xdg_configs   # list[LocalConf] — the user/XDG layer(s)
```

There is no `.user` attribute. The editable user config is the **last** entry in
`Configuration.xdg_configs`. The list runs from lowest to highest precedence — system-wide
XDG dirs such as `/etc/xdg/mycroft/mycroft.conf` first, then `$XDG_CONFIG_HOME` — and the
merge runs left to right, so the last entry wins: the user's own file. See [Config Layer
Stack](config.md#config-layer-stack). To write the user file directly, use `MycroftUserConfig()`
(see Config Models above). Or call `update_mycroft_config()` to merge a change and emit the
`configuration.patch` bus notification in one step.

---

## Environment Variable Overrides

**Module:** `ovos_config.meta`

| Variable | Default | Effect |
|---|---|---|
| `OVOS_CONFIG_BASE_FOLDER` | `"mycroft"` | XDG subdirectory name for all config/data/cache paths |
| `OVOS_CONFIG_FILENAME` | `"mycroft.conf"` | Config filename inside the XDG config directory |
| `OVOS_DEFAULT_CONFIG` | package `mycroft.conf` | Path to the bundled default config |

The framework reads these when `ovos_config.config` is first imported: the `Configuration`
singleton resolves its layer paths (`default`, `distribution`, `system`, `xdg_configs`) as
class attributes at that moment, and nothing later rebuilds them — `Configuration.reset()`
and `reload()` re-read the existing file paths, they do not recompute the path list.

Python setters exist (`set_xdg_base`, `set_config_filename`, `set_default_config` in
`ovos_config.meta`), but they only affect code that later calls the dynamic path helpers
(`get_xdg_config_save_path()`, `find_user_config()`, `get_xdg_config_dirs()`). They cannot
redirect the `Configuration` singleton itself: importing `ovos_config.meta` executes the
package `__init__`, which imports `ovos_config.config` first, so by the time a setter is
even importable the singleton's paths are already frozen. **Setting the environment
variables before the process starts is the only mechanism that changes where
`Configuration` looks**:

```bash
export OVOS_CONFIG_BASE_FOLDER=my_distro          # ~/.config/my_distro/
export OVOS_CONFIG_FILENAME=mycroft.conf          # filename inside the XDG dir
export OVOS_DEFAULT_CONFIG=/opt/my_distro/default.conf
```

### Distribution Overrides

Distributions can change the default XDG base folder or config filename by setting environment variables:

- `OVOS_CONFIG_BASE_FOLDER`: changes `~/.config/mycroft/` to `~/.config/custom/` (default: `mycroft`).


- `OVOS_CONFIG_FILENAME`: changes `mycroft.conf` to `custom.json` (default: `mycroft.conf`).


- `OVOS_DEFAULT_CONFIG`: provides a full path to a custom default configuration file.

---

## XDG Path Helpers

**Module:** `ovos_config.locations`. Helper functions such as `get_xdg_config_save_path()`
and `find_user_config()` compute the paths above. See [Locations](locations-ref.md) for the
full reference and usage examples.

---

## Package Layout

```text
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

## Entry Points

`ovos-config` registers no plugin entry points of its own. Every other OVOS component consumes it as a dependency.

The CLI is registered in `pyproject.toml`:

```toml
[project.scripts]
ovos-config = "ovos_config.__main__:config"
```

---

*Source code: [OpenVoiceOS/ovos-config](https://github.com/OpenVoiceOS/ovos-config).*

---
**Read next:** [Configuration Management](config.md)
**Related:** [Configuration Reference](config-reference.md) · [Locations](locations-ref.md) · [All Configuration Keys](config-all-keys.md)

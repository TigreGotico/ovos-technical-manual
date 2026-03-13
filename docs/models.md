# Config Models

**Module:** `ovos_config.models`

Each layer of the configuration stack is a `LocalConf` instance — a file-backed `dict` subclass. Specialised subclasses represent each layer.

---

## `LocalConf`

Base class for all file-backed config layers.

```python
from ovos_config.models import LocalConf

conf = LocalConf("/path/to/mycroft.conf")
conf["lang"] = "en-us"
conf.store()   # write back to disk

```

### Supported File Formats

| Extension | Format |
|---|---|
| `.conf`, `.json` | JSON (with C-style `//` comments stripped) |
| `.yaml`, `.yml` | YAML |

If the file does not exist, `LocalConf` initialises as an empty dict and creates it on `store()`.

### Key Methods

| Method | Description |
|---|---|
| `load_config()` | Read from `self.path` and merge into self |
| `store(path=None)` | Write current contents to disk (default: `self.path`) |
| `merge(conf)` | Deep-merge another dict into self |
| `reload()` | Re-read from disk, discarding in-memory changes |

### File Locking

`LocalConf` uses a `NamedLock` (keyed by file path) to coordinate concurrent reads and writes across threads/processes.

---

## `ReadOnlyConfig`

`LocalConf` subclass that raises `PermissionError` on any mutation.

```python
from ovos_config.models import ReadOnlyConfig

conf = ReadOnlyConfig("/etc/mycroft/mycroft.conf")
conf["lang"] = "de-de"  # raises PermissionError

```

Used for system and default config layers that must not be modified at runtime.

---

## Concrete Layer Classes

All of these are `LocalConf` subclasses (or `ReadOnlyConfig`) with hard-coded paths.

### `MycroftDefaultConfig`

```python
from ovos_config.models import MycroftDefaultConfig

```

- Points to the bundled `default.conf` shipped with the package


- Path resolved from `ovos_config/mycroft.conf` inside the installed package


- `ReadOnlyConfig` — cannot be modified

### `OvosDistributionConfig`

```python
from ovos_config.models import OvosDistributionConfig

```

- Distribution-level override, e.g. `/etc/xdg/mycroft/ovos.conf`


- Path controlled by `OVOS_CONFIG_BASE_FOLDER` and `OVOS_CONFIG_FILENAME` (see [meta.md](config.md))


- Loaded second in the stack; intended for OS/image-level defaults

### `MycroftSystemConfig`

```python
from ovos_config.models import MycroftSystemConfig

```

- System config at `/etc/mycroft/mycroft.conf`


- Can set `protected_keys`, `disable_user_config`, `disable_remote_config`


- `ReadOnlyConfig` — runtime writes raise `PermissionError`

### `RemoteConf`

```python
from ovos_config.models import RemoteConf

```

- Remote config cache at `~/.config/mycroft/web_cache.json` (XDG)


- Updated by `ovos-core` when the backend pushes settings


- Skipped entirely if `disable_remote_config: true` in system config

### `MycroftUserConfig`

```python
from ovos_config.models import MycroftUserConfig

```

- Primary user-editable config at `~/.config/mycroft/mycroft.conf` (XDG)


- Path controlled by `OVOS_CONFIG_BASE_FOLDER` and `OVOS_CONFIG_FILENAME`


- This is the layer modified by `update_mycroft_config()` and the CLI `set` command


- Skipped entirely if `disable_user_config: true` in system config

---

## Merge Semantics

`LocalConf.merge(other)` performs a recursive deep merge:

- Scalar values: `other` wins


- Dict values: recursively merged


- List values: `other` replaces (no deduplication)

This is the same merge strategy used by `Configuration.filter_and_merge()` when assembling the full stack.

---

## Direct Usage Example

```python
from ovos_config.models import MycroftUserConfig

user = MycroftUserConfig()
user["tts"] = {"module": "ovos-tts-plugin-mimic3"}
user.store()

```

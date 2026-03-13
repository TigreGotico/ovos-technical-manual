# Locations

**Module:** `ovos_config.locations`

Path constants and XDG path helpers used by the rest of `ovos-config` to locate configuration files.

---

## Path Constants

All paths respect the `OVOS_CONFIG_BASE_FOLDER` environment variable (default: `"mycroft"`).

| Constant | Default Path | Description |
|---|---|---|
| `DEFAULT_CONFIG` | `<package>/mycroft.conf` | Bundled default config (read-only) |
| `DISTRIBUTION_CONFIG` | `/etc/xdg/mycroft/mycroft.conf` | Distribution-level override |
| `SYSTEM_CONFIG` | `/etc/mycroft/mycroft.conf` | System-level config |
| `USER_CONFIG` | `~/.config/mycroft/mycroft.conf` | XDG user config (primary editable) |
| `WEB_CONFIG_CACHE` | `~/.config/mycroft/web_cache.json` | Remote config cache |
| `OLD_USER_CONFIG` | `~/.mycroft/mycroft.conf` | Legacy pre-XDG location (migration) |

---

## XDG Path Helpers

These return the canonical XDG-compliant paths for config, data, and cache directories.

### `get_xdg_config_save_path()`

```python
from ovos_config.locations import get_xdg_config_save_path

path = get_xdg_config_save_path()

# e.g. "/home/user/.config/mycroft"

```

Returns the XDG config directory for the current base folder. Creates it if it does not exist.

### `get_xdg_data_save_path()`

```python
from ovos_config.locations import get_xdg_data_save_path

path = get_xdg_data_save_path()

# e.g. "/home/user/.local/share/mycroft"

```

Returns the XDG data directory. Creates it if it does not exist.

### `get_xdg_cache_save_path()`

```python
from ovos_config.locations import get_xdg_cache_save_path

path = get_xdg_cache_save_path()

# e.g. "/home/user/.cache/mycroft"

```

Returns the XDG cache directory. Creates it if it does not exist.

### `find_user_config()`

```python
from ovos_config.locations import find_user_config

path = find_user_config()

```

Returns the path to the user config file. Checks `USER_CONFIG` (XDG) first, then falls back to `OLD_USER_CONFIG` for migration compatibility.

### `get_config_locations()`

```python
from ovos_config.locations import get_config_locations

paths = get_config_locations()

# returns list of all config paths in stack order

```

Returns an ordered list of all config file paths that `Configuration` will load, from lowest to highest priority. Useful for debugging which files are in use.

---

## Environment Variable Influence

The paths above are all affected by:

| Environment Variable | Effect |
|---|---|
| `OVOS_CONFIG_BASE_FOLDER` | Replaces `"mycroft"` as the XDG subdirectory name |
| `OVOS_CONFIG_FILENAME` | Replaces `"mycroft.conf"` as the config filename |

See [meta.md](config.md) for the full env var API.

# Skill Settings

Settings provide per-skill persistent key-value storage backed by a JSON file. They allow users to configure and personalize skill behaviour — changing defaults, providing API keys, or adjusting integration preferences.

---

## Storage Location

```
~/.config/ovos/skills/<skill_id>/settings.json
```

For `OVOSAbstractApplication`:
```
~/.config/ovos/apps/<skill_id>/settings.json
```

---

## Accessing Settings

`self.settings` is a `JsonStorage` dict-like object. Read and write it like a normal dict:

```python
# Read with default
name = self.settings.get("username", "stranger")

# Write
self.settings["username"] = "Alice"

# Persist immediately (normally auto-saved on shutdown)
self.settings.store()
```

Always use `.get(key, default)` — never `self.settings["key"]` directly, as that raises `KeyError` if the key is absent.

Do not access `self.settings` in `__init__()`. Wait until `initialize()` to ensure settings are fully loaded.

Do not replace the whole `self.settings` dict:

```python
# WRONG — replaces the JsonStorage object
self.settings = {"key": "value"}

# CORRECT — update individual keys
self.settings["key"] = "value"
```

---

## Default Values

Set defaults as individual key assignments in `initialize()`, not by replacing `self.settings`. Defaults are only applied if the key does not already exist in the stored settings file.

The `__mycroft_skill_firstrun` key is managed automatically to track first-run state.

---

## Change Callback

Set `self.settings_change_callback` to a callable that is invoked whenever settings change:

```python
def initialize(self):
    self.settings_change_callback = self.on_settings_changed
    self.on_settings_changed()  # Also apply current values immediately

def on_settings_changed(self):
    self.log.info("Settings updated!")
    self._apply_new_volume(self.settings.get("volume", 50))
```

---

## File Watching

Settings changes can arrive two ways:

1. **Bus event** (`ovos.skills.settings_changed`) — emitted by `ovos-core`'s file watcher. This is the primary mechanism in a standard setup.
2. **Local file watcher** — enabled by setting `monitor_own_settings: true` in the skill's own settings. Useful in isolated setups (e.g. containers) where the skill and core do not share a filesystem.

---

## Remote Settings

Skills can receive remote settings updates via `mycroft.skills.settings.changed`. Only settings for this skill (keyed by `skill_id`) are applied. After applying remote settings the file watcher is started if not already running.

---

## Private Settings

Skills also have access to `self.private_settings` (`PrivateSettings`) — a separate storage for data that should not be shared or synced. Backed by a JSON file outside the standard settings path.

---

## Web-Based Settings UI (Community)

A community-built web interface, [OVOS Skill Config Tool](https://github.com/OscillateLabsLLC/ovos-skill-config-tool), provides a modern UI for configuring OVOS skills.

**Features:**
- Clean UI for managing skill-specific settings
- Grouping and organization of skills
- Dark mode support
- Built-in Basic Authentication

**Installation:**

```bash
pip install ovos-skill-config-tool
ovos-skill-config-tool
```

Access at `http://0.0.0.0:8000`. Default credentials: `ovos` / `ovos`.

Customize credentials via environment variables:

```bash
export OVOS_CONFIG_USERNAME=myuser
export OVOS_CONFIG_PASSWORD=mypassword
```

---

## Tips

- Always use `.get(key, default)` for safe reads.
- Use `initialize()` instead of `__init__()` for anything that depends on settings.
- Use `settings_change_callback` to keep your skill reactive to user changes.
- Use `self.private_settings` for sensitive data that should not leave the device.

---

## Related Pages

- [Skill Classes](412-skill-classes.md) — `OVOSSkill` base class
- [Skill Settings Meta](408-skill_settings_meta.md) — `settingsmeta.json` schema for GUI settings UI
- [ovos-core](102-core.md) — settings file watcher and `ovos.skills.settings_changed` event

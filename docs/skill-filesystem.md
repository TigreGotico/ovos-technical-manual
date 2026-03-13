# Filesystem Access

`FileSystemAccess` provides each skill with an isolated, XDG-compliant directory for persistent file storage. It prevents skills from accidentally writing to arbitrary locations and handles migration from legacy Mycroft paths.

**Source:** `ovos_workshop/filesystem.py`

---

## Storage Path

Files are stored under:

```
~/.local/share/ovos/filesystem/<skill_id>/

```

The exact base is determined by `get_xdg_data_save_path()` from `ovos-config`. The directory is created automatically if it does not exist.

---

## Migration from Legacy Paths

If a directory exists at the legacy Mycroft location (`~/.mycroft/<skill_id>`) but the XDG path does not yet exist, the directory is automatically **moved** to the new location. A deprecation warning is logged during migration.

---

## `self.file_system` Property

Every `OVOSSkill` (and `OVOSAbstractApplication`) exposes `self.file_system` — a `FileSystemAccess` instance pre-configured with the skill's `skill_id`. You do not need to construct `FileSystemAccess` manually.

```python

# Inside a skill method:
with self.file_system.open("data.json", "w") as f:
    import json
    json.dump({"key": "value"}, f)

```

---

## API

### `open(filename, mode)`

Open a file inside the skill's sandboxed directory. Equivalent to `open(skill_dir / filename, mode)`.

| Parameter | Description |
|---|---|
| `filename` | Filename relative to the skill's storage directory |
| `mode` | File open mode (`"r"`, `"w"`, `"rb"`, `"a"`, etc.) |

### `exists(filename)`

Check whether a file exists inside the skill's sandboxed directory. Returns `True` or `False`.

### `path`

`self.file_system.path` is the absolute path to the skill's storage directory. Use `open()` and `exists()` rather than accessing files directly by path when possible.

---

## Persistent Files

```python
def write_line_to_file(self, file_name, line):
    """Write a single line to a file in the skill's persistent filesystem."""
    with self.file_system.open(file_name, "w") as my_file:
        my_file.write(line)

def read_file(self, file_name):
    """Read the contents of a file in the skill's persistent filesystem."""
    with self.file_system.open(file_name, "r") as my_file:
        return my_file.read()

```

Check existence before reading:

```python
file_name = "example.txt"
if self.file_system.exists(file_name):
    content = self.read_file(file_name)

```

---

## Subdirectories

`file_system.open()` does not create subdirectories automatically. Create them manually using `os.mkdir`:

```python
from os import mkdir
from os.path import join

def initialize(self):
    cache_dir = "cache"
    if not self.file_system.exists(cache_dir):
        mkdir(join(self.file_system.path, cache_dir))
    with self.file_system.open(join(cache_dir, "example.txt"), "w") as f:
        f.write("cached content")

```

---

## Temporary Cache

For data that can be discarded and regenerated, use the `get_cache_directory()` helper from `ovos-utils`:

```python
from os.path import join
from ovos_utils.file_utils import get_cache_directory

def initialize(self):
    cache_dir = get_cache_directory("MySkill")
    self.cache_file = join(cache_dir, "myfile.txt")

```

The cache directory may reside on a RAM disk and can be cleared at any time. Always handle the case where cached files are absent.

---

## Skill Root Directory

```python
self.root_dir

```

The absolute path to the skill's installed root directory (e.g. `~/.local/share/mycroft/skills/my-skill.me/`). Skills should not modify files inside `root_dir` — doing so may trigger a skill reload.

---

## Full Example

```python
import json
from ovos_workshop.skills.ovos import OVOSSkill
from ovos_workshop.decorators import intent_handler


class HighScoreSkill(OVOSSkill):
    """Skill that persists a high score to disk."""

    SCORES_FILE = "highscores.json"

    def initialize(self):
        self._scores = self._load_scores()

    def _load_scores(self) -> dict:
        if not self.file_system.exists(self.SCORES_FILE):
            return {}
        with self.file_system.open(self.SCORES_FILE, "r") as f:
            return json.load(f)

    def _save_scores(self):
        with self.file_system.open(self.SCORES_FILE, "w") as f:
            json.dump(self._scores, f, indent=2)

    @intent_handler("get_high_score.intent")
    def handle_get_score(self, message):
        player = message.data.get("player", "anonymous")
        score = self._scores.get(player, 0)
        self.speak(f"{player} has a high score of {score}.")

    @intent_handler("set_high_score.intent")
    def handle_set_score(self, message):
        player = message.data.get("player", "anonymous")
        score = int(message.data.get("score", 0))
        self._scores[player] = max(self._scores.get(player, 0), score)
        self._save_scores()
        self.speak(f"High score updated for {player}.")

```

---

## Using `FileSystemAccess` Outside a Skill

```python
from ovos_workshop.filesystem import FileSystemAccess

fs = FileSystemAccess("my-app.author")

# Files stored at ~/.local/share/ovos/filesystem/my-app.author/

if not fs.exists("config.json"):
    with fs.open("config.json", "w") as f:
        import json
        json.dump({"initialized": True}, f)

```

---

## Related Pages

- [Skill Classes](skill-classes.md) — `OVOSSkill` properties including `file_system` and `root_dir`


- [Skill Settings](skill-settings.md) — `self.settings` for configuration storage


- [Configuration](config.md) — XDG path helpers used internally

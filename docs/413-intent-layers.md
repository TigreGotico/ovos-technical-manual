# Intent Layers and Permissions

---

## Intent Layers

Intent layers let a skill enable or disable groups of intents at runtime. This is useful for building modal interactions where different commands are valid in different states.

**Module:** `ovos_workshop.decorators.layers` / `ovos_workshop.skills.layers`

### Concept

A skill can define multiple named "layers", each containing a set of intents. Only the intents belonging to the currently active layer(s) are enabled at any time. The skill starts with no layers active — the global (non-layered) intents are always active.

### Layer Decorators

#### `@layer_intent`

Register a handler that only fires when a specific layer is active:

```python
from ovos_workshop.decorators.layers import layer_intent, enables_layer, disables_layer

class MySkill(OVOSSkill):

    @intent_handler("start.game.intent")
    @enables_layer("game_mode")
    def handle_start_game(self, message):
        self.speak("Game started!")

    @layer_intent("game_mode", "guess.intent")
    def handle_guess(self, message):
        guess = message.data.get("number")
        self.speak(f"You guessed {guess}")

    @layer_intent("game_mode", "quit.intent")
    @disables_layer("game_mode")
    def handle_quit(self, message):
        self.speak("Game over!")
```

#### `@enables_layer` / `@disables_layer`

Activate or deactivate a layer when a handler runs (executes after the function body):

```python
@enables_layer("listening_mode")
def start_listening(self, message): ...

@disables_layer("listening_mode")
def stop_listening(self, message): ...
```

#### `@replaces_layer`

Deactivate all layers and activate only the named one:

```python
from ovos_workshop.decorators.layers import replaces_layer

@replaces_layer("new_mode")
def switch_mode(self, message): ...
```

#### `@removes_layer`

Remove a named layer entirely (all its intents are deregistered):

```python
from ovos_workshop.decorators.layers import removes_layer

@removes_layer("obsolete_mode")
def cleanup_mode(self, message): ...
```

#### `@resets_layers`

Deactivate all layers, returning to the global state:

```python
from ovos_workshop.decorators.layers import resets_layers

@resets_layers()
def reset_all(self, message): ...
```

### Using `IntentLayers` Directly

`self.intent_layers` is an `IntentLayers` instance available on every skill:

```python
# Activate a layer
self.intent_layers.activate_layer("game_mode")

# Deactivate a layer
self.intent_layers.deactivate_layer("game_mode")

# Check if a layer is active
if self.intent_layers.is_active("game_mode"):
    ...

# Activate one layer and deactivate all others
self.intent_layers.replace_layer("new_mode")

# Reset to no active layers
self.intent_layers.reset()
```

### Registering a Layer Programmatically

```python
self.register_intent_layer("my_layer", [
    "my.first.intent",
    "my.second.intent",
    IntentBuilder("AdaptLayerIntent").require("LayerKeyword"),
])
```

This registers the intents without activating the layer. Call `activate_layer` to enable them.

---

## Permissions

**Module:** `ovos_workshop.permissions`

Permission enums control how the converse and fallback systems select which skills may participate.

### ConverseMode

Controls which skills are allowed to participate in converse at all.

```python
from ovos_workshop.permissions import ConverseMode
```

| Value | Meaning |
|---|---|
| `ACCEPT_ALL` | Any skill may converse (default) |
| `WHITELIST` | Only explicitly whitelisted skills may converse |
| `BLACKLIST` | All skills except blacklisted ones may converse |

Configure in `mycroft.conf`:

```json
{
  "skills": {
    "converse": {
      "converse_mode": "accept_all",
      "converse_whitelist": ["skill-id-1"],
      "converse_blacklist": ["skill-id-2"]
    }
  }
}
```

### ConverseActivationMode

Controls when a skill is allowed to add itself to the active skills list (enabling converse).

```python
from ovos_workshop.permissions import ConverseActivationMode
```

| Value | Meaning |
|---|---|
| `ACCEPT_ALL` | Any skill may activate itself (default) |
| `PRIORITY` | Skill may only activate if no higher-priority skill is already active |
| `WHITELIST` | Only explicitly whitelisted skills may self-activate |
| `BLACKLIST` | All skills except blacklisted ones may self-activate |

Configure in `mycroft.conf`:

```json
{
  "skills": {
    "converse": {
      "converse_activation": "accept_all",
      "converse_activation_whitelist": [],
      "converse_activation_blacklist": []
    }
  }
}
```

### FallbackMode

Controls which skills may register as fallback handlers.

```python
from ovos_workshop.permissions import FallbackMode
```

| Value | Meaning |
|---|---|
| `ACCEPT_ALL` | Any `FallbackSkill` may handle utterances (default) |
| `WHITELIST` | Only explicitly whitelisted fallback skills may respond |
| `BLACKLIST` | All fallback skills except blacklisted ones may respond |

Configure in `mycroft.conf`:

```json
{
  "skills": {
    "fallbacks": {
      "fallback_mode": "accept_all",
      "fallback_whitelist": [],
      "fallback_blacklist": []
    }
  }
}
```

### Utility Functions

```python
from ovos_workshop.permissions import blacklist_skill, whitelist_skill

# Add a skill to the global blacklist in mycroft.conf
blacklist_skill("my-unwanted-skill-id")

# Remove from the blacklist
whitelist_skill("my-unwanted-skill-id")
```

These functions directly modify `mycroft.conf` and take effect on the next skill manager reload.

---

## Related Pages

- [Converse Pipeline](converse_pipeline.md) — `ConverseService`, active skills list, converse protocol
- [Fallback Pipeline](fallback_pipeline.md) — `FallbackService`, priority ranges, fallback protocol
- [Skill Classes](412-skill-classes.md) — `ConversationalSkill`, `FallbackSkill` base classes
- [ovos-core](102-core.md) — skill manager configuration and pipeline stages

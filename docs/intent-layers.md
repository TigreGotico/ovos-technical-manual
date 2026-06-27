# Intent Layers and Permissions

!!! abstract "In a nutshell"
    An "intent" is a thing a user can ask the assistant to do. "Intent layers" let a skill switch groups of these on and off depending on what's happening — for example, only listening for "north," "south," "attack" while a game is actually being played, then turning them off again. It's like having different sets of buttons appear only when they make sense. The second half of this page covers "permissions" — rules for which skills are even allowed to join in. For more on intents see [Intents](intents.md); for term definitions see the [Glossary](glossary.md).

!!! info "📐 Formal specification"
    Intent layers are a thin convenience over **intent context**: each layer is a session context token that gates its intents. The underlying mechanism is specified by **[OVOS-CONTEXT-1 — Intent Context](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-context.md)** — see [Context](context.md) and the [spec index](architecture-specs.md).

---

## Intent Layers

Intent layers let a skill enable or disable groups of intents at runtime. This is useful for building modal interactions where different commands are valid in different states.

**Module:** `ovos_workshop.decorators.layers` / `ovos_workshop.skills.layers`

### Concept

A skill can define multiple named "layers", each containing a set of intents. Only the intents belonging to the currently active layer(s) are matchable at any time. The skill starts with no layers active — the global (non-layered) intents are always active.

!!! abstract "How it works — per-session, via intent context"
    A layer does **not** globally detach and re-attach intents. Each layer maps to a synthetic [intent-context](context.md) token (`layer_<name>`), and every intent in the layer additionally **requires** that context ([OVOS-CONTEXT-1](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-context.md)). Activating a layer sets the context on the session (`set_context`); deactivating removes it (`remove_context`). The intents stay registered for the skill's lifetime — only their *required context* comes and goes, which keeps the intent service stable (no detach/attach churn). Because the gate lives in the **session**, layer state is **per-session and concurrency-safe**: two callers (for example two [HiveMind](https://jarbashivemind.github.io/HiveMind-community-docs/) satellites) can be in different layers at the same time. The decorator and `IntentLayers` API below is unchanged — this is an implementation refactor introduced in **ovos-workshop 9.0.0**.

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

    @layer_intent("guess.intent", layer_name="game_mode")
    def handle_guess(self, message):
        guess = message.data.get("number")
        self.speak(f"You guessed {guess}")

    @layer_intent("quit.intent", layer_name="game_mode")
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

# Replace a layer's intent list (creates it if missing)
self.intent_layers.replace_layer("new_mode", ["my.intent"])

# Disable all layers (back to no active layers)
self.intent_layers.disable()

```

### Registering a Layer Programmatically

```python
self.intent_layers.update_layer("my_layer", [
    "my.first.intent",
    "my.second.intent",
    IntentBuilder("AdaptLayerIntent").require("LayerKeyword"),
])

```

`update_layer` adds the intents to the named layer (creating it if needed) **without**
activating it — call `self.intent_layers.activate_layer("my_layer")` to enable them. Use
`replace_layer(layer_name, intent_list)` instead to overwrite a layer's intents.

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
| `PRIORITY` | [Skill](skill-design-guidelines.md) may only activate if no higher-priority skill is already active |
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

- [Converse Pipeline](converse-pipeline.md) — `ConverseService`, active skills list, converse protocol


- [Fallback Pipeline](fallback-pipeline.md) — `FallbackService`, priority ranges, fallback protocol


- [Skill Classes](skill-classes.md) — `ConversationalSkill`, `FallbackSkill` base classes


- [ovos-core](core.md) — skill manager configuration and pipeline stages

---

*Source code: [OpenVoiceOS/ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop).*

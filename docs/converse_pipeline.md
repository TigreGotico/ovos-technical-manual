# Converse Pipeline

The **Converse Pipeline** in **OpenVoiceOS (OVOS)** manages active conversational contexts between the assistant and skills. It allows skills to keep handling user input across multiple turns, enabling more natural, stateful conversations.

---

## Purpose

The **Converse pipeline** enables **multi-turn conversations** by prioritizing which skills are given the opportunity to handle an utterance through their `converse()` method before normal intent parsing occurs.

Key purposes include:

* **Preserve conversational context** across multiple turns.
* **Prioritize recently used skills** for more natural interactions.
* **Enable stateful behavior**, such as follow-up questions or corrections.
* **Prevent unnecessary intent parsing** when a skill is already engaged.
* **Support skill-defined session control** via manual activation/deactivation.

---

## Implementation

**Module:** `ovos_core.intent_services.converse_service.ConverseService`
**Pipeline plugin ID:** `ovos-converse-pipeline-plugin`
**Stage name:** `converse`

`ConverseService` is shipped inside `ovos-core` and registered via its own `pyproject.toml` entry point.

---

## Active Skill List

A skill is considered active if it has been called in the last 5 minutes (configurable via `timeout`).

Skills are called in order of when they were last active. For example, if a user spoke the following commands:

> Hey Mycroft, set a timer for 10 minutes
>
> Hey Mycroft, what's the weather

Then the utterance "what's the weather" would first be sent to the Timer Skill's `converse()` method, then to the intent service for normal handling where the Weather Skill would be called.

As the Weather Skill was called it has now been added to the front of the Active Skills List. Hence, the next utterance received will be directed to:

1. `WeatherSkill.converse()`
2. `TimerSkill.converse()`
3. Normal intent parsing service

### When does a skill become active?

1. **Before** an intent is called the skill is **activated**
2. If a fallback **returns True** (to consume the utterance) the skill is **activated** right **after** the fallback
3. If converse **returns True** (to consume the utterance) the skill is **reactivated** right **after** converse
4. A skill can activate/deactivate itself at any time via `self.make_active()` / `self.deactivate()`

Active skills are tracked in `Session.active_skills` — `ovos_bus_client.session.Session`. The converse service reads and updates this list via `sess.activate_skill()` / `sess.deactivate_skill()`.

---

## Pipeline Stages

| Pipeline ID | Description | Recommended Use |
|---|---|---|
| `converse` | Continuous dialog for skills | Should always be present; do not remove unless you know what you are doing |

---

## How It Works

1. `converse` stage is hit in the pipeline
2. `ConverseService.match()` iterates active skills in priority order
3. For each skill, emits `{skill_id}.converse.request` and waits for a response
4. If the skill returns `True`, the utterance is consumed
5. If not, the next active skill is tried
6. If no active skill accepts the input, the pipeline falls back to normal intent matching

---

## Skill Integration

Skills integrate with the converse pipeline by:

* Implementing a `converse()` method that checks if the skill wants to handle an utterance.
* Returning `True` if the utterance was handled, `False` otherwise.
* Managing internal state to determine when to exit conversation mode.

```python
from ovos_workshop.skills.converse import ConversationalSkill

class MySkill(ConversationalSkill):
    def converse(self, message):
        utterance = message.data["utterances"][0]
        if "help" in utterance:
            self.speak("Here to help!")
            return True   # consumed
        return False      # pass to next handler
```

This enables modular, stateful conversations without hardcoding turn-taking logic into the core assistant.

---

## Configuration

Customize the pipeline via `mycroft.conf` under `skills.converse`:

```json
{
  "skills": {
    "converse": {
      "timeout": 300,
      "skill_timeouts": {},
      "converse_mode": "accept_all",
      "converse_whitelist": [],
      "converse_blacklist": [],
      "converse_activation": "accept_all",
      "max_activations": -1,
      "skill_activations": {},
      "cross_activation": true,
      "cross_deactivation": true,
      "converse_priorities": {},
      "max_skill_runtime": 10
    }
  }
}
```

**Key Options**

| Config Key | Description |
|---|---|
| `timeout` | Default seconds before an idle skill is removed from converse mode (default 300) |
| `skill_timeouts` | Per-skill override of `timeout` |
| `converse_mode` | Global mode for allowing/disallowing skills from converse participation |
| `converse_blacklist` | Skills not allowed to enter converse mode |
| `converse_whitelist` | Skills explicitly allowed to converse |
| `converse_activation` | Controls when a skill can self-activate |
| `max_activations` | Default number of consecutive times a skill can activate itself per minute (`-1` = unlimited) |
| `skill_activations` | Per-skill override of `max_activations` |
| `cross_activation` | If `true`, any skill can activate any other skill |
| `cross_deactivation` | If `true`, any skill can deactivate any other skill |
| `max_skill_runtime` | Maximum seconds to wait for a skill's `converse()` response |

---

## Converse Modes

| Mode | Description |
|---|---|
| `accept_all` | All skills are allowed to use converse mode (default) |
| `whitelist` | Only skills explicitly listed in `converse_whitelist` can use converse mode |
| `blacklist` | All skills can use converse mode except those in `converse_blacklist` |

## Converse Activation Modes

| Mode | Description |
|---|---|
| `accept_all` | Any skill can activate itself unconditionally (default) |
| `priority` | Skills can only activate themselves if no skill with higher priority is active |
| `whitelist` | Only skills in `converse_whitelist` can activate themselves |
| `blacklist` | Only skills NOT in `converse_blacklist` can activate themselves |

> Note: `converse_activation` does not apply to regular skill activation, only to skill-initiated activation requests (e.g. `self.make_active()`).

---

## Bus Events Handled

| Event | Handler |
|---|---|
| `intent.service.skills.activate` | `handle_activate_skill_request` |
| `intent.service.skills.deactivate` | `handle_deactivate_skill_request` |
| `intent.service.active_skills.get` | `handle_get_active_skills` |
| `skill.converse.get_response.enable` | `handle_get_response_enable` |
| `skill.converse.get_response.disable` | `handle_get_response_disable` |
| `converse:skill` | `handle_converse` |

### `get_response` Support

During `skill.get_response`, the skill temporarily holds the converse channel:
- `skill.converse.get_response.enable` → lock converse to this skill
- `skill.converse.get_response.disable` → release lock

---

## Security & Performance

A malicious or badly designed skill using the converse method can potentially hijack the whole conversation loop and render the skills service unusable.

Protections include:

* Timeouts for inactivity (`timeout`) and maximum runtime (`max_skill_runtime`).
* `max_activations` limits per skill.
* Blacklist/whitelist enforcement to restrict which skills can enter converse mode.
* `cross_activation` can be disabled to prevent skill-to-skill manipulation.

---

## Notes

* The plugin **does not enforce a fallback behavior** if no skill accepts the input.
* If no skill handles the utterance via converse, the pipeline falls back to normal intent matching or fallback skills.
* This mechanism is ideal for multi-turn conversations like dialogs, games, or assistant flows that require memory of previous input.
* Converse priority is under active development; priority is currently assumed to be 50. Per-skill overrides are available via `converse_priorities` in config.

---

## Related Pages

- [ovos-core](102-core.md) — `ConverseService` implementation and bus events
- [Fallback Pipeline](fallback_pipeline.md) — what runs when converse returns nothing
- [Skill Classes](412-skill-classes.md) — `ConversationalSkill`, `ActiveSkill` base classes
- [Bus Session](901-bus-session.md) — `Session.active_skills`, `activate_skill()`, `deactivate_skill()`

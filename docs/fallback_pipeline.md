# Fallback Pipeline

The **Fallback Pipeline** in **OpenVoiceOS (OVOS)** manages how fallback skills are queried when no primary skill handles a user's utterance. It coordinates multiple fallback handlers, ensuring the system gracefully attempts to respond even when regular intent matching fails.

---

## Implementation

**Module:** `ovos_core.intent_services.fallback_service.FallbackService`
**Pipeline plugin ID:** `ovos-fallback-pipeline-plugin`
**Stage names:** `fallback_high`, `fallback_medium`, `fallback_low`

`FallbackService` is shipped inside `ovos-core` and registered via its own `pyproject.toml` entry point.

---

## Pipeline Stages

| Pipeline ID | Priority Range | Description | Use Case |
|---|---|---|---|
| `fallback_high` | 0–49 | High-priority fallback skills | Critical fallback handlers |
| `fallback_medium` | 50–89 | Medium-priority fallback skills | General fallback skills |
| `fallback_low` | 90–100+ | Low-priority fallback skills | Catch-all or chatbot fallback skills |

Fallback skills register with a priority, allowing the pipeline to query them in order. Priority can be overridden by users via config.

---

## How It Works

1. A fallback stage is hit in the pipeline (after all other matchers fail)
2. `FallbackService.match_high/medium/low()` filters registered fallbacks by priority range
3. For each fallback skill (sorted by priority), emits a converse-style request
4. First skill that returns `True` wins — the utterance is consumed
5. If no fallback skill accepts the utterance, no fallback response is generated

---

## Skill Integration

Skills integrate as fallbacks by:

* Inheriting from `FallbackSkill` and implementing `can_answer()` and a `@fallback_handler`
* Registering on the message bus with a fallback priority via `ovos.skills.fallback.register`
* Listening for fallback queries carrying all utterance variations
* Responding with success/failure on whether they handled the fallback

```python
from ovos_workshop.skills.fallback import FallbackSkill
from ovos_workshop.decorators import fallback_handler

class MyFallback(FallbackSkill):
    def can_answer(self, utterances, lang) -> bool:
        return True   # always willing to try

    @fallback_handler(priority=50)
    def handle_fallback(self, message):
        self.speak("I don't know, but I tried.")
        return True   # consumed
```

This enables modular and customizable fallback behavior depending on your skill ecosystem.

---

## Configuration

```json
{
  "skills": {
    "fallbacks": {
      "fallback_priorities": {
        "my-skill-id": 10
      },
      "fallback_mode": "accept_all",
      "fallback_whitelist": [],
      "fallback_blacklist": []
    }
  }
}
```

| Config Key | Description |
|---|---|
| `fallback_priorities` | Override developer-defined priorities per skill ID |
| `fallback_mode` | `"accept_all"`, `"whitelist"`, or `"blacklist"` |
| `fallback_whitelist` | Skills allowed to act as fallbacks (when mode is `whitelist`) |
| `fallback_blacklist` | Skills blocked from fallback (when mode is `blacklist`) |

### FallbackMode

| Mode | Description |
|---|---|
| `accept_all` | Default — any registered skill can act as fallback |
| `whitelist` | Only skills in `fallback_whitelist` can act as fallback |
| `blacklist` | All skills can act as fallback except those in `fallback_blacklist` |

---

## Bus Events Handled

| Event | Handler |
|---|---|
| `ovos.skills.fallback.register` | `handle_register_fallback` |
| `ovos.skills.fallback.deregister` | `handle_deregister_fallback` |

---

## Notes

* The pipeline itself **does not define or enforce a default fallback response**.
* The default "I don't understand" reply is implemented in the separate `ovos-skill-fallback-unknown` skill.
* This modular design allows developers to create custom fallback strategies or add fallback chatbot skills without modifying the core pipeline.
* Fallback skills are expected to implement some dialog if they consume the utterance.

---

## Security

Just like with converse, a badly designed or malicious skill can hijack the fallback skill loop. While this is not as serious as with converse, protections are provided:

* You can configure what skills are allowed to use the fallback mechanism via `fallback_mode`.
* `fallback_priorities` allows users to adjust priorities when the default values don't work well with the installed skill collection.

---

## Related Pages

- [ovos-core](102-core.md) — `FallbackService` implementation and bus events
- [Converse Pipeline](converse_pipeline.md) — what runs before fallback
- [Skill Classes](412-skill-classes.md) — `FallbackSkill` base class

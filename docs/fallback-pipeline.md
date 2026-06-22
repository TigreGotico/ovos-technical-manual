# Fallback Pipeline

!!! abstract "In a nutshell"
    When you say something and none of your assistant's regular skills know how to respond, the fallback pipeline is the safety net that tries one last set of "catch-all" skills so the assistant still says something instead of going silent. Think of it as the help desk that gets your question only after everyone else has passed on it. It asks these backup skills in a set order until one of them handles the request. See the [Converse Pipeline](converse-pipeline.md) for what runs before this, or the [Glossary](glossary.md) for terms.

The **Fallback Pipeline** in **OpenVoiceOS (OVOS)** manages how fallback skills are queried when no primary skill handles a user's utterance. It coordinates multiple fallback handlers, ensuring the system gracefully attempts to respond even when regular intent matching fails.

---

## Implementation

**Module:** `ovos_core.intent_services.fallback_service.FallbackService`
**Pipeline plugin ID:** `ovos-fallback-pipeline-plugin`
**Stage names:** `fallback_high`, `fallback_medium`, `fallback_low`

`FallbackService` subclasses `ConfidenceMatcherPipeline`, so the single base ID auto-expands into the three `match_high`/`match_medium`/`match_low` matchers exposed as `fallback_high`, `fallback_medium`, `fallback_low`. It ships inside `ovos-core`:

```ini
[project.entry-points."opm.pipeline"]
ovos-fallback-pipeline-plugin = "ovos_core.intent_services.fallback_service:FallbackService"
```

---

## Pipeline Stages

| Pipeline ID | Priority Range | Description | Use Case |
|---|---|---|---|
| `fallback_high` | `0 < p ≤ 5` | High-priority fallback skills | Critical fallback handlers |
| `fallback_medium` | `5 < p ≤ 90` | Medium-priority fallback skills | General fallback skills |
| `fallback_low` | `90 < p ≤ 101` | Low-priority fallback skills | Catch-all or chatbot fallback skills |

Each matcher filters registered fallbacks with `range.start < priority ≤ range.stop` (exclusive start, inclusive stop). Lower priority numbers run first. A fallback that registers without a priority defaults to `101`, placing it in the `fallback_low` tier. Priorities can be overridden by users via config.

---

## How It Works

1. A fallback stage is hit in the pipeline (after all other matchers fail)


2. `FallbackService.match_high/medium/low()` filters registered fallbacks to the stage's priority range


3. It pings candidates via `ovos.skills.fallback.ping` (carrying the priority `range`) and collects `ovos.skills.fallback.pong` acknowledgements (`can_handle`) within ~0.5s


4. Candidates are sorted by priority ascending; the winning match dispatches to that skill via `ovos.skills.fallback.{skill_id}.request`


5. First skill that handles the utterance wins — it is consumed


6. If no fallback skill accepts the utterance, no fallback response is generated

---

## Skill Integration

Skills integrate as fallbacks by:

* Inheriting from `FallbackSkill` and decorating one or more handlers with `@fallback_handler(priority=...)` (lower number = higher priority; default `50`)


* Optionally overriding `can_answer(self, message)` to declare upfront whether the skill is willing to try (utterances are in `message.data["utterances"]`)


* On startup `ovos-workshop` registers the skill's lowest handler priority with the service via `ovos.skills.fallback.register`


* Returning `True` from a handler when it consumes the utterance, `False` to pass to the next fallback

```python
from ovos_workshop.skills.fallback import FallbackSkill
from ovos_workshop.decorators import fallback_handler

class MyFallback(FallbackSkill):
    def can_answer(self, message) -> bool:
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

- [ovos-core](core.md) — `FallbackService` implementation and bus events


- [Converse Pipeline](converse-pipeline.md) — what runs before fallback


- [Skill Classes](skill-classes.md) — `FallbackSkill` base class

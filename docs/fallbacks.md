# Fallback [Skill](skill-design-guidelines.md)

!!! abstract "In a nutshell"
    A fallback skill is a catch-all that only gets a turn when no regular skill understood what you said. It is where you put things like "sorry, I didn't catch that", a web search, or a large language model that should answer only when nothing more specific did. Each fallback has a priority number so you can decide which ones try first, with broad "I don't understand" handlers going last. To see how this fits into the bigger picture, read the [Fallback Pipeline](fallback-pipeline.md), or the [Glossary](glossary.md) for terms.

??? info "📐 Formal specification"
    Fallback handling is specified by **[OVOS-FALLBACK-1 — Fallback Pipeline Plugin](https://github.com/OpenVoiceOS/architecture/blob/dev/fallback.md)** (a formal [architecture spec](architecture-specs.md)). A skill declares itself a fallback handler by calling `register_fallback()`, which emits `ovos.skills.fallback.register` with a `skill_id` and integer `priority`; the fallback **pipeline plugin** builds a pool ordered by **ascending** priority (**lower number runs earlier** — matching this page), then pings each candidate with `ovos.skills.fallback.ping` and reads its `can_answer()` verdict off the `ovos.skills.fallback.pong` reply, dispatching in priority order to the first willing skill via `ovos.skills.fallback.<skill_id>.request`. A catch-all skill is typically registered at a high number (e.g. `100`) so every utterance gets a response; the recommended bands are `0–49` for skills that must run **early** (very specific handlers), `50–74` for skills that run in the **middle**, and `75–100` for skills that must run **late** (broad catch-alls). Note this is the opposite of what "priority" usually implies elsewhere: a *lower* number here means the handler is tried *sooner*, not that it is more important.

A **Fallback** skill is the last line of defense: it is only consulted when no intent matched the utterance. This is where you put a catch-all ("I didn't understand"), an LLM, a web search, or any handler that should run *only* when nothing more specific did.

## Order of precedence

Fallback Skills each have a **priority** and are tried in order from low priority value to high priority value (lower number = tried earlier). When a Fallback Skill handles the **[Utterance](life-of-an-utterance.md)** it returns `True` and no further fallbacks are tried.

Pick your priority number by how broad your handler is — remember, a smaller number runs **earlier**, a larger number runs **later**:

- Very specific handlers should use a **small number** (e.g. 20-50) so they run before broad ones and get first refusal.
- Broad, catch-all handlers (an LLM, "I don't understand") should use a **large number** (80-100) so specific skills run and win first.

---

## Fallback Handlers

Import the `FallbackSkill` base class, derive from it, and register a handler with the fallback system.

The handler decides whether it can handle the **Utterance**, speaks if it can, and returns `True` if it handled it or `False` if not.

```python
from ovos_workshop.skills.fallback import FallbackSkill


class MeaningFallback(FallbackSkill):
    """
    A Fallback skill to answer the question about the
    meaning of life, the universe and everything.
    """

    def initialize(self):
        # register the handler with priority 10
        self.register_fallback(self.handle_fallback, 10)

    def handle_fallback(self, message):
        utterance = message.data.get("utterances", [""])[0]
        if ("what" in utterance and "meaning" in utterance and
                ("life" in utterance or "universe" in utterance
                 or "everything" in utterance)):
            self.speak("42")
            return True
        return False
```

> **NOTE**: a `FallbackSkill` can register any number of fallback handlers.

The above example can be found [here](https://github.com/forslund/fallback-meaning).

---

## Decorators

Alternatively, use the `@fallback_handler` decorator — no manual `register_fallback` call needed.

```python
from ovos_workshop.skills.fallback import FallbackSkill
from ovos_workshop.decorators import fallback_handler


class MeaningFallback(FallbackSkill):

    @fallback_handler(priority=10)
    def handle_fallback(self, message):
        utterance = message.data.get("utterances", [""])[0]
        if ("what" in utterance and "meaning" in utterance and
                ("life" in utterance or "universe" in utterance
                 or "everything" in utterance)):
            self.speak("42")
            return True
        return False
```

`fallback_handler` can also be imported from `ovos_workshop.decorators.fallback_handler`.

---

## `can_answer`

Fallback skills can report *whether* they would answer a question, without actually executing the action or speaking. This lets other OVOS components probe how an utterance will be handled with no side effects, and can skip work in the fallback pipeline.

This method is **not implemented by default** — the base implementation raises `NotImplementedError`. Since the skills service pings every fallback skill (`ovos.skills.fallback.ping` → `can_answer()`) to decide whether it is even worth invoking, you should always override `can_answer` in a real `FallbackSkill`:

```python
from ovos_bus_client.session import SessionManager


class MeaningFallback(FallbackSkill):

    def can_answer(self, message) -> bool:
        """
        Return True if this skill could answer the utterance as a fallback.

        - Utterance transcriptions: message.data["utterances"]
        - Session (e.g. for language): SessionManager.get(message)
        """
        utterances = message.data.get("utterances", [])
        return any("meaning" in u for u in utterances)
```

> The `can_answer` signature takes the full `Message` (transcriptions are in `message.data["utterances"]`), not a bare list of strings.

---

*Source code: [OpenVoiceOS/ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop).*

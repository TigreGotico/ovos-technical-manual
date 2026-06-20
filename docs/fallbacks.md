# Fallback [Skill](skill-design-guidelines.md)

A **Fallback** skill is the last line of defense: it is only consulted when no intent matched the utterance. This is where you put a catch-all ("I didn't understand"), an LLM, a web search, or any handler that should run *only* when nothing more specific did.

## Order of precedence

Fallback Skills each have a **priority** and are tried in order from low priority value to high priority value (lower number = tried earlier). When a Fallback Skill handles the **[Utterance](life-of-an-utterance.md)** it returns `True` and no further fallbacks are tried.

Pick your priority by how broad your handler is:

- Very specific handlers should use a **low** value (e.g. 20-50) so they get a chance before broad ones.
- Broad, catch-all handlers (an LLM, "I don't understand") should use a **high** value (80-100) so specific skills win first.

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
        utterance = message.data.get("utterance", "")
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
        utterance = message.data.get("utterance", "")
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

This method is **not implemented by default** — override it in your skill if you want this behavior:

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

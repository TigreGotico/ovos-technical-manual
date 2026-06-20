# Common Query Framework

> Specification: [OVOS-INTENT-3](https://github.com/OpenVoiceOS/architecture/blob/dev/ovos-intent-3.md) (Intent Definition)

The Common Query Framework handles the common use case of "general information" or question answering. Many Skills may implement handlers for "what is X" or "when did Y"; the Common Query Framework queries all of them and selects a single "best" answer to speak. This is similar to the [OCP](ocp-skills.md) framework that handles the common use of "playing" music or other media.

**What / why (beginners):** if your skill can answer free-form questions ("how old is X", "what is Y"), you do *not* register `.intent` files for every phrasing. Instead you mark one method with the `@common_query` decorator. The Common Query pipeline detects question-shaped utterances, asks every common-query skill in parallel, and only the winner gets to speak. You return an answer plus a confidence score and the framework does the arbitration.

## The `@common_query` decorator

A common-query handler is a regular method on an `OVOSSkill` decorated with `@common_query`. It receives the question phrase and the language, and returns a `(answer, confidence)` tuple — or `None` if it cannot answer.

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import common_query


class MyQuestionSkill(OVOSSkill):

    @common_query()
    def handle_query(self, phrase: str, lang: str):
        # return None if you can't answer
        # otherwise return (answer_string, confidence)  where 0.0 <= confidence <= 1.0
        return "the answer", 0.8
```

The handler contract:

- **Input:** `phrase` (the question string) and `lang` (a BCP-47 code).
- **Output:** a `(answer: str, confidence: float)` tuple, or `None`.
- **Confidence** is a float between `0.0` and `1.0`. The pipeline ignores answers with confidence below `0.5`. The highest-confidence answer across all skills is the one spoken to the user.

> The classic `CommonQuerySkill` / `UniversalCommonQuerySkill` base classes and the `CQS_match_query_phrase()` / `CQSMatchLevel` API have been **removed**. Use the `@common_query` decorator on a plain `OVOSSkill` instead. The pipeline still selects a single best answer the same way; only the skill-side API changed.

## An Example

Let's make a simple Skill that tells us the age of the various Monty Python members.

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import common_query

# Dict mapping python members to their age and whether they're alive or dead
PYTHONS = {
    'eric idle': (77, 'alive'),
    'michael palin': (77, 'alive'),
    'john cleese': (80, 'alive'),
    'graham chapman': (48, 'dead'),
    'terry gilliam': (79, 'alive'),
    'terry jones': (77, 'dead')
}


def python_in_utt(utterance):
    """Find a monty python member in the utterance, or return None."""
    for key in PYTHONS:
        if key in utterance.lower():
            return key
    return None


class PythonAgeSkill(OVOSSkill):
    """A Skill for checking the age of the python crew."""

    def format_answer(self, python):
        """Create the answer string for the specified "python" person."""
        age, status = PYTHONS[python]
        key = 'age_alive' if status == 'alive' else 'age_dead'
        return self.dialog_renderer.render(key, {'person': python, 'age': age})

    @common_query()
    def match_age_query(self, phrase, lang):
        # Check if this is an age query and a python is mentioned
        age_query = self.voc_match(phrase, 'age')
        python = python_in_utt(phrase)

        if age_query and python:
            confidence = 1.0 if 'monty python' in phrase.lower() else 0.7
            return self.format_answer(python), confidence
        # can't answer -> return None
        return None
```

`match_age_query()` checks whether this is an age-related question that also names a Monty Python member. If both are true it returns the rendered answer plus a confidence; otherwise it returns `None`, signalling it cannot answer.

This will provide answers to queries such as

> "how old is Graham Chapman"
>
> "what's Eric Idle's age"

There are many toolkits for parsing the question itself — [Adapt](https://pypi.org/project/adapt-parser/), [little questions](https://pypi.org/project/little-questions/), [padaos](https://pypi.org/project/padaos/) and more — but `self.voc_match` against a `.voc` file is usually enough.

## Match Confidence

Confidence is a single float in `[0.0, 1.0]`. Use a higher value when you are more certain you have the *exact* answer the user wants, and a lower value when your skill is a more general fallback for a category of questions. In the example above, an explicit "monty python" mention bumps confidence to `1.0`, making this skill very likely to be chosen.

Only answers with confidence `>= 0.5` are considered. The pipeline collects all qualifying answers and speaks the single highest-confidence one.

## Selection Callback

In some cases the Skill should do additional work *only when its answer was the one selected and spoken* — for example, preparing for follow-up questions or showing an image. Pass a callback to the decorator; it runs after your answer is spoken.

The callback signature is `(phrase, answer, lang)` for a plain function, or `(self, phrase, answer, lang)` for an instance method — the framework inspects the signature and passes `self` only when the first parameter is named `self`.

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import common_query


def on_selected(self, phrase, answer, lang):
    self.log.info(f"I was selected to answer: {phrase}")
    self.gui.show_text(answer)


class PythonAgeSkill(OVOSSkill):

    @common_query(callback=on_selected)
    def match_age_query(self, phrase, lang):
        ...
        return answer, confidence
```

> The selected answer is spoken automatically by the framework; you do **not** call `self.speak()` inside the common-query handler. The callback is purely for side effects (visuals, follow-up state, logging).

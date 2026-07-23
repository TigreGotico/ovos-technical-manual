# Asking the User for Responses in OVOS Skills

!!! abstract "In a nutshell"
    Sometimes a skill needs to ask the user something back — "which flavor?", "are you sure?",
    "pick one of these". This page shows the four built-in ways an OVOS skill does that: an
    open-ended question, a specific question that captures the reply (`get_response`), a yes/no
    question (`ask_yesno`), and a multiple-choice question (`ask_selection`). OVOS keeps the
    microphone open and parses the answer for you. For the *design* side — when to ask versus
    just tell the user — see the [Skill Design Guidelines](skill-design-guidelines.md).

!!! info "📐 Formal specification"
    Asking the user back is the spec's **response mode**, defined by
    **[OVOS-CONVERSE-1 — Active Handlers and Interactive Response](https://github.com/OpenVoiceOS/architecture/blob/dev/converse.md)**.
    When a handler enters response mode (it sets `session.response_mode`), the
    orchestrator suspends normal intent matching and routes the *next*
    utterance straight back to that handler as the awaited reply — the
    interactive-response window. The methods below (`get_response`,
    `ask_yesno`, `ask_selection`) are the skill-API surface over this one
    session-resident mechanism. For the full set see the
    **[spec index](architecture-specs.md)**.

OVOS provides several built-in methods for engaging users in interactive conversations. These include asking open-ended questions, confirming yes/no responses, and offering multiple-choice selections — all handled in a natural, voice-first way.

Here we look at how to implement the most common ways of asking the user for input. For more information on conversation design see
the [Skill Design Guidelines](skill-design-guidelines.md).

---

## Usage Guide

Here's how to ask the user for different kinds of input in your OVOS skills:

### 1. Open-Ended Questions

Let the user respond freely, either to trigger another skill or to handle the response with a custom intent.

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler
import random

class AskMeSkill(OVOSSkill):
    @intent_handler('ask_me_something.intent')
    def handle_set_favorite(self):
        question = random.choice(self.question_list)
        self.speak(question, expect_response=True)

```

> `expect_response=True` keeps the mic open after speaking, so the response can be handled by OVOS's intent pipeline.

---

### 2. Request Extra Information with `get_response()`

Use this to ask a specific question and directly capture the user's reply.

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler

class IceCreamSkill(OVOSSkill):
    @intent_handler('set.favorite.intent')
    def handle_set_favorite(self):
        favorite_flavor = self.get_response('what.is.your.favorite.flavor')
        self.speak_dialog('confirm.favorite.flavor', {'flavor': favorite_flavor})

```

**Optional `get_response()` arguments:**

- `data`: Dictionary to format the dialog file (default `None`)


- `validator`: A function `(str) -> bool` to check if the user response is valid


- `on_fail`: A fallback string — or a `(str) -> str` callable — to say if validation fails


- `num_retries`: How many times to retry if the response isn't valid (default `-1`, retry until valid)

`get_response()` returns the matched utterance as a `str`, or `None` if no valid response
was captured. The first argument is the dialog to speak.

---

### 3. Yes/No Questions with `ask_yesno()`

Detects affirmations or negations from user responses.

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler

class IceCreamSkill(OVOSSkill):
    @intent_handler('do.you.like.intent')
    def handle_do_you_like(self):
        likes_ice_cream = self.ask_yesno('do.you.like.ice.cream')
        if likes_ice_cream == 'yes':
            self.speak_dialog('does.like')
        elif likes_ice_cream == 'no':
            self.speak_dialog('does.not.like')
        else:
            self.speak_dialog('could.not.understand')

```

**Behavior:**

- Returns `"yes"` or `"no"` for matching phrases.


- Returns the full utterance if unclear.


- Returns `None` if no valid response is detected.

> Yes/No detection is a pluggable OPM agent plugin (group `opm.agents.yesno`). The
> default is [ovos-yes-no-plugin](https://github.com/OpenVoiceOS/ovos-YesNo-plugin), a
> heuristic engine that understands complex affirmations and denials — even double
> negations. Override it per skill via the `ask_yesno_plugin` setting.

Example mappings:

| User Says                        | Detected As |
|----------------------------------|--------------|
| "yes"                            | yes          |
| "no"                             | no           |
| "don't think so"                 | no           |
| "that's affirmative"             | yes          |
| "no, but actually, yes"          | yes          |
| "yes, but actually, no"          | no           |
| "yes, yes, yes, but actually, no" | "no"            |
| "please"                          | "yes"           |
| "please don't"                    | "no"            |
| "no! please! I beg you"           | "no"            |
| "yes, i don't want it for sure"   | "no"            |
| "please! I beg you"               | "yes"           |
| "i want it for sure"              | "yes"           |
| "obviously"                       | "yes"           |
| "indeed"                          | "yes"           |
| "no, I obviously hate it"         | "no"            |
| "that's certainly undesirable"    | "no"            |
| "yes, it's a lie"                 | "yes"           |
| "no, it's a lie"                  | "no"            |
| "he is lying"                     | "no"            |
| "correct, he is lying"            | "yes"           |
| "it's a lie"                      | "no"            |
| "you are mistaken"                | "no"            |
| "that's a mistake"                | "no"            |
| "wrong answer"                    | "no"            |
| "it's not a lie"                  | "yes"           |
| "he is not lying"                 | "yes"           |
| "you are not mistaken"            | "yes"           |
| "tou are not wrong"               | "yes"           |
| "beans"                           | None            |

---

### 4. Multiple-Choice Questions with `ask_selection()`

Let users choose from a list of options, by name or number.

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler

class IceCreamSkill(OVOSSkill):
    def initialize(self):
        self.flavors = ['vanilla', 'chocolate', 'mint']

    @intent_handler('request.icecream.intent')
    def handle_request_icecream(self):
        self.speak_dialog('welcome')
        selection = self.ask_selection(self.flavors, 'what.flavor')
        self.speak_dialog('coming.right_up', {'flavor': selection})

```

**Optional arguments:**

- `min_conf` (float): Minimum confidence threshold for fuzzy matching (default `0.65`)


- `numeric` (bool): If `True`, speak the list with numbered options (default `False`)


- `num_retries` (int): How many times to re-ask on no match (default `-1`)

Returns the selected list element, or `None` if nothing matched. User responses like
"chocolate", "the second one", or "option three" are all supported.

---

## Technical Notes

- All methods handle microphone activation and parsing behind the scenes.


- OVOS automatically integrates with the intent engine to resolve follow-up responses.


- These interactions are designed to support natural dialogue flows, validating and re-asking as needed.

---

## Tips

- Always confirm user input when using `get_response()` or `ask_selection()` for clarity.


- Use `validator` with `get_response()` to catch unclear or unwanted input.


- Use `ask_yesno()` for quick binary decisions, but gracefully handle unexpected answers.


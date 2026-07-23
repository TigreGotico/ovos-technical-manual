# Follow up questions

!!! abstract "In a nutshell"
    Normally each thing you say to your assistant is treated on its own, with no memory of the last sentence. Conversational context is the short-term memory that lets you ask a follow-up like "where's *he* from?" right after "how tall is John Cleese?" — the assistant remembers you were talking about Cleese and fills in the blank. Skill authors mark which details to remember, and that memory is kept separate for each ongoing conversation so different people or devices don't get mixed up. See [Skill design guidelines](skill-design-guidelines.md) or the [Glossary](glossary.md).

!!! info "📐 Formal specification"
    Intent context is specified by **[OVOS-CONTEXT-1 — Intent Context](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-context.md)**, the *declarative* gating primitive over **[OVOS-PIPELINE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)** (its imperative complement is the converse plugin, **[OVOS-CONVERSE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/converse.md)**, see [Converse Pipeline](converse-pipeline.md)). See the [spec index](architecture-specs.md).

Conversational context in Open Voice OS (OVOS) allows voice interactions to feel more natural by remembering parts of a conversation, like the subject being discussed. This is especially useful for follow-up questions where repeating context (like a person's name) would otherwise be necessary.

!!! note "The spec model: a decaying per-session store that *gates* matching"
    In CONTEXT-1 terms, intent context is the field **`session.intent_context`** — a flat map of **entries**, each `{value, expires_at?, turns_remaining?}`. Every entry **decays**: the orchestrator prunes dead entries before each match round and decrements `turns_remaining` after it (CONTEXT-1 §4), so a confirmation flag set with `turns_remaining: 1` lives for exactly the next utterance. An intent **gates** on context by declaring **`requires_context`** (match only while a key is live) and/or **`excludes_context`** (match only while a key is absent) — these are normative across *every* intent engine (CONTEXT-1 §6/§6.1). Keys are **scoped by shape**: a bare key like `person` is **shared** (cross-skill); a prefixed key `<skill_id>:flag` is **private** to that owner. Bare-string `requires_context` entries default to *private* scope — the safe default — so a foreign skill's shared `person` can never accidentally satisfy a private gate (you must write `{key: person, scope: shared}` to read across skills).

!!! warning "Four different things called 'context' — do not conflate them"
    CONTEXT-1 §1.1 is explicit that the word *context* names four unrelated things:

    | Name | What it is | JSON path |
    |---|---|---|
    | `Message.context` | the bus-envelope metadata on every Message (routing keys, the `session` carrier) | `context` |
    | `session.intent_context` | the field *inside* the session that holds context entries | `context.session.intent_context` |
    | **intent context** (the term) | the decaying key/value state itself — the entries in that field | (entries of the above) |
    | `Match.slots` | the slot map produced *at match time* for one dispatch | `data.slots` |

    This page is about the third (and the field that holds it). It is *not* `Message.context`, and a context entry is *not* a `Match.slot` — though CONTEXT-1 §7's context-supplied-slot rule is the bridge: when a `requires_context` key also names a slot, its value fills that slot if the utterance did not (this is exactly the "remember which person" mechanism below).

Currently, keyword-based conversational context is only consumed by the
[Adapt](adapt-pipeline.md) pipeline, not [Padatious](padatious-pipeline.md).

Context lives on the per-conversation [Session](session.md) (`Session.context`, an
`IntentContextManager` from `ovos_bus_client.session`). It is **session-scoped** —
not a single global store — so concurrent users/devices keep separate context.

---

## Keyword Contexts

> How tall is John Cleese?

`"John Cleese is 196 centimeters"`

> Where's he from?

`"He's from England"`

Context is added manually by the **[Skill](skill-design-guidelines.md)** creator using either the `self.set_context()` method or the `@adds_context()` decorator.

Consider the following intent handlers:

```python
    @intent_handler(IntentBuilder().require('PythonPerson').require('Length'))
    def handle_length(self, message):
        python = message.data.get('PythonPerson')
        self.speak(f'{python} is {length_dict[python]} cm tall')

    @intent_handler(IntentBuilder().require('PythonPerson').require('WhereFrom'))
    def handle_from(self, message):
        python = message.data.get('PythonPerson')
        self.speak(f'{python} is from {from_dict[python]}')

```

To interact with the above handlers the user would need to say

```text
User: How tall is John Cleese?
OVOS: John Cleese is 196 centimeters
User: Where is John Cleese from?
OVOS: He's from England

```

To get a more natural response the functions can be changed to let OVOS know which `PythonPerson` we're talking about by using the `self.set_context()` method to give context:

```python
    @intent_handler(IntentBuilder().require('PythonPerson').require('Length'))
    def handle_length(self, message):
        # PythonPerson can be any of the Monty Python members
        python = message.data.get('PythonPerson')
        self.speak(f'{python} is {length_dict[python]} cm tall')
        self.set_context('PythonPerson', python)

    @intent_handler(IntentBuilder().require('PythonPerson').require('WhereFrom'))
    def handle_from(self, message):
        # PythonPerson can be any of the Monty Python members
        python = message.data.get('PythonPerson')
        self.speak(f'He is from {from_dict[python]}')
        self.set_context('PythonPerson', python)

```

When either of the methods are called the `PythonPerson` keyword is added to OVOS's context, which means that if there is a match with `Length` but `PythonPerson` is missing OVOS will assume the last mention of that keyword. The interaction can now become the one described at the top of the page.

> User: How tall is John Cleese?

OVOS detects the `Length` keyword and the `PythonPerson` keyword

> OVOS: 196 centimeters

John Cleese is added to the current context

> User: Where's he from?

OVOS detects the `WhereFrom` keyword but not any `PythonPerson` keyword. The Context Manager is activated and returns the latest entry of `PythonPerson` which is _John Cleese_

> OVOS: He's from England


## Cross Skill Context

The context is limited by the keywords provided by the **current** Skill. 

There is also `self.set_cross_skill_context` / `self.remove_cross_skill_context`, intended
to share a keyword with **other** Skills as well.

`set_cross_skill_context` emits the `mycroft.skill.set_cross_context` bus
message; every loaded `OVOSSkill` subscribes to it (and to the matching
`mycroft.skill.remove_cross_context`) and re-applies the keyword under its
own namespace, which is how it becomes visible to other skills' context
gates.

```python
    @intent_handler(IntentBuilder().require(PythonPerson).require(WhereFrom))
    def handle_from(self, message):
        # PythonPerson can be any of the Monty Python members
        python = message.data.get('PythonPerson')
        self.speak(f'He is from {from_dict[python]}')
        self.set_context('PythonPerson', python) # context for this skill only
        
        self.set_cross_skill_context('Location', from_dict[python])  # context for ALL skills

```


In this example `Location` keyword is shared with the WeatherSkill

```text
User: Where is John Cleese from?
OVOS: He's from England
User: What's the weather like over there?
OVOS: Raining and 14 degrees...

```

## Hint Keyword contexts

Context do not need to have a value, their presence can be used to simply indicate a previous interaction happened

In this case Context can also be implemented by using decorators instead of calling `self.set_context`

```python
from ovos_workshop.decorators import adds_context, removes_context


class TeaSkill(OVOSSkill):
    @intent_handler(IntentBuilder('TeaIntent').require("TeaKeyword"))
    @adds_context('MilkContext')
    def handle_tea_intent(self, message):
        self.milk = False
        self.speak('Of course, would you like Milk with that?',
                   expect_response=True)

    @intent_handler(IntentBuilder('NoMilkIntent').require("NoKeyword").
                                  require('MilkContext').build())
    @removes_context('MilkContext')
    @adds_context('HoneyContext')
    def handle_no_milk_intent(self, message):
        self.speak('all right, any Honey?', expect_response=True)

```


> **NOTE**: cross skill context is not yet exposed via decorators


## Using context to enable **Intents**

To make sure certain **Intents** can't be triggered unless some previous stage in a conversation has occurred. Context can be used to create "bubbles" of available intent handlers.

> This is the **`requires_context`** gate of CONTEXT-1 §6 in action: `MilkContext` is a private flag (the `@adds_context` decorator stores it under the skill's own prefix), and an intent that `.require('MilkContext')` declares it as a precondition — so the `yes`/`no` intents are *invisible except in the narrow window* between the question and the reply, with no skill-side state machine. The complementary `excludes_context` gate (CONTEXT-1 §6.1) handles fire-once intents (e.g. "greet only once per session").

```text
User: Hey Mycroft, bring me some Tea
OVOS: Of course, would you like Milk with that?
User: No
OVOS: How about some Honey?
User: All right then
OVOS: Here you go, here's your Tea with Honey

```

```python
from ovos_workshop.decorators import adds_context, removes_context

class TeaSkill(OVOSSkill):
    @intent_handler(IntentBuilder('TeaIntent').require("TeaKeyword"))
    @adds_context('MilkContext')
    def handle_tea_intent(self, message):
        self.milk = False
        self.speak('Of course, would you like Milk with that?',
                   expect_response=True)

    @intent_handler(IntentBuilder('NoMilkIntent').require("NoKeyword").
                                  require('MilkContext').build())
    @removes_context('MilkContext')
    @adds_context('HoneyContext')
    def handle_no_milk_intent(self, message):
        self.speak('all right, any Honey?', expect_response=True)

    @intent_handler(IntentBuilder('YesMilkIntent').require("YesKeyword").
                                  require('MilkContext').build())
    @removes_context('MilkContext')
    @adds_context('HoneyContext')
    def handle_yes_milk_intent(self, message):
        self.milk = True
        self.speak('What about Honey?', expect_response=True)

    @intent_handler(IntentBuilder('NoHoneyIntent').require("NoKeyword").
                                  require('HoneyContext').build())
    @removes_context('HoneyContext')
    def handle_no_honey_intent(self, message):
        if self.milk:
            self.speak('Heres your Tea with a dash of Milk')
        else:
            self.speak('Heres your Tea, straight up')

    @intent_handler(IntentBuilder('YesHoneyIntent').require("YesKeyword").
                                require('HoneyContext').build())
    @removes_context('HoneyContext')
    def handle_yes_honey_intent(self, message):
        if self.milk:
            self.speak('Heres your Tea with Milk and Honey')
        else:
            self.speak('Heres your Tea with Honey')

```

When starting up only the `TeaIntent` will be available. When that has been triggered and _MilkContext_ is added the `MilkYesIntent` and `MilkNoIntent` are available since the _MilkContext_ is set. when a _yes_ or _no_ is received the _MilkContext_ is removed and can't be accessed. In it's place the _HoneyContext_ is added making the `YesHoneyIntent` and `NoHoneyIntent` available.

You can find an example [Tea Skill using conversational context on Github](https://github.com/krisgesling/tea-skill).

As you can see, Conversational Context lends itself well to implementing a [dialog tree or conversation tree](https://en.wikipedia.org/wiki/Dialog_tree).

## Under the hood

`set_context` / `remove_context` are thin wrappers — they prefix the keyword with the
skill id and emit bus messages that `ovos-core` handles on the active Session:

| Message | Effect |
|---|---|
| `add_context` | inject a keyword (and optional value) into `Session.context` |
| `remove_context` | drop a single keyword |
| `clear_context` | wipe all context for the session |

The decorators are equivalent to calling these methods:

- `@adds_context('MilkContext')` calls `set_context('MilkContext')` after the handler runs.
- `@removes_context('MilkContext')` calls `remove_context('MilkContext')`.

Because context is attached to the Session, each handler receives the message it was
triggered by; the Adapt pipeline reads `Session.context` when scoring intents, which is
why missing keywords fall back to the most recent matching context entry.


# Follow up questions

!!! abstract "In a nutshell"
    Normally each thing you say to your assistant is treated on its own, with no memory of the last sentence. Conversational context is the short-term memory that lets you ask a follow-up like "where's *he* from?" right after "how tall is John Cleese?" — the assistant remembers you were talking about Cleese and fills in the blank. Skill authors mark which details to remember, and that memory is kept separate for each ongoing conversation so different people or devices don't get mixed up. See [Skill design guidelines](skill-design-guidelines.md) or the [Glossary](glossary.md).

Conversational context in Open Voice OS (OVOS) allows voice interactions to feel more natural by remembering parts of a conversation, like the subject being discussed. This is especially useful for follow-up questions where repeating context (like a person's name) would otherwise be necessary.

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

!!! warning "Cross-skill context is not wired up"
    `set_cross_skill_context` emits the `mycroft.skill.set_cross_context` bus message,
    but no consumer for it currently exists in `ovos-core`, so on current releases it is
    effectively a no-op. Prefer per-skill `set_context` (or inject shared values into the
    Session context directly). The example below documents the intended behaviour.

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


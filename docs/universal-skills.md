# UniversalSkill

!!! abstract "In a nutshell"
    A "Universal" skill is one you write in a single language but that works in many. It automatically translates what the user said into your chosen working language before your code runs, and translates your replies back into the user's language afterward — so you handle everything in, say, English while users speak whatever they like. Think of it as a built-in interpreter sitting on either side of your skill. It needs translation plugins set up to work. For the family of skill templates see [Skill Classes](skill-classes.md); for term definitions see the [Glossary](glossary.md).

The `UniversalSkill` class is designed to facilitate automatic translation of input and output messages between different languages. 

This skill is particularly useful when native language support is not feasible, providing a convenient way to handle multilingual interactions.

> A `UniversalFallback` class (`ovos_workshop.skills.auto_translatable.UniversalFallback`) combines `UniversalSkill` with `FallbackSkill` for auto-translating [fallback](fallbacks.md) handlers. There is no `UniversalCommonQuerySkill` — for translated question answering, combine the `@common_query` decorator with the translation helpers yourself.

## Overview

This skill ensures that intent handlers receive utterances in the skill's internal language and are expected to produce responses in the same internal language. 

The `speak` method, used for generating spoken responses, automatically translates utterances from the internal language to the original query language.

> **NOTE:** The `self.lang` attribute reflects the original query language, while received utterances are always in `self.internal_language`.

## Language Plugins

To run `UniversalSkills` you need to configure [Translation plugins](translation-plugins.md) in `mycroft.conf`

```javascript
  // Translation plugins
  "language": {
    // by default uses public servers
    // https://github.com/OpenVoiceOS/ovos-translate-server    
    "detection_module": "ovos-lang-detector-plugin-server",
    "translation_module": "ovos-translate-plugin-server"
  },

```

!!! warning "Latency and missing-plugin behavior"
    Every incoming utterance and every spoken reply that needs translating adds a round trip
    to the configured translation plugin (a remote server call for `ovos-translate-plugin-server`,
    or local model inference for an offline plugin) — plan for this extra delay before speech
    starts. If no `translation_module` (or `detection_module`) is configured, or the configured
    plugin fails to load, `self.translator` / `self.lang_detector` raise the underlying exception
    the first time they are accessed — there is no silent fallback to "no translation"; the
    `OVOSLangTranslationFactory.create()` call is deliberately left unguarded
    (`ovos_workshop/skills/ovos.py`, `translator` property) so a missing plugin surfaces loudly
    instead of silently mistranslating. If you want your skill to degrade gracefully instead of
    crashing, wrap the access yourself:

    ```python
    try:
        translated = self.translator.translate(text, target="en")
    except Exception as e:
        self.log.warning(f"Translation unavailable, using original text: {e}")
        translated = text
    ```

## Usage

### Initialization

```python

# Example initialization
from ovos_workshop.skills.auto_translatable import UniversalSkill

class MyMultilingualSkill(UniversalSkill):
    """
    Skill that auto translates input/output from any language

    This skill is designed to automatically translate input and output messages
    between different languages. The intent handlers are ensured to receive
    utterances in the skill's internal language, and they are expected to produce
    utterances in the same internal language.

    The `speak` method will always translate utterances from the internal language
    to the original query language (`self.lang`).

    NOTE: `self.lang` reflects the original query language, but received utterances
          are always in `self.internal_language`.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the UniversalSkill.

        Parameters for super():

        - internal_language (str): The language in which the skill internally operates.


        - translate_tags (bool): Whether to translate the private __tags__ value (adapt entities).
                                 Default True; set False to skip translating that internal
                                 bookkeeping value if your skill doesn't rely on it.


        - autodetect (bool): If True, the skill will detect the language of the utterance
                            and ignore self.lang / Session.lang.

        - translate_keys (list): default ["utterance", "utterances"] 
                                 Keys added here will have values translated in message.data.
        """
        # skill hardcoded in portuguese
        super().__init__(internal_language="pt-pt", translate_tags=True,
                         autodetect=False, translate_keys=["utterance", "utterances"],
                         *args, **kwargs)

```

### Intents and Utterances

Use the `register_intent` and `register_intent_file` methods to register intents with universal intent handlers. The usual decorators also work

The `speak` method is used to generate spoken responses.
It automatically translates utterances if the output language is different from the skill's internal language or autodetection is enabled.

```python

# Example speaking utterance, hardcoded to self.internal_language
self.speak("Hello, how are you?")

```

### Universal Intent Handler

!!! info
    Users should NOT use the `create_universal_handler` method manually in skill intents; it is automatically utilized by `self.register_intent`. 

The following example demonstrates its usage with `self.add_event`.

```python

# Example universal handler creation
def my_event_handler(message):
    # Your event handling logic here
    pass

# Manual usage with self.add_event
my_handler = self.create_universal_handler(my_event_handler)
self.add_event("my_event", my_handler)

```

## EnglishCatFacts [Skill](skill-design-guidelines.md) Example

Let's create a simple tutorial skill that interacts with an API to fetch cat facts in English. 

We'll use the `UniversalSkill` class to support translations for other languages.

```python
from ovos_workshop.skills.auto_translatable import UniversalSkill
from ovos_workshop.decorators import intent_handler


class EnglishCatFactsSkill(UniversalSkill):
    def __init__(self, *args, **kwargs):
        """
        This skill is hardcoded in english, indicated by internal_language
        """
        super().__init__(internal_language="en-us", *args, **kwargs)
        
    def fetch_cat_fact(self):
        # Your logic to fetch a cat fact from an API
        cat_fact = "Cats have five toes on their front paws but only four on their back paws."
        return cat_fact

    @intent_handler("cat_fact.intent")
    def handle_cat_fact_request(self, message):
        # Fetch a cat fact in self.internal_language
        cat_fact = self.fetch_cat_fact()
        # Speak the cat fact, it will be translated to self.lang if needed
        self.speak(cat_fact)

```

In this example, the `CatFactsSkill` class extends `UniversalSkill`, allowing it to seamlessly translate cat facts into the user's preferred language.


## SpanishDatabase Skill Example

A more advanced example, let's consider a skill that listens to bus messages.

Our skill listens for messages containing a `"phrase"` payload in message.data that can be in any language, and it saves this phrase *in spanish* to a database. 
Then it speaks a hardcoded spanish utterance, and it gets translated into the language of the bus message [Session](session.md)

```python
from ovos_bus_client.message import Message
from ovos_workshop.skills.auto_translatable import UniversalSkill

class SpanishDatabaseSkill(UniversalSkill):
    def __init__(self, *args, **kwargs):
        """
        This skill is hardcoded in spanish, indicated by internal_language
        """
        translate_keys=["phrase"] # translate "phrase" in message.data
        super().__init__(internal_language="es-es",
                         translate_keys=translate_keys,
                         *args, **kwargs)
    
    def initialize(self):
        # wrap the event into a auto translation layer
        handler = self.create_universal_handler(self.handle_entry)
        self.add_event("skill.database.add", handler)
        
    def handle_entry(self, message: Message):
        phrase = message.data["phrase"]  # assured to be in self.internal_language
        
        # Your logic to save phrase to a database
        
        self.speak("agregado a la base de datos") # will be spoken in self.lang

```

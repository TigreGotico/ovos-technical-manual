# SSMLBuilder 

!!! abstract "In a nutshell"
    Normally the assistant just reads text aloud in a flat voice. SSML is a way to add stage directions to that text — pause here, say this word louder, slow down, whisper, change the pitch — so speech sounds more natural and expressive. It's like the difference between reading a script plainly and acting it out. The `SSMLBuilder` helper on this page lets you add those directions without memorizing the markup by hand. Heads-up: **most TTS voices don't actually support SSML** — but that's harmless, OVOS just strips the directions and reads the plain words, so it's always safe to send. For spoken replies in general see [Statements](statements.md); for term definitions see the [Glossary](glossary.md).

## What is SSML?

Speech Synthesis Markup Language (SSML) is a markup language used to enhance synthesized speech output. It provides developers with a way to control various aspects of speech synthesis, such as pronunciation, intonation, volume, and speed, by using predefined tags and attributes.

SSML allows developers to create more natural and expressive speech output, making interactions with voice-based applications more engaging and user-friendly.

These use cases demonstrate how SSML can be applied in various contexts to improve the quality, expressiveness, and accessibility of synthesized speech output, ultimately enhancing the overall user experience.

1. **Narration with Emphasis**: In storytelling applications or audiobooks, developers can use SSML to emphasize specific words or phrases to convey emotions or highlight key points in the narrative. For example, during a suspenseful moment in a story, the narrator's voice could be slowed down for dramatic effect using SSML.


2. **Interactive Voice Responses**: In voice-based applications such as virtual assistants or customer service bots, SSML can be used to provide more natural and engaging interactions with users. For instance, developers can use SSML to insert pauses between sentences to mimic natural speech patterns or adjust the pitch and volume of the voice to convey empathy or urgency.


3. **Educational Content**: SSML can be valuable in educational applications where synthesized speech is used to deliver instructional content or quizzes. Developers can use SSML to modify the speaking rate to accommodate different learning paces or employ phonetic pronunciation tags to ensure correct pronunciation of specialized terms or foreign words.


4. **Accessibility Features**: For applications designed to assist users with visual impairments or reading difficulties, SSML can play a crucial role in enhancing accessibility. Developers can use SSML to provide auditory cues, such as tone changes or speech emphasis, to indicate important information or user interface elements.


## SSMLBuilder

The `SSMLBuilder` class simplifies the creation of SSML strings by providing intuitive methods to control various aspects of speech synthesis. It offers a range of methods for manipulating text, adjusting timing and prosody, specifying voice and phoneme characteristics, and more.

```python
from ovos_utils.ssml import SSMLBuilder
from ovos_workshop.skills import OVOSSkill

class MySkill(OVOSSkill):

    def handle_intent(self, message):
        # Create an instance of SSMLBuilder (speak_tag=True wraps output in <speak>)
        ssml_builder = SSMLBuilder(speak_tag=True)
        
        # Generate SSML
        ssml_text = ssml_builder.sentence("Hello, world!").pause(500, "ms").say_slow("How are you today?").build()
        
        # Output:
        # "<speak>\n<s>Hello, world!</s> <break time=500ms/> <prosody rate='0.4'>How are you today?</prosody>\n</speak>"
        
        # Speak the SSML text
        self.speak(ssml_text)

```

### Text Manipulation

1. `sub(alias, word)`: Replaces a word with a specified alias.


2. `emphasis(level, word)`: Emphasizes a word with a specified level.


3. `parts_of_speech(word, role)`: Specifies the usage or role of a word.


4. `pause_by_strength(strength)`: Inserts a pause with a specified strength.


5. `sentence(text)`: Wraps text with `<s>` tags to denote a sentence.


6. `say_emphasis(text)`: Emphasizes the text strongly.


7. `say_strong(text)`: Modifies the vocal-tract length to increase speech intensity.


8. `say_weak(text)`: Modifies the vocal-tract length to decrease speech intensity.


9. `say_softly(text)`: Modifies the phonation to produce softer speech.


10. `say_auto_breaths(text)`: Adds automatic breaths to the speech.


11. `paragraph(text)`: Wraps text with `<p>` tags to denote a paragraph.


12. `audio(audio_file, text)`: Embeds audio with specified text.

### Timing and Prosody

1. `pause(time, unit)`: Inserts a pause for a specified duration.


2. `prosody(attribute, text)`: Modifies prosodic attributes of the text such as pitch, rate, or volume.


3. `pitch(pitch, text)`: Changes the pitch of the text.


4. `volume(volume, text)`: Modifies the volume of the text.


5. `rate(rate, text)`: Adjusts the speaking rate of the text.

### Voice and Phoneme

1. `say(text)`: Adds normal speed text to SSML.


2. `say_loud(text)`: Increases the volume of the text.


3. `say_slow(text)`: Slows down the speaking rate of the text.


4. `say_fast(text)`: Speeds up the speaking rate of the text.


5. `say_low_pitch(text)`: Lowers the pitch of the text.


6. `say_high_pitch(text)`: Raises the pitch of the text.


7. `say_whispered(text)`: Converts text into whispered speech.


8. `phoneme(ph, text)`: Specifies the phonetic pronunciation of the text.


9. `voice(voice, text)`: Specifies the voice to use for the text.


10. `whisper(text)`: Converts text into whispered speech.

### Build and Utility

1. `build()`: Constructs the final SSML string.


2. `remove_ssml(text)`: Removes SSML tags from the given text.


3. `extract_ssml_tags(text)`: Extracts SSML tags from the given text.

## SSML Support in [TTS](tts-plugins.md) Plugins

!!! tip "It is always safe to send SSML — even to engines that don't support it"
    **Most TTS engines do not support SSML.** That's fine: you can emit SSML from any skill
    without checking the engine first. The base `TTS` class **strips the tags before the engine
    ever sees them**, so a non-SSML engine simply speaks the plain text — the markup is dropped,
    nothing breaks. You only need an SSML-capable engine if you actually want the *effect* (a
    pause, emphasis, a pitch change) to be heard.

By default a plugin declares **no** SSML support: the `ssml_tags` list is empty, so OVOS removes
all SSML before synthesis. A plugin opts in by passing `ssml_tags=[...]` (the standard tags it can
handle) to the `TTS` base class. The base class then does the filtering for it:

- **SSML Validation**: `validate_ssml()` runs on the text *before* it reaches the engine's
  `get_tts()`. If `ssml_tags` is empty (the common case), **every** tag is stripped via
  `remove_ssml()`. If the engine declared some supported tags, only those are kept and any other
  tags are removed.


- **SSML Tag Handling**: for the tags an engine *does* support, `modify_tag()` lets the plugin
  rewrite each one (e.g. translate a standard tag into a vendor-specific form) before it is passed
  through to synthesis.

In other words, the plugin never has to worry about unsupported tags — by the time its `get_tts()`
sees the text, the markup has already been reduced to what it declared it can handle.

```python

# default handling of ssml, advanced plugins may override this method
def modify_tag(self, tag):
    """Override to modify each supported ssml tag.

    Arguments:
        tag (str): SSML tag to check and possibly transform.
    """
    return tag

def validate_ssml(self, utterance):
    """Check if engine supports ssml, if not remove all tags.

    Remove unsupported / invalid tags

    Arguments:
        utterance (str): Sentence to validate

    Returns:
        str: validated_sentence
    """

    # Validate speak tags
    if not self.ssml_tags or "speak" not in self.ssml_tags:
        self.format_speak_tags(utterance, False)
    elif self.ssml_tags and "speak" in self.ssml_tags:
        self.format_speak_tags(utterance)

    # if ssml is not supported by TTS engine remove all tags
    if not self.ssml_tags:
        return self.remove_ssml(utterance)

    # find ssml tags in string
    tags = SSML_TAGS.findall(utterance)

    for tag in tags:
        if any(supported in tag for supported in self.ssml_tags):
            utterance = utterance.replace(tag, self.modify_tag(tag))
        else:
            # remove unsupported tag
            utterance = utterance.replace(tag, "")

    # return text with supported ssml tags only
    return utterance.replace("  ", " ")

```

### Platform-Specific SSML Handling

Some TTS plugins, like the PollyTTS plugin, may support platform-specific SSML tags that are not part of the standard specification. For example, Amazon Polly supports additional SSML tags specific to Amazon's speech synthesis service.

Let's take a closer look at how SSML support is implemented in the `PollyTTS` plugin:

```python
class PollyTTS(TTS):
    def __init__(self, *args, **kwargs):
        ssml_tags = ["speak", "say-as", "voice", "prosody", "break",
                     "emphasis", "sub", "lang", "phoneme", "w", "whisper",
                     "amazon:auto-breaths", "p", "s", "amazon:effect", "mark"]
        super().__init__(*args, **kwargs, audio_ext="mp3",
                         ssml_tags=ssml_tags, validator=PollyTTSValidator(self))

    def get_tts(self, sentence, wav_file, lang=None, voice=None):
        # SSML handling specific to PollyTTS
        # Replace custom SSML tags for Amazon Polly
        sentence = sentence.replace("\whispered", "/amazon:effect") \
            .replace("\\whispered", "/amazon:effect") \
            .replace("whispered", "amazon:effect name=\"whispered\"")

        # altermatively the plugin could override self.modify_tag method instead

        # Synthesize speech using Amazon Polly API
        # Write audio stream to WAV file
        return wav_file, None

```

In this example, the `PollyTTS` plugin defines a list of supported SSML tags, including both standard and Amazon-specific tags. During initialization, the plugin sets up SSML support by providing the list of tags to the `TTS` superclass.

When synthesizing speech using Amazon Polly, the plugin translates platform-specific SSML tags like `amazon:effect` to ensure compatibility with Amazon's speech synthesis service.

### Behavior with Plugins That Do Not Support SSML

When SSML text is sent to a TTS plugin that does not support SSML — again, **the common case** —
OVOS strips the tags (via `remove_ssml()`) before the engine runs, and the engine speaks the
remaining plain text. The SSML-specific effects (pauses, emphasis, prosody) are simply **dropped**;
nothing errors and the user still hears the words.

Because of this, **you do not need to check whether the engine supports SSML before sending it** —
it is always safe. The only consideration is whether the effect *matters*: if a pause or emphasis
is essential to be heard, choose an SSML-capable engine (such as Amazon Polly above). If it is just
a nice-to-have, emit the SSML anyway and let non-supporting engines fall back to the plain text.

---

*Source code: [OpenVoiceOS/ovos-utils](https://github.com/OpenVoiceOS/ovos-utils).*

# Cool Things You Can Do

!!! abstract "In a nutshell"
    OVOS is not just a weather-and-timer box — it's a voice-first assistant you can point at
    other people's brains, other people's voices, and your own code. This page is a tour of fun,
    slightly silly things you can build or turn on today, each one a real skill or feature that
    already ships with OVOS, with a link to go deeper. No hardware skills required to start; the
    last example combines several pieces for a Halloween-prop style build.

---

## Make it tell jokes

The [Dad Jokes skill](skill-examples.md#dad-jokes) (`ovos-skill-icanhazdadjokes`) answers "tell me
a joke", "do you know any Chuck Norris jokes?", or "tell me a joke about dentists" with a fresh
pun every time. Install it with `pip install ovos-skill-icanhazdadjokes` and restart `ovos-core`.

## Turn it into a parrot

The [Parrot skill](skill-examples.md#parrot) (`ovos-skill-parrot`) makes OVOS repeat whatever you
say back to you: "repeat Once upon a midnight dreary…" or "say Goodnight, Gracie" gets echoed
verbatim. It's a one-line install (`pip install ovos-skill-parrot`) and a fun way to demonstrate
that speech really is being captured and understood, not faked.

## Give it a personality — in three steps

Beyond built-in skills, OVOS can hand off anything it doesn't understand to a large language model,
answering ChatGPT-style. The [Personas page](personas.md) has the full three-step recipe:

1. Install a chat backend — a cloud [OpenAI-compatible](openai-plugin.md) model or a fully local
   [GGUF](gguf-plugin.md) model.
2. Create a small persona JSON file describing who it is.
3. Turn on the [persona pipeline](persona-pipeline.md) so unanswered questions reach it.

Give the persona a name and a system prompt ("You are a grumpy pirate who answers every question
in character") and every fallback question gets answered in that voice — a cheap way to build a
themed assistant for a party or a kid's room.

## Change its voice

Swapping which [TTS plugin](tts-plugins.md) OVOS uses changes what it sounds like — some plugins
also expose several distinct voices through their own `voice` config key. For example,
[`ovos-tts-plugin-matxa-multispeaker-cat`](tts-plugins.md#ovos-tts-plugin-matxa-multispeaker-cat)
picks a specific speaker/dialect with `"voice": "valencia/gina"`, and
[`ovos-tts-plugin-edge-tts`](tts-plugins.md#ovos-tts-plugin-edge-tts) offers dozens of
cloud voices across many languages and accents. Set the plugin (and, where supported, its `voice`)
under the `tts` section of `mycroft.conf` and restart `ovos-audio` to hear the change.

## Change how it sounds

Most spoken replies are flat, one-tone sentences — but they don't have to be. The reliable way
to change how OVOS sounds is to pick a different [TTS plugin or voice](tts-plugins.md), as in
the section above: an eerie voice, a different accent, a faster or slower speaker all exist as
plugin/voice choices, and they work the same on every install. [SSML](ssml.md) markup (pauses,
emphasis, a slower rate for one sentence) exists too, but it is an **experimental**,
engine-dependent feature that most TTS plugins ignore — treat it as a niche option for the few
engines that support it, not the primary way to change a voice's character.

## Combine it all: a Halloween prop

None of the above needs to be used alone. A classic seasonal build — a talking jack-o'-lantern or
skeleton that reacts to trick-or-treaters — is really just three ordinary OVOS pieces stacked
together:

1. **A scheduled greeting.** Use `self.schedule_event(...)` (see
   [Scheduled events with restart persistence](skill-cookbook.md#1-a-reminder-skill-scheduled-events-with-restart-persistence)
   for the pattern) to have the prop speak on its own every so often, unprompted — "Who dares
   approach?" every few minutes while it's active.
2. **A spooky voice.** Pick an eerie-sounding [TTS voice](tts-plugins.md) so the scheduled lines
   and any replies sound in character.
3. **A parrot-style reply for trick-or-treaters.** Reuse the same idea as the
   [Parrot skill](skill-examples.md#parrot) — echo back whatever the kids say, in the spooky
   voice, for an instant "it's alive!" reaction — or use
   [`converse`](skill-cookbook.md#4-continuous-conversation-multi-turn-dialog-with-converse-and-get_response)
   to hold a short back-and-forth instead of a single line.

Nothing here needs custom hardware — a speaker and a device running OVOS is enough to try the
pattern indoors before building it into a prop. See [Hardware Integrators](hardware-integrators.md)
if you do want to build a standalone battery/speaker enclosure for it.

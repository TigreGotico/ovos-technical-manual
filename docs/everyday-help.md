# It's Not Working — Quick Fixes

!!! abstract "In a nutshell"
    Something is wrong and you just want your assistant talking again — no terminal, no
    programming. This page is a short list of the most common everyday problems ("it won't
    listen", "I can't hear it", "it doesn't understand me") and the plain fixes for each, entirely
    by voice or with a couple of taps in a settings screen. If your problem isn't here, jump to
    [What can I say?](skill-examples.md) to check the exact words to use, or to
    [Troubleshooting & Debugging](troubleshooting.md) for the deeper, log-reading version of this
    page.

---

## First, check the basics

Before anything else, these four things cause most "it's just not working" moments and take
seconds to check — no terminal, no config file:

- **Is it muted?** Look for a mute light/icon, or ask *"are you muted?"* — if it can't hear you
  to answer, check the physical mute switch/button if your device has one.
- **Is the volume up?** Ask *"what's the volume?"* — a spoken answer means the speaker path
  works.
- **Is it powered on?** A dead device won't react to anything — check the power light/cable
  before assuming a software problem.
- **Is it connected to the network?** Most skills (weather, radio, trivia) need internet access;
  check your router or the device's Wi-Fi indicator/settings screen if answers about the outside
  world consistently fail while purely local things (time, volume) still work.

If all four check out and something's still wrong, the sections below cover the specific
symptom.

## "It's not listening to me"

- **Say the wake word clearly, with a short pause after it.** OVOS listens for a wake word (by
  default *"Hey Mycroft"*) before it pays attention to anything else. Say the wake word, wait a
  beat, then say your request — "Hey Mycroft… what's the weather" — rather than running the two
  together.
- **Check you're not muted.** If a light or on-screen icon shows the microphone is muted, say
  *"unmute microphone"* or use the physical mute switch/button if your device has one.
- **Move closer, or reduce background noise.** Wake-word detection is a local audio match — a TV,
  music, or a fan right next to the microphone can drown it out.
- **The wake word keeps missing or keeps false-triggering.** This is a sensitivity setting, not a
  hardware fault — see [Wake Word Plugins](wake-word-plugins.md#wake-word-configuration) for how to
  adjust `sensitivity` and `trigger_level` in `mycroft.conf`, and pick a less noise-prone wake word
  if needed. Unlike the fixes above, this one needs opening a text config file, not just talking
  to the assistant — see [Make It Yours](personalize.md) for the general edit-and-restart
  routine.

## "It's not talking back to me" / "It's muted"

- **Ask it to check itself:** say *"what's the volume?"* — if you get a spoken answer, audio
  output works and the problem is elsewhere (see the next section).
- **Say *"unmute"* or *"unmute volume"*.** OVOS keeps mic-mute and speaker-mute separate; muting
  the microphone does not silence the speaker and vice versa.
- **Say *"volume up"* or *"set volume to 80".*** These are handled by the built-in
  [Volume skill](skill-examples.md#volume) (`ovos-skill-volume`), which understands phrasing like
  "volume up", "quieter", "mute", "unmute", "toggle mute", "set volume to 50", and "what's the
  current volume".
- **Check the physical connections** if voice control makes no difference at all: speaker cable
  fully seated, powered speaker turned on and its own volume dial not at zero, and (on a Raspberry
  Pi or similar box) the audio output routed to the jack/HDMI/USB device you expect — see
  [Hardware Integrators](hardware-integrators.md) if you're building your own box and need to pick
  an audio path.

## "It heard me but got it wrong"

- **Speak in short, plain sentences.** Long, run-on requests are harder for both wake-word and
  speech-to-text to parse correctly than "what time is it" or "set a timer for ten minutes".
- **Check you're using words it actually understands** — every OVOS skill only reacts to specific
  phrasings ("intents"). [What can I say?](skill-examples.md) lists real, working example phrases
  for every skill that ships with OVOS, grouped by what they do (jokes, timers, weather, and more).
- **If it keeps mishearing the same words** (names, local places), that is a
  speech-to-text accuracy limit rather than something fixable from voice alone — see
  [STT Plugins](stt-plugins.md) if you want to try a different recognizer.

## "I don't know what to say to it"

You don't need to memorize a command syntax — [What can I say?](skill-examples.md) is a
browsable list of every skill that ships with (or can be added to) OVOS, each with real usage
examples straight from that skill's own vocabulary, e.g. "tell me a joke", "what's the weather in
Lisbon", "set a timer for five minutes".

## Still broken?

If none of the above fixes it, the problem needs a bit more digging — but you still don't need to
be a programmer to follow along. [Troubleshooting & Debugging](troubleshooting.md) walks through
exactly the same journey (wake word → speech-to-text → understanding → skill → speaking) stage by
stage, showing which log file or on-screen tool proves where things went wrong.

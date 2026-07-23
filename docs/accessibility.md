# Accessibility

!!! abstract "In a nutshell"
    OVOS is a **voice-first** assistant: talking to it and hearing it talk back is the primary way
    of using it, not a fallback for a graphical app. That matters if you or someone you're setting
    this up for can't reliably use a screen, mouse, or keyboard — a voice interface removes those
    requirements entirely for day-to-day use. This page states plainly what OVOS does and does not
    offer today: the install path that avoids a screen reader fighting an installer wizard, how to
    slow down or change the speaking voice for long listening sessions, and an honest note on where
    support is currently thin. See the [Glossary](glossary.md) for terms and
    [Troubleshooting](troubleshooting.md) if something isn't working.

---

## Voice is not a fallback here

Every core interaction — waking the assistant, asking a question, hearing the answer, adjusting
[volume](skill-examples.md#volume), asking what it can do — works with sound alone, no display
required. This isn't a design aspiration: the [GUI service](gui-service.md) is explicitly
**optional** for a skill (`requires_gui` defaults to `False` in
[`runtime_requirements`](skill-runtime-requirements.md)), and a skill with nothing to show on
screen is expected to fall back to speaking instead. As it happens, the current OVOS GUI stack is
itself [deprecated and not generally usable](gui-service.md) while its replacement is built — so
today, voice-only really is how most OVOS devices operate in practice, screen or no screen.

## Installing without fighting a screen reader

The interactive [`ovos-installer`](ovos-installer.md) wizard is a series of arrow-key menus in a
terminal, which can be awkward to navigate with a screen reader reading a live, redrawing TUI.
The installer has a second path built for exactly this kind of non-interactive setup: a
[**scenario file**](ovos-installer.md#non-interactive-scenario-install) — a plain YAML file
listing every choice up front (installation method, channel, profile, features) — that the
installer reads and applies without displaying a single menu. Writing (or having someone write)
the scenario file once, in a plain text editor, and running the installer against it avoids the
interactive wizard entirely: write the file to `~/.config/ovos-installer/scenario.yaml` before
running the installer, and it reads that file automatically instead of showing any menus. See
[Non-interactive (scenario) install](ovos-installer.md#non-interactive-scenario-install) for the
full file format and ready-made examples.

## Tuning speech for long listening sessions

For someone listening to OVOS for extended periods, two things help most: a comfortable speaking
rate, and a voice that stays intelligible at that rate. There is no single global "speaking rate"
setting shared by every voice — OVOS supports many [TTS plugins](tts-plugins.md), and the exact
rate/voice keys they accept live in each plugin's own configuration block under `tts` in
`mycroft.conf`. For example, [`ovos-tts-plugin-matxa-multispeaker-cat`](tts-plugins.md#ovos-tts-plugin-matxa-multispeaker-cat)
and [`ovos-tts-plugin-edge-tts`](tts-plugins.md#ovos-tts-plugin-edge-tts) each expose their own
`voice` key for picking a specific speaker; check a given plugin's page for whether it also
exposes a rate/speed option.

What works with **every** voice, regardless of plugin, is [SSML](ssml.md)'s `<prosody rate="...">`
tag, applied per-utterance from a skill:

```python
from ovos_utils.ssml import SSMLBuilder

ssml_text = SSMLBuilder(speak_tag=True).say_slow("Here is the reminder you asked for.").build()
self.speak(ssml_text)
```

If the active voice doesn't support SSML, OVOS strips the tag and speaks the plain text instead of
failing — so it's always safe to slow things down this way even if you're not sure the current
voice honors it.

## Where support is thin today

- **The legacy GUI stack is deprecated.** Anything that depended on visual screen content (rather
  than speech) is not a reliable path right now regardless of assistive technology — see
  [GUI Service](gui-service.md) for the current status and the replacement effort underway.
- **No dedicated screen-reader integration exists for the installer's interactive wizard mode**
  beyond the scenario-file path above; the wizard itself is a standard terminal menu, not one
  built with screen-reader affordances.
- **Speaking-rate control is per-plugin, not a single global switch** (see above) — expect to look
  up the specific voice/plugin in use rather than finding one universal setting.

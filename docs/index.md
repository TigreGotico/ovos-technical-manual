<div class="ovos-hero">
  <h1>OpenVoiceOS Technical Manual</h1>
  <p>The complete guide to using, building on, and understanding the OVOS voice assistant — from your first install to the deepest internals.</p>
</div>

![OVOS Logo](https://github.com/OpenVoiceOS/ovos_assets/blob/master/Logo/ovos-logo-512.png?raw=true){ align=right width="160" }

## What is OpenVoiceOS?

**OpenVoiceOS (OVOS)** is a free, open-source, privacy-respecting **voice assistant** —
think of it as an open alternative to Alexa or Google Assistant that *you* control. It
listens for a wake word, understands what you ask, and responds with speech (and
optionally a screen).

You can run it on a Raspberry Pi, a desktop, or a server. Because it's **modular** —
built from many small, swappable pieces called *plugins* and *skills* — you can change
how it hears, thinks, and speaks, or teach it brand-new abilities.

!!! tip "New to all this? Don't worry."
    This manual covers everything from "I just want it working" to "I'm rewriting the
    intent pipeline." You don't need to read it front to back — pick the path below that
    matches what you want to do. Unfamiliar word? Check the **[Glossary](glossary.md)**.

---

## Choose your path

<div class="grid cards" markdown>

-   :material-rocket-launch: __I just want to run OVOS__

    ---

    Get a working voice assistant on your device.

    [:octicons-arrow-right-24: Installation options](release-channels.md) ·
    [ovos-installer](ovos-installer.md) ·
    [Skill examples](skill-examples.md)

-   :material-school: __I want to build a skill__

    ---

    Teach OVOS to do something new — your first voice skill, step by step.

    [:octicons-arrow-right-24: Start with skill design](skill-design-guidelines.md) ·
    [Anatomy of a skill](skill-structure.md) ·
    [Skill FAQ](skill-dev-faq.md)

-   :material-cog: __I want to understand how it works__

    ---

    Follow a spoken command from microphone to spoken reply.

    [:octicons-arrow-right-24: Architecture overview](architecture-overview.md) ·
    [Life of an utterance](life-of-an-utterance.md) ·
    [MessageBus](bus-service.md)

-   :material-translate: __I want to help translate__

    ---

    Make OVOS speak your language — no coding required.

    [:octicons-arrow-right-24: Translator guide](ovos-localize-tutorial.md) ·
    [Language support](lang-support.md)

-   :material-robot-happy: __I want it to use AI / an LLM__

    ---

    Give your assistant a chat brain — ChatGPT-style, a local model, or a custom persona.

    [:octicons-arrow-right-24: Personas](personas.md) ·
    [Agent engines](agent-plugins.md) ·
    [Local LLM (GGUF)](gguf-plugin.md)

</div>

---

## How OVOS is organized

OVOS is not one program — it's a small team of cooperating services that talk to each
other over a shared **[message bus](bus-service.md)**. Knowing the cast of characters
makes the rest of the manual click into place:

| Piece | In plain terms | Learn more |
|---|---|---|
| **Listener** | Hears the wake word and records your speech | [Speech Service](speech-service.md) |
| **STT** | Turns your speech into text | [STT plugins](stt-plugins.md) |
| **ovos-core** | The "brain" — decides which skill should answer | [ovos-core](core.md) |
| **Skills** | The abilities (weather, timers, music…) | [Skill development](skill-design-guidelines.md) |
| **TTS** | Turns the reply text back into speech | [TTS plugins](tts-plugins.md) |
| **GUI** | Optional screen / visuals — ⚠️ *legacy GUI deprecated; no usable GUI right now, replacement in progress* | [GUI Service](gui-service.md) |
| **MessageBus** | The shared channel they all talk over | [MessageBus Service](bus-service.md) |

!!! info "Plugins vs. Skills — the two ways to extend OVOS"
    A **skill** adds an *ability* ("set a timer", "play the news"). A **plugin** swaps
    out a *building block* (a different speech-to-text engine, a new wake word, another
    voice). See the **[Plugin Ecosystem](plugins-index.md)** to explore what's available,
    or the **[OVOS Repository Index](ecosystem-index.md)** for a map of every public
    repository in the project.

---

## Explore by topic

### 🏗️ Core Architecture

Understand the "brain" and "nervous system" of the platform:

*   **[Architecture Overview](architecture-overview.md)**: How all the components fit together.
*   **[Life of an Utterance](life-of-an-utterance.md)**: Trace a command from sound to speech.
*   **[MessageBus Service](bus-service.md)**: Deep dive into the communication backbone.
*   **[Configuration](config.md)**: Master the layered configuration system.

### 💻 Developer Resources

Ready to build your own plugins or skills?

*   **[Skill Development](skill-design-guidelines.md)**: Learn how to write your first voice skill.
*   **[Plugin Ecosystem](plugins-index.md)**: Explore and create plugins for STT, TTS, VAD, and more.
*   **[Intent Pipelines](pipelines-overview.md)**: Understand how OVOS parses natural language.
*   **[Skill Testing](skill-testing.md)**: Ensure your skills are robust with `ovoscope`.

### 🌍 Language Support

OVOS is built for a global community:

*   **[Overview](lang-support.md)**: Current status and requirements for full language support.
*   **[Contributing Translations](ovos-localize-tutorial.md)**: Help translate skills and intents — no coding needed — with OVOS Localize.
*   **[Technical Parsers](lang-parser.md)**: How OVOS handles numbers, dates, and colors across languages.
*   **[Translation Plugins](translation-plugins.md)**: Explore translation plugins and self-hosting options.

---

!!! info "Help improve these docs"
    This manual is maintained by the OVOS community. Every page is cross-checked against
    the real source code. If you find an error or something unclear, please
    [open a pull request or issue](https://github.com/OpenVoiceOS/ovos-technical-manual).

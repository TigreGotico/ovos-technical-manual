<div class="ovos-hero">
  <h1>OpenVoiceOS Technical Manual</h1>
  <p>The definitive guide to building, configuring, and extending the OVOS ecosystem.</p>
</div>

![OVOS Logo](https://github.com/OpenVoiceOS/ovos_assets/blob/master/Logo/ovos-logo-512.png?raw=true){ align=right width="200" }

Welcome to the **OpenVoiceOS (OVOS)** developer documentation. This manual is designed for developers, tinkerers, and advanced users who want to understand the inner workings of the system.

OpenVoiceOS is a **modular, community-driven voice assistant platform**. It is built on a plugin-based architecture, making it highly flexible and customizable.

---

### 🚀 Getting Started

If you are new to OVOS, these guides will help you get up and running:

*   **[Installation Options](release-channels.md)**: Choose the best installation method for your hardware.


*   **[ovos-installer](ovos-installer.md)**: The recommended way to install OVOS on Linux.


*   **[RaspOVOS Tutorial](install-raspovos.md)**: Quick-start for Raspberry Pi users.
*   **[Skill Examples](skill-examples.md)**: See what OVOS can do out of the box.

---

### 🌍 Language Support

OVOS is built for a global community. Learn how to use and improve multilingual support:

*   **[Overview](lang-support.md)**: Current status and requirements for full language support.
*   **[Contributing](gitlocalize-tutorial.md)**: Help translate skills and intents via GitLocalize.
*   **[Language Parser](lang-parser.md)**: Technical details on numbers, dates, and color parsing.
*   **[Translation](translation-plugins.md)**: Explore translation plugins and self-hosting options.

---

### 🏗️ Core Architecture


Understand the "brain" and "nervous system" of the platform:

*   **[Architecture Overview](architecture-overview.md)**: How all the components fit together.


*   **[Life of an Utterance](life-of-an-utterance.md)**: Trace a command from sound to speech.


*   **[MessageBus Service](bus-service.md)**: Deep dive into the communication backbone.


*   **[Configuration](config.md)**: Master the layered configuration system.

---

### 💻 Developer Resources

Ready to build your own plugins or skills?

*   **[Skill Development](skill-design-guidelines.md)**: Learn how to write your first voice skill.


*   **[Plugin Ecosystem](plugins-index.md)**: Explore and create plugins for STT, TTS, VAD, and more.


*   **[Intent Pipelines](pipelines-overview.md)**: Understand how OVOS parses natural language.


*   **[Skill Testing](skill-testing.md)**: Ensure your skills are robust with `ovoscope`.

---

::: info
This manual is maintained by the OVOS community. If you find errors or have suggestions, please [open a pull request](https://github.com/OpenVoiceOS/ovos-technical-manual).
:::

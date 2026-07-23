# Language Support in OpenVoiceOS

!!! abstract "In a nutshell"
    Making OVOS truly work in a given language takes more than translating menu text — it needs translated skill phrases, a speech-to-text engine that understands that language, and a text-to-speech voice that can speak it. This page explains the current state of language support, how to get a working setup quickly with the `ovos-config autoconfigure` command, and how you can help improve your language by translating phrases or testing real speech. If you just want it running now, jump to [Auto-Configuration](#auto-configuration). See also [Customizing Language Resources](lang-customization.md) and the [Glossary](glossary.md).

OpenVoiceOS (OVOS) aims to support multiple languages across its components, including intent recognition, speech-to-text ([STT](stt-plugins.md)), text-to-speech ([TTS](tts-plugins.md)), and skill dialogs. However, full language support requires more than translation of interface text. This document outlines the current state of language support, known limitations, and how contributors can help improve multilingual performance in OVOS.

**Want it working now?** Jump to [Auto-Configuration](#auto-configuration) — `ovos-config autoconfigure -l <lang> ...` sets up recommended STT/TTS plugins in one command. **Want to make your language work better?** See [How to Improve Language Support](#how-to-improve-language-support).

Related pages: [Language Selection](lang-selection.md) (how OVOS picks a language per utterance), [Customizing Language Resources](lang-customization.md) (override/translate skill text), and [Bidirectional Translation](bidirectional-translation.md) (use a single-language skill in any language).

---

While the OVOS installer allows users to select a preferred language, **selecting a language does not guarantee full support across all subsystems**. True multilingual support requires dedicated:

- ✅ Translations (intents, dialogs, settings, etc.)


- ✅ STT ([Speech-to-Text](stt-plugins.md)) plugins trained on the target language


- ✅ TTS ([Text-to-Speech](tts-plugins.md)) plugins capable of generating speech in the selected language


- ✅ Language-specific intent adaptation and fallback logic

Without these, many core features (e.g., voice commands, speech output, skill interactions) may not function as expected.

---

## Adding a New Language

Adding support for a new language in OVOS is a multi-step process requiring:

- Translations of assistant dialog and intent files


- A compatible STT plugin with reliable speech recognition


- A natural-sounding TTS voice


- Validation using real-world user data

We welcome and encourage community participation to improve language support. Every contribution helps make OVOS more accessible to speakers around the world.

---

## Technical Language Handling

OVOS handles languages dynamically throughout the interaction cycle. For a deep dive into how the system picks which language to use for an utterance, see **[Language Selection and Disambiguation](lang-selection.md)**.

### STT and TTS Requirements

For a language to function correctly in a voice assistant environment, it must have **dedicated STT and TTS plugins** that support the language reliably.

### STT (Speech-to-Text)

- STT plugins must be able to recognize speech in the target language with high accuracy.


- Some plugins are multilingual (e.g., Whisper, MMS), but accuracy varies across languages.


- For production use, **language-specific tuning or models are recommended**.

### TTS (Text-to-Speech)

- The TTS engine must generate clear, natural-sounding speech in the selected language.


- Not all TTS plugins support all languages.


- Quality varies significantly by model and backend.

---

## Translation Coverage

OVOS uses [**OVOS Localize**](https://openvoiceos.github.io/ovos-localize/) — a GitHub-native, in-browser translation tool purpose-built for OVOS — to manage translation files across its repositories. (It replaces the retired third-party *GitLocalize* service.) This includes:

- [Skill](skill-design-guidelines.md) dialog files


- Intent files (used by [Padatious](padatious-pipeline.md)/[Adapt](adapt-pipeline.md))


- Configuration metadata

### 📊 Translation Progress

Translation progress is tracked at:  
👉 [https://openvoiceos.github.io/lang-support-tracker](https://openvoiceos.github.io/lang-support-tracker)

The tracker provides daily updates and displays all languages that have reached at least 25% translation coverage.

> ❗ If your language is missing from [OVOS Localize](https://openvoiceos.github.io/ovos-localize/), [open an issue](https://github.com/OpenVoiceOS/lang-support-tracker/issues) to request it. Currently, languages must be added manually.

See **[Contribute Translations with OVOS Localize](ovos-localize-tutorial.md)** for the step-by-step translator guide.

### Open-data ML datasets

OVOS Localize also auto-generates **machine-learning-ready JSONL datasets** from the scanned
skill data (hosted statically, refreshed daily), under `data/datasets/`:

- **Intent classification** (`classification/{lang}.jsonl`) — `.intent`/`.voc` phrases mapped
  to their skill domain and intent name (for training NLU / small language models).
- **Parallel corpora** (`translation/{lang_pair}.jsonl`) — English keys paired with their
  translations from `.dialog`/`.intent` files (for machine translation).

These load directly via HuggingFace `datasets.load_dataset(...)`.

---

## Known Limitations

- Selecting a language during installation only automatically configures a compatible STT/TTS plugin for **some languages**. Manual action might be required for full support


- Many skills contain only partial translations or outdated strings.


- Skills may be partially translated, with only a subset of intents available for your language


- Skills may have translated intents but missing dialog translations. The assistant typically speaks the dialog filename if it is not translated

---

## Auto-Configuration

The fastest way to get a working setup for your language is `ovos-config autoconfigure`. It writes recommended STT and TTS plugin settings into your user config:

```bash
ovos-config autoconfigure -l en-us --offline --female
ovos-config autoconfigure -l de-de --online --male
ovos-config autoconfigure -l fr-fr --hybrid --female
```

The recommendations are data-driven: they come from per-language `*.conf` files bundled in `ovos-config` (`recommends/`), so the exact models depend on your installed version. See [`ovos-config`](config.md) for full options.

### Flags

| Flag | Meaning |
|------|---------|
| `-l`, `--lang` | **Required.** Language code (e.g. `en-us`). Standardized internally (e.g. `en-US`). |
| `--offline` / `-off` | Offline STT + TTS. |
| `--online` / `-on` | Online (public-server) STT + TTS. |
| `--hybrid` / `-hy` | Offline TTS with online STT. |
| *(none of the three)* | **Defaults to hybrid.** |
| `--male` / `-m`, `--female` / `-f` | Pick a voice. Pass exactly one. If you pass **neither**, TTS configuration is skipped. |

After writing the config it lists the installed STT/TTS plugins and warns about any recommended plugin you still need to `pip install`.

!!! note "Upcoming"
    A `--gpu` flag (GPU-accelerated offline STT) and a `--platform` flag (hardware-tuned
    intent-pipeline presets for `rpi3`/`rpi4`/`rpi5`/`linux`/`mac`/`termux`) are in
    development for a future `ovos-config` release. `--gpu` is tracked in
    [ovos-config#274](https://github.com/OpenVoiceOS/ovos-config/pull/274).

### Supported Languages

> The table below is a snapshot of the bundled recommendations. The authoritative list is whatever `recommends/base/*.conf`, `recommends/offline_stt/*.conf`, and related files ship in your installed `ovos-config`.

| Language | Offline STT | Offline TTS (Male) | Offline TTS (Female) |
|----------|-------------|---------------------|---------------------|
| **en-US** | `ovos-stt-plugin-fasterwhisper` (`small.en`) | `ovos-tts-plugin-piper` (ryan-low) | `ovos-tts-plugin-piper` (amy-low) |
| **en-GB** | — | `ovos-tts-plugin-piper` (alan-low) | `ovos-tts-plugin-piper` (alba-medium) |
| **de-DE** | `ovos-stt-plugin-citrinet` (de) | `ovos-tts-plugin-piper` (thorsten-low) | `ovos-tts-plugin-piper` (ramona-low) |
| **fr-FR** | `ovos-stt-plugin-citrinet` (fr) | `ovos-tts-plugin-piper` (gilles-low) | `ovos-tts-plugin-piper` (siwis-low) |
| **es-ES** | `ovos-stt-plugin-fasterwhisper-zuazo` (es, base) | `ovos-tts-plugin-piper` (carlfm-x_low) | `ovos-tts-plugin-ahotts` |
| **it-IT** | `ovos-stt-plugin-citrinet` (it) | `ovos-tts-plugin-piper` (riccardo-x_low) | `ovos-tts-plugin-piper` (paola-medium) |
| **nl-NL** | `ovos-stt-plugin-citrinet` (nl) | `ovos-tts-plugin-piper` (ronnie-medium) | `ovos-tts-plugin-piper` (nathalie-medium) |
| **pt-PT** | `ovos-stt-plugin-fasterwhisper` (custom model) | `ovos-tts-plugin-piper` (tugão-medium) | — |
| **pt-BR** | — | `ovos-tts-plugin-piper` (faber-medium) | — |
| **ca-ES** | `ovos-stt-plugin-citrinet` (ca) | `ovos-tts-plugin-matxa-multispeaker-cat` (grau) | `ovos-tts-plugin-matxa-multispeaker-cat` (elia) |
| **gl-ES** | `ovos-stt-plugin-fasterwhisper-zuazo` (gl, base) | `ovos-tts-plugin-cotovia` (iago) | `ovos-tts-plugin-nos` (celtia) |
| **eu-ES** | `ovos-stt-plugin-fasterwhisper-zuazo` (eu, base) | — | `ovos-tts-plugin-ahotts` |
| **da-DK** | `ovos-stt-plugin-fasterwhisper` (small) | `ovos-tts-plugin-piper` (nst_talesyntese-medium) | — |
| **en-AU** | — | — | — |

!!! note
    Where a cell shows "—", the bundled recommendations don't cover that combination yet;
    `autoconfigure` will skip that part of the configuration and tell you so.

---

## How to Improve Language Support

### 1. **Contribute Translations**

Use [OVOS Localize](https://openvoiceos.github.io/ovos-localize/) to translate dialog and intent files right in your browser:

- [OVOS Localize translation app](https://openvoiceos.github.io/ovos-localize/)


- [Translator Tutorial](ovos-localize-tutorial.md)

Translation stats for each language are also available in:

- [Markdown summaries (e.g., `translate_status_pt.md`)](https://openvoiceos.github.io/lang-support-tracker/tx_info/translate_status_pt-PT.md)


- [JSON format (e.g., `pt-PT.json`)](https://openvoiceos.github.io/lang-support-tracker/tx_info/pt-PT.json)

---

### 2. **Test in Real-World Usage**

Translation coverage alone does not ensure accuracy. Native speakers are encouraged to test OVOS with real speech input and report issues with:

- Intent matching failures


- Mispronunciations or robotic speech


- Incorrect or unnatural translations

You can help by **enabling open data collection** in your OVOS instance by pointing `intent_urls` at a reporting server:

```json
"open_data": {
  "intent_urls": [
    "https://your-opendata-server.example.com/intents"
  ]
}

```

> 💡 You can self-host the reporting server: [ovos-opendata-server on GitHub](https://github.com/OpenVoiceOS/ovos-opendata-server)

---

## Benchmark Projects (Open Data)

Explore public benchmark tools for evaluating model performance:

| Project                                                         | Description |
|-----------------------------------------------------------------|-------------|
| [OVOS Localize](https://openvoiceos.github.io/ovos-localize/)   | Browse intent translation coverage per language and skill |


---

##  Tips for Contributors

- Translators: Use [OVOS Localize](https://openvoiceos.github.io/ovos-localize/)’s side-by-side editor — it shows the skill code behind each phrase — to keep intent logic intact.


- Developers: Review user-submitted errors on the dashboard to improve skill performance.


- Curious users: Explore benchmark results to see how well OVOS handles your language.

## Further reading

- [Cloning Voices for Endangered Languages: Asturian & Aragonese](https://blog.openvoiceos.org/posts/2025-12-09-ast) — OVOS blog
- [Reflections on Our Collaboration: an Open Arabic Voice](https://blog.openvoiceos.org/posts/2025-10-01-arabic_tts_collaboration) — OVOS blog

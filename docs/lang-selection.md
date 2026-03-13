# Language Selection and Disambiguation

OpenVoiceOS is designed to be multi-language from the ground up. This page explains the technical logic used by `ovos-core` to determine which language should be used for a given user utterance.

---

## The Disambiguation Logic

When a `recognizer_loop:utterance` message arrives on the [MessageBus](bus-service.md), `ovos-core` (specifically the `IntentService`) runs a disambiguation routine to decide which language to use for intent matching.

The service checks the following message context keys in order of priority:

| Priority | Context Key | Source |
|---|---|---|
| **1** | `stt_lang` | Set by the STT engine that transcribed the speech. |
| **2** | `request_lang` | Volunteered by the source (e.g., a specific wake word or remote client). |
| **3** | `detected_lang` | Set by a [Transformer](transformer-plugins.md) plugin (e.g., a language classifier). |
| **4** | *Default* | The system default `lang` from `mycroft.conf` or the message's `data["lang"]`. |

### Validation against `valid_langs`

The identified language is validated against the list of enabled languages (`valid_langs` in config). OVOS uses the `langcodes` library to find the closest match:

*   If a match is found within a "distance" of 10 (standard regional difference), that language is used.
*   If no valid match is found, the system logs a warning and falls back to the system default language.

---

## Language Helper Utilities

Developers can use standard helpers from `ovos-utils` to handle BCP-47 tags correctly.

### `standardize_lang_tag(lang_code)`
Normalizes a language tag to a canonical form (e.g., `"en-us"` -> `"en-US"`). It is used internally to ensure comparisons are reliable.

### `get_language_dir(base_path, lang)`
A crucial helper for [Skills](skill-design-guidelines.md). It scans a directory (like `locale/`) and returns the best matching subdirectory for the requested language, tolerating regional variations.

---

## Configuration Helpers

The `ovos-config` library provides several helpers to retrieve language settings from `mycroft.conf`.

### `get_default_lang()`
Returns the primary language tag for the system.

### `get_valid_languages()`
Returns a list of all enabled language tags. This is used by the Intent Service to know which languages are allowed for matching.

### `get_config_langs()`
Returns a prioritized list of languages to try, often starting with the current session language and falling back to the system default.

---

## Multilingual Intent Matching

If `intents.multilingual_matching` is enabled in `mycroft.conf`, the intent pipeline will attempt to match the utterance in **all** configured languages if the primary disambiguated language fails to produce a match.

This allows for seamless switching between languages without manual reconfiguration.

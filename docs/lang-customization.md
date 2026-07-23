# Customizing Language Resources

!!! abstract "In a nutshell"
    Every skill ships small text files that say what phrases to listen for and what to say back. This page shows how to swap in your own versions of those files — to reword a reply, fix wording for your accent or dialect, or add a language a skill doesn't include — all without editing the skill's actual code. You drop your edited copy into a personal folder, and OVOS loads yours instead, falling back to the skill's original for anything you didn't change. See [Language Support](lang-support.md) for the bigger picture, or the [Glossary](glossary.md) for terms.

OpenVoiceOS lets you override or extend a skill's **locale resources** — the plain-text files that tell the assistant what to listen for and what to say — without touching the skill's source code. This is how you localize responses, fix intent matching for your accent, reword a reply, or add a language a skill doesn't ship.

**New here?** A skill ships small text files grouped by language. You can drop your own copy of any one of those files into a user folder, and OVOS will load yours instead of the skill's. You only override the files you care about; everything else falls back to the skill.

??? info "📐 Formal specification"
    Locale resource layout and file formats are defined by **[OVOS-INTENT-2 — Locale Resource Formats](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-2.md)** (companion to [OVOS-INTENT-1](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-1.md), the sentence-template grammar). See the [spec index](architecture-specs.md). This page describes how OVOS implements that spec; the spec is the normative reference.

---

## Resource Roles

Per OVOS-INTENT-2, every resource is identified by a **(role, base name)** pair, where the role is the file **extension**. There are five roles:

| Role | Extension | Slots? | Purpose |
|------|-----------|--------|---------|
| Intent | `.intent` | yes (slot-bearing) | Templates matched against the user's speech (ASR input). Slots are filled by the engine at match time. |
| Dialog | `.dialog` | yes (slot-bearing) | Phrases the assistant speaks back (TTS output). Slots are filled by the skill before speaking. |
| Entity | `.entity` | no (slot-free) | Example values that can fill a named slot. |
| Vocabulary | `.voc` | no (slot-free) | A named set of localized phrasings. |
| Blacklist | `.blacklist` | no (slot-free) | Words that suppress an intent. |

Two files may share a base name only if their roles differ (`confirm.intent` and `confirm.dialog` are distinct resources); two files with the **same** extension must not share a base name anywhere in one language's directory tree.

---

## Locale Folder Layout

All localized resources live under a single `locale/` directory, with **one subdirectory per language**, named with a BCP-47 tag (case-insensitive — `en-US` and `en-us` are the same):

```text
my-skill/
└── locale/
    ├── en-US/
    │   ├── turn_on.intent
    │   ├── confirm.dialog
    │   ├── device.entity
    │   ├── thing.voc
    │   └── dialogs/            # subdirectories are allowed…
    │       └── greeting.dialog # …and searched recursively
    └── pt-BR/
        └── …
```

A language directory **may** contain subdirectories; a loader resolves a resource by searching the language directory and all its subdirectories recursively. Subdirectory names are an authoring convenience and carry no meaning to the loader.

!!! note "Legacy layouts"
    Older skills used `vocab/<lang>/` and `dialog/<lang>/` directories instead of `locale/<lang>/`. OVOS still searches these for backwards compatibility, but new skills and overrides should use `locale/`.

---

## Resolution Precedence

The same resource — the same `(role, base name)` pair — may exist in three places. OVOS resolves it in this order (**first match wins**):

1. **User overrides** — `<xdg_data>/resources/<skill_id>/locale/<lang>/`
2. **Skill resources** — the skill's own bundled `locale/<lang>/`
3. **Core resources** — fallback files shipped by the framework (e.g. `ovos-workshop`)

Overrides apply at **whole-file granularity**: an override file replaces the corresponding lower-precedence file entirely. You do **not** merge line-by-line, and you do **not** need to copy files you aren't changing.

### Where the user override folder lives

The user override base is `<xdg_data>/resources/<skill_id>/`, where `<xdg_data>` is the XDG data path — by default `~/.local/share/mycroft`. So a typical override file path is:

```text
~/.local/share/mycroft/resources/<skill_id>/locale/<lang>/<file>
```

### How to Override

1. **Find the skill ID** — e.g. `ovos-skill-weather.openvoiceos`.
2. **Create the folders** — `~/.local/share/mycroft/resources/<skill_id>/locale/<lang>/`.
3. **Copy and edit** — copy the `.dialog`, `.intent`, `.voc`, `.entity`, or `.blacklist` file you want to change from the skill's source into that folder and edit it.
4. **Restart** `ovos-core` to pick up the change.

!!! tip "Partial overrides"
    Only place the specific files you want to change. The loader falls back to the skill (and then core) resources for everything you didn't override.

### Language fallback

If the requested language has no directory, the loader prefers an exact match but **may** fall back to the nearest available language. OVOS uses the `langcodes` `tag_distance()` function and treats a distance below `10` as a usable regional match (e.g. `en-au` resolving to `en-us`). Per the spec this fallback is an implementation choice, not a guarantee — ship the exact language directory you need.

---

## File Format Basics

All five roles are line-oriented UTF-8 text (OVOS-INTENT-2 §3):

- one template per line;
- blank lines and lines beginning with `#` (comments) are skipped;
- both `LF` and `CRLF` line endings are accepted.

Slot-bearing files (`.intent`, `.dialog`) use the OVOS-INTENT-1 sentence-template grammar — expansion `(a|b)` / optional `[x]` and named slots `{name}`. Slot-free files (`.entity`, `.voc`, `.blacklist`) use expansion only, with no `{slots}`.

```text
# turn_on.intent  (slot-bearing)
turn on (the|) {device}
(switch|power) on {device}
```

```text
# thing.voc  (slot-free)
light
lamp
```

---

## System-wide Resource Overrides

Some core, non-skill resources (sounds, common error/boot dialogs) are resolved by the framework outside the per-skill scheme above. Custom `.wav` sounds and core `.dialog` files placed in the framework's resource locations let you rebrand the assistant's "personality". These paths are framework-defined; only the `locale/<lang>/` layout beneath a resource root is normative.

---

## Customizing Number, Date, and Language-Name Parsers

The technical parsers for numbers, dates, and spoken language names are separate libraries, not skill resources:

- **Language names** — `ovos-lang-parser` maps BCP-47 codes to spoken names.
- **Numbers** — `ovos-number-parser` (e.g. if "22nd" doesn't parse in your language).
- **Dates** — `ovos-date-parser`.

These are rule-driven per language. Fixes are best contributed upstream to the respective repository so every install benefits; local edits to an installed package are not persistent across upgrades.

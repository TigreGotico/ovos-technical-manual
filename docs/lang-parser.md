
# ovos-lang-parser

OpenVoiceOS's multilingual language-name parsing and pronouncing library. It converts spoken language names ("Spanish", "Espagnol") to BCP-47 codes (`"es"`) and vice versa, enabling skills and components to handle language-selection commands in natural speech.

## Why it exists

OVOS supports runtime language switching and multi-language awareness. When a user says "switch to French" or "reply in German", the platform needs to map a spoken word to a BCP-47 code. Conversely, when displaying or speaking the name of a language back to the user, the platform needs the localized spoken name. `ovos-lang-parser` provides both directions for any supported OVOS UI language.

---

## Package layout

| File | Responsibility |
|------|---------------|
| `ovos_lang_parser/__init__.py` | Entire public API — 3 functions |
| `ovos_lang_parser/res/<lang>/langs.json` | Per-UI-language JSON files mapping BCP-47 codes to their spoken name(s) in that UI language |

Dependencies: `langcodes` (closest language match), `ovos-utils` (bracket template expansion, fuzzy `match_one`).

---

## Architecture

The library is intentionally minimal. `__init__.py` contains three functions and a module-level resource directory scan:

```python
RES_DIR = f"{os.path.dirname(__file__)}/res"
LANGS = os.listdir(RES_DIR)    # list of language codes with resource files
```

### `get_lang_data(lang)`

1. Uses `langcodes.closest_match(lang, LANGS)` to tolerate BCP-47 variants (e.g. `"en-US"` matches `"en"`). Raises `ValueError` if distance > 10.
2. Opens `res/<closest_lang>/langs.json`.
3. Expands bracket templates (e.g. `"[Español|Castellano]"` → `["Español", "Castellano"]`) using `ovos_utils.bracket_expansion.expand_template`.
4. Returns a flat `dict` of `spoken_name → bcp47_code` for all known languages in that UI language.

The `langs.json` format maps BCP-47 codes to one or more spoken names:

```json
{
  "en": "English",
  "es": "[Spanish|Español|Castellano]",
  "fr": "French"
}
```

---

## API reference

All three public functions are defined in `ovos_lang_parser/__init__.py`.

### `get_lang_data`

```python
def get_lang_data(lang: str) -> dict
```

Return the full spoken-name-to-code mapping for UI language `lang`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `lang` | `str` | BCP-47 code of the UI language (the language the user is speaking in) |

Returns `dict[spoken_name, bcp47_code]`. Multiple spoken names for the same language produce multiple keys mapping to the same code.

Raises `ValueError` if no resource file is close enough to `lang` (closeness threshold: distance ≤ 10 in `langcodes.closest_match`).

---

### `extract_langcode`

```python
def extract_langcode(text: str, lang: str) -> Tuple[str, float]
```

Identify the language being referred to in `text`, where the user is speaking in `lang`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Utterance containing a language name, e.g. `"set the language to French"` |
| `lang` | `str` | BCP-47 code of the UI language |

Returns `(bcp47_code, confidence_score)` — the best-matching language code and its match confidence (0.0–1.0). Uses `ovos_utils.parse.match_one` with `MatchStrategy.TOKEN_SET_RATIO`.

Example:
```python
extract_langcode("switch to Spanish please", "en")
# ("es", 0.95)
```

---

### `pronounce_lang`

```python
def pronounce_lang(lang_code: str, lang: str) -> str
```

Return the spoken name of a language code in the UI language `lang`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `lang_code` | `str` | BCP-47 code of the language to pronounce, e.g. `"fr"` |
| `lang` | `str` | BCP-47 code of the UI language |

Returns a single spoken name string. If multiple names exist, the first is returned. Falls back to the `lang_code` itself if no entry is found.

Example:
```python
pronounce_lang("fr", "en")   # "French"
pronounce_lang("es", "en")   # "Spanish"
pronounce_lang("en", "fr")   # "Anglais"
```

---

## Language resource files

Resources live in `ovos_lang_parser/res/<lang>/langs.json`. Each file is written in the UI language indicated by the directory name and lists language names as they would be spoken by a user of that UI language.

The bracket template syntax `"[Name1|Name2]"` is expanded to a list of valid spoken forms, allowing for multiple correct names (e.g., both "Spanish" and "Castilian" map to `"es"` in English).

---

## Cross-references

| Package | Relationship |
|---------|-------------|
| `ovos-bus-client` | Uses `ovos-lang-parser` for language normalization in message contexts |
| `ovos-core` | Language selection commands handled via skills that call this library |
| `ovos-workshop` | Skill helpers for language-switching may use this library |
| `ovos-number-parser` | Peer library in the OVOS NLP stack; not a dependency |
| `ovos-date-parser` | Peer library in the OVOS NLP stack; not a dependency |
| `ovos-color-parser` | Peer library in the OVOS NLP stack; not a dependency |

See also:
- [Number Parser](number-parser.md)
- [Date Parser](date-parser.md)
- [Color Parser](color-parser.md)

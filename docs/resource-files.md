# Resource Files

!!! abstract "In a nutshell"
    Skills keep their words in separate text files rather than buried in the program code. These "resource files" hold things like the phrases the assistant can say, the example sentences it listens for, and the keywords it recognizes — each language gets its own folder. This separation makes a skill easy to translate and tweak without touching the code. This page explains the folder layout and the kinds of files. See also [Statements](statements.md) for spoken replies and the [Glossary](glossary.md).

??? info "📐 Formal specification"
    The locale folder layout and the plain-text resource formats are specified by **[OVOS-INTENT-2 — Locale Resource Formats](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-2.md)** (a formal [architecture spec](architecture-specs.md)); the template grammar inside them is **[OVOS-INTENT-1](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-1.md)**. OVOS-INTENT-2 defines **six canonical roles** by extension: `.intent` and `.dialog` (slot-bearing — they may use `{name}` slots), `.entity`, `.voc`, and `.blacklist` (slot-free — expansion only), and `.prompt` (a whole-file language-model prompt with `{{name}}` substitution, **not** a template). Resources live under `locale/<lang>/` (BCP-47 tags, compared case-insensitively, searched recursively), resolved user → skill → core (§2.1). The `.rx`, `.list`, and `.word` files below are **framework extensions**, not OVOS-INTENT-2 roles — prefer `.entity`/`.voc`/`.blacklist` for portability.

Skills load localized resources from a structured directory layout. Resources are loaded automatically at startup for every language in `native_langs` (`core_lang` + `secondary_langs`).

## Directory Layout

The recommended layout uses a single `locale/` directory:

```text
my-skill/
├── locale/
│   ├── en-US/
│   │   ├── my.dialog        # spoken responses
│   │   ├── my.intent        # padatious intent examples
│   │   ├── my.voc           # adapt vocabulary keywords
│   │   ├── my.entity        # adapt entity examples
│   │   ├── my.rx            # regex patterns for adapt
│   │   └── skill.json       # skill metadata (examples for homescreen)
│   └── es-ES/
│       ├── my.dialog
│       └── my.intent
└── gui/
    └── my_page.qml

```

Legacy skills may use separate `dialog/`, `vocab/`, `regex/` subdirectories — these are still supported.

## Resource Types

| Extension | Type | Description |
|---|---|---|
| `.dialog` | Dialog | Spoken responses, one template per line, random selection (OVOS-INTENT-2 role; slot-bearing) |
| `.intent` | Intent | [Padatious](padatious-pipeline.md) training examples (OVOS-INTENT-2 role; slot-bearing) |
| `.voc` | Vocabulary | [Adapt](adapt-pipeline.md) keyword definitions, one per line, first is canonical (OVOS-INTENT-2 role; slot-free) |
| `.entity` | Entity | Example values for a `{slot}` (OVOS-INTENT-2 role; slot-free) |
| `.blacklist` | Blacklist | Phrases that suppress a paired `.intent` (OVOS-INTENT-2 role; slot-free) |
| `.prompt` | Prompt | A whole-file language-model prompt with `{{name}}` substitution (OVOS-INTENT-2 role) |
| `.rx` | Regex | Adapt regex patterns (**framework extension**, not an OVOS-INTENT-2 role) |
| `.list` | List | A flat list resource (**framework extension**) |
| `.word` | Word | A single word (**framework extension**) |
| `skill.json` | Metadata | `{"examples": ["...", "..."]}` for homescreen example utterances (**framework extension**) |

## Dialog Files

Each line in a `.dialog` file is a possible response. One line is chosen randomly when `speak_dialog` is called:

```text

# my.dialog
Hello there!
Hi! How are you?
Greetings, {name}!

```

Mustache template variables are filled from the `data` dict:

```python
self.speak_dialog("my", data={"name": "Alice"})

```

## Vocab Files (Adapt)

Each line is registered as its own keyword, and every line matches the same entity:

```text

# hello.voc
hello
hi
hey there
good morning

```

Parenthesized alternation expands *within a single line*: `(hello|hi|hey)` becomes several forms
that share one canonical value — the first — with the rest registered as its aliases. That
canonical/alias relationship exists only inside the line that produced it. Separate plain lines
are independent keywords with no aliasing between them, so write alternatives on one line if you
want them collapsed into a single canonical form plus aliases:

```text

# hello.voc
(hello|hi|hey there|good morning)

```

The Adapt entity name is the file name without its extension (`hello` for `hello.voc`); reference it in an `IntentBuilder` with `.require("hello")` / `.optionally("hello")`. Internally the keyword is namespaced as `alphanumeric_skill_id + "hello"` so skills never collide.

## Intent Files (Padatious)

One example utterance per line. Supports entity slots `{entity}` and alternation `(a | b)`:

```text

# my.intent
what is the weather in {location}
(show | tell me) the weather

```

## Language [Fallback](fallback-pipeline.md)

When a resource is not found for the exact `lang`, the skill falls back to dialects of the same language. For example, if `en-AU` is requested but only `en-US` resources exist, `en-US` is used.

## Loading Resources Manually

```python

# Get SkillResources for current lang
resources = self.resources                         # current self.lang
resources = self.load_lang(self.res_dir, "es-ES")  # specific lang

# Find a specific file
path = self.find_resource("my.dialog", "dialog")
path = self.find_resource("hello.mp3", "snd")

```

## SkillResources API

`SkillResources` is returned by `self.resources` and `self.load_lang()`:

```python

# Render a dialog (returns a string, does not speak)
text = self.resources.render_dialog("my.dialog", data={"key": "value"})

# Check if a vocab word matches
matches = self.voc_match("hello there", "hello")  # True

# Load a vocab file into a list
words = self.resources.load_vocabulary_file("my.voc")

# Load a dialog renderer
renderer = self.dialog_renderer

```

## `skill.json` Metadata

Optional file for homescreen integration. Placed at `locale/<lang>/skill.json`:

```json
{
  "name": "My Skill",
  "description": "Does something useful",
  "examples": [
    "what is the weather",
    "tell me the weather in Paris"
  ]
}

```

These examples are emitted to the homescreen as `homescreen.register.examples` on skill startup.

---

*Source code: [OpenVoiceOS/ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop).*

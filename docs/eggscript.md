# Eggscript

Eggscript is a small markup language that compiles into a valid OVOS [Skill](skill-design-guidelines.md) (or a standalone Python chatbot). It is the fastest way to go from "I want the assistant to say X when the user says Y" to a real, installable, testable skill — without writing skill boilerplate by hand.

> **EXPERIMENTAL** — the language and tooling are still evolving (current language spec `v0.2`).

**What you get:**

- A plain-text format where one line ≈ one piece of behaviour: `#` declares an intent, `+` adds a training phrase, `-`/`>` add responses.
- An interactive terminal interpreter to test scripts before compiling anything.
- A compiler that emits a complete OVOS skill package (with tests) or a standalone chatbot script.
- A linter that catches mistakes (undefined slot references, parse errors) before you run.

The package is published as `ovos-eggscript`; the source lives on [GitHub](https://github.com/OpenVoiceOS/eggscript).

## Installation

```bash
pip install ovos-eggscript

# or, from source:
git clone https://github.com/OpenVoiceOS/eggscript
cd eggscript
pip install -e .
```

This installs the `eggscript` console command (and an `eggscript-lint` alias) plus the `eggscript` Python package.

## The `eggscript` CLI

```
eggscript <command> [args]
```

| Command | Purpose |
|---|---|
| `eggscript lint <files...>` | Static analysis: parse errors and warnings. `-Werror` treats warnings as errors, `--no-info` hides info-level diagnostics, `--format {human,json}` selects output. |
| `eggscript parse <file>` | Parse one file and dump its AST (intents, slots, actions). `--debug` for verbose parsing. |
| `eggscript run <file>` | Start the interactive CLI interpreter on a script (Ctrl-D / Ctrl-C to exit). |
| `eggscript compile <file> -o <dir> [-t {ovos,cli}]` | Compile to an OVOS skill (`-t ovos`, default) or a standalone chatbot (`-t cli`). `-o/--output` is required. |
| `eggscript version` | Print the version and language-spec level. |

`eggscript-lint` is a back-compat alias for `eggscript lint`.

Compiling an OVOS skill prints follow-up commands, e.g.:

```bash
eggscript compile greet.eggscript -t ovos -o greet-skill
# compiled OVOS skill → greet-skill/
#   install:  pip install -e 'greet-skill[test]'
#   test:     pytest greet-skill/tests/
```

Compiling a standalone chatbot (`-t cli`) emits `<dir>/chatbot.py`, runnable with `python <dir>/chatbot.py`.

## Language Crash Course

Every non-comment, non-blank line starts with exactly one sigil. **Indentation is cosmetic — it is not significant.**

| Sigil | Purpose |
|---|---|
| `//` | comment — ignored |
| `@key value` | directive (metadata or structural) |
| `#` | intent header |
| `+` | user utterance / training phrase (may declare slots) |
| `-` | bot response; consecutive `-` lines are **alternates** (one is picked) |
| `>` | bot response; consecutive `>` lines are **sequential** (all are spoken, in order) |
| ` ``` ` | open/close a Python code block |

### A minimal script

`hello.eggscript`:

```eggscript
// metadata can be set once, anywhere
@name hello world
@author jarbasai
@email jarbasai@mailfence.com
@license MIT
@url https://github.com/author/repo
@version 0.1.0

// intent definition
# hello world
+ hello world
- hello world

// optional python, runs after the dialog is selected
```
print("python code!")
```
```

### Metadata directives (set once)

| Directive | Effect |
|---|---|
| `@name` | skill display name |
| `@author` | skill author |
| `@email` | author email |
| `@license` | license identifier (`MIT`, `Apache-2.0`, …) |
| `@url` | repository or project URL |
| `@version` | skill version string |
| `@lang` | BCP-47 language tag (default `en-us`) |
| `@pkgname` | override the generated Python package name |

### Slots

Declare slots inside `+` lines and reference them in `-`/`>` lines or code blocks with `{name}`:

```eggscript
# weather in location
+ how is the weather in {location}
- how am i supposed to know the weather in {location}
```

Slots can be typed and/or optional:

| Form | Meaning |
|---|---|
| `{name}` / `{name:str}` | string slot (default) |
| `{name:int}` | integer; coercion failure means the intent does not match |
| `{name:float}` | float; same coercion rule |
| `{name?}` / `{name:int?}` | optional (typed) slot |

Slot names match `[a-z_][a-z0-9_]*` and are intent-local. The names `scope`, `session`, `lang`, `intent`, and `layer` are reserved. Referencing a `{name}` that is neither a declared slot nor assigned in a prior code block is a **parse-time error** — the script refuses to load.

### Alternate vs sequential responses

```eggscript
# count to 5
+ count to 5
// consecutive `-` = alternates (one chosen at random)
- i will only count to 5
- i only know how to count to 5

# count up
+ count
// consecutive `>` = sequential (all spoken, in order)
> 1
> 2
> 3
> 4
> 5
```

### Python code blocks

Fenced with triple backticks. Inside, two dicts are available:

- `scope` — built fresh each turn from slot values; mutations are visible to later `-`/`>` lines of the same intent.
- `session` — persists across turns; use it to remember user state.

```eggscript
# double
+ count {n:int}
```
scope["double"] = scope["n"] * 2
session["last_count"] = scope["n"]
```
- {n} doubled is {double}
```

Only `scope[...]` and `session[...]` writes are visible to dialog lines; bare local assignments (`x = ...`) are not. A code block placed between `+` and `-`/`>` runs after slot fill and before the dialog speaks; a block after the dialog lines runs after speaking.

### Intent layers

Layer 1 is always active. An intent in a higher layer can match only when that layer is in the active set. Layers are controlled with structural directives:

| Directive | Effect |
|---|---|
| `@layer N` | place the **next** `#` intent in layer N (default 1); consumed once |
| `@enable N` | when this intent fires, enable layer N |
| `@disable N` | when this intent fires, disable layer N |

```eggscript
# tell me about
+ tell me about {thing}
- {thing} exists
// enable layer 2 when this intent fires
@enable 2

// gate the next intent behind layer 2
@layer 2
# tell me more
+ tell me more
+ continue
- i do not know more
// turn layer 2 back off
@disable 2
```

## Python API

The CLI wraps a small Python API you can also use directly.

Run a script interactively:

```python
from eggscript import CliInterpreter

c = CliInterpreter()
c.load_eggscript_file("dialogs.eggscript")
c.run()
```

Compile to an OVOS skill or standalone chatbot:

```python
from eggscript import OVOSSkillCompiler, CliCompiler

c = OVOSSkillCompiler()
c.load_eggscript_file("layers.eggscript")
c.export("myskill")           # writes an OVOS skill package to ./myskill

CliCompiler().load_eggscript_file("layers.eggscript")  # standalone chatbot
```

Lint from Python:

```python
from eggscript import lint_file, Severity

diagnostics = lint_file("greet.eggscript")
for d in diagnostics:
    print(d.severity, d.message)
```

`eggscript` also exports `EggParser` (for parsing/AST access), `lint`, `Diagnostic`, and `Severity`.

After compiling, continue extending the exported skill to add more advanced functionality. For the normative language definition, slot grammar, and worked examples see the [`docs/`](https://github.com/OpenVoiceOS/eggscript/tree/dev/docs) tree in the repository (`language-reference.md`, `tutorial.md`, and `cookbook.md`).

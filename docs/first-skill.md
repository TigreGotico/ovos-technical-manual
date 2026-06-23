# Your First Skill

!!! abstract "In a nutshell"
    A **skill** is an add-on that teaches OVOS a new ability. This page is a hands-on
    walkthrough: you'll create a tiny skill from scratch, install it, and talk to it — in about
    ten minutes. You only need to be comfortable creating a few text files. New to the words
    here? Keep the [Glossary](glossary.md) open.

By the end you'll have a skill that answers when you say *"hello"*. Once you've done it once,
every other skill is just more of the same idea.

## What a skill is made of

A skill is a small folder with three kinds of files:

| File | What it holds | Example |
|---|---|---|
| **the skill code** (`__init__.py`) | the Python that runs when an intent matches | "when the user says hello, speak a greeting" |
| **intent files** (`*.intent`) | example sentences **the user might say** | `hello`, `hi there` |
| **dialog files** (`*.dialog`) | lines **OVOS can speak back** (it picks one at random) | `Hello! Nice to meet you.` |

The intent and dialog files live in a `locale/<language>/` folder, so the same skill can be
translated. That's the whole model — [Anatomy of a Skill](skill-structure.md) covers it in depth.

## Step 1 — Create the folder layout

Make this structure (replace `youruser` with your name/handle later):

```
ovos-skill-my-first/
├── pyproject.toml
└── ovos_skill_my_first/
    ├── __init__.py
    └── locale/
        └── en-US/
            ├── intents/
            │   └── Hello.intent
            └── dialog/
                └── hello.dialog
```

## Step 2 — Write the skill code

`ovos_skill_my_first/__init__.py`:

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler


class MyFirstSkill(OVOSSkill):

    @intent_handler("Hello.intent")
    def handle_hello(self, message):
        self.speak_dialog("hello")
```

That's the entire skill. `@intent_handler("Hello.intent")` says *"run this function when the
user says something matching `Hello.intent`"*, and `self.speak_dialog("hello")` speaks a random
line from `hello.dialog`. (The class **must** subclass [`OVOSSkill`](ovos-skill.md).)

## Step 3 — Tell OVOS what the user might say

`ovos_skill_my_first/locale/en-US/intents/Hello.intent` — one example phrase per line. OVOS
learns the *pattern* from these, so you don't have to list every wording:

```
hello
hi there
say hello
greet me
```

## Step 4 — Write what OVOS says back

`ovos_skill_my_first/locale/en-US/dialog/hello.dialog` — one option per line; OVOS picks one at
random so the assistant doesn't sound robotic:

```
Hello! Nice to meet you.
Hi there!
Hey — how can I help?
```

## Step 5 — Make it installable

A skill is just a Python package that advertises itself to OVOS through an **entry point**.
`pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ovos-skill-my-first"
version = "0.0.1"
description = "My first OVOS skill"
license = {text = "Apache-2.0"}
dependencies = ["ovos-workshop"]

# "<skill-name>.<author>" becomes the skill_id; the right-hand side is package:ClassName
[project.entry-points."opm.skill"]
"my-first.youruser" = "ovos_skill_my_first:MyFirstSkill"

[tool.setuptools]
packages = ["ovos_skill_my_first"]

[tool.setuptools.package-data]
ovos_skill_my_first = ["locale/*/*/*"]
```

The entry-point key (`my-first.youruser`) becomes your skill's **`skill_id`**
(`<skill-name>.<author>`); the value points at your skill class. The `opm.skill` group is
how the [Plugin Manager](plugin-manager.md) discovers installed skills.

## Step 6 — Install it and talk to it

From inside the `ovos-skill-my-first/` folder:

```bash
pip install -e .
```

Restart `ovos-core` (or it will pick the skill up on its next scan). Then say:

> "Hey Mycroft, **hello**"

…and OVOS replies with one of your dialog lines. 🎉 You just wrote a skill.

## Where to go next

- **Pull a value out of what the user said** (a name, a city, a number) — see [Intent Design](intents.md).
- **Have a back-and-forth** ("what's your name?" → reply) — see [Continuous Conversation](converse.md).
- **Save settings or files** — see [Skill Settings](skill-settings.md) and [Filesystem](skill-filesystem.md).
- **Make it sound good and behave well** — see [Skill Best Practices](skill-best-practices.md).
- **Test it automatically** — see [Skill Testing](skill-testing.md).
- Browse real skills for ideas in [Skill Examples](skill-examples.md).

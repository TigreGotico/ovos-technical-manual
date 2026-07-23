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

```text
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

!!! note "Both layouts work"
    OVOS walks the *entire* `locale/<lang>/` folder looking for a file by name, so grouping
    files into `intents/`/`dialog/` subfolders (as above) or dropping them flat directly in
    `locale/en-US/` both work equally well — pick whichever keeps your skill readable. The
    language folder name itself is also case-insensitive (`en-US` and `en-us` are the same
    folder to OVOS). See [Anatomy of a Skill](skill-structure.md) and
    [Intent Design](intents.md) for more on this layout.

## Step 2 — Write the skill code

Every skill is a Python class that subclasses [`OVOSSkill`](ovos-skill.md). A **decorator** — a
line starting with `@` placed just above a function — tells OVOS what that function is for; here
`@intent_handler("Hello.intent")` means *"run this function when the user says something matching
`Hello.intent`"* (see [Decorators](decorators.md) for the full list). `self.speak_dialog("hello")`
then speaks a random line from `hello.dialog`.

`ovos_skill_my_first/__init__.py`:

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler


class MyFirstSkill(OVOSSkill):

    def initialize(self):
        # runs once, after the skill is fully loaded and connected to the bus —
        # this is the place for setup that needs self.settings, self.bus, etc.
        # (a plain __init__ still runs too early for that; see Skill Settings)
        self.log.info("MyFirstSkill is ready")

    @intent_handler("Hello.intent")
    def handle_hello(self, message):
        self.speak_dialog("hello")
```

That's the entire skill. `initialize()` is optional — you only need it once you have setup work
that depends on the skill being fully wired up (reading [settings](skill-settings.md), registering
extra event handlers, and so on).

## Step 3 — Tell OVOS what the user might say

`ovos_skill_my_first/locale/en-US/intents/Hello.intent` — one example phrase per line. OVOS
learns the *pattern* from these, so you don't have to list every wording:

```text
hello
hi there
say hello
greet me
```

## Step 4 — Write what OVOS says back

`ovos_skill_my_first/locale/en-US/dialog/hello.dialog` — one option per line; OVOS picks one at
random so the assistant doesn't sound robotic:

```text
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

Restart `ovos-core` (or it will pick the skill up on its next scan) — see
[Stage 1 of Troubleshooting](troubleshooting.md#stage-1-is-the-service-even-running-and-is-the-bus-reachable)
for exactly how to start/restart the OVOS services. Then say your configured wake word first
(default **"Hey Mycroft"**), wait for the listening chime, and then say:

> "**hello**"

…and OVOS replies with one of your dialog lines. 🎉 You just wrote a skill.

!!! note "If OVOS doesn't reply"
    Check the skills log for your skill_id: `ovos-logs show -l skills` — see
    [Troubleshooting](troubleshooting.md) for how to read what it's telling you.

!!! tip "No microphone handy, or want to test without talking?"
    You can send the utterance straight onto the bus as text, skipping the wake word and mic
    entirely: `ovos-say-to "hello"`. See [Troubleshooting](troubleshooting.md#stage-3-did-stt-produce-text)
    for more on this and other text-based ways to test a skill.

## Where to go next

- **Pull a value out of what the user said** (a name, a city, a number) — see [Intent Design](intents.md).
- **Have a back-and-forth** ("what's your name?" → reply) — see [Continuous Conversation](converse.md).
- **Save settings or files** — see [Skill Settings](skill-settings.md) and [Filesystem](skill-filesystem.md).
- **Make it sound good and behave well** — see [Skill Best Practices](skill-best-practices.md).
- **Test it automatically** — see [Skill Testing](ovoscope-overview.md).
- **See how an utterance actually travels through OVOS** — see [Life of an Utterance](life-of-an-utterance.md).
- Browse real skills for ideas in [Skill Examples](skill-examples.md).
- Questions along the way? Ask in the
  [skills channel on OVOS Chat](https://matrix.to/#/#openvoiceos-skills:matrix.org).

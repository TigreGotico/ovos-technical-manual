# Skill Metadata File

!!! abstract "In a nutshell"
    `skill.json` is a small "info card" for your skill — its name, a short description, an icon, and a few example phrases. OVOS and skill stores read this card to install your skill and show it off nicely in menus and on screens, much like the listing page for an app in an app store. It does not change what the skill does; it just describes it. For the saved-preferences side of things see [Skill Settings](skill-settings.md); for term definitions see the [Glossary](glossary.md).

The `skill.json` file is an optional but powerful way to describe your Open Voice OS (OVOS) skill. It provides metadata used for installation, discovery, and display in GUIs or app stores.

## Purpose

- Helps OVOS identify and install your skill.


- Enhances GUI experiences with visuals and usage examples.


- Lays the foundation for future help dialogs and skill documentation features.

---

## Usage Guide

1. Create a `skill.json` file inside your skill's `locale/<language-code>` folder.


2. Fill in the metadata fields as needed (see below).


3. If your skill supports multiple languages, include a separate `skill.json` in each corresponding `locale` subfolder.

> ⚠️ **Avoid using old `skill.json` formats** found in some legacy skills where the file exists at the root level. These are deprecated.

---

## Example `skill.json`

```json
{
  "skill_id": "skill-xxx.exampleauthor",
  "source": "https://github.com/ExampleAuthor/skill-xxx",
  "package_name": "ovos-skill-xxx",
  "pip_spec": "git+https://github.com/ExampleAuthor/skill-xxx@main",
  "license": "Apache-2.0",
  "author": "ExampleAuthor",
  "extra_plugins": {
    "core": ["ovos-utterance-transformer-xxx"],
    "PHAL": ["ovos-PHAL-xxx"],
    "listener": ["ovos-audio-transformer-xxx", "ovos-ww-plugin-xxx", "ovos-vad-plugin-xxx", "ovos-stt-plugin-xxx"],
    "audio": ["ovos-dialog-transformer-xxx", "ovos-tts-transformer-xxx", "ovos-tts-plugin-xxx"],
    "media": ["ovos-ocp-xxx", "ovos-media-xxx"],
    "gui": ["ovos-gui-extension-xxx"]
  },
  "icon": "http://example.com/icon.svg",
  "images": ["http://example.com/logo.png", "http://example.com/screenshot.png"],
  "name": "My Skill",
  "description": "Does awesome skill stuff!",
  "examples": [
    "do the thing",
    "say this to use the skill"
  ],
  "tags": ["productivity", "entertainment", "aliens"]
}

```

---

## Field Reference

None of these fields are enforced by `ovos-workshop` at runtime — only
`examples` is actually read (it is registered with the homescreen so it can
show sample phrases for the skill). Everything else is a convention followed
by skill-store and CI tooling. Ecosystem lint tooling (the `check_skill.py`
compliance check used in CI) treats `skill_id`, `name`, `description`,
`examples`, and `tags` as the fields it expects to be present; treat the rest
as recommended, not mandatory.

| Field            | Type     | Recommended | Description |
|------------------|----------|----------|-------------|
| `skill_id`       | string   | ✅ Yes    | Unique ID, typically `repo.author` style (lowercase). |
| `source`         | string   | ❌ Optional | Git URL to install from source. |
| `package_name`   | string   | ❌ Optional | Python package name (e.g., for PyPI installs). |
| `pip_spec`       | string   | ❌ Optional | [PEP 508](https://peps.python.org/pep-0508/) install spec. |
| `license`        | string   | ❌ Optional | License ID (see [SPDX list](https://spdx.org/licenses/)). |
| `author`         | string   | ❌ Optional | Display name of the skill author. |
| `extra_plugins`  | object   | ❌ Optional | Dependencies to be installed in other OVOS services (not this skill). |
| `icon`           | string   | ❌ Optional | URL to a skill icon (SVG recommended). |
| `images`         | list     | ❌ Optional | Screenshots or promotional images. |
| `name`           | string   | ✅ Yes    | User-facing skill name (some skills use `title` instead or as well). |
| `description`    | string   | ✅ Yes    | Short, one-line summary of the skill. |
| `examples`       | list     | ✅ Yes    | Example utterances your skill handles — the only field `ovos-workshop` actually reads, to register with the homescreen. |
| `tags`           | list     | ✅ Yes    | Keywords for searchability. |

!!! note
    In practice, real-world `skill.json` files vary quite a bit — some use
    `title` instead of `name`, and older, auto-generated `skill.json` files
    (from the legacy skills-manager tooling) carry many more fields
    (`version`, `url`, `requirements`, `platforms`, and more). Stick to the
    fields above for new skills; anything extra is ignored by `ovos-workshop`.

---

## Language Support

To support multiple languages, place a `skill.json` file in each corresponding `locale/<lang>` folder. Fields like `name`, `description`, `examples`, and `tags` can be translated for that locale.

---

## Installation Behavior

`pip_spec`, `package_name`, and `source` are hints for skill-installer /
skill-store tooling about where to fetch a skill from — `ovos-workshop`
itself does not install skills or read these fields. Provide at least one
so external installers have somewhere to pull the skill from.

---

## Packaging: the `opm.skill` Entry Point

`skill.json` describes a skill for discovery and display, but it is not how OVOS *loads* an installed skill. A pip-installed skill is found through the `opm.skill` entry-point group (singular) declared in its `pyproject.toml` / `setup.py`:

```toml
[project.entry-points."opm.skill"]
"skill-xxx.exampleauthor" = "skill_xxx:MySkill"
```

The entry-point name is the `skill_id` and the value points at the skill class. `find_skill_plugins()` in `ovos-plugin-manager` enumerates this group to load skills.

---

## Tips & Caveats

- This metadata format is a **standard** part of the OVOS skill discovery process and continues to evolve to support new ecosystem features.


- `extra_plugins` allows for declaring companion plugins your skill may require, but that aren't direct Python dependencies.


- The [Skill store](https://store.openvoiceos.org) and GUI tools like `ovos-shell` use `icon`, `images`, `examples`, and `description` to present the skill visually.

---

## Sharing your skill

Once your skill works, publishing it is the same as publishing any Python package:

1. **Push it to a GitHub repository** under your own account (or the `OpenVoiceOS` org if you're
   contributing an official skill). The `source` field in `skill.json` should point at it.
2. **Optionally publish it to PyPI** so it can be installed with a plain `pip install`, and set
   `package_name` in `skill.json` to that PyPI name. Skills without a PyPI release are still
   installable directly from git via `pip_spec` (see the [PEP 508](https://peps.python.org/pep-0508/)
   spec syntax used there).
3. **List it on the [OVOS Skill store](https://store.openvoiceos.org)** — see
   [OVOS-skills-store](https://github.com/OpenVoiceOS/OVOS-skills-store) for how skills get added.
   The store reads the `skill.json` fields above (`name`, `description`, `examples`, `tags`,
   `icon`, `images`) to build the listing card, and `source`/`pip_spec`/`package_name` to know how
   to install it.

!!! tip
    A complete, accurate `skill.json` is what makes the difference between a bare repository link
    and a nicely presented store entry — see the [Field Reference](#field-reference) above.

## See Also

- [PEP 508 – Dependency specification](https://peps.python.org/pep-0508/)


- [SPDX License List](https://spdx.org/licenses/)

# Contributing to the OVOS Technical Manual

This manual is an mkdocs-material site. It serves two very different readers at once — someone
who has never run a voice assistant before, and a senior developer integrating a plugin — so
style choices here favor **clarity and honesty over brevity**. This guide collects the
conventions the existing pages already follow, so new contributions read as part of the same
manual rather than a patchwork.

## Brand and terminology

- Write the project name as **OpenVoiceOS** in prose (one word, two capital letters). Do not use
  "Open Voice OS" in new writing.
- Leave brand spelling untouched inside quoted material — log output, JSON example values,
  external article titles — where it should read exactly as the source does.
- Use **OVOS** as the short form after the first mention on a page.
- Expand jargon and acronyms on first use on a page (e.g. "Speech-to-Text (STT)"), even if the
  term is explained elsewhere in the manual — readers rarely start at the top.

## Headings

- New headings are sentence case ("Configuring the microphone", not "Configuring The
  Microphone"). This is a style for **new content only** — do not mass-rename existing headings
  purely for casing, since that breaks every incoming anchor link.
- Headings describe what the reader will learn or do, not just a component name — prefer "Adding
  a fallback handler" over "Handlers".

## Admonitions

mkdocs-material admonitions layer detail without forcing every reader through it. Use them with a
consistent meaning, not interchangeably:

| Admonition | Use it for |
|---|---|
| `!!! abstract "In a nutshell"` | The page-opening summary — what this is and why the reader should care, in plain language. Every page has exactly one, near the top. |
| `!!! info` | Background/context the reader can skip if they already know it (e.g. a formal spec pointer). |
| `!!! note` | An edge case or exception to the main explanation. |
| `!!! tip` | A shortcut, a recommended default, or a faster path than the one just described. |
| `!!! warning` | A risk of breaking something or a foot-gun, short of a security concern. |
| `!!! danger` | A security-relevant risk (data exposure, RCE-adjacent, credentials). |
| `??? example` / `??? abstract` (collapsible) | Reference material that is useful but would otherwise push the main flow down the page — tables of exhaustive options, deep API listings. |

## Code fences

Every fenced code block **must** carry a language tag (` ```python `, ` ```bash `, ` ```json `,
` ```yaml `, ` ```qml `, or ` ```text ` for logs/diagrams/plain output that isn't a real
language). This drives syntax highlighting and tells the reader what kind of block they are
looking at before reading it. A bare ` ``` ` is only ever acceptable for the *closing* fence.

## Timeless writing

- No "recently", "new in `<version>`", "as of `<date>`", and no changelog narration. The manual
  describes the system as it stands, not its history of getting there.
- No PR numbers or PR links in prose. If something is unreleased or still in development, mark it
  **Upcoming** (the bold word, nothing else) instead of citing the tracking issue or PR.
- No first-person voice, and no meta-commentary about the documentation itself (no "this section
  will...", "as we discussed above" — just say the thing).
- Never attribute or blame a change to a person; the manual describes the system, not its authors.
- Don't add funding, sponsorship, or grant-program mentions to page content.
- Internal links are relative, page-to-page (`other-page.md`, `other-page.md#anchor`), matching
  the rest of the manual — not absolute site URLs.

## Citing something that must not shift under the link

Most links in this manual point at a `dev` branch on purpose, so the reader always sees the
current wording. If you need to **cite** an exact passage elsewhere — an issue, a commit, another
project's docs — link to that file at a specific commit hash instead of `dev`, so the quoted text
cannot change after the fact.

## Single-sourcing facts that appear on more than one page

If the same fact needs to appear on two or more pages (e.g. an exact config value, an ordered
list that must stay byte-identical everywhere it's shown), put it once in `docs/snippets/` and
transclude it with `pymdownx.snippets`' include syntax:

```markdown
--8<-- "snippets/your-fact.md"
```

Never hand-copy the same list into two pages — it will drift. Update the snippet, not the pages
that include it.

## Verify before you write

Every factual claim — class names, method signatures, config keys, bus message types, CLI
commands — should be checked against the installed package or the upstream repository before it
goes in the manual. If a claim can't be verified, soften it or leave it out; don't guess.

## Page templates

Two shapes cover almost everything in this manual:

- **Tutorial** (a reader following along step by step to build something) — see
  [`first-skill.md`](docs/first-skill.md) as the reference example: a nutshell box, then
  numbered steps in the order a reader actually performs them, ending in a working result and a
  "Where next" pointer.
- **Reference** (a reader looking something up) — nutshell box, then a formal-specification
  pointer if one exists, then the technical detail organized under headings a reader can jump to,
  tables for enumerable facts, and a "Related Pages" section at the end.

## Adding a new page

1. Open with the nutshell box: 2-4 plain-language sentences — what this is, why the reader should
   care — before any jargon.
2. Progressively deepen from there; keep the technical depth, just layer it with admonitions
   instead of front-loading it.
3. Add the page to the nav in `mkdocs.yml` — every page must be reachable from navigation.
4. Run the site's pinned mkdocs build and confirm it introduces no new build warnings.

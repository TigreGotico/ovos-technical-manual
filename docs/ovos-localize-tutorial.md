# Contribute Translations with OVOS Localize

!!! abstract "In a nutshell"
    OVOS only speaks the languages that volunteers have translated it into — and you can be one of them without writing any code. OVOS Localize is a website where you translate the short phrases the assistant says and listens for, right in your browser. If you can use a translation app, you can help OVOS understand and speak your language. See the [Glossary](glossary.md) for unfamiliar terms.

Want OVOS to speak your language? You don't need to be a programmer to help. **OVOS
Localize** is a web app where you translate the phrases OVOS says and understands,
right in your browser — no code, no setup, no command line.

!!! info "What replaced GitLocalize"
    OVOS used to translate on a third-party service called *GitLocalize*. That has
    been **retired** and replaced by **[OVOS Localize](https://openvoiceos.github.io/ovos-localize/)**,
    a purpose-built tool that understands OVOS resource files (intents, dialogs,
    vocabularies) and shows you the actual skill code each phrase belongs to. If you
    have old GitLocalize bookmarks, switch to the link above.

> **Live site:** **[openvoiceos.github.io/ovos-localize](https://openvoiceos.github.io/ovos-localize/)**

---

## What you'll be translating

OVOS skills keep their language in small text files. You'll mostly meet three kinds:

| File | Holds | Plain English |
|---|---|---|
| **dialogs** (`.dialog`) | sentences **OVOS speaks** | "The weather today is {temperature} degrees." |
| **intents** (`.intent`) | sentences **the user says** | "what is the weather like" |
| **vocab** (`.voc`) | keywords / fragments | "weather", "forecast" |

You translate the *meaning*, not word-for-word. The tool shows you, on screen, which
skill and which line of code each phrase comes from — so you always have context.

---

## Step 1 — Open the site and pick a language

1. Go to **[openvoiceos.github.io/ovos-localize](https://openvoiceos.github.io/ovos-localize/)**.
2. Choose the **language** you want to translate into and the **skill** you want to work on.
   The dashboard shows how complete each language is, so you can see where help is needed most.

!!! tip "Don't see your language?"
    Languages are added on request. Ask in the
    [Matrix chat](https://matrix.to/#/#openvoiceos-languages:matrix.org) or
    [open an issue](https://github.com/OpenVoiceOS/lang-support-tracker/issues) and
    we'll enable it.

## Step 2 — Translate

The editor has three columns:

- **Left** — the original English phrase.
- **Center** — where you type your translation (with a live preview so you can see how
  it expands).
- **Right** — the **skill code context**: the actual Python function that uses this
  phrase, so you understand *when* OVOS says or expects it.

You can also use the **auto-translate** button to get a machine-translation starting
point, then fix it up — much faster than starting from a blank box.

## Step 3 — Submit

When you're happy with a file, click **Submit**. OVOS Localize files your work for you
and a bot turns it into a pull request on GitHub. A native speaker or maintainer reviews
it, and once merged your translation ships in the next skill release. You'll need a free
**GitHub account** to submit, but you never have to touch git or write code.

---

## The syntax rules (important)

OVOS phrases use a few special markers. Keep these intact or the skill can break.

### Variables — `{curly braces}`

Variables are placeholders that get filled in at runtime (a name, a number, a city).

- Original: `My name is {name}`
- Spanish: `Mi nombre es {name}`

**Rules:**

- **Never translate** the text inside `{ }` — copy it exactly.
- You may **move** a variable to fit your language's grammar.
- Don't invent new variables, and don't let two variables touch — keep at least one
  real word between them.

### Alternatives & optional words — `(a|b|c)`

The `(option1|option2)` syntax offers interchangeable choices; an empty option makes a
word optional.

- Alternatives: `I love (cats|dogs|birds)` → `Amo (gatos|perros|pájaros)`
- Optional word: `I (really|) love it` → `(Realmente|) me encanta`

### Slots (repeated variations)

Sometimes one phrase appears several times so OVOS can recognise different phrasings.
Each variation is a **slot**.

- Translate **at least one** slot per file.
- If a slot doesn't make sense in your language, enter `[UNUSED]` — that tells us you
  reviewed it on purpose.
- Need more room for natural variations? Add a new line and write another translation.

---

## Tips for good translations

- **Meaning over literalness** — convey what's meant, not a word-for-word swap.
- **Be consistent** — use the same term for the same concept throughout.
- **Use the code context** (right column) when a phrase is ambiguous.
- **Sound natural** — these are things a person says out loud to a voice assistant.

---

## Where this fits in OVOS

OVOS Localize is the front door for translators. Under the hood it reads the same locale
files described in **[Customizing Language Resources](lang-customization.md)** and
feeds the broader **[Language Support](lang-support.md)** effort. Developers who want to
validate locale files in CI can use its `ovos-localize-cli` tool; translators never need it.

For the technical side of multilingual support — language selection, parsers, and
translation plugins — see the **[Language Support overview](lang-support.md)**.

---

## Need help?

- **Matrix chat:** [#openvoiceos-languages:matrix.org](https://matrix.to/#/#openvoiceos-languages:matrix.org)
- **Email:** support@openvoiceos.org

Thank you — every translation makes OVOS usable for more people around the world. 🌍

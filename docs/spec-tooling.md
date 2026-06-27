# Specification Tooling

!!! abstract "In a nutshell"
    The [Formal Specifications](architecture-specs.md) say *what* must happen.
    Three pieces of tooling turn that from prose into something you can build on
    and check: **ovos-spec-tools** (a ready-made, conformant implementation of
    the low-level primitives), **ovos-test-harness** (an executable test suite
    that proves a running stack obeys the specs), and the **bus-client namespace
    migration** (which lets the ecosystem adopt the new spec topic names without
    a flag day).

!!! info "📐 Formal specification"
    These tools serve the **[OpenVoiceOS/architecture](https://github.com/OpenVoiceOS/architecture)** specs — see the [spec index](architecture-specs.md).

---

## ovos-spec-tools — the reference implementation

[**ovos-spec-tools**](https://github.com/OpenVoiceOS/ovos-spec-tools) is the
**single conformant implementation** of the low-level primitives the specs
describe. OVOS components used to reimplement template expansion, resource
loading, and language matching in several places — and the copies drifted.
Rather than reimplement (and re-introduce the bugs), depend on this package; it
is dependency-light (the core has **no dependencies**) and tracks the specs
clause-for-clause.

| Primitive | Spec | What it does |
|-----------|------|--------------|
| Sentence-template expander | [OVOS-INTENT-1](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-1.md) | Expands `(a\|b)` / `[opt]` / `{slot}` / `<vocab>` into the sentences it denotes |
| Locale resource loader | [OVOS-INTENT-2](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-2.md) | Loads a skill's `locale/` `.intent` / `.dialog` / `.voc` / `.entity` / `.prompt` files |
| Dialog & prompt renderer | [OVOS-INTENT-2 §4](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-2.md) | Renders a spoken `.dialog` line or a `.prompt` with slot substitution |
| Language-tag matching | [OVOS-INTENT-2 §2.2](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-2.md) | Picks the closest available BCP-47 language for a request |
| Message envelope | [OVOS-MSG-1](https://github.com/OpenVoiceOS/architecture/blob/dev/msg-1.md) | The `{type, data, context}` `Message` and its `forward`/`reply`/`response` derivations |
| `ovos-spec-lint` | [OVOS-INTENT-1](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-1.md) / [-2](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-2.md) | A linter that validates a `locale/` folder against the resource-format specs |

```bash
pip install ovos-spec-tools            # core — no dependencies (Python 3.10+)
pip install ovos-spec-tools[langcodes] # adds smart language fallback
```

```python
from ovos_spec_tools import expand, LocaleResources, render, closest_lang, Message

expand("(turn|switch) [the] light")             # every sentence the template denotes
res = LocaleResources("my-skill/locale")
render(res.load_dialog("weather", "en-US"),     # a spoken response
       slots={"temperature": 21})
closest_lang("en-AU", ["pt-BR", "en-US"])       # -> 'en-US'
m = Message("ovos.intent.list", {}, {"source": "skill.id"})
m.response({"intents": ["..."]}).serialize()    # -> the 'ovos.intent.list.response' JSON
```

Lint a skill's locale folder against the grammar and format specs:

```bash
ovos-spec-lint my-skill/locale
```

!!! tip "When to reach for it"
    Building an intent engine, a skill loader, a satellite, or any third-party
    tool that touches OVOS templates, locale files, language selection, or the
    bus envelope? Depend on `ovos-spec-tools` instead of hand-rolling — that is
    exactly the drift the package exists to prevent. See also
    [Resource Files](resource-files.md) and [Language Selection](lang-selection.md).

---

## ovos-test-harness — the conformance suite

[**ovos-test-harness**](https://github.com/OpenVoiceOS/ovos-test-harness) is the
**executable counterpart** of the specs. Each test asserts one observable bus
behaviour a spec mandates, against a *real running OVOS stack*. If the specs are
the law, this harness is the courtroom: it puts a concrete combination of OVOS
repos on trial against the law and returns a verdict per normative clause —
**pass**, **`xfail`** (a documented gap), or **fail**.

**Why a separate repo.** A single spec clause is only satisfied when a
*combination* of branches across a dozen repos lines up — `ovos-core`,
`ovos-workshop`, `ovos-bus-client`, the pipeline plugins, fixture skills. You
cannot prove that from inside any one repo, because that repo's CI installs only
its own package plus whatever pip resolves, and pip is free to downgrade a
sibling out of the exact combination you are trying to validate.

**The model.** The harness is **not a package** — there is no `pip install .`.
Its [`requirements.txt`](https://github.com/OpenVoiceOS/ovos-test-harness) is the
**stack under test**: every line pins one repo to an exact git ref or version, so
CI never re-resolves and never downgrades a component. Each test then:

- imports the spec vocabulary from [`ovos-spec-tools`](https://github.com/OpenVoiceOS/ovos-spec-tools), so a topic name is *provably spec-defined* rather than a magic string;
- drives and captures the live bus through [`ovoscope`](https://github.com/TigreGotico/ovoscope) (see [Testing Skills](ovoscope-overview.md));
- asserts the spec-mandated behaviour and records pass / `xfail` / fail.

This is where an implementation is **proven to conform** to the merged
architecture specs — the bridge between the prescriptive Markdown and the code
that has to honour it.

---

## Adopting the spec namespace — without a flag day

The specs rename many bus topics into the `ovos.*` namespace (for example
`recognizer_loop:utterance` → `ovos.utterance.handle`). Migrating an ecosystem
of independently-released repos to new topic names all at once is impossible —
so [**ovos-bus-client**](bus-service.md) does it **automatically and
incrementally**. A migrated message is dual-sent on **both** the legacy and the
`ovos.*` topic, and a subscription to either name receives both (de-duplicated),
so a producer and consumer can each switch to `ovos.*` **in any order, with no
coordination**.

This is what makes spec adoption gradual rather than a breaking change. The full
mechanism — and how to turn the bridges off once a deployment is fully
modernised — is documented under
[**MessageBus Service → Namespace migration**](bus-service.md#namespace-migration).

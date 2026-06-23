# Nebulento

!!! abstract "In a nutshell"
    Nebulento is an [intent](glossary.md) parser that figures out what a user *meant* even when
    they make typos, reorder words, or phrase things loosely — it matches by *fuzzy similarity*
    rather than exact words. Think of it as a more forgiving sibling of [Padatious](padatious-pipeline.md):
    you still give it example sentences, but it tolerates messy input. No training step, no model
    files. See the [Glossary](glossary.md) for terms like *intent* and *entity*.

*A lightweight fuzzy-matching intent parser.*

[`nebulento`](https://github.com/OpenVoiceOS/nebulento) finds the closest matching intent by
comparing the utterance against all of an intent's training sentences using configurable fuzzy
similarity strategies (built on [rapidfuzz](https://github.com/maxbachmann/rapidfuzz)). It
handles spelling errors, word-order variation, contractions, and natural phrasing that
exact-match parsers would miss. It is best suited for **small-to-medium** intent sets (dozens to
hundreds of training sentences per intent).

## Install

```bash
pip install nebulento            # the library
pip install "nebulento[ovos]"    # + the OVOS pipeline plugin
```

## Usage

```python
from nebulento import IntentContainer

container = IntentContainer()
container.add_intent("hello", ["hello", "hi there", "hey"])
container.add_intent("weather", ["what's the weather", "weather in {place}"])

match = container.calc_intent("helo there")   # note the typo
print(match)   # best fuzzy match, with name, entities and a confidence score
```

## In the OVOS pipeline

Installed as a pipeline plugin (`nebulento[ovos]`), Nebulento listens on the **same
`padatious:register_intent` bus events as [Padatious](padatious-pipeline.md)**, so it is a
drop-in alternative — skills register their `.intent` files exactly as before. A hierarchical
variant is also available. See [Pipelines Overview](pipelines-overview.md) for how matchers are
ordered and configured.

!!! tip "When to choose Nebulento"
    Use it when users phrase things inconsistently or make typos (e.g. typed input, noisy STT),
    and your intent set is small enough that fuzzy comparison stays fast. For large intent sets
    or strict matching, prefer [Padatious](padatious-pipeline.md) (neural) or
    [Adapt](adapt-pipeline.md) (keyword).

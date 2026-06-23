# Palavreado

!!! abstract "In a nutshell"
    Palavreado is an [intent](glossary.md) parser that decides what a user wants by looking for
    specific **keywords** in what they said — if the right words are present, the intent fires.
    It is a dead-simple, drop-in replacement for [Adapt](adapt-pipeline.md). See the
    [Glossary](glossary.md) for terms like *intent* and *entity*.

*A keyword-based intent parser — the drop-in replacement for [Adapt](adapt-pipeline.md).*

[`palavreado`](https://github.com/OpenVoiceOS/palavreado) matches utterances against named
intents built from **required** and **optional** keyword slots. Each slot holds a list of
vocabulary words; if the required words are present in the utterance, the intent fires. Optional
regex and [simplematch](https://github.com/tfeldmann/simplematch) "autoregex" patterns enable
**entity extraction** (pulling out a value, like a city name).

## Install

```bash
pip install palavreado            # the library
pip install "palavreado[ovos]"    # + the OVOS pipeline plugin
```

## Usage

```python
from palavreado import IntentContainer

container = IntentContainer()
container.add_intent("greet", {
    "required": ["HelloKeyword"],
    "optional": ["NameKeyword"],
})
match = container.calc_intent("hello there")
print(match)   # name, entities and a confidence score
```

## In the OVOS pipeline

Installed as a pipeline plugin (`palavreado[ovos]`), Palavreado responds to the **same
`register_vocab` / `register_intent` bus events as [Adapt](adapt-pipeline.md)**, so swapping it
in requires zero skill changes — your `.voc` files keep working. See
[Pipelines Overview](pipelines-overview.md) for how matchers are ordered and configured.

!!! tip "When to choose Palavreado"
    Use it as a lighter, simpler stand-in for Adapt when you want keyword matching without
    Adapt's full rule engine. For example-based (whole-sentence) matching, use
    [Padatious](padatious-pipeline.md) or [Nebulento](nebulento.md) instead.

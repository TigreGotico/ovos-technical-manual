# Padacioso

!!! abstract "In a nutshell"
    Padacioso is a simple tool that figures out what a user *meant* by matching what they said against a list of example phrases you write out by hand — like a phrasebook. Unlike its smarter sibling Padatious, it does no machine learning and needs no training: it just checks the words literally, with a little flexibility for optional words and fill-in-the-blank slots. It also pulls out useful pieces (an "entity", e.g. the city name in "weather in Lisbon"). See the [Glossary](glossary.md) for terms like *intent* and *entity*.

*A lightweight, dead-simple intent parser*

Built on top of [simplematch](https://github.com/tfeldmann/simplematch), inspired by [Padaos](https://github.com/MycroftAI/padaos).

Padacioso matches an utterance against example sentences using plain string templates — no training, no model files. It is the pure-Python sibling of Padatious: where Padatious learns from examples, Padacioso matches them literally (with a few placeholder syntaxes). Each call to `calc_intent` returns the best match as `{"name", "entities", "conf"}`, or `name: None` when nothing matches.

## Example

```python
from padacioso import IntentContainer

container = IntentContainer()

# plain samples
container.add_intent('hello', ['hello', 'hi', 'how are you', "what's up"])

# "optionally" syntax — [word] is optional
container.add_intent('hello world', ["hello [world]"])

# "one_of" syntax — any of the alternatives
container.add_intent('greeting', ["(hi|hey|hello)"])

# entity extraction with {placeholders}
container.add_intent('search', [
    'search for {query} on {engine}', 'using {engine} (search|look) for {query}',
    'find {query} (with|using) {engine}'
])
container.add_entity('engine', ['abc', 'xyz'])
container.calc_intent('find cats using xyz')
# {'name': 'search', 'entities': {'query': 'cats', 'engine': 'xyz'}, 'conf': 0.96}

# wildcards — * matches anything; the name is the registered intent name
container.add_intent('say', ["say *"])
container.calc_intent('say something, whatever')
# {'name': 'say', 'entities': {}, 'conf': 0.85}
```

Slot names follow the OVOS sentence-template grammar (`{lowercase_with_underscores}`);
the colon-typed `simplematch` syntax such as `{number:int}` is **not** supported —
templates are expanded and normalized through `ovos_spec_tools`, which rejects it.

A wildcard (`*`) carries a confidence penalty proportional to how much of the
template it covers — `"say *"` is one wildcard out of two tokens, so the score
drops from `1.0` to `0.85`. Entity placeholders like `{number}` are not
wildcards and carry no penalty. An entity whose name was never registered with
`add_entity` still matches but at a slightly reduced confidence (a small `0.04`
penalty, e.g. `0.96`).

---

*Source code: [OpenVoiceOS/padacioso](https://github.com/OpenVoiceOS/padacioso).*

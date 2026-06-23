# OVOS Number Parser

!!! abstract "In a nutshell"
    Computers store numbers as digits (`123`), but people say them as words ("one hundred and twenty-three") — and the words differ in every language. This library is the translator between the two: it can read a number out loud for the assistant to speak, or pick a number out of something you said ("set a timer for twenty-five minutes") and turn it back into digits. It also understands fractions and ordinals like "third". See the [Glossary](glossary.md) for unfamiliar terms.

`ovos-number-parser` converts numbers between digits and spoken words across many languages: it speaks a number aloud (`123` → "one hundred and twenty-three"), pulls a number out of free text ("I have twenty apples" → `20`), and detects fractions and ordinals.

**What you get in 30 seconds:**

```python
from ovos_number_parser import pronounce_number, extract_number

pronounce_number(123, "en")            # "one hundred and twenty three"
extract_number("I have twenty apples", "en")   # 20
```

Every function takes an explicit `lang` (a BCP-47 code such as `"en"` or `"pt-br"`); there is no global default language. When a language lacks a hand-written implementation for `pronounce_number`/`pronounce_ordinal`, the library falls back to [unicode-rbnf](https://github.com/rhasspy/unicode-rbnf). For functions without a fallback (`extract_number`, `is_fractional`, `numbers_to_digits`), an unsupported language raises `NotImplementedError`.

## Features

- **Pronounce Numbers:** Converts numerical values to their spoken forms (`pronounce_number`).


- **Pronounce Ordinals:** Converts numbers to their ordinal forms (`pronounce_ordinal`).


- **Pronounce Fractions:** Speaks a fraction string such as `"3/2"` (`pronounce_fraction`, `pt`/`mwl` only).


- **Extract Numbers:** Extracts a number from text (`extract_number`).


- **Words to Digits:** Rewrites spelled-out numbers in a sentence as digits (`numbers_to_digits`).


- **Detect Fractions:** Identifies exact fractional expressions (`is_fractional`).


- **Detect Ordinals:** Checks if a text input is an ordinal number (`is_ordinal`).

## Supported Languages

- ✅ - supported


- ❌ - not supported


- 🚧 - imperfect placeholder, usually a language agnostic implementation or external library


| Language Code           | Pronounce Number | Pronounce Ordinal | Extract Number | numbers_to_digits |
|-------------------------|------------------|-------------------|----------------|-------------------|
| `en` (English)          | ✅               | 🚧                | ✅             | ✅                |
| `az` (Azerbaijani)      | ✅               | 🚧                | ✅             | ✅                |
| `ca` (Catalan)          | ✅                | 🚧                 | ✅              | 🚧                 |
| `gl` (Galician)         | ✅                | ❌                | ✅              |  🚧                  |
| `cs` (Czech)            | ✅                | 🚧                 | ✅              | ✅                 |
| `da` (Danish)           | ✅                | ✅                 | ✅              | 🚧                 |
| `de` (German)           | ✅                | ✅                 | ✅              | ✅                 |
| `es` (Spanish)          | ✅                | 🚧                 | ✅              | 🚧                 |
| `eu` (Euskara / Basque) | ✅                | ❌                 | ✅              | ❌                 |
| `fa` (Farsi / Persian)  | ✅                | 🚧                 | ✅              | ❌                 |
| `fr` (French)           | ✅                | 🚧                 | ✅              | ❌                 |
| `hu` (Hungarian)        | ✅                | ✅                 | ❌              | ❌                 |
| `it` (Italian)          | ✅                | 🚧                | ✅              | ❌                 |
| `mwl` (Mirandese)       | ✅                | ✅                 | ✅              | ✅                 |
| `nl` (Dutch)            | ✅                | ✅                 | ✅              | ✅                 |
| `pl` (Polish)           | ✅                | 🚧                 | ✅              | ✅                 |
| `pt` (Portuguese)       | ✅                | ✅                 | ✅              | 🚧                 |
| `ru` (Russian)          | ✅                | 🚧                 | ✅              | ✅                 |
| `sv` (Swedish)          | ✅                | ✅                 | ✅              | ❌                 |
| `sl` (Slovenian)        | ✅                | 🚧                 | ❌              | ❌                 |
| `uk` (Ukrainian)        | ✅                | 🚧                 | ✅              | ✅                 |


> 💡 If a language is not implemented for `pronounce_number` or `pronounce_ordinal` then [unicode-rbnf](https://github.com/rhasspy/unicode-rbnf) will be used as a fallback.

> 🚧 **Upcoming:** Asturian (`ast`) support and a shared `RomanceNumberExtractor` base class are proposed in [ovos-number-parser#38](https://github.com/OpenVoiceOS/ovos-number-parser/pull/38).

## Installation

To install OVOS Number Parser, use:

```bash
pip install ovos-number-parser

```

## Usage

### Pronounce a Number

Convert a number to its spoken equivalent.

```python
def pronounce_number(number: Union[int, float], lang: str, places: int = 3, short_scale: bool = True,
                     scientific: bool = False, ordinals: bool = False,
                     digits: DigitPronunciation = DigitPronunciation.FULL_NUMBER,
                     gender: GrammaticalGender = GrammaticalGender.MASCULINE) -> str:
    """
    Convert a number to its spoken equivalent.

    Args:
        number: The number to pronounce.
        lang (str): A BCP-47 language code.
        places (int): Number of decimal places to express. Default is 3.
        short_scale (bool): Use short (True) or long scale (False) for large numbers.
        scientific (bool): Pronounce in scientific notation if True.
        ordinals (bool): Pronounce as an ordinal if True.
        digits (DigitPronunciation): Digit-reading style (e.g. read digit-by-digit). Honored by pt/mwl.
        gender (GrammaticalGender): Grammatical gender for languages that inflect numbers. Honored by pt/mwl.

    Returns:
        str: The pronounced number.

    Raises:
        NotImplementedError: if the language has neither an implementation nor a unicode-rbnf fallback.
    """

```

> Most language backends only consume `number`, `places`, `short_scale`, `scientific`, and `ordinals`. The `digits` and `gender` arguments (and `DigitPronunciation`/`GrammaticalGender`, importable from `ovos_number_parser.util`) currently only affect Portuguese (`pt`) and Mirandese (`mwl`).

**Example Usage:**

```python
from ovos_number_parser import pronounce_number

# Example
result = pronounce_number(123, "en")
print(result)  # "one hundred and twenty three"

```

### Pronounce an Ordinal

Convert a number to its ordinal spoken equivalent.

```python
def pronounce_ordinal(number: Union[int, float], lang: str, short_scale: bool = True,
                      gender: GrammaticalGender = GrammaticalGender.MASCULINE) -> str:
    """
    Convert an ordinal number to its spoken equivalent.

    Args:
        number: The number to pronounce.
        lang (str): A BCP-47 language code.
        short_scale (bool): Use short (True) or long scale (False) for large numbers.
        gender (GrammaticalGender): Grammatical gender (honored by pt/mwl).

    Returns:
        str: The pronounced ordinal number.

    Raises:
        NotImplementedError: if the language has neither an implementation nor a unicode-rbnf fallback.
    """

```

Hand-written ordinal pronunciation exists for `da`, `de`, `hu`, `nl`, `sv`, `pt`, and `mwl`; all other languages route through the unicode-rbnf fallback.

**Example Usage:**

```python
from ovos_number_parser import pronounce_ordinal

# Example
result = pronounce_ordinal(5, "en")
print(result)  # "fifth"

```

### Extract a Number

Extract a number from a given text string.

```python
def extract_number(text: str, lang: str, short_scale: bool = True, ordinals: bool = False) -> Union[int, float, bool]:
    """
    Extract a number from text.

    Args:
        text (str): The string to extract a number from.
        lang (str): A BCP-47 language code.
        short_scale (bool): Use short scale if True, long scale if False.
        ordinals (bool): Consider ordinal numbers.

    Returns:
        int, float, or False: The extracted number, or False if no number found.
    """

```

**Example Usage:**

```python
from ovos_number_parser import extract_number

# Example
result = extract_number("I have twenty apples", "en")
print(result)  # 20

```

### Check for Fractional Numbers

Identify if the text contains a fractional number.

```python
def is_fractional(input_str: str, lang: str, short_scale: bool = True) -> Union[bool, float]:
    """
    Check if the text is a fraction.

    Args:
        input_str (str): The string to check if fractional.
        lang (str): A BCP-47 language code.
        short_scale (bool): Use short scale if True, long scale if False.

    Returns:
        bool or float: False if not a fraction, otherwise the fraction as a float.
    """

```

**Example Usage:**

```python
from ovos_number_parser import is_fractional

# Example
result = is_fractional("half", "en")
print(result)  # 0.5

```

### Check for Ordinals

Determine if the text contains an ordinal number.

```python
def is_ordinal(input_str: str, lang: str) -> Union[bool, float]:
    """
    Check if the text is an ordinal number.

    Args:
        input_str (str): The string to check if ordinal.
        lang (str): A BCP-47 language code.

    Returns:
        bool or float: False if not an ordinal, otherwise the ordinal as a float.
    """

```

**Example Usage:**

```python
from ovos_number_parser import is_ordinal

# Example
result = is_ordinal("third", "en")
print(result)  # 3

```

> `is_ordinal` is only implemented for `en`, `de`, `da`, `pt`, and `mwl`; other languages raise `NotImplementedError`.

### Words to Digits

Rewrite spelled-out numbers inside a sentence as digits, leaving the rest of the text intact.

```python
from ovos_number_parser import numbers_to_digits

numbers_to_digits("set a timer for twenty five minutes", "en")
# "set a timer for 25 minutes"
```

```python
def numbers_to_digits(utterance: str, lang: str, scale: Scale = Scale.LONG) -> str: ...
```

`scale` (`Scale.LONG` / `Scale.SHORT`, from `ovos_number_parser.util`) only matters for `pt`/`mwl`. Supported languages: `az`, `ca`, `gl`, `cs`, `da`, `de`, `en`, `es`, `nl`, `pl`, `pt`, `mwl`, `ru`, `uk`. Unsupported languages raise `NotImplementedError`.

### Pronounce a Fraction

Speak a fraction string such as `"3/2"`. Only Portuguese (`pt`) and Mirandese (`mwl`) are implemented; any other language raises `NotImplementedError`.

```python
from ovos_number_parser import pronounce_fraction

pronounce_fraction("3/2", "pt")   # "três meios"
```

```python
def pronounce_fraction(fraction_word: str, lang: str, scale: Scale = Scale.LONG) -> str: ...
```

## Related Projects

- [ovos-date-parser](https://github.com/OpenVoiceOS/ovos-date-parser) - for handling dates and times


- [ovos-lang-parser](https://github.com/OpenVoiceOS/ovos-lang-parser) - for handling language names


- [ovos-color-parser](https://github.com/OpenVoiceOS/ovos-color-parser) - for handling colors

## License

This project is licensed under the Apache License 2.0.

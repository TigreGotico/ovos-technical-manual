# ovos-date-parser

!!! abstract "In a nutshell"
    This is a helper that translates between everyday date and time phrases and the precise dates a computer understands. It works both ways: it can read "next Friday at 3pm" and pin down the exact moment, and it can turn an exact time back into natural words like "three o'clock". It handles many languages, which is what lets the assistant understand and speak dates the way you do. See the [Number parser](number-parser.md) for the same idea applied to numbers, or the [Glossary](glossary.md) for terms.

`ovos-date-parser` is a multilingual library for turning human date/time phrases into Python objects (`extract_datetime`, `extract_duration`) and for turning `datetime`/`timedelta` objects back into natural spoken or written text (`nice_time`, `nice_date`, `nice_duration`, ...).

**What you get in 30 seconds:**

```python
from ovos_date_parser import extract_datetime, nice_time
from datetime import datetime

extract_datetime("remind me next friday at 3pm", lang="en")
# [datetime(...), "remind me"]    -> parsed datetime + leftover text, as a 2-item list

nice_time(datetime(2024, 1, 1, 15, 0), lang="en")   # "three o'clock"
```

Every function takes an explicit `lang` (BCP-47 code). For `extract_datetime`, languages without a dedicated implementation fall back to the [dateparser](https://dateparser.readthedocs.io/en/latest/) library. The `nice_*` formatters fall back to a language-agnostic English-style generic implementation when a language-specific one is missing.

## Features

- **Date and Time Extraction**: Extract specific dates and times from natural language phrases in various languages.


- **Duration Parsing**: Parse phrases that indicate a span of time, such as "two hours and fifteen minutes."


- **Friendly Time Formatting**: Format time for human-friendly output, supporting both 12-hour and 24-hour formats.


- **Relative Time Descriptions**: Generate relative descriptions (e.g., "tomorrow," "in three days") for given dates.


- **Multilingual Support**: Includes extraction and formatting methods for multiple languages, such as English, Spanish,
  French, German, and more.

## Installation

```bash
pip install ovos-date-parser

```

### Languages Supported

`ovos-date-parser` supports a wide array of languages, each with its own set of methods for handling natural language
time expressions.

- ✅ - supported


- ❌ - not supported


- 🚧 - imperfect placeholder, usually a language agnostic implementation or external library

**Parse**

| Language | `extract_duration` | `extract_datetime` |
|----------|--------------------|--------------------|
| az       | ✅                  | ✅                  |
| ca       | ✅                  | ✅                  |
| cs       | ✅                  | ✅                  |
| da       | ✅                  | ✅                  |
| de       | ✅                  | ✅                  |
| en       | ✅                  | ✅                  |
| es       | ✅                  | ✅                  |
| gl       | ✅                  | ✅                 |
| eu       | ✅                  | ✅                  |
| fa       | ✅                  | ✅                  |
| fr       | ✅                  | ✅                  |
| hu       | ✅                  | ✅                 |
| it       | ✅                  | ✅                  |
| nl       | ✅                  | ✅                  |
| pl       | ✅                  | ✅                  |
| pt       | ✅                  | ✅                  |
| ru       | ✅                  | ✅                  |
| sv       | ✅                  | ✅                  |
| sl       | ✅                  | ✅                  |
| uk       | ✅                  | ✅                  |


> 💡 If a language is not implemented for `extract_datetime` then [dateparser](https://dateparser.readthedocs.io/en/latest/) will be used as a fallback

**Format**

| Language | `nice_date`<br>`nice_date_time`<br>`nice_day` <br>`nice_weekday` <br>`nice_month` <br>`nice_year` <br>`get_date_strings` | `nice_time` | `nice_relative_time` | `nice_duration` |
|----------|--------------------------------------------------------------------------------------------------------------------------|-------------|----------------------|-----------------|
| az       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| ca       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| cs       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| da       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| de       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| en       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| es       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| gl       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| eu       | ✅                                                                                                                        | ✅           | ✅                    | ✅               |
| fa       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| fr       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| hu       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| it       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| nl       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| pl       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| pt       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| ru       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| sv       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| sl       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| uk       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |

## Usage

### Date and Time Extraction

Extract specific dates and times from a phrase. This function identifies date-related terms in natural language and
returns both the datetime object and any remaining text.

```python
from ovos_date_parser import extract_datetime

result = extract_datetime("Meet me next Friday at 3pm", lang="en")
print(result)  # [datetime object, "meet me"]

```

!!! note
    `extract_datetime` returns a 2-item `list` — `[datetime, leftover_text]` — not a tuple, and the leftover text is lowercased.

### Duration Extraction

Identify duration phrases in text and convert them into a `timedelta` object. This can parse common human-friendly
duration expressions like "30 minutes" or "two and a half hours."

```python
from ovos_date_parser import extract_duration

duration, remainder = extract_duration("It will take about 2 hours and 30 minutes", lang="en")
print(duration)   # timedelta(hours=2, minutes=30)
print(remainder)  # "It will take about and"

```

!!! note
    The remainder keeps whatever surrounds the extracted duration phrase verbatim — connective words like "and" that sat between the matched number groups are not cleaned up.

### Formatting Time

Generate a natural-sounding time format suitable for voice or display in different languages, allowing customization for
speech or written text.

```python
from ovos_date_parser import nice_time
from datetime import datetime

dt = datetime(2024, 1, 1, 15, 0)
formatted_time = nice_time(dt, lang="en", speech=True, use_24hour=False)
print(formatted_time)  # "three o'clock"

```

### Relative Time Descriptions

Create relative phrases for describing dates and times in relation to the current moment or a reference datetime.

```python
from ovos_date_parser import nice_relative_time
from datetime import datetime, timedelta

relative_time = nice_relative_time(datetime.now() + timedelta(days=1), datetime.now(), lang="en")
print(relative_time)  # "twenty four hours"

```

> The generic implementation speaks the rounded difference as words — `"two hours"`, `"twenty four hours"`, `"seven days"` — using `pronounce_number` internally (it does not produce words like "tomorrow"). Basque (`eu`) is the only language with a dedicated `nice_relative_time` implementation; everything else uses the generic one.

## Related Projects

- [ovos-number-parser](https://github.com/OpenVoiceOS/ovos-number-parser) - for handling numbers


- [ovos-lang-parser](https://github.com/OpenVoiceOS/ovos-lang-parser) - for handling language names


- [ovos-color-parser](https://github.com/OpenVoiceOS/ovos-color-parser) - for handling colors

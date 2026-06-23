# Quebra Frases

!!! abstract "In a nutshell"
    This is a small text-handling toolkit that does the everyday chores of breaking writing into pieces — splitting a block of text into sentences, or a sentence into individual words ("tokens") — and comparing several phrases to find what they have in common. OVOS leans on it to tidy up what you said before trying to understand it. The name is Portuguese for "phrase breaking". See the [Glossary](glossary.md) for unfamiliar terms.

`quebra_frases` is a lightweight text-processing toolkit for tokenization (words / sentences / paragraphs), chunking around delimiters, and comparing several utterances to find their common / uncommon / exclusive parts. OVOS uses it for utterance normalization and intent-sample analysis.

**What you get in 30 seconds:**

```python
import quebra_frases

quebra_frases.word_tokenize("mycroft is FOSS!")   # ['mycroft', 'is', 'FOSS', '!']
quebra_frases.sentence_tokenize("Hi there. How are you?")
# ['Hi there.', 'How are you?']
```

**Dependencies:** lightweight — only the `regex` library is required.

## Installation

You can install the `quebra_frases` package using pip:

```bash
pip install quebra_frases

```

## Overview

The `quebra_frases` package includes several modules and functionalities:

- **Tokenization**: Text tokenization is the process of splitting text into meaningful units such as words, sentences, or paragraphs.


- **Chunking**: Text chunking involves dividing text into smaller chunks based on specified delimiters or patterns.


- **Token Analysis**: This package also provides methods to analyze tokens across multiple text samples, extracting common, uncommon, and exclusive tokens.

## Usage

### Tokenization

The `quebra_frases` package offers various tokenization methods:

- `word_tokenize(input_string)`: Tokenizes an input string into words.


- `sentence_tokenize(input_string)`: Splits an input string into sentences.


- `paragraph_tokenize(input_string)`: Divides an input string into paragraphs.

### Chunking

Chunking is performed using the following functions:

- `chunk(text, delimiters)`: Splits text into chunks based on specified delimiters.


- `get_common_chunks(samples)`: Extracts common chunks from a list of text samples.


- `get_uncommon_chunks(samples)`: Extracts uncommon chunks from text samples.


- `get_exclusive_chunks(samples)`: Extracts exclusive chunks that are unique to each text sample.

### Token Analysis

Token analysis functions are available for text sample comparison:

- `get_common_tokens(samples)`: Extracts tokens that are common across multiple text samples.


- `get_uncommon_tokens(samples)`: Extracts tokens that are uncommon across multiple text samples.


- `get_exclusive_tokens(samples)`: Extracts tokens that are exclusive to each individual text sample.

### Span / index variants and helpers

For every tokenizer there are `span_indexed_*` and `char_indexed_*` variants that return offsets alongside the text:

- `span_indexed_word_tokenize`, `char_indexed_word_tokenize`
- `span_indexed_sentence_tokenize`, `char_indexed_sentence_tokenize`
- `span_indexed_paragraph_tokenize`, `char_indexed_paragraph_tokenize`
- `empty_space_tokenize`, `span_indexed_empty_space_tokenize`, `char_indexed_empty_space_tokenize`, `get_empty_spans` — work with whitespace runs

Other utilities:

- `chunk_list(some_list, delimiters)`: like `chunk`, but splits a list of tokens instead of a string.
- `find_spans(text, samples)`: locate the character spans of `samples` within `text`.
- `flatten(some_list)`: flatten a nested list.

The chunk/token-analysis functions accept a `squash` keyword (default `True`): when `False`, results are kept grouped per sample instead of merged into a single set (see the `get_exclusive_chunks(..., squash=False)` example below). `chunk()` also accepts `strip=True` (default) to trim whitespace from each chunk.

## Example Usage

Tokenization

```python
import quebra_frases

sentence = "sometimes i develop stuff for mycroft, mycroft is FOSS!"
print(quebra_frases.word_tokenize(sentence))

# ['sometimes', 'i', 'develop', 'stuff', 'for', 'mycroft', ',', 

# 'mycroft', 'is', 'FOSS', '!']

print(quebra_frases.span_indexed_word_tokenize(sentence))

# [(0, 9, 'sometimes'), (10, 11, 'i'), (12, 19, 'develop'), 

# (20, 25, 'stuff'), (26, 29, 'for'), (30, 37, 'mycroft'), 

# (37, 38, ','), (39, 46, 'mycroft'), (47, 49, 'is'), 

# (50, 54, 'FOSS'), (54, 55, '!')]

print(quebra_frases.sentence_tokenize(
    "Mr. Smith bought cheapsite.com for 1.5 million dollars, i.e. he paid a lot for it. Did he mind? Adam Jones Jr. thinks he didn't. In any case, this isn't true... Well, with a probability of .9 it isn't."))
#['Mr. Smith bought cheapsite.com for 1.5 million dollars, i.e. he paid a lot for it.',
#'Did he mind?',
#"Adam Jones Jr. thinks he didn't.",
#"In any case, this isn't true...",
#"Well, with a probability of .9 it isn't."]

print(quebra_frases.span_indexed_sentence_tokenize(
    "Mr. Smith bought cheapsite.com for 1.5 million dollars, i.e. he paid a lot for it. Did he mind? Adam Jones Jr. thinks he didn't. In any case, this isn't true... Well, with a probability of .9 it isn't."))
#[(0, 82, 'Mr. Smith bought cheapsite.com for 1.5 million dollars, i.e. he paid a lot for it.'),
#(83, 95, 'Did he mind?'),
#(96, 128, "Adam Jones Jr. thinks he didn't."),
#(129, 160, "In any case, this isn't true..."),
#(161, 201, "Well, with a probability of .9 it isn't.")]

print(quebra_frases.paragraph_tokenize('This is a paragraph!\n\t\nThis is another '
                                       'one.\t\n\tUsing multiple lines\t   \n     '
                                       '\n\tparagraph 3 says goodbye'))
#['This is a paragraph!\n\t\n',
#'This is another one.\t\n\tUsing multiple lines\t   \n     \n',
#'\tparagraph 3 says goodbye']

print(quebra_frases.span_indexed_paragraph_tokenize('This is a paragraph!\n\t\nThis is another '
                                                    'one.\t\n\tUsing multiple lines\t   \n     '
                                                    '\n\tparagraph 3 says goodbye'))
#[(0, 23, 'This is a paragraph!\n\t\n'),
#(23, 77, 'This is another one.\t\n\tUsing multiple lines\t   \n     \n'),
#(77, 102, '\tparagraph 3 says goodbye')]

```

chunking

```python
import quebra_frases

delimiters = ["OpenVoiceOS"]
sentence = "sometimes i develop stuff for OpenVoiceOS, OpenVoiceOS is FOSS!"
print(quebra_frases.chunk(sentence, delimiters))

# ['sometimes i develop stuff for', 'OpenVoiceOS', ',', 'OpenVoiceOS', 'is FOSS!']

```

token analysis

```python
import quebra_frases

samples = ["tell me what do you dream about",
           "tell me what did you dream about",
           "tell me what are your dreams about",
           "tell me what were your dreams about"]
print(quebra_frases.get_common_chunks(samples))

# {'tell me what', 'about'}
print(quebra_frases.get_uncommon_chunks(samples))

# {'do you dream', 'did you dream', 'are your dreams', 'were your dreams'}
print(quebra_frases.get_exclusive_chunks(samples))

# {'do', 'did', 'are', 'were'}

samples = ["what is the speed of light",
           "what is the maximum speed of a firetruck",
           "why are fire trucks red"]
print(quebra_frases.get_exclusive_chunks(samples))

# {'light', 'maximum', 'a firetruck', 'why are fire trucks red'})
print(quebra_frases.get_exclusive_chunks(samples, squash=False))
#[['light'],
#['maximum', 'a firetruck'],
#['why are fire trucks red']])

```

---

*Source code: [OpenVoiceOS/quebra_frases](https://github.com/OpenVoiceOS/quebra_frases).*

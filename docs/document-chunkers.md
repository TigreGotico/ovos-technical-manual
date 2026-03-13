
# `ovos-document-chunkers` — Documentation Index

`ovos-document-chunkers` is a library of document chunking utilities for NLP preprocessing and Retrieval-Augmented Generation (RAG) pipelines. It splits raw documents — plain text, Markdown, HTML, PDF, DOC, and DOCX — into sentences or paragraphs using multiple backend strategies ranging from simple regex tokenisation to state-of-the-art neural models.

The library was sponsored by [Royal Dutch Visio](https://visio.org/) for use in assistive technology and voice-accessible NLP pipelines.

## Contents

| Document | Description |
|---|---|
| [chunkers.md](document-chunkers.md) | All chunker classes with full API reference |

## Design

All chunkers inherit from `AbstractDocumentChunker` (defined in `ovos_document_chunkers.base`). The core API is a single method:

```python
def chunk(self, data: Any) -> Iterable[str]:
    ...

```

The `data` argument type varies by chunker:

- **Text chunkers** (`AbstractTextDocumentChunker`) accept a `str`.


- **File chunkers** accept a `str` that is either a local file path, a URL, or raw content.

## Module Layout

```
ovos_document_chunkers/
├── base.py                  ← AbstractDocumentChunker, AbstractTextDocumentChunker
├── __init__.py              ← public re-exports
├── text/
│   ├── sentence.py          ← RegexSentenceSplitter, PySBDSentenceSplitter, SaTSentenceSplitter, WtPSentenceSplitter
│   └── paragraphs.py        ← RegexParagraphSplitter, WtPParagraphSplitter, SaTParagraphSplitter
└── files/
    ├── markdown.py          ← MarkdownSentenceSplitter, MarkdownParagraphSplitter
    ├── webpages.py          ← HTMLSentenceSplitter, HTMLParagraphSplitter
    ├── pdf.py               ← PDFSentenceSplitter, PDFParagraphSplitter
    ├── doc.py               ← DOCSentenceSplitter, DOCParagraphSplitter
    └── docx.py              ← DOCxSentenceSplitter, DOCxParagraphSplitter

```

## Text Segmenters

Three backends are available for text segmentation:

| Backend | Type | Languages | Notes |
|---|---|---|---|
| `quebra_frases` (regex) | Rule-based | Language-agnostic | Lightweight, no model download |
| `PySBD` | Rule-based | 22 languages | Pragmatic sentence boundary disambiguation |
| `WtP` | Neural (ONNX or PyTorch) | 85 languages | [Transformer](transformer-plugins.md)-based, optional CUDA |
| `SaT` | Neural (PyTorch) | 85 languages | State-of-the-art, optional CUDA |

## File Format Support

| Format | Paragraph class | Sentence class | Input |
|---|---|---|---|
| Plain text | `RegexParagraphSplitter` | `RegexSentenceSplitter` | `str` |
| Markdown | `MarkdownParagraphSplitter` | `MarkdownSentenceSplitter` | path, URL, or raw text |
| HTML | `HTMLParagraphSplitter` | `HTMLSentenceSplitter` | path, URL, or raw HTML |
| PDF | `PDFParagraphSplitter` | `PDFSentenceSplitter` | local path or URL |
| DOC | `DOCParagraphSplitter` | `DOCSentenceSplitter` | local path or URL |
| DOCX | `DOCxParagraphSplitter` | `DOCxSentenceSplitter` | local path or URL |

## Quick Start

```python

# Sentence splitting — lightweight regex approach
from ovos_document_chunkers.text.sentence import RegexSentenceSplitter

splitter = RegexSentenceSplitter()
for sentence in splitter.chunk("This is sentence one. This is sentence two."):
    print(sentence)

# Paragraph splitting — neural model (SaT)
from ovos_document_chunkers import SaTSentenceSplitter

splitter = SaTSentenceSplitter({"model": "sat-3l-sm", "use_cuda": False})
for sentence in splitter.chunk(long_text):
    print(sentence)

# Markdown from URL
from ovos_document_chunkers.files.markdown import MarkdownParagraphSplitter

splitter = MarkdownParagraphSplitter()
for para in splitter.chunk("https://github.com/OpenVoiceOS/ovos-core/raw/dev/README.md"):
    print(para)

# HTML from URL
from ovos_document_chunkers.files.webpages import HTMLSentenceSplitter

splitter = HTMLSentenceSplitter()
for sent in splitter.chunk("https://example.com/page.html"):
    print(sent)

```

## Dependencies

| Package | Required for |
|---|---|
| `quebra-frases` | `RegexSentenceSplitter`, `RegexParagraphSplitter` |
| `pysbd` | `PySBDSentenceSplitter` |
| `wtpsplit` | `WtPSentenceSplitter`, `WtPParagraphSplitter`, `SaTSentenceSplitter`, `SaTParagraphSplitter` |
| `markdown-to-json` | `MarkdownParagraphSplitter`, `MarkdownSentenceSplitter` |
| `textract-py3` | `PDFParagraphSplitter`, `DOCParagraphSplitter`, `DOCxParagraphSplitter` and sentence variants |
| `requests` | URL-based input for all file chunkers |

## Quick Links

| Resource | Path |
|---|---|
| Machine-readable facts | `../QUICK_FACTS.md` |
| Common questions | `../FAQ.md` |
| Change log | `../MAINTENANCE_REPORT.md` |
| Known issues | `../AUDIT.md` |
| Improvement proposals | `../SUGGESTIONS.md` |

## Cross-References

- [ovos-media-classifier](https://github.com/OpenVoiceOS/ovos-media-classifier) — companion media classification library


- [ovos-plugin-manager](https://github.com/OpenVoiceOS/ovos-plugin-manager) — provides the base templates for chunker plugins.

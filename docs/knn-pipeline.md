# Hierarchical KNN Intent Pipeline

!!! abstract "In a nutshell"
    This is a *semantic* [intent](glossary.md) matcher: instead of matching keywords or example
    phrases literally, it understands what an utterance **means** by comparing it (via
    [embeddings](glossary.md)) to the intents your skills registered, and picks the closest one.
    It's the heavyweight option you reach for when the simpler, deterministic matchers
    ([Adapt](adapt-pipeline.md), [Padatious](padatious-pipeline.md)) can't confidently decide.

[`ovos-hierarchical-knn-pipeline`](https://github.com/OpenVoiceOS/ovos-hierarchical-knn-pipeline)
is an intent-matching [pipeline plugin](pipelines-overview.md) (entry point `opm.pipeline`,
class `HierarchicalKNNIntentPipeline`) powered by a **two-stage hierarchical k-NN classifier**
backed by **IBM Granite** embeddings and a **[FAISS](https://github.com/facebookresearch/faiss)**
index.

## How it works

- **Two-stage search**: it first narrows to the likely **domain**, then to the **intent** within
  it (using Wu–Lin pairwise probability estimation) — keeping search fast as the intent set grows.
- It classifies utterances into the intent labels **already registered** by loaded skills (Adapt,
  Padatious, and plugin-specific labels), and **ignores** labels from skills that aren't loaded.
  Adapt and Padatious intents are synced into the index dynamically at runtime.
- Search is automatically scoped to the **domains of loaded skills** (domain pre-filtering).

It is ideal as a **high-recall semantic stage** for cases where the deterministic engines fail to
produce a high-confidence match — conceptually similar to [Model2Vec](m2v-pipeline.md), but using
a pre-built FAISS index and a hierarchical classifier.

## Requirements & footprint

- **Languages**: en, pt, es, fr, it, de, nl, ca, gl, da, eu (11).
- **Model**: IBM Granite Embedding 97M Multilingual R2 (quantised ONNX, ~94 MB).
- **Index**: FAISS IVF+PQ — fast and memory-efficient for edge devices.
- The quantised encoder (`model_quint8_avx2.onnx`) requires an **AVX2-capable CPU**. Total
  footprint is ~560 MB (index + encoder).

```bash
pip install ovos-hierarchical-knn-pipeline
```

See [Pipelines Overview](pipelines-overview.md) for how to place it in your pipeline and how
matchers are ordered. For lighter alternatives see [Padacioso](padacioso.md) (literal),
[Nebulento](nebulento.md) (fuzzy), or [Palavreado](palavreado.md) (keyword).

# Plugin Arena

!!! abstract "In a nutshell"
    OVOS lets you swap in different plugins for jobs like understanding speech or recognizing commands — but which one is actually best? The Plugin Arena answers that by comparing them two ways: objective scores measured against test data, and a "which sounds better?" vote where people blindly pick between two plugins' results, scored a bit like chess rankings. It is purely a scoreboard for comparing plugins; it never installs or runs them itself. See the [Glossary](glossary.md) for unfamiliar terms.

> **Status:** [OpenVoiceOS/ovos-plugin-arena](https://github.com/OpenVoiceOS/ovos-plugin-arena) — in development. The **intent**, **STT**, **wake word**, and **VAD** leagues have live battles and ELO standings; **TTS** competitors are registered but not yet benchmarked (all entries sit at the seed ELO with zero battles).

**What this is:** a way to answer *"which OVOS plugin should I use?"* It compares plugins on two signals:

1. **Benchmarks** — accuracy/F1 for intent, WER for STT, detection metrics for wake word — computed offline against labeled datasets and published openly as HuggingFace datasets.
2. **Human preference** — chess-style ELO ratings from blind A/B "battles" where people pick the better of two plugin outputs. The initial ELO is seeded from the benchmarks; human votes refine it.

The arena is the *rating and voting* venue — **not** an execution venue. It never installs, isolates, or runs plugins.

---

## GitHub-Native, Zero Servers

The arena is a **repository**, not a service. There is no backend, no database, and no account system:

- **Data artifacts** are JSON files committed by scheduled GitHub Actions (`assemble.yml` daily, `tally.yml` hourly).
- **The UI** is a static Astro site published to **GitHub Pages**.
- **Votes** are **GitHub issues**.
- **Plugin predictions** are produced *outside* the arena as offline batch jobs and published as HuggingFace datasets.

Forking the repo and editing JSON yields a working arena. A local FastAPI shim may exist as a development tool only; it is not a deployment target.

---

## Design Principles

| Principle | Description |
|-----------|-------------|
| **GitHub-native** | Artifacts are committed JSON, the UI is GitHub Pages, votes are GitHub issues. No backend, no database. |
| **Decentralized predictions** | Plugins run outside the arena as offline jobs anywhere. The arena never installs or executes plugins in CI. |
| **HuggingFace as artifact layer** | Every prediction run is published as a queryable HF dataset, independent of the arena. |
| **Everything declarative** | Every competitor and dataset is a JSON file under `registry/`. Editing JSON is enough to extend the arena. |
| **Replayable ratings** | Battle ids are content hashes; the ELO seed is a deterministic function of the published predictions; human votes replay in **issue-number order**. Standings are reproducible from public data alone. |
| **All predictions kept** | Bad predictions are first-class content — failure cases guide plugin improvements. |

---

## Leagues (Modalities)

Each modality is an independent league with its own benchmarks, battle pools and ELO standings: `stt`, `tts`, `wake_word`, `vad`, and **three intent leagues** (keyword and template paradigms consume different supervision, so they are never ranked against each other):

| League | Who competes |
|---|---|
| `intent_template` | template/embedding engines (Padatious, Padacioso, Nebulento, …) |
| `intent_keyword` | keyword engines (Adapt, Palavreado, …) |
| `intent` | open league — mixed-paradigm pipeline **fusions** (ensembles) |

A "competitor" is a **shippable config**, not just a plugin: a single-stage pipeline benchmarks one engine, a multi-stage pipeline is an ensemble fighter in its own right, and the same plugin under a different config is a *different competitor*. `competitor_id` is the stable key for predictions, battles, ELO and leaderboards.

---

## Declarative Registry

- **Competitors** — `registry/competitors/<modality>/<id>.json`. For intent, `config` is a valid `mycroft.conf` fragment (an `intents` section with an ordered `pipeline` of `<plugin>-<tier>` stages).
- **Datasets** — `registry/datasets/<modality>/<id>.json`. One corpus per entry: HF source id + revision, `reference_fields` (the datashape contract), license, `lang` (or `lang: multi` + `langs`), and a `role` (`train`/`eval`). Keyword and template training corpora are distinct datasets with distinct datashapes.

---

## Prediction Contract (HuggingFace)

Predictions live in HF dataset repos — one per benchmark modality, named `ovos-<modality>-bench-<dataset_id>` (league underscores dashed), as per-competitor JSON lines at `predictions/<competitor_id>.jsonl`, one row per sample (language is a field on each row, not a path segment).

Core `PredictionRow` fields (`arena/models.py`):

| Field | Notes |
|--------|-------|
| `competitor_id` | Stable competitor key |
| `sample_id` | Stable ID within the source dataset |
| `dataset_id` | Source corpus identifier |
| `lang` | BCP-47 |
| `modality` | League (inferred from fields when absent) |
| `plugin_id`, `plugin_version` | Plugin name + exact installed version |
| `prediction` | Modality-specific payload |
| `runner_version` | Reproducibility anchor |
| `created_at` | Timestamp |

Modality-specific fields (kept inline or in `extras`):

- **Intent**: `utterance`, `reference_intent`, `exact_match`, `confidence`, `bucket`, `reference_slots`, `predicted_slots`.
- **STT**: `reference_text`, `wer`.
- **Shared diagnostics**: `latency_ms`.

---

## ELO Ratings

- Standard ELO formula (`arena/elo.py`): `K_FACTOR = 32` for new competitors (`< 30` battles), `K_FACTOR_VETERAN = 16` once past the `VETERAN_THRESHOLD = 30` battles.
- The ELO seed is derived deterministically from the published benchmark predictions; human votes (GitHub issues) replay in issue-number order on top of it.
- Standings are fully recomputable from public data alone — the leaderboard JSON committed by `tally.yml` is a cache, not the source of truth.

---

## Supported Modalities

| Modality | Status |
|----------|--------|
| Intent | Live (`benchmarks/intent_intents_for_eval.py`, multiple engines × languages) |
| STT | Live (`benchmarks/stt_minds14.py`, multiple languages) |
| VAD | Live (`benchmarks/vad_speech.py`, many languages) |
| Wake word | Live (`benchmarks/ww_hey_jarvis.py`, `ww_hey_mycroft.py`, `ww_computer.py`) |
| TTS | Registered, not yet benchmarked — competitors are declared but have no predictions or battles yet, so every entry sits at the seed ELO (human-vote-only boards planned, no auto metric or ELO seed) |

---

## Related Pages

- [STT Plugins](stt-plugins.md)
- [TTS Plugins](tts-plugins.md)
- [Wake Word Plugins](wake-word-plugins.md)
- [Wake Word Verifier](ww-verifier.md)
- [Testing & Ovoscope](ovoscope-overview.md)

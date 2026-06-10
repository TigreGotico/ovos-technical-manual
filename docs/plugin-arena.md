# Plugin Arena

> **Status:** [TigreGotico/ovos-plugin-arena](https://github.com/TigreGotico/ovos-plugin-arena) — in development.

The Plugin Arena answers the question *"which OVOS plugin should I use?"* with two complementary signals:

1. **Traditional benchmarks** — WER/CER for STT, detection metrics for wake word, accuracy for intent — computed offline and published as queryable HuggingFace datasets.
2. **Human preference** — chess-style ELO ratings produced by blind A/B battles where users pick the better of two plugin outputs.

---

## Design Principles

| Principle | Description |
|-----------|-------------|
| **Decentralized predictions** | Plugins run *outside* the arena, as offline batch jobs anywhere. The arena never installs, isolates, or executes plugins. |
| **HuggingFace as artifact layer** | Every prediction run is published as a queryable HF dataset (e.g. `OpenVoiceOS/ovos-stt-bench-pt-PT`). Predictions are a public benchmark independent of the arena. |
| **Arena stores battle outcomes only** | Votes, ratings, users — never raw predictions, never audio blobs. |
| **Organic growth** | New datasets and plugins are added by publishing more prediction datasets — no arena code changes. |
| **Replayable ratings** | ELO standings are deterministically recomputable from the persisted vote log. |

---

## System Architecture

```
┌────────────────────┐   publish    ┌──────────────────────────────────┐
│ Prediction Runners │ ───────────► │ HuggingFace datasets             │
│ (offline, cron)    │              │ ovos-<mod>-bench-<ds>-<lang>     │
└────────────────────┘              └───────────┬──────────────────────┘
                                                │ sample
                                                ▼
                       ┌──────────────────────────────────────┐
                       │ Arena backend (FastAPI + SQLite)     │
                       │  matchmaking · battles · votes · ELO │
                       └───────────┬──────────────────────────┘
                                   │ blind A/B
                                   ▼
                       ┌──────────────────────┐
                       │ Frontend (web)       │
                       │  listen/read · vote  │
                       └──────────────────────┘
```

---

## HF Dataset Contract

Dataset naming: `OpenVoiceOS/ovos-<modality>-bench-<dataset>-<lang>`

Minimum columns (all modalities):

| Column | Type | Notes |
|--------|------|-------|
| `sample_id` | str | Stable ID within the source dataset |
| `dataset_id` | str | Source corpus identifier + revision |
| `lang` | str | BCP-47 |
| `plugin_id` | str | OPM plugin name |
| `plugin_version` | str | Exact installed version |
| `prediction` | str/audio | Modality-specific payload |
| `runner_version` | str | Reproducibility anchor |
| `created_at` | timestamp | |

Per-modality extensions:

- **STT**: `audio` (ref to source sample), `reference_text`, `wer`, `cer`, `rtf`.
- **TTS**: `input_text`, synthesized `prediction` audio, `voice`, `rtf`.
- **Wake word**: `audio`, `label` (contains-ww or not), `prediction` (score/decision), `latency_ms`.

---

## ELO Ratings

- Standard ELO formula, K=32 for new plugins (< 30 battles), K=16 for veterans.
- Automated benchmark results (WER, RTF, detection F1) flow through the same ELO pipeline via `POST /api/v1/arena/votes/metric`.
- Full vote log is replayable: `POST /api/v1/arena/ranking/recompute` replays all votes in chronological order.

---

## API Endpoints (Arena Core)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/arena/plugins` | List registered plugins |
| POST | `/api/v1/arena/battles` | Create a blind A/B matchup |
| POST | `/api/v1/arena/votes` | Submit a human preference vote |
| POST | `/api/v1/arena/votes/metric` | Submit an automated metric vote |
| GET | `/api/v1/arena/ranking` | Current ELO leaderboard |
| POST | `/api/v1/arena/ranking/recompute` | Replay all votes and recompute |

---

## Supported Modalities

| Modality | Adapter status |
|----------|----------------|
| TTS | Working |
| Intent | Working |
| STT | Stub |
| Wake word | Stub |

---

## Related Pages

- [STT Plugins](stt-plugins.md)
- [TTS Plugins](tts-plugins.md)
- [Wake Word Plugins](wake-word-plugins.md)
- [Wake Word Verifier](ww-verifier.md)
- [Testing & Ovoscope](ovoscope-overview.md)

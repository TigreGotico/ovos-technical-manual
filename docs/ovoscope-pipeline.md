# Pipeline Plugin Testing

!!! abstract "In a nutshell"
    When the assistant hears a sentence, it tries to figure out which task you
    meant, handing the sentence to a series of matchers until one recognizes it.
    This page is a developer tool for testing those matchers on their own, to
    answer one focused question: does this sentence get matched, and to which
    task? It skips the rest of the assistant so the test runs quickly. See the
    [Glossary](glossary.md).

`ovoscope.pipeline` provides `PipelineHarness` for testing intent / pipeline
plugins in isolation — no skill is needed.

## New here? When to use this vs `End2EndTest`

Use `PipelineHarness` when you are writing or debugging a **pipeline plugin**
(Adapt, Padatious, Padacioso, OCP, …) and want to ask one question: *does this
utterance match, and to which intent?* It loads only the matching stages — no
real skill handlers run — so it is fast and focused.

Use [`End2EndTest`](ovoscope-end2end-test.md) instead when you are testing a
**skill** end to end (utterance in, `speak`/side-effects out).

## What Is Tested

Pipeline plugins (Adapt, Padatious, Padacioso, OCP, etc.) match utterances to
intents. `PipelineHarness` loads the specified stages on a `MiniCroft` that
has no skills, so only the pipeline matching logic is exercised.

## `_SinkSkill` — Internal Catch-all

`_SinkSkill` — `ovoscope/pipeline.py:37`

When `PipelineHarness` creates a `MiniCroft`, it injects an internal
`__ovoscope_sink__` skill as a routing target for matched intents.  This is
necessary because OVOS routes intent matches to a skill handler; without a
skill present the match is discarded.  `_SinkSkill` simply records the matched
intent message and signals the waiting `match()` call.

Users never interact with `_SinkSkill` directly.

## `PipelineHarness` — Context Manager

`PipelineHarness` — `ovoscope/pipeline.py:91`

```python
from ovoscope.pipeline import PipelineHarness

with PipelineHarness(
    pipeline=["ovos-adapt-pipeline-plugin.openvoiceos"],
    lang="en-US",
) as harness:
    msg = harness.assert_matches("turn on the kitchen lights")
    harness.assert_no_match("garbled nonsense xyz 123")

```

### Constructor Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `pipeline` | `List[str]` | `[]` | OPM pipeline stage IDs to load. |
| `pipeline_config` | `Dict[str, Dict]` | `{}` | Per-stage config overrides keyed by stage ID. |
| `lang` | `str` | `"en-US"` | Language tag. |

### Methods

| Method | Source | Returns | Description |
|--------|--------|---------|-------------|
| `match(utterance, timeout=5.0)` | `ovoscope/pipeline.py:156` | `Optional[Message]` | Send utterance; return matched `Message` or `None` on timeout/failure. |
| `assert_matches(utterance, intent_type=None, timeout=5.0)` | `ovoscope/pipeline.py:226` | `Message` | Assert at least one stage matches. Raises `AssertionError` if no match. `intent_type` is a substring check on `msg_type`. |
| `assert_no_match(utterance, timeout=2.0)` | `ovoscope/pipeline.py:256` | `None` | Assert no stage matches. Raises `AssertionError` if a match is found. |

### Pipeline Stage Ordering and Success vs Failure

OVOS evaluates pipeline stages in the order listed in `pipeline`.  The first
stage that returns a non-empty match list wins; remaining stages are skipped.

**Success signal**: `intent.service.skills.activated` bus message — emitted
when a stage commits to handling the utterance.

**Failure signal**: `intent_failure` or `mycroft.skill.handler.start` bus
messages — emitted when no stage matched after all stages have been consulted.

`match()` — `ovoscope/pipeline.py:156` — uses separate `threading.Event`
objects for success and failure so that an `intent_failure` arriving first
does not mask a subsequent late success match.  On timeout or failure the
method returns `None`; on success it returns the captured `Message`.

## Examples

### Testing Adapt Pipeline Matching

```python
from ovoscope.pipeline import PipelineHarness

with PipelineHarness(
    pipeline=["ovos-adapt-pipeline-plugin.openvoiceos"],
    lang="en-US",
) as harness:
    # Adapt must have registered an intent containing "LightsOnIntent"
    msg = harness.assert_matches(
        "turn on the kitchen lights",
        intent_type="LightsOnIntent",
    )
    print(msg.data)  # {"LightsOnKeyword": "lights", ...}

    # Unrecognised utterance must not match
    harness.assert_no_match("garbled xyz 123")

```

### Testing Padatious Entity Extraction

```python
from ovoscope.pipeline import PipelineHarness

with PipelineHarness(
    pipeline=["ovos-padatious-pipeline-plugin.openvoiceos"],
    lang="en-US",
) as harness:
    # Padatious must have a trained intent that matches this utterance
    msg = harness.assert_matches(
        "set a timer for 5 minutes",
        intent_type="timer.intent",
    )
    # Entity extraction is in msg.data
    assert msg.data.get("duration") == "5 minutes"

```

### `assert_matches(intent_type=...)` semantics

`intent_type` is a **substring** check on the matched message's `msg_type`
— `ovoscope/pipeline.py:208`:

```python

# Pass: msg_type "padatious:0.95:LightsOnIntent" contains "LightsOnIntent"
msg = harness.assert_matches("turn on the lights", intent_type="LightsOnIntent")

# Pass: no intent_type check — any match accepted
msg = harness.assert_matches("turn on the lights")

# Fail: "LightsOffIntent" not in "padatious:0.95:LightsOnIntent"
msg = harness.assert_matches("turn on the lights", intent_type="LightsOffIntent")

# → AssertionError: Expected intent type to contain 'LightsOffIntent', got '...'

```

## Advanced

### Two names for a pipeline: OPM ID vs priority-suffixed stage ID
There are two distinct identifier forms and they are easy to confuse:

- **OPM entry-point ID** — e.g. `ovos-adapt-pipeline-plugin.openvoiceos`. This is
  the `opm.pipeline` plugin name. It is what `PipelineHarness(pipeline=[...])`
  expects, and what you pass to `MiniCroft(default_pipeline=...)`.
- **Priority-suffixed stage ID** — e.g. `ovos-adapt-pipeline-plugin-high`,
  `-medium`, `-low`. Each plugin exposes three confidence tiers; the
  stage-group constants below list these suffixed IDs. `is_pipeline_available`
  strips the suffix before checking installation.

### Stage-group constants
Exported from the package top level for assembling realistic pipelines:

```python
from ovoscope import (
    DEFAULT_TEST_PIPELINE, LIGHT_TEST_PIPELINE,
    STOP_PIPELINE, CONVERSE_PIPELINE, ADAPT_PIPELINE,
    PADATIOUS_PIPELINE, PADACIOSO_PIPELINE, FALLBACK_PIPELINE,
    COMMON_QUERY_PIPELINE, PERSONA_PIPELINE, M2V_PIPELINE,
    NEBULENTO_PIPELINE, PALAVREADO_PIPELINE,
)
```

| Constant | Contents | Notes |
|----------|----------|-------|
| `DEFAULT_TEST_PIPELINE` | stop / converse / adapt / padatious / padacioso / common-query / fallback, interleaved high→medium→low | Needs `ovos-adapt-pipeline-plugin` **and** `ovos-padatious-pipeline-plugin` installed (Padatious pulls in swig/C). |
| `LIGHT_TEST_PIPELINE` | stop / converse / padacioso / fallback only | **No C extensions.** Padacioso is the pure-Python, swig-free Padatious-compatible engine bundled with `ovos-workshop`, so this runs in any skill-test env. |
| `STOP_PIPELINE`, `ADAPT_PIPELINE`, `PADATIOUS_PIPELINE`, `PADACIOSO_PIPELINE`, `FALLBACK_PIPELINE`, `M2V_PIPELINE` | the three `-high`/`-medium`/`-low` stage IDs | Confidence-tiered plugins. |
| `CONVERSE_PIPELINE`, `COMMON_QUERY_PIPELINE`, `NEBULENTO_PIPELINE`, `PALAVREADO_PIPELINE` | a single stage ID | Single-tier plugins (manager handles routing). |
| `PERSONA_PIPELINE` | `-high` and `-low` only | No medium tier. |

`MiniCroft` auto-selects: it defaults to `DEFAULT_TEST_PIPELINE` when its
plugins are installed, otherwise falls back to `LIGHT_TEST_PIPELINE`.

### Guarding tests on plugin availability — `is_pipeline_available`
`is_pipeline_available(pipeline: list[str]) -> bool` checks the `opm.pipeline`
entry points (via `importlib.metadata`, no MiniCroft spun up) and returns
`True` only if every stage's base plugin is installed. Use it to skip cleanly
when a C-extension engine is absent in CI:

```python
import unittest
from ovoscope import is_pipeline_available, M2V_PIPELINE

class TestM2V(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not is_pipeline_available(M2V_PIPELINE):
            raise unittest.SkipTest("ovos-m2v-pipeline not installed")
```

## Implementation Notes

`PipelineHarness.__enter__` — `ovoscope/pipeline.py:124` — creates a
`MiniCroft` with `skill_ids=[]` and the specified pipeline.

`PipelineHarness.match()` — `ovoscope/pipeline.py:156` — subscribes to
`intent.service.skills.activated` (success) and `intent_failure` /
`mycroft.skill.handler.start` (failure) before emitting the utterance,
then waits on a `threading.Event` with the given timeout.  Bus handlers are
removed after the wait completes to avoid cross-test leakage.

---

*Source code: [OpenVoiceOS/ovoscope](https://github.com/OpenVoiceOS/ovoscope).*

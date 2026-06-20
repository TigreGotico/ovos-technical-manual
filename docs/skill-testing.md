# Skill Testing with [ovoscope](ovoscope-overview.md)

This section is the entry point for end-to-end testing of OVOS skills using
**ovoscope** — the framework for verifying that skills behave correctly at the
bus message level.

See also: [Skill Design Guidelines](skill-design-guidelines.md) and
[Developer FAQ](skill-dev-faq.md).

---

## Your first test

If you only care that an utterance makes the skill *say* the right thing, the
whole test is one call. `End2EndTest.assert_spoke()` spins up a MiniCroft, fires
the utterance, and asserts a matching `speak` was emitted:

```python
from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import End2EndTest

SKILL_ID = "ovos-skill-hello-world.openvoiceos"

session = Session("first-test")
utterance = Message(
    "recognizer_loop:utterance",
    {"utterances": ["hello world"], "lang": "en-US"},
    {"session": session.serialize(), "source": "A", "destination": "B"},
)

End2EndTest(
    skill_ids=[SKILL_ID],
    source_message=utterance,
    expected_messages=[],            # not used by assert_spoke
).assert_spoke("Hello world")
```

Note the skill_id format: `<entry-point-name>.<author-namespace>`, e.g.
`ovos-skill-hello-world.openvoiceos`. This is the plugin entry point, not the PyPI
package name. When you need to assert the *full* message sequence (ordering,
routing, session state), use `.execute()` instead — covered below.

---

## What is ovoscope?

ovoscope is an end-to-end testing framework for OVOS skills. It runs a lightweight
in-process OVOS Core using a `FakeBus`, loads real skill plugins, fires a
`recognizer_loop:utterance` message, and captures every bus message produced in response
— then asserts against the captured sequence.

The key insight is that all OVOS skill behaviour is fully observable through bus messages.
Intent matching, converse, fallback, speak, and session changes all produce bus messages.
ovoscope intercepts every message on the in-process `FakeBus`, making the entire
skill interaction verifiable.

```
Test                         FakeBus
────                         ───────
source_message ──emit──►  [MiniCroft + loaded skills]
                                  │
                    ◄──capture────┤ all emitted messages
                                  │ until EOF message
                                  ▼
            assert against expected_messages[]

```

---

## Architecture

ovoscope is composed of three primary components:

### MiniCroft

`MiniCroft` (`ovoscope.MiniCroft`) is a subclass of `ovos_core.skill_manager.SkillManager`.
It replaces the real WebSocket [MessageBus](bus-service.md) with an in-process `FakeBus`, disables components
not needed for testing (file watcher, event scheduler, runtime installer), and loads only
the skill plugin IDs you specify.

It is created via the `get_minicroft()` factory function, which starts the instance and
waits for it to reach `READY` state before returning:

```python
from ovoscope import get_minicroft

croft = get_minicroft(["ovos-skill-hello-world.openvoiceos"])

# croft.status.state == ProcessState.READY

```

`MiniCroft` sets `isolate_config=True` by default, which clears user XDG configuration
so tests are reproducible regardless of the developer's local `mycroft.conf`. It also
sets a deterministic `default_pipeline` (`DEFAULT_TEST_PIPELINE`) that excludes AI/persona,
[OCP](ocp-pipeline.md), and m2v stages — ensuring consistent intent matching.

See [ovoscope: minicroft.md](ovoscope-minicroft.md) for the full constructor reference.

### FakeBus

`FakeBus` (from `ovos_utils.fakebus`) is an in-process pub/sub bus that implements
the same `emit` / `on` / `remove` API as the real `MessageBusClient`, but operates
entirely in memory. No WebSocket server is started. This makes tests fast and
self-contained with no network requirements.

### CaptureSession

`CaptureSession` (`ovoscope.CaptureSession`) subscribes to all messages on the `FakeBus`
for a single interaction. It sorts incoming messages into:

- **`responses`** — ordered synchronous messages from the intent pipeline


- **`async_responses`** — messages arriving from external threads (collected separately, unordered)


- **discarded** — messages matching `ignore_messages` or GUI namespace messages
  (when `ignore_gui=True`)

Capture ends when an EOF message (`ovos.utterance.handled` by default) is received.

### End2EndTest

`End2EndTest` (`ovoscope.End2EndTest`) is the primary API. It is a `dataclass` that wires
together `MiniCroft`, `CaptureSession`, and all assertion logic. You configure it once
and call `.execute()` to run the test:

```python
from ovoscope import End2EndTest
from ovos_bus_client.message import Message
from ovos_bus_client.session import Session

SKILL_ID = "ovos-skill-hello-world.openvoiceos"

session = Session("test-123")
session.pipeline = ["ovos-adapt-pipeline-plugin-high"]   # restrict to Adapt
utterance = Message(
    "recognizer_loop:utterance",
    {"utterances": ["hello world"], "lang": "en-US"},
    {"session": session.serialize(), "source": "A", "destination": "B"},
)

test = End2EndTest(
    skill_ids=[SKILL_ID],
    source_message=utterance,
    expected_messages=[
        utterance,
        Message(f"{SKILL_ID}:HelloWorldIntent",
                {"utterance": "hello world", "lang": "en-US"}),
        Message("speak", {"utterance": "Hello world", "lang": "en-US"}),
        Message("ovos.utterance.handled", {}),
    ],
)
test.execute(timeout=10)

```

`execute(timeout=30)` raises `AssertionError` on any mismatch. The assertion model is a
**subset match**: only keys present in `expected.data` and `expected.context` are
checked — extra keys in the received message are ignored. This lets you assert
precisely on the fields you care about.

See [ovoscope: end2end-test.md](ovoscope-usage.md) for the full
field and assertion reference.

---

## When to Use ovoscope vs FakeBus Unit Tests

| Scenario | Use |
|---|---|
| Test that a skill intent handler runs correct logic | FakeBus unit test |
| Test skill settings, decorators, or `initialize()` | FakeBus unit test |
| Test skill lifecycle (load / unload / reload) | FakeBus unit test |
| Test that an utterance matches a specific intent | **ovoscope** |
| Test the full message sequence a skill produces | **ovoscope** |
| Test message ordering and routing context | **ovoscope** |
| Test session state after an interaction | **ovoscope** |
| Test multi-turn dialogue (converse / fallback) | **ovoscope** |
| Test that a skill is blacklisted and does NOT match | **ovoscope** |

**Rule of thumb**: if you are asserting on *what gets emitted on the bus* — type,
order, data, or routing — use ovoscope. If you are testing the internal Python logic
of a handler in isolation, use FakeBus unit tests.

---

## What ovoscope Does NOT Cover

ovoscope focuses on the skill pipeline. The following are out of scope:

- **[PHAL](ovoscope-phal.md) plugins** — use `ovoscope.phal.MiniPHAL` / `PHALTest` instead (see [453-ovoscope-advanced.md](ovoscope-usage.md))


- **Audio service / [TTS](tts-plugins.md) lifecycle** — use `AudioServiceHarness` / `PlaybackServiceHarness` (see [453-ovoscope-advanced.md](ovoscope-usage.md))


- **[STT](stt-plugins.md) and audio transformer plugins** — use `MiniListener` / `ListenerTest` (see [453-ovoscope-advanced.md](ovoscope-usage.md))


- **GUI rendering** — `End2EndTest` discards GUI namespace messages by default
  (`ignore_gui=True`). To assert on `gui.*` traffic, use `GUICaptureSession`
  (see [Testing GUI messages](#testing-gui-messages) below) instead of widening
  the main capture.


- **Wake-word and [VAD](vad-plugins.md)** — use `FakeBus` unit tests directly

---

## Testing GUI messages

`GUICaptureSession` (`ovoscope.GUICaptureSession`) captures only `gui.*` /
`mycroft.gui.*` messages, so you can assert page navigation and namespace state
without polluting the main `End2EndTest` capture. It is a context manager taking
the bus:

```python
import time
from ovos_bus_client.message import Message
from ovoscope import get_minicroft, GUICaptureSession

mc = get_minicroft(["ovos-skill-hello-world.openvoiceos"])
with GUICaptureSession(mc.bus) as gui:
    mc.bus.emit(Message(
        "recognizer_loop:utterance",
        {"utterances": ["hello"], "lang": "en-US"},
    ))
    time.sleep(2)
    gui.assert_page_shown("helloworldskill", "hello.qml")
mc.stop()
```

Available assertions on `GUICaptureSession`:

| Assertion | Checks |
|---|---|
| `assert_page_shown(namespace, page, timeout=2.0)` | a page was shown in the namespace |
| `assert_namespace_value(namespace, key, value)` | a namespace data value equals `value` |
| `assert_namespace_has_key(namespace, key)` | a namespace data key was set |
| `assert_namespace_cleared(namespace)` | the namespace was cleared |

> **Upcoming.** Higher-level template assertions for `SYSTEM_*` GUI templates —
> `assert_template_shown(namespace, template, values=None)` — are **not yet on
> the released API**. They are proposed in DRAFT PR
> [ovoscope#83](https://github.com/OpenVoiceOS/ovoscope/pull/83); until it
> merges, assert on `assert_page_shown` / `assert_namespace_value` instead.

---

## Installation

```bash
uv pip install ovoscope
```

ovoscope requires Python 3.10+ and `ovos-core >= 2.0.4a2` (pulled automatically as a
dependency). The skill plugin under test must also be installed and discoverable via its
entry point.

Optional extras gate the harnesses on other pages:

- `ovoscope[audio]` → `ovos-audio` for the audio service harnesses (see
  [Audio Testing](audio-testing.md)).
- `ovoscope[tts]` → `jiwer` + a reference STT plugin for TTS intelligibility scoring.
- `ovoscope[pydantic]` → `ovos-pydantic-models` for typed fixtures.

Verify the skill under test is discoverable:

```bash
python -c "from ovos_plugin_manager.skills import find_skill_plugins; print(list(find_skill_plugins()))"
# should include: ovos-skill-hello-world.openvoiceos
```

---

## Directory Convention

End-to-end tests live in a separate directory from unit tests to allow independent
execution:

```
my-skill-repo/
├── test/
│   ├── unittests/
│   │   └── test_handlers.py
│   └── end2end/
│       ├── test_intent_match.py
│       ├── test_session_state.py
│       └── fixtures/
│           ├── hello_world_adapt.json
│           └── hello_world_padatious.json

```

Run them separately:

```bash

# Fast unit tests
uv run pytest test/unittests/ -v

# End-to-end tests (slower — spins up MiniCroft)
uv run pytest test/end2end/ -v --timeout=60

```

---

## Public API Summary

The core skill-testing classes are always importable from `ovoscope` directly:

```python
from ovoscope import (
    MiniCroft,          # in-process skill runtime (subclass of ovos_core SkillManager)
    get_minicroft,      # factory: create + wait for READY
    CaptureSession,     # message recorder for a single interaction
    End2EndTest,        # declarative test runner
    GUICaptureSession,  # capture gui.* messages for GUI assertions
)
```

The listener/audio harnesses are re-exported at the top level too, but only when
their optional dependency is installed — import them from their submodule to be
explicit:

```python
from ovoscope.listener import MiniListener, get_mini_listener, ListenerTest  # needs ovos-dinkum-listener
from ovoscope.audio import PlaybackServiceHarness, AudioServiceHarness        # needs ovos-audio
```

---

## Canonical Examples

- `Skills/ovos-skill-hello-world/test/test_helloworld.py` — [Adapt](adapt-pipeline.md) + [Padatious](padatious-pipeline.md) match + no-match


- `ovos-core/test/end2end/` — pipeline tests, blacklist tests

---

## Further Reading

- [451-ovoscope-usage.md](ovoscope-usage.md) — practical usage guide with all patterns and code examples


- [452-ovoscope-ci.md](ovoscope-ci.md) — CI/CD integration with GitHub Actions


- [453-ovoscope-advanced.md](ovoscope-usage.md) — audio, OCP, PHAL, listener, pipeline, and pydantic testing

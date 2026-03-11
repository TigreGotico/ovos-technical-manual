# Skill Testing with ovoscope

This section covers end-to-end testing of OVOS skills using **ovoscope** — the official
framework for verifying that skills behave correctly at the bus message level.

See also: [Skill Design Guidelines](400-skill-design-guidelines.md) and
[Developer FAQ](430-skill_dev_faq.md).

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
It replaces the real WebSocket MessageBus with an in-process `FakeBus`, disables components
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
OCP, and m2v stages — ensuring consistent intent matching.

See [ovoscope: minicroft.md](../ovoscope/docs/minicroft.md) for the full constructor reference.

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

session = Session("test-123")
utterance = Message(
    "recognizer_loop:utterance",
    {"utterances": ["hello world"], "lang": "en-us"},
    {"session": session.serialize(), "source": "A", "destination": "B"},
)

test = End2EndTest(
    skill_ids=["skill-hello-world.openvoiceos"],
    source_message=utterance,
    expected_messages=[
        utterance,
        Message("speak", {"utterance": "Hello!"}),
        Message("ovos.utterance.handled", {}),
    ],
)
test.execute()
```

`execute()` raises `AssertionError` on any mismatch. The assertion model is a
**subset match**: only keys present in `expected.data` and `expected.context` are
checked — extra keys in the received message are ignored. This lets you assert
precisely on the fields you care about.

See [ovoscope: end2end-test.md](../ovoscope/docs/end2end-test.md) for the full
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

- **PHAL plugins** — use `ovoscope.phal.MiniPHAL` / `PHALTest` instead (see [453-ovoscope-advanced.md](453-ovoscope-advanced.md))
- **Audio service / TTS lifecycle** — use `AudioServiceHarness` / `PlaybackServiceHarness` (see [453-ovoscope-advanced.md](453-ovoscope-advanced.md))
- **STT and audio transformer plugins** — use `MiniListener` / `ListenerTest` (see [453-ovoscope-advanced.md](453-ovoscope-advanced.md))
- **GUI rendering** — GUI namespace messages are discarded by default (`ignore_gui=True`)
- **Wake-word and VAD** — use `FakeBus` unit tests directly

---

## Installation

```bash
pip install ovoscope
```

ovoscope requires Python 3.10+ and `ovos-core >= 2.0.4a2` (pulled automatically as a
dependency). The skill plugin under test must also be installed and discoverable via its
entry point.

Verify discovery:

```bash
python -c "
from ovos_plugin_manager.skills import find_skill_plugins
print(list(find_skill_plugins()))
"
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

All primary classes are importable from `ovoscope` directly:

```python
from ovoscope import (
    MiniCroft,          # in-process skill runtime
    get_minicroft,      # factory: create + wait for READY
    CaptureSession,     # message recorder for a single interaction
    End2EndTest,        # declarative test runner
    MiniListener,       # in-process audio transformer pipeline
    get_mini_listener,  # factory: create MiniListener with plugins
    ListenerTest,       # declarative listener test runner
)
```

---

## Canonical Examples

- `Skills/ovos-skill-hello-world/test/test_helloworld.py` — Adapt + Padatious match + no-match
- `ovos-core/test/end2end/` — pipeline tests, blacklist tests

---

## Further Reading

- [451-ovoscope-usage.md](451-ovoscope-usage.md) — practical usage guide with all patterns and code examples
- [452-ovoscope-ci.md](452-ovoscope-ci.md) — CI/CD integration with GitHub Actions
- [453-ovoscope-advanced.md](453-ovoscope-advanced.md) — audio, OCP, PHAL, listener, pipeline, and pydantic testing

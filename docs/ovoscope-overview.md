# End-to-End Testing with `ovoscope`

**ovoscope** is the official testing framework for OpenVoiceOS skills and core components. It provides a lightweight, in-process environment for running **End-to-End (E2E) tests** without requiring a full system installation.

!!! success "The Gold Standard for Skills"
    E2E testing is the most reliable way to verify that your skill correctly understands intents, interacts with the MessageBus, and speaks the expected responses. Every official OVOS skill is required to pass `ovoscope` E2E tests.

---

## Why E2E Testing?

Traditional unit tests often miss integration issues (e.g., a skill loading correctly but failing to match a Padatious intent). `ovoscope` solves this by running a **MiniCroft** instance:

*   **Real Intent Matching**: Uses the actual Adapt and Padatious engines.


*   **Bus-Level Verification**: Asserts that the correct `speak` or `gui.show` messages are emitted.


*   **No Hardware Needed**: Uses a `FakeBus` and mocked audio/hardware layers.


*   **CI Ready**: Designed to run in GitHub Actions on every pull request.

---

## Core Components

| Component | Description |
|---|---|
| **[MiniCroft](ovoscope-minicroft.md)** | A lightweight `SkillManager` that runs in-process. |
| **[End2EndTest](ovoscope-usage.md)** | A declarative test runner for single or multi-turn interactions. |
| **[CaptureSession](capture-session.md)** | Records a sequence of bus messages for later replay or assertion. |
| **[FakeBus Reference](fakebus.md)** | The low-level mock bus implementation used by ovoscope. |

---

## Your First Test

`End2EndTest` is declarative: you give it the skill(s) to load, the utterance to
send, and the messages you expect back on the bus. The simplest assertion is
`assert_spoke()` — it runs the interaction and checks that the skill spoke a given
line, without you having to spell out the full message sequence:

```python
from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import End2EndTest

SKILL_ID = "ovos-skill-hello-world.openvoiceos"

def test_hello_world():
    session = Session("test-1")
    session.pipeline = ["ovos-adapt-pipeline-plugin-high"]
    utterance = Message(
        "recognizer_loop:utterance",
        {"utterances": ["hello world"], "lang": "en-US"},
        {"session": session.serialize(), "source": "A", "destination": "B"},
    )
    test = End2EndTest(
        skill_ids=[SKILL_ID],
        source_message=utterance,
        expected_messages=[],          # we are not checking the full sequence
        test_message_number=False,     # so don't assert on the message count
    )
    test.assert_spoke("Hello world")   # runs execute() internally, then scans for speak

```

`assert_spoke(text, lang="en-US", timeout=30)` runs `execute()` and then raises
`AssertionError` if no `speak` message with that exact utterance (and `lang`) was
emitted. Because it still runs the full `execute()`, leave `expected_messages`
empty **and** set `test_message_number=False` — otherwise `execute()` first asserts
that the received-message count equals the (empty) expected list and fails before the
speak is ever checked.

For full sequence assertions — message types, ordering, routing, and session
state — populate `expected_messages` and call `test.execute()` directly. See the
[Usage Guide](ovoscope-usage.md) for those patterns.

---

## Deep Dive Guides

*   **[Usage Guide](ovoscope-usage.md)** — Patterns for Adapt, Padatious, and multi-turn dialog.


*   **[Advanced Testing](ovoscope-usage.md)** — Testing OCP, PHAL, and Audio service interactions.


*   **[CI Integration](ovoscope-ci.md)** — How to add `ovoscope.yml` to your repository.


*   **[MiniCroft API](ovoscope-minicroft.md)** — Full reference for the in-process core.

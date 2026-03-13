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
| **[CaptureSession](ovoscope-overview.md)** | Records a sequence of bus messages for later replay or assertion. |
| **[FakeBus Reference](fakebus.md)** | The low-level mock bus implementation used by ovoscope. |

---

## Quick Start Example

A basic E2E test for a "Hello World" skill looks like this:

```python
from ovoscope import End2EndTest

def test_hello_world():
    # 1. Setup the test
    test = End2EndTest(skill_id="ovos-skill-hello-world.openvoiceos")
    
    # 2. Define the interaction
    test.say("hello")
    
    # 3. Assert the response
    test.expect_speak("hello world")
    
    # 4. Execute
    test.execute()

```

---

## Deep Dive Guides

*   **[Usage Guide](ovoscope-usage.md)** — Patterns for Adapt, Padatious, and multi-turn dialog.


*   **[Advanced Testing](ovoscope-usage.md)** — Testing OCP, PHAL, and Audio service interactions.


*   **[CI Integration](ovoscope-ci.md)** — How to add `ovoscope.yml` to your repository.


*   **[MiniCroft API](ovoscope-minicroft.md)** — Full reference for the in-process core.

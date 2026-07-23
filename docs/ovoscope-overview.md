# Testing Skills with `ovoscope`

!!! abstract "In a nutshell"
    `ovoscope` is the official tool for testing OpenVoiceOS skills and core parts. It runs a small,
    fast, pretend version of the whole assistant in one process, so you can confirm a request is
    understood and answered correctly without real hardware. "End-to-end" just means it checks the
    whole journey — from what the user said to what the assistant did. This page gets you started;
    the **full, always-current reference lives in the [ovoscope repo's `docs/`](https://github.com/OpenVoiceOS/ovoscope/tree/dev/docs)**. See the [Glossary](glossary.md).

!!! info "This page is a guide; the reference is in the repo"
    `ovoscope` is actively developed, so its detailed per-harness reference is kept **in the tool's
    own [`docs/`](https://github.com/OpenVoiceOS/ovoscope/tree/dev/docs)** rather than copied here
    (which would drift out of sync). This page gives you the concept and a working first test, then
    links to the authoritative reference for each harness.

**ovoscope** provides a lightweight, in-process environment for running **End-to-End (E2E) tests**
without a full system installation. Every official OVOS skill is required to pass `ovoscope` E2E
tests.

---

## Why E2E testing?

Traditional unit tests miss integration issues (e.g. a skill that loads fine but fails to match a
Padatious intent). `ovoscope` solves this by running a **MiniCroft** instance — a real in-process
`SkillManager`:

- **Real intent matching** — uses the actual Adapt and Padatious engines.
- **Bus-level verification** — asserts the correct `speak` / `gui.page.show` messages are emitted.
- **No hardware** — uses a `FakeBus` and mocked audio/hardware layers.
- **CI ready** — designed to run in GitHub Actions on every pull request.

---

## Your first test

`End2EndTest` is declarative: give it the skill(s) to load, the utterance to send, and the messages
you expect back. The simplest assertion is `assert_spoke()` — it runs the interaction and checks the
skill spoke a given line, without spelling out the full message sequence:

```python
from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import End2EndTest

SKILL_ID = "ovos-skill-hello-world.openvoiceos"

def test_hello_world():
    session = Session("test-1")
    session.pipeline = ["ovos-padatious-pipeline-plugin"]
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

`assert_spoke(text, lang="en-US", timeout=30)` runs `execute()` and then raises `AssertionError` if
no `speak` message with that exact utterance (and `lang`) was emitted. Because it still runs the full
`execute()`, leave `expected_messages` empty **and** set `test_message_number=False` — otherwise
`execute()` first asserts the received-message count equals the (empty) expected list and fails before
the speak is ever checked.

For full sequence assertions — message types, ordering, routing, and session state — populate
`expected_messages` and call `test.execute()` directly (see the
[usage guide](https://github.com/OpenVoiceOS/ovoscope/blob/dev/docs/usage-guide.md)).

---

## The harnesses (full reference in the repo)

`ovoscope` ships a harness per subsystem. Each is documented in the tool's
[`docs/`](https://github.com/OpenVoiceOS/ovoscope/tree/dev/docs):

| Harness / topic | What it tests | Reference |
|---|---|---|
| `MiniCroft` | The in-process core that loads your skills | [minicroft.md](https://github.com/OpenVoiceOS/ovoscope/blob/dev/docs/minicroft.md) |
| `End2EndTest` | Declarative single/multi-turn interactions | [end2end-test.md](https://github.com/OpenVoiceOS/ovoscope/blob/dev/docs/end2end-test.md) · [usage-guide.md](https://github.com/OpenVoiceOS/ovoscope/blob/dev/docs/usage-guide.md) |
| `CaptureSession` | Recording bus messages for assertion/replay | [capture-session.md](https://github.com/OpenVoiceOS/ovoscope/blob/dev/docs/capture-session.md) |
| Pipeline testing | Intent-pipeline matching | [pipeline.md](https://github.com/OpenVoiceOS/ovoscope/blob/dev/docs/pipeline.md) |
| OCP testing | Media ("play …") skills | [ocp.md](https://github.com/OpenVoiceOS/ovoscope/blob/dev/docs/ocp.md) · [media-testing.md](https://github.com/OpenVoiceOS/ovoscope/blob/dev/docs/media-testing.md) |
| Audio service testing | TTS / sound playback lifecycle | [audio-testing.md](https://github.com/OpenVoiceOS/ovoscope/blob/dev/docs/audio-testing.md) |
| Listener testing | The speech/listener service | [listener.md](https://github.com/OpenVoiceOS/ovoscope/blob/dev/docs/listener.md) · [voice-loop.md](https://github.com/OpenVoiceOS/ovoscope/blob/dev/docs/voice-loop.md) |
| PHAL testing | Hardware-abstraction plugins | [phal.md](https://github.com/OpenVoiceOS/ovoscope/blob/dev/docs/phal.md) |
| GUI testing | `gui.page.show` and GUI state | [gui-testing.md](https://github.com/OpenVoiceOS/ovoscope/blob/dev/docs/gui-testing.md) |
| Pydantic integration | Typed message assertions | [pydantic-integration.md](https://github.com/OpenVoiceOS/ovoscope/blob/dev/docs/pydantic-integration.md) |
| Bus coverage | Which message types your test exercised | [bus-coverage.md](https://github.com/OpenVoiceOS/ovoscope/blob/dev/docs/bus-coverage.md) |
| CLI | The `ovoscope` command-line runner | [cli.md](https://github.com/OpenVoiceOS/ovoscope/blob/dev/docs/cli.md) |

The low-level `FakeBus` it builds on lives in `ovos-utils` (`ovos_utils.fakebus`).

---

## Running in CI

Add the shared `ovoscope` workflow to your skill repo so the tests run on every pull request — see
[CI Integration](https://github.com/OpenVoiceOS/ovoscope/blob/dev/docs/ci-integration.md) and the
manual's [gh-automations](gh-automations-overview.md) page for the OVOS CI conventions.

---

*Source code & full reference: [OpenVoiceOS/ovoscope](https://github.com/OpenVoiceOS/ovoscope) — see its [`docs/`](https://github.com/OpenVoiceOS/ovoscope/tree/dev/docs).*

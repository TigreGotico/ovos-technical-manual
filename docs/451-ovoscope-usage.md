# ovoscope Usage Guide

This page covers practical usage of ovoscope — from installation through all common
testing patterns. See [450-skill-testing.md](450-skill-testing.md) for the conceptual
overview and architecture.

---

## Installation

Install ovoscope and the skill under test in the same virtual environment:

```bash
# Editable installs — recommended during development
uv pip install -e ovoscope/ -e Skills/ovos-skill-hello-world/

# Or via PyPI
pip install ovoscope ovos-skill-hello-world
```

Verify the skill is discoverable via its entry point before writing tests:

```bash
python -c "
from ovos_plugin_manager.skills import find_skill_plugins
plugins = list(find_skill_plugins())
print('Found skills:', plugins)
assert 'ovos-skill-hello-world.openvoiceos' in plugins
"
```

If the skill is not listed, check your `pyproject.toml` entry point registration:

```toml
[project.entry-points."ovos.plugin.skill"]
"my-skill.author" = "my_skill:MySkill"
```

---

## Quick Start

The canonical example uses `ovos-skill-hello-world.openvoiceos`, which has two intents:

- **HelloWorldIntent** (Adapt) — triggered by "hello world"
- **Greetings.intent** (Padatious) — triggered by greetings like "good morning"

```python
import unittest
from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import End2EndTest

SKILL_ID = "ovos-skill-hello-world.openvoiceos"

class TestHelloWorld(unittest.TestCase):
    def test_hello_world(self):
        session = Session("test-session-1")
        session.pipeline = ["ovos-adapt-pipeline-plugin-high"]
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
                Message(f"{SKILL_ID}.activate", data={}, context={"skill_id": SKILL_ID}),
                Message(f"{SKILL_ID}:HelloWorldIntent",
                        data={"utterance": "hello world", "lang": "en-US"},
                        context={"skill_id": SKILL_ID}),
                Message("mycroft.skill.handler.start",
                        data={"name": "HelloWorldSkill.handle_hello_world_intent"},
                        context={"skill_id": SKILL_ID}),
                Message("speak",
                        data={"lang": "en-US", "expect_response": False},
                        context={"skill_id": SKILL_ID}),
                Message("mycroft.skill.handler.complete",
                        data={"name": "HelloWorldSkill.handle_hello_world_intent"},
                        context={"skill_id": SKILL_ID}),
                Message("ovos.utterance.handled", data={}, context={"skill_id": SKILL_ID}),
            ],
        )
        test.execute(timeout=10)
```

`execute()` raises `AssertionError` on the first mismatch. Assertions use subset matching:
only keys present in `expected.data` and `expected.context` are checked — extra keys in
the received message are ignored.

---

## Pattern 1 — Adapt Intent Match

Set `session.pipeline` to restrict matching to Adapt only. This avoids accidental
Padatious matches and makes tests deterministic:

```python
from ovoscope import ADAPT_PIPELINE

session = Session("test-adapt")
session.pipeline = ADAPT_PIPELINE  # ["ovos-adapt-pipeline-plugin-high", ...medium, ...low]
```

The pipeline constants exported by ovoscope cover all standard stages:

```python
from ovoscope import (
    ADAPT_PIPELINE,
    PADATIOUS_PIPELINE,
    CONVERSE_PIPELINE,
    FALLBACK_PIPELINE,
    STOP_PIPELINE,
    COMMON_QUERY_PIPELINE,
    DEFAULT_TEST_PIPELINE,  # all standard stages, no AI/persona/OCP
)
```

---

## Pattern 2 — Padatious Intent Match

Padatious uses `.intent` file names as the message type. Restrict the session pipeline
to Padatious only so Adapt does not shadow the match:

```python
session = Session("test-padatious")
session.pipeline = ["ovos-padatious-pipeline-plugin-high"]
message = Message(
    "recognizer_loop:utterance",
    {"utterances": ["good morning"], "lang": "en-US"},
    {"session": session.serialize(), "source": "A", "destination": "B"},
)
test = End2EndTest(
    skill_ids=[SKILL_ID],
    source_message=message,
    expected_messages=[
        message,
        Message(f"{SKILL_ID}.activate", data={}, context={"skill_id": SKILL_ID}),
        Message(f"{SKILL_ID}:Greetings.intent",   # Padatious intent file name
                data={"utterance": "good morning", "lang": "en-US"},
                context={"skill_id": SKILL_ID}),
        Message("mycroft.skill.handler.start",
                data={"name": "HelloWorldSkill.handle_greetings"},
                context={"skill_id": SKILL_ID}),
        Message("speak",
                data={"lang": "en-US", "expect_response": False},
                context={"skill_id": SKILL_ID}),
        Message("mycroft.skill.handler.complete",
                data={"name": "HelloWorldSkill.handle_greetings"},
                context={"skill_id": SKILL_ID}),
        Message("ovos.utterance.handled", data={}, context={"skill_id": SKILL_ID}),
    ],
)
test.execute(timeout=10)
```

For Padatious the `speak` message's `utterance` value may vary due to dialog file
randomisation. Omit `"utterance"` from `expected.data` if it is non-deterministic —
assert on `lang` and `meta` instead.

---

## Pattern 3 — Recording Mode (Bootstrap Fixtures)

When you don't yet know the exact message sequence, let ovoscope record it from a live
run:

```python
from ovoscope import End2EndTest
from ovos_bus_client.message import Message
from ovos_bus_client.session import Session

SKILL_ID = "ovos-skill-hello-world.openvoiceos"
session = Session("recorder-session")
session.pipeline = ["ovos-adapt-pipeline-plugin-high"]
message = Message(
    "recognizer_loop:utterance",
    {"utterances": ["hello world"], "lang": "en-US"},
    {"session": session.serialize(), "source": "A", "destination": "B"},
)

# Run live, capture messages, return a ready-to-use End2EndTest
test = End2EndTest.from_message(
    message=message,
    skill_ids=[SKILL_ID],
    timeout=20,
)

# Save to a JSON fixture — safe to commit (anonymize=True strips personal data)
test.save("tests/fixtures/hello_world_adapt.json", anonymize=True)
```

`anonymize=True` (the default) strips real location and personal data from the session
context before saving.

---

## Pattern 4 — Replay from JSON Fixture

Committed JSON fixtures make tests fully self-contained:

```python
import unittest
from ovoscope import End2EndTest

class TestFromFixture(unittest.TestCase):
    def test_adapt_from_fixture(self):
        test = End2EndTest.from_path("tests/fixtures/hello_world_adapt.json")
        test.execute(timeout=10)

    def test_padatious_from_fixture(self):
        test = End2EndTest.from_path("tests/fixtures/hello_world_padatious.json")
        test.execute(timeout=10)
```

Skills still need to be installed: the JSON stores `skill_ids` and `execute()` calls
`get_minicroft()` which loads the real plugin. The fixture stores the expected message
sequence, not the skill code.

You can also use the CLI to replay fixtures without writing test code:

```bash
ovoscope run tests/fixtures/hello_world_adapt.json --timeout 30
```

---

## Pattern 5 — Reusing MiniCroft Across Tests

Creating a `MiniCroft` is expensive because it trains intent models. Reuse it across
tests in the same class:

```python
import unittest
from ovoscope import End2EndTest, get_minicroft

SKILL_ID = "ovos-skill-hello-world.openvoiceos"

class TestHelloWorldShared(unittest.TestCase):
    def setUp(self):
        self.minicroft = get_minicroft([SKILL_ID])

    def tearDown(self):
        if self.minicroft:
            self.minicroft.stop()

    def test_adapt_match(self):
        session = Session("shared")
        session.pipeline = ["ovos-adapt-pipeline-plugin-high"]
        message = Message(
            "recognizer_loop:utterance",
            {"utterances": ["hello world"], "lang": "en-US"},
            {"session": session.serialize(), "source": "A", "destination": "B"},
        )
        test = End2EndTest(
            minicroft=self.minicroft,   # pass existing instance — NOT stopped after execute()
            skill_ids=[SKILL_ID],
            source_message=message,
            expected_messages=[...],
        )
        test.execute(timeout=10)
```

When `minicroft` is passed explicitly, `End2EndTest` sets `managed=False` and does
**not** call `minicroft.stop()` at the end of `execute()`. Your `tearDown` owns cleanup.

---

## Pattern 6 — Multi-Turn Conversation

Pass a list of `Message` objects as `source_message` to test a multi-turn dialogue.
ovoscope emits them in order and propagates session state between turns:

```python
session = Session("multi-turn")
session.pipeline = ["ovos-adapt-pipeline-plugin-high"]

turn1 = Message(
    "recognizer_loop:utterance",
    {"utterances": ["hello world"], "lang": "en-US"},
    {"session": session.serialize(), "source": "A", "destination": "B"},
)

# Turn 2 omits "session" — ovoscope propagates it from the last received message
turn2 = Message(
    "recognizer_loop:utterance",
    {"utterances": ["good morning"], "lang": "en-US"},
    {"source": "A", "destination": "B"},
)

test = End2EndTest(
    skill_ids=[SKILL_ID],
    source_message=[turn1, turn2],   # list of turns
    expected_messages=[
        turn1,
        # ... turn 1 messages ...
        Message("ovos.utterance.handled", data={}, context={"skill_id": SKILL_ID}),
        turn2,
        # ... turn 2 messages ...
        Message("ovos.utterance.handled", data={}, context={"skill_id": SKILL_ID}),
    ],
)
test.execute(timeout=20)
```

---

## Pattern 7 — Testing Fallback Skills

Fallback skills receive a `"ovos.skills.fallback.ping"` message before the main fallback
handler fires. The expected sequence is longer than a normal intent match:

```python
session = Session("fallback-session")
session.pipeline = ["ovos-fallback-skill-plugin-high"]
message = Message(
    "recognizer_loop:utterance",
    {"utterances": ["what is the meaning of life"], "lang": "en-US"},
    {"session": session.serialize(), "source": "A", "destination": "B"},
)
test = End2EndTest(
    skill_ids=["my-fallback-skill.author"],
    source_message=message,
    expected_messages=[
        message,
        Message("ovos.skills.fallback.ping", {}),
        # ... handler messages ...
        Message("ovos.utterance.handled", {}),
    ],
)
test.execute(timeout=15)
```

`DEFAULT_KEEP_SRC` (pre-populated in ovoscope) ensures that `ovos.skills.fallback.ping`
routing is always validated against the original source message context, not the rolling
flip-point tracker.

---

## Pattern 8 — Session State Validation

Use `final_session` and `activation_points` to assert on session state at the end of
a test:

```python
from ovos_bus_client.session import Session
from ovoscope import End2EndTest

SKILL_ID = "ovos-skill-hello-world.openvoiceos"

expected_session = Session("state-check")
expected_session.pipeline = ["ovos-adapt-pipeline-plugin-high"]
expected_session.activate_skill(SKILL_ID)   # must remain active after the interaction

session = Session("state-check")
session.pipeline = ["ovos-adapt-pipeline-plugin-high"]
message = Message(
    "recognizer_loop:utterance",
    {"utterances": ["hello world"], "lang": "en-US"},
    {"session": session.serialize(), "source": "A", "destination": "B"},
)

test = End2EndTest(
    skill_ids=[SKILL_ID],
    source_message=message,
    expected_messages=[...],
    final_session=expected_session,
    test_final_session=True,
    test_active_skills=True,
    activation_points=[f"{SKILL_ID}.activate"],
    deactivation_points=["intent.service.skills.deactivate"],
)
test.execute(timeout=10)
```

Fields validated against `final_session`: `active_skills`, `lang`, `pipeline`,
`system_unit`, `date_format`, `time_format`, `site_id`, `session_id`,
`blacklisted_skills`, `blacklisted_intents`.

---

## Disabling Individual Assertion Groups

Some assertion groups can be turned off when a message is noisy or non-deterministic:

| Parameter | Default | Effect |
|---|---|---|
| `test_message_number` | `True` | Assert exact message count |
| `test_msg_type` | `True` | Assert message type for each position |
| `test_msg_data` | `True` | Assert expected data keys match |
| `test_msg_context` | `True` | Assert expected context keys match |
| `test_routing` | `True` | Assert source/destination routing |
| `test_active_skills` | `True` | Assert skill activation state |
| `test_final_session` | `True` | Assert final session state |

Example — disable data and routing checks for a noisy third-party message:

```python
test = End2EndTest(
    ...
    test_msg_data=False,
    test_routing=False,
)
```

---

## Async Messages

Some messages arrive from external threads and may appear at any time (e.g., GUI updates
that race with bus messages). Declare them in `async_messages` to collect them separately
without affecting the ordered assertion:

```python
test = End2EndTest(
    skill_ids=[SKILL_ID],
    source_message=message,
    expected_messages=[...],      # sync messages only
    async_messages=["gui.page.show"],
    test_async_messages=True,     # assert "gui.page.show" was received
    test_async_message_number=True,
)
```

Async messages are stored in `CaptureSession.async_responses` and are excluded from
`test_message_number` count.

---

## CLI Shortcuts

The `ovoscope` command-line tool provides five subcommands:

```bash
# Record a fixture from an installed skill
ovoscope record \
    --skill-id ovos-skill-hello-world.openvoiceos \
    --utterance "hello" \
    --output fixture.json \
    --lang en-US

# Replay a fixture
ovoscope run fixture.json --verbose --timeout 30

# Compare two fixtures
ovoscope diff expected.json actual.json

# Validate fixture schema
ovoscope validate test/fixtures/*.json

# Scan workspace for E2E coverage
ovoscope coverage "OpenVoiceOS Workspace/" --format table
```

Live recording from a running OVOS instance:

```bash
ovoscope record --live \
    --bus-url ws://localhost:8181/core \
    --skill-id ovos-skill-date-time.openvoiceos \
    --utterance "what time is it" \
    --output datetime_fixture.json
```

---

## Troubleshooting

**Timeout — no messages received**: the skill plugin is not loaded. Verify
`find_skill_plugins()` returns your skill ID. Also check that `session.pipeline` is not
empty.

**Skill not loading**: set `LOG.set_level("DEBUG")` and watch for `"Loaded skill: ..."` in
output. If it never prints, the entry point is wrong.

**Intent not matching**: for Adapt, confirm all required keywords are present in the
utterance. For Padatious, check that training phrase files exist under
`~/.local/share/`.

**`get_minicroft()` hangs**: a skill is raising an exception during `_startup`. Set
`LOG.set_level("DEBUG")` and watch for tracebacks.

**Flaky tests from session ID collisions**: use unique session IDs per test class, or
generate them:

```python
import uuid
session = Session(str(uuid.uuid4()))
```

---

## See Also

- [450-skill-testing.md](450-skill-testing.md) — architecture overview
- [452-ovoscope-ci.md](452-ovoscope-ci.md) — CI/CD integration
- [453-ovoscope-advanced.md](453-ovoscope-advanced.md) — audio, OCP, PHAL, pydantic testing
- [ovoscope: end2end-test.md](../ovoscope/docs/end2end-test.md) — full `End2EndTest` field reference
- [ovoscope: minicroft.md](../ovoscope/docs/minicroft.md) — full `MiniCroft` reference

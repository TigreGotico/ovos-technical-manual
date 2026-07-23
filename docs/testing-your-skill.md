# Test Your Skill

!!! abstract "In a nutshell"
    This page picks up right after [Your First Skill](first-skill.md): the `ovos-skill-my-first`
    skill you just wrote. Here you'll add an automated test for it — one that sends it the
    utterance "hello" and checks it replies correctly, without needing a microphone, speakers, or
    a running assistant. By the end you'll have a test you can run locally and in CI on every
    change.

## Why test a skill end-to-end?

A skill can *look* correct — the code imports cleanly, the files are in the right place — and
still fail the moment a real user talks to it: the intent phrasing might not actually match, the
dialog file might have a typo, or the entry point might not point at the right class. An
**end-to-end (E2E) test** catches these by running a small, in-process copy of OVOS, sending it a
real utterance, and checking what comes back out — the same journey a spoken command takes, minus
the microphone. `ovoscope` is the tool the OVOS project itself uses for this; every skill accepted
into the ecosystem is expected to ship at least one.

## Step 1 — Install ovoscope

Add it as a test dependency of the skill you built in [Your First Skill](first-skill.md):

```bash
pip install ovoscope
```

For a real skill repository, list it under a `[project.optional-dependencies]` "test" extra in
`pyproject.toml` instead of installing it loose, so `pip install -e .[test]` pulls in everything a
contributor needs:

```toml
[project.optional-dependencies]
test = ["ovoscope"]
```

## Step 2 — Write the first `End2EndTest`

Create `test/test_hello.py` next to your skill's `pyproject.toml`:

```python
from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import End2EndTest

SKILL_ID = "my-first.youruser"


def test_hello_matches_and_speaks():
    session = Session("test-1")
    session.pipeline = ["ovos-padatious-pipeline-plugin"]
    utterance = Message(
        "recognizer_loop:utterance",
        {"utterances": ["hello"], "lang": "en-US"},
        {"session": session.serialize(), "source": "A", "destination": "B"},
    )
    test = End2EndTest(
        skill_ids=[SKILL_ID],
        source_message=utterance,
        expected_messages=[],
        test_message_number=False,
    )
    # hello.dialog has three possible lines and OVOS picks one at random,
    # so assert the skill spoke one of the real candidates, not one fixed string.
    messages = test.execute()
    spoken = [m.data.get("utterance") for m in messages if m.msg_type == "speak"]
    assert spoken, "expected the skill to speak, got nothing"
    assert spoken[0] in {
        "Hello! Nice to meet you.",
        "Hi there!",
        "Hey — how can I help?",
    }
```

!!! note "Why `ovos-padatious-pipeline-plugin`, not Adapt?"
    `Hello.intent` is a **Padatious** intent file (one example phrase per line) — that's a
    different matcher from Adapt's keyword grammar. `session.pipeline` tells OVOS which intent
    engines to try, and in which order; it has to include the engine that actually understands
    your intent file, or the utterance is never matched. See [Pipelines Overview](pipelines-overview.md)
    for how the stages fit together.

`skill_ids` restricts which skill(s) `ovoscope` loads for the test, so you're only ever testing
your own skill — not every skill installed on the machine.

## Step 3 — Run it

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest test/test_hello.py -v
```

`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` avoids autoloading unrelated pytest plugins that some OVOS
dependencies register — harmless to leave set for any OVOS test run. A real run looks like this
(trimmed of the framework's own deprecation-warning noise):

```text
test/test_hello.py::test_hello_matches_and_speaks PASSED                [100%]

================== 1 passed, 563 warnings in 70.16s (0:01:10) ==================
```

!!! tip "First run is slow, and that's normal"
    The bulk of that ~70s is `ovoscope` spinning up a full in-process `SkillManager` and loading
    **every** intent-pipeline plugin installed on the machine (Adapt, Padatious, Padacioso, and any
    others you have) — not just the one your test needs. On a machine with only the pipeline
    plugins your skill actually depends on, startup is much faster.

## Step 4 — Test the failure path

A test that only ever sends utterances your skill *should* match doesn't tell you much. Add a
second test that sends something unrelated and checks the skill stays silent — this is what
catches an intent file matching too eagerly:

```python
# test/test_hello_nomatch.py
from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import End2EndTest

SKILL_ID = "my-first.youruser"


def test_unrelated_utterance_is_not_handled():
    """An utterance the intent files never taught the skill must NOT trigger it."""
    session = Session("test-2")
    session.pipeline = ["ovos-padatious-pipeline-plugin"]
    utterance = Message(
        "recognizer_loop:utterance",
        {"utterances": ["what is the capital of france"], "lang": "en-US"},
        {"session": session.serialize(), "source": "A", "destination": "B"},
    )
    test = End2EndTest(
        skill_ids=[SKILL_ID],
        source_message=utterance,
        expected_messages=[],
        test_message_number=False,
    )
    messages = test.execute()
    spoken = [m.data.get("utterance") for m in messages if m.msg_type == "speak"]
    assert not spoken, f"skill should stay silent for an unrelated utterance, got: {spoken}"
```

```text
test/test_hello_nomatch.py::test_unrelated_utterance_is_not_handled PASSED [100%]

================== 1 passed, 303 warnings in 72.87s (0:01:12) ==================
```

!!! warning "Testing an *error* dialog"
    If your skill calls `self.speak_dialog("some_error")` on a caught exception (a missing API
    key, a network failure, …), test that path the same way: drive the skill into the failing
    condition and assert it spoke the error dialog's text instead of crashing silently or leaking
    a raw traceback to the user. `ovos-skill-my-first` has no such path — it can't fail — so there
    is nothing further to add here for this particular skill.

## Step 5 — Fixtures and the `ovoscope` CLI

`ovoscope` also ships a standalone CLI (`ovoscope --help`) for working with fixtures — recorded
bus-message sequences you can replay without writing a pytest file:

| Subcommand | What it does |
|---|---|
| `ovoscope record` | Capture a fixture: send one utterance to a MiniCroft instance and save the resulting messages to a JSON file. |
| `ovoscope run FIXTURE` | Replay a saved fixture and exit non-zero if it no longer matches. |
| `ovoscope diff A B` | Compare two fixture files. |
| `ovoscope validate FILE...` | Schema-validate one or more fixture files. |
| `ovoscope coverage` | Scan a workspace for which behaviors have E2E test coverage. |
| `ovoscope bus-coverage` | Run fixtures and report which bus message types were exercised. |

A fixture is just the saved output of an `End2EndTest`. `End2EndTest.from_message()` runs the
utterance through a real `MiniCroft`, captures *every* message that comes back, and hands you a
test object whose `.save(path)` writes that captured sequence to JSON — this is what `ovoscope
record` does internally:

```python
# test/record_hello_fixture.py — one-off script, not a pytest file
from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import End2EndTest

session = Session("test-1")
session.pipeline = ["ovos-padatious-pipeline-plugin"]
utterance = Message(
    "recognizer_loop:utterance",
    {"utterances": ["hello"], "lang": "en-US"},
    {"session": session.serialize(), "source": "A", "destination": "B"},
)
test = End2EndTest.from_message(
    utterance,
    ["my-first.youruser"],
    timeout=30,
    default_pipeline=["ovos-padatious-pipeline-plugin"],
)
test.save("test/fixtures/hello.json")
```

Running it produces a fixture with the full 7-message sequence for this interaction — the
utterance coming in, the skill activating, the intent matching, the handler starting, the `speak`,
and the handler/utterance completing:

```text
$ python3 test/record_hello_fixture.py
saved OK
```

Validate its shape, then replay it:

```bash
ovoscope validate test/fixtures/hello.json
```

```text
[validate] OK  test/fixtures/hello.json
```

```bash
ovoscope run test/fixtures/hello.json -v
```

!!! warning "A recorded fixture can be non-deterministic — watch for timestamps"
    Replaying the fixture above with `ovoscope run` reliably reports a mismatch, not because
    anything is actually broken, but because the session's `active_handlers` records a Unix
    timestamp (*when the skill activated*) at capture time — and that timestamp is different every
    time you re-run it:
```text
    [run] FAIL: ❌ message context mismatch for key 'session' - expected
    '...activated_at': 1784823640.9039652...' | got '...activated_at': 1784823715.739504...'
    ```
    Timestamps, request IDs, and anything else that legitimately changes between runs will do this
    to any fixture that captures full message context. Compare only the fields you actually care
    about instead of the whole context — either pass `assert_spoke()`/`execute()` with a narrower
    `expected_messages` list in a pytest test (as in Steps 2–4), or use `ovoscope diff` with the
    default (context-skipping) comparison rather than `--include-context` when comparing fixtures.

!!! tip "`ovoscope record` from the command line"
    The `ovoscope record` subcommand does the same capture directly from the shell —
    `ovoscope record --skill-id my-first.youruser --utterance "hello" --output test/fixtures/hello.json`
    — without writing any Python. Both routes produce the same fixture format; use whichever fits
    your workflow. The Python API is handy when you want to tweak the `Session` (language,
    pipeline list) before recording.

## Step 6 — Wire it into CI

Add a workflow that runs the test suite on every pull request:

```yaml
name: Skill End-to-End Tests (ovoscope)

on:
  pull_request:
    branches: [dev, master, main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install skill + test deps
        run: pip install -e .[test]
      - name: Run ovoscope end-to-end tests
        run: |
          export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
          pytest test/ -v
```

!!! tip "A shared workflow already exists"
    Rather than maintaining this yaml by hand in every skill repo, official OVOS skills call a
    shared, reusable ovoscope workflow instead:
    ```yaml
    jobs:
      ovoscope:
        uses: OpenVoiceOS/gh-automations/.github/workflows/ovoscope.yml@dev
        secrets: inherit
        with:
          python_version: '3.11'
          install_extras: 'test'
          test_path: 'test'
    ```
    See [GH-Automations Workflows](gh-automations-workflows.md) for the full set of shared CI
    building blocks and what each input configures.

## Where to go next

- The full `End2EndTest` API — multi-turn conversations, asserting exact message sequences,
  session state, GUI pages, and every other harness `ovoscope` ships — lives in
  [Testing Skills with ovoscope](ovoscope-overview.md).
- Give the skill something to extract from what the user said — see [Intent Design](intents.md).
- Back to the beginning — see [Your First Skill](first-skill.md).

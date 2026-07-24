# Troubleshooting & Debugging

!!! abstract "In a nutshell"
    You said something to OVOS and nothing happened. This page is a decision tree for finding out
    why. It follows the same journey as [The Life of an Utterance](life-of-an-utterance.md) — mic,
    wake word, speech-to-text, intent matching, skill, text-to-speech — and at each stop shows where
    the evidence lives (which log file, which bus message), what a healthy result looks like, and
    the exact command to check it yourself. No programming background required to follow along;
    deeper technical detail is layered in as the page goes.

Every stage below can be checked two ways: **tail a log file** (works everywhere, including headless
boxes over SSH), or **watch the bus live** with `ovos-busmon` (works anywhere a browser can reach the
device, and shows every stage in one place instead of six log files). Start with the logs — they
need no extra install — then reach for `ovos-busmon` when you want everything in one filterable view.

---

## Where the logs live

OVOS runs several independent services (listener, intent/skills, audio, messagebus, GUI), and each
one writes its **own** log file, named after the service. By default they land under the XDG state
directory — on a typical Linux install that is:

```text
~/.local/state/mycroft/
├── audio.log     # ovos-audio — TTS + playback
├── bus.log       # ovos-messagebus
├── skills.log    # ovos-core — intent matching + skill execution
├── voice.log     # ovos-dinkum-listener — mic, wake word, STT
└── ovos.log      # any process that never set its own service name (see note)
```

!!! note "Where `ovos.log` comes from"
    The shared logger (`ovos-utils`) names its log file after whatever service name was set;
    if a process never sets one — a one-off script, a plugin running standalone, or a service
    started before it calls its own name-setting step — it falls back to the logger's own
    default name, `OVOS`, lower-cased to `ovos.log`. Seeing this file usually just means some
    component is logging under the generic default rather than its own service log.

The directory can be overridden per-service via the `logs.path` config key (or `logging.<service>.
logs.path` for a per-service override); see [Turning up log detail](#turning-up-log-detail) below.
Each service also logs to `stdout`, so if it runs under systemd or Docker, `journalctl` /
`docker logs` shows the same lines.

`ovos-logs` (shipped by `ovos-utils`) is the quickest way to read them without hunting for the path:

```bash
ovos-logs show -l skills      # page through skills.log with `less`
ovos-logs list --error        # every ERROR line across all logs
ovos-logs slice --start "1-1-2024 09:00"   # a time-bounded slice
```

See the [Command-line Tools](cli-tools.md#reading-the-logs-ovos-logs) page for the full flag
reference.

---

## Watch the bus while you speak — `ovos-busmon`

All the stages in this guide talk to each other over the [messagebus](bus-service.md): the listener
emits an utterance message, the intent service emits a match, the skill emits a `speak`, and so on.
**[`ovos-busmon`](https://github.com/OpenVoiceOS/ovos-busmon)** is a small web app that connects to
the bus as a client and streams every one of those messages live to a browser tab — it turns six
separate log files into one filterable, searchable timeline.

Under the hood it is a FastAPI + WebSocket/SSE service that opens an `ovos-bus-client` connection to
the messagebus and keeps an in-memory ring buffer of everything it sees. The browser UI lets you:

- filter the live stream by message type (glob patterns, e.g. `ovos.*` or `recognizer_loop:*`)
- full-text search across message type, data, context, and session
- filter by session ID, source, and destination
- pause/resume capture and sort newest/oldest first
- export the captured buffer as JSON/JSONL for later inspection
- inject an arbitrary message onto the bus from the UI (the same trick as `ovos-say-to`, but visual)

There is also a zero-install mode: the UI is a single static page that can open a WebSocket straight
to `ws://<device>:8181/core` with no server component at all — useful for a one-off look without
installing anything.

### Installing and running it

```bash
pip install ovos-busmon
ovos-busmon
```

To hack on it (or track `dev`), install from a clone instead:

```bash
git clone https://github.com/OpenVoiceOS/ovos-busmon
cd ovos-busmon
pip install .
ovos-busmon
```

By default it binds to `http://127.0.0.1:8005` and connects outward to a messagebus at
`localhost:8181`. Both ends are configurable through environment variables (or a `.env` file next to
where you run it):

| Variable | Default | Meaning |
|---|---|---|
| `OVOS_BUS_HOST` / `OVOS_BUS_PORT` | `localhost` / `8181` | Where the *target* OVOS messagebus is. |
| `BUSMON_HOST` / `BUSMON_PORT` | `127.0.0.1` / `8005` | Where busmon's own web UI listens. |
| `BUSMON_USERNAME` / `BUSMON_PASSWORD` | `ovos` / `ovos` | HTTP Basic auth for the web UI. |
| `BUFFER_SIZE` | `2000` | How many messages the ring buffer keeps. |

A Docker route is also available (`docker compose up --build` from the repo), using the image
`jarbasai/ovos-busmon:latest`; its bundled compose file binds the container to `127.0.0.1:8005` only
and sets `OVOS_BUS_HOST=host.docker.internal` so it can reach a bus running on the host.

!!! warning "Local debugging only — never expose this to the internet"
    `ovos-busmon` mirrors **every** message on the bus — including STT transcripts, intent matches,
    and skill responses — and ships with a default username/password (`ovos` / `ovos`) that most
    people never change. Its message-injection feature also lets anyone who can reach it emit
    arbitrary commands onto your assistant's bus. Keep it bound to `127.0.0.1` or your local LAN,
    change the default credentials before leaving it running, and never port-forward it to the
    public internet.

### A concrete walkthrough

1. Start `ovos-busmon` (it will keep retrying the bus connection until the device is reachable).
2. Open `http://127.0.0.1:8005` in a browser and log in with the configured credentials.
3. Speak (or trigger) an utterance on the OVOS device.
4. Filter by `recognizer_loop:*` — the first hit is the raw utterance leaving the listener
   (Stage 2 below); if nothing appears here, the problem is upstream of the bus entirely (Stage 1).
5. Filter by `ovos.intent.matched` and `ovos.utterance.handled` — these tell you which pipeline
   stage claimed the utterance and confirm the lifecycle actually closed (Stage 4/5 below).
6. Filter by `ovos.utterance.speak` — its absence, with everything else present, points at a silent
   skill handler; its presence with no audio points at the TTS/playback stage (Stage 6).

Each stage further down cites the exact message type to filter on, so this same walkthrough can be
repeated stage-by-stage instead of glancing at the whole stream at once.

---

## Stage 1 — Is the service even running, and is the bus reachable?

**Log:** `bus.log` — **Bus visual:** any message appearing at all in `ovos-busmon`

Before anything else, confirm the [messagebus](bus-service.md) server is up: everything else in
OVOS is a client of it, so if it is down nothing downstream can work.

```bash
ovos-listen
```

`ovos-listen` is the simplest possible probe — it just emits `mycroft.mic.listen` and exits. If the
bus isn't reachable, the client itself logs the failure to the terminal:

```text
WARNING - Connection Refused. Is Messagebus Service running?
WARNING - Message Bus Client will reconnect in 5.0 seconds.
```

If you see that, start (or restart) `ovos-messagebus`, then `ovos-core` and `ovos-dinkum-listener`,
and check `bus.log` for a clean startup (no repeated `Connection Refused` lines). In `ovos-busmon`,
this stage is trivially visible: if the bus is down, busmon's own connection retries forever and the
stream stays empty.

!!! tip "Nothing wrong with the mic yet"
    This stage says nothing about audio hardware — it only confirms the messagebus itself accepts
    connections. Hardware problems show up in Stage 2.

---

## Stage 2 — Did the mic/wake word fire?

**Log:** `voice.log` (service `ovos-dinkum-listener`) — **Bus filter:** `recognizer_loop:record_begin`
/ `record_end`, `ovos.listener.record.started` / `ovos.listener.record.ended`

A healthy wake-word trigger and recording cycle looks like this in `voice.log`:

```text
DEBUG - Record begin
DEBUG - Hotword utterance: hey mycroft
DEBUG - Emitting hotword event: recognizer_loop:wakeword
...
DEBUG - Record end
```

Common failure signatures:

| Symptom in `voice.log` | Likely cause |
|---|---|
| No `Record begin` line at all when you speak | Wake word plugin isn't hearing you — check the mic device/gain, or the [wake word](wake-word-plugins.md) model/sensitivity. |
| `Record begin` fires but never followed by `Record end` | VAD never detects silence — check the [VAD plugin](vad-plugins.md) config. |
| Repeated wake-word triggers with no speech after | False positives — the wake word threshold may be too low. |

To hear the recorded audio yourself, turn on the listener's own recording keys in
[configuration](config.md) (user config, under `"listener"`):

```json
{
  "listener": {
    "save_utterances": true,
    "record_wake_words": true,
    "save_path": "/tmp/ovos-audio-debug"
  }
}
```

`save_utterances` writes every STT-bound recording as a `.wav` file under
`<save_path>/utterances/`; `record_wake_words` does the same for wake-word triggers under
`<save_path>/wake_words/`. Set them with:

```bash
ovos-config set -k save_utterances -v true
```

`ovos-listen` can also be used to force a listening cycle without saying the wake word at all —
useful for isolating STT problems (Stage 3) from wake-word problems.

---

## Stage 3 — Did STT produce text?

**Log:** `voice.log` — **Bus filter:** `recognizer_loop:utterance` (spec name `ovos.utterance.handle`)

Once recording stops, the audio is handed to the [STT plugin](stt-plugins.md). A healthy
transcription shows up as:

```text
DEBUG - STT: ['what time is it']
```

Common failure signatures:

| Symptom | Likely cause |
|---|---|
| `ERROR - Empty transcription, either recorded silence or STT failed!` | The STT engine returned nothing — check the STT plugin is installed/configured and (for online engines) that the network/API key is working. |
| `INFO - Ignoring low confidence STT transcriptions: [...]` | A confidence filter dropped the candidate — check `min_stt_confidence` in the listener config. |
| Transcription text is garbled/wrong words | STT engine or language mismatch, not a bug in the pipeline — try a different STT plugin or model size. |

To skip the microphone and STT entirely and test everything **downstream** of this point, inject the
text directly onto the bus as if STT had already produced it:

```bash
ovos-say-to "what time is it"
```

This runs `MessageBusClient().emit(Message("recognizer_loop:utterance", {"utterances": ["what time
is it"], "lang": "en-us"}))` — exactly the same message the listener would have emitted. It is the
single most useful command for isolating "is my problem in audio, or in matching/skills?" without
having to speak into a microphone at all.

In `ovos-busmon`, filter by `recognizer_loop:*` (or the spec name `ovos.utterance.handle`): seeing
the utterance land there with the right text confirms STT worked, regardless of what happens next.

---

## Stage 4 — Which pipeline stage matched (or didn't)?

**Log:** `skills.log` (or `intents.log` if the intent service runs standalone) — **Bus filter:**
`ovos.intent.matched`, `ovos.utterance.handled`

`ovos-core`'s `IntentService` logs every step of matching. A healthy match looks like:

```text
INFO - Parsing utterance: ['what time is it']
INFO - adapt_high match (en-us): IntentMatch(...)
DEBUG - final intent match: {...}
```

`adapt_high` here is one entry of the configurable `intents.pipeline` list. The bundled default
pipeline (see [Pipelines Overview](pipelines-overview.md)) uses the canonical plugin IDs, in this
order:

--8<-- "snippets/default-pipeline.md"

If nothing matches, every matcher in that list logs a
miss (as `no match from <bound method ...>`, naming the matcher's Python function) before the
utterance falls through to the next stage, and eventually to nothing:

```text
DEBUG - no match from <bound method ...StopService.match_high ...>
DEBUG - no match from <bound method ...ConverseService.match ...>
DEBUG - no match from <bound method ...OCPPipelineMatcher.match_high ...>
DEBUG - no match from <bound method ...PadatiousPipeline.match_high ...>
DEBUG - no match from <bound method ...AdaptPipeline.match_high ...>
...
```

Use `ovos-say-to` (Stage 3) to reproduce this deterministically without speaking, then grep
`skills.log` for the exact utterance text:

```bash
ovos-say-to "some phrase that does nothing" && ovos-logs show -l skills
```

Every request ends with exactly one `ovos.utterance.handled` event, whether an intent matched or
not — its absence means the intent service itself crashed or hung; its presence with no matched
intent means every pipeline plugin genuinely rejected the utterance (usually a vocabulary/training
data problem in the target skill, not a bug). See [Intent Layers](layers.md) and the
[Pipelines Overview](pipelines-overview.md) for how to add or reorder matchers.

In `ovos-busmon`, filter by `ovos.intent.matched` (see which skill/intent name claimed it) or by
`ovos.utterance.handled` (confirm the lifecycle closed at all) — this reproduces the same
information as the log grep above but across the whole pipeline at a glance, and lets you inspect
the full JSON payload of the match.

---

## Stage 5 — Did the skill handler raise?

**Log:** `skills.log` — **Bus filter:** `ovos.intent.handler.error` (legacy `mycroft.skill.handler.
error`) — part of the handler-lifecycle trio `...handler.start` → `...complete` / `...error`
described in [The Life of an Utterance](life-of-an-utterance.md#5-skill-execution)

Once a skill's intent handler is invoked, any unhandled exception inside it is caught by the skill
base class, logged, and (unless disabled) spoken back as a generic error dialog:

```text
ERROR - <full traceback of the exception>
```

and the corresponding `...error` bus message is emitted so the orchestrator knows the handler
failed rather than silently returning nothing. Common failure signatures to grep for in
`skills.log`:

| Symptom | Likely cause |
|---|---|
| A traceback right after `final intent match` | The skill's own handler code raised — read the traceback, it names the exact file/line. |
| `Failed to update settings.json` | Non-fatal — a settings write failed after a successful handler run; doesn't explain a silent utterance. |
| No traceback, no `speak`, handler simply never runs | The bus dispatch itself failed to reach the skill process — check the skill actually loaded (see [Skill Manager](skill-manager.md)) and its `skill_id` matches the matched intent. |

In `ovos-busmon`, filter by `*handler.error` to catch any handler-lifecycle error message across
every skill in one view, or filter by the specific skill's ID to isolate its traffic.

---

## Stage 6 — Did TTS speak?

**Log:** `audio.log` (service `ovos-audio`) — **Bus filter:** `ovos.utterance.speak` (legacy
`speak`), `ovos.utterance.handled`

Once a skill calls `self.speak()`, `ovos-audio` picks up the message. A healthy synthesis + playback
cycle logs:

```text
INFO - Speak: what time is it, it's three o'clock
```

Common failure signatures:

| Symptom in `audio.log` | Likely cause |
|---|---|
| `EXCEPTION - TTS synth failed! ...` | The [TTS plugin](tts-plugins.md) itself errored (model missing, API failure for an online engine, bad voice config). |
| `ERROR - No fallback TTS available and main TTS failed!` | Both the primary and fallback TTS engines failed — check both are configured, or that the fallback exists at all. |
| No `Speak:` line at all, despite the skill having matched | The `ovos.utterance.speak` message never reached `ovos-audio` — check `ovos-audio` is actually running (Stage 1) and not crashed. |
| `Speak:` line present but no sound | Not a bug in the pipeline — check the audio sink: ALSA/PulseAudio device selection, system volume, or that the WAV file was actually written and playable. |

To test synthesis in isolation, without going through STT or intent matching at all:

```bash
ovos-speak "testing one two three"
```

This emits a bare `speak` message directly, exercising exactly the dialog-transformer → TTS plugin →
tts-transformer → playback path described in [The Life of an Utterance](life-of-an-utterance.md#6-text-to-speech-tts).
If this command produces sound but a real skill interaction doesn't, the problem is upstream (Stages
1-5), not in audio output.

In `ovos-busmon`, filter by `ovos.utterance.speak`: present with no sound points at the audio sink;
absent (with everything upstream present) points at a silent or failed skill handler (Stage 5).

---

## Turning up log detail

By default every service logs at `INFO`. To see the `DEBUG` lines quoted throughout this page
(pipeline misses, hotword events, STT confidence filtering, etc.), raise the log level in the
[user configuration](config.md).

!!! note "`ovos-config set` only edits keys that already exist somewhere"
    `ovos-config set -k log_level -v DEBUG` looks for `log_level` in the *currently merged*
    configuration first, and on a fresh install nothing ships that key by default — so the
    command fails with `Error: No key that fits the query` before you've ever set a log level.
    The reliable first-time path is to add the key directly to your user config file
    (`~/.config/mycroft/mycroft.conf`, creating it if it doesn't exist yet):

    ```json
    {
      "log_level": "DEBUG"
    }
    ```

    Once the key exists anywhere in the merged configuration (including after you've added it
    this way once), `ovos-config set -k log_level -v DEBUG` will find and update it on later runs.

This applies to every service (they all watch the same configuration and pick up the change
without a restart). To raise the level for only one service, add the nested `"logging"` section
instead — the same first-time caveat applies, so add it directly to the user config file:

```json
{
  "logging": {
    "voice": { "log_level": "DEBUG" }
  }
}
```

!!! note "`log_level` only takes effect from user or system configuration"
    This key is deliberately not honored in the bundled defaults or the remote/backend
    configuration layer — it must be set locally (user or system config) to take effect. See
    [Configuration](config.md) for how the configuration layers are merged.

Two environment variables set the *starting* level and logger name before any configuration loads,
mostly useful when running a service by hand: `OVOS_DEFAULT_LOG_LEVEL` and `OVOS_DEFAULT_LOG_NAME`.

---

## Reproducing an issue offline with `ovoscope`

If a bug reproduces reliably, don't keep re-triggering it on real hardware — capture it once and
replay it. **[`ovoscope`](ovoscope-overview.md)** runs an in-process, mocked assistant (`MiniCroft`)
that loads real skills and the real intent-matching engines without any audio hardware, and its CLI
can turn a live bus session into a fixture file:

```bash
# capture a fixture; --live records from a running OVOS instance
ovoscope record --utterance "what time is it" --output fixture.json --live

# replay a fixture and exit non-zero on failure
ovoscope run fixture.json

# compare two fixture files
ovoscope diff expected.json actual.json
```

`record` also takes `--skill-id` to choose which skills load, `--lang` (default `en-US`),
`--pipeline` to restrict the stages, and `--bus-url` for a non-default bus address.

This turns "it happens sometimes on the device but I can't tell why" into a fixed, replayable test
case — see the [ovoscope guide](ovoscope-overview.md) for the full workflow, including
`End2EndTest` for writing an assertion once the fixture is captured.

---

## Where to ask for help

If the logs and bus traffic don't explain the problem, the OpenVoiceOS community is active on:

- **[OVOS Chat on Matrix](https://matrix.to/#/!XFpdtmgyCoPDxOMPpH:matrix.org?via=matrix.org)** —
  real-time chat with maintainers and other users; the
  [skills channel](https://matrix.to/#/#openvoiceos-skills:matrix.org) is specific to skill
  development questions.
- **[Open Conversational AI forum](https://community.openconversational.ai/)** — longer-form
  questions, bug reports, and searchable past discussions.

When asking for help, include the relevant log excerpt (or an `ovos-busmon` JSON export) for the
stage where the trail goes cold — it is almost always faster to diagnose with the actual message
sequence than with a description of the symptom alone.

---

## Related Pages

- [The Life of an Utterance](life-of-an-utterance.md) — the full journey this page's stages mirror.
- [Command-line Tools](cli-tools.md) — every CLI referenced above, with full flag references.
- [Configuration](config.md) — how `log_level` and other keys are layered and merged.
- [ovoscope Overview](ovoscope-overview.md) — full end-to-end testing reference.
- [Bus Service](bus-service.md) — what the messagebus is and how clients connect to it.

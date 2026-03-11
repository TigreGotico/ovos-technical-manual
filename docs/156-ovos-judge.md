# ovos-judge — LLM-Driven QA Testing

`ovos-judge` is an automated QA tool for OpenVoiceOS skills and personas. A configurable LLM
acts as a **judge**: it generates test utterances, sends them to a running OVOS instance (or any
compatible persona), captures the spoken response and MessageBus events, and evaluates whether
the skill under test behaved correctly.

Install: `pip install ovos-judge`

Repository: `OpenVoiceOS Workspace/Agent Plugins/ovos-judge`

---

## Quick Start

```bash
pip install ovos-judge ovos-solver-openai-plugin
ovos-judge              # http://localhost:8888
```

Open the browser, pick a chat plugin for the judge, select a persona target (e.g. OVOS Local),
write a test prompt, and click **Start Test**.

---

## Architecture

```
Browser (index.html + app.js)
    │  HTTP / WebSocket
FastAPI app (app.py)
    │                   │
JudgeLLM             PersonaTarget
(judge.py)           (persona_client.py)
    │                   │
Any OPM              ovos-persona
chat plugin          + BusEventCollector (optional)
```

The session loop — `session.py:TestSession` — alternates between two passes:

1. **Judge → send_utterance**: the judge LLM chooses the next utterance to test.
2. **PersonaTarget → response**: the utterance is sent to OVOS; the response and any bus events
   are collected.
3. **Judge → evaluate**: the judge receives a JSON context object (spoken text, skill_id,
   intent, intent_failed, response_time, bus_events) and returns a pass/fail verdict with
   reasoning.

Session states: `IDLE → RUNNING → COMPLETED` — `session.py:27`

---

## Judge Actions

The judge LLM responds with one of three JSON actions on each round.

### `send_utterance`

```json
{
  "action": "send_utterance",
  "utterance": "what is the weather in Lisbon",
  "expected_skill": "skill-weather",
  "test_description": "weather in a specific city"
}
```

`expected_skill` is an optional substring match against the captured `skill_id`. If set and
the skill does not match, the judge automatically marks the exchange as FAIL critical —
regardless of what the test prompt says.

### `evaluate`

```json
{
  "action": "evaluate",
  "pass": true,
  "reasoning": "Skill responded with temperature and conditions as expected.",
  "severity": "info"
}
```

`severity` values: `critical` (skill completely broken), `warning` (partial/degraded),
`info` (minor issue or pass).

### `done`

```json
{
  "action": "done",
  "summary": "6/8 tests passed. Weather by city and forecast work. Wind speed queries fail."
}
```

---

## Test Prompts

The test prompt is injected into the judge LLM's system prompt at `{user_prompt}` —
`judge.py:16`. It directly controls what gets tested.

### Minimal prompt

```
Test the alarm skill. Set alarms, cancel them, and list upcoming alarms.
```

### Full regression prompt

```
Test the date/time skill (skill-date-time.openvoiceos).

Utterances to try:
- "what time is it"
- "what's today's date"
- "what time is it in Tokyo"
- "how many days until Christmas"

Pass criteria:
- Response must include a specific time, date, or duration
- skill_id must match "skill-date-time"

Fail criteria:
- Empty response
- "I don't know" or fallback phrase

Run 8–10 tests then summarise.
```

### Tips

- **Be specific about the skill** — include its skill ID so the judge uses `expected_skill`
  automatically.
- **Specify pass/fail criteria** — improves consistency across different LLM backends.
- **Include edge cases** — invalid inputs, ambiguous queries, rapid follow-ups.
- **Set a scope limit** — e.g. "Run 10–15 utterances" to keep CI runtimes bounded.
- **Use `max_rounds`** — 10–20 rounds is usually sufficient for a single skill.

---

## Target Personas

ovos-judge sends test utterances to a `PersonaTarget` — `persona_client.py`. Three bundled
personas are included:

### OVOS Local

Connects to a running `ovos-core` via MessageBus. This is the primary target for skill QA.
`BusEventCollector` (`persona_client.py:44`) also subscribes to the same bus to capture
`skill_id`, `intent_type`, and `intent_failed`.

```json
{
  "name": "OVOS Local",
  "solvers": ["ovos-solver-bus-plugin"],
  "ovos-solver-bus-plugin": {"autoconnect": true, "host": "127.0.0.1", "port": 8181}
}
```

### HiveMind

Connects to a HiveMind satellite or hub. Bus event capture is not available for HiveMind
targets — `skill_id` and `intent` will be empty.

### OpenAI ChatBot

Points at the OpenAI API. Useful for testing prompt-based personas or as a reference baseline
to compare against OVOS skill responses.

### Custom personas

In the web UI, select **Persona File Path** and enter the absolute path to any persona JSON
file, or select **Custom JSON** and paste the config directly. Any OPM solver plugin can be
used as a persona backend.

---

## Headless / CI Mode

Run ovos-judge without a browser for CI pipelines:

```bash
ovos-judge --config my_test.json
ovos-judge --config my_test.json --output result.json
```

Exit codes: `0` = all exchanges passed; `1` = one or more failures.

Config file format (`TestSessionConfig` — `models.py:16`):

```json
{
  "persona": {
    "name": "OVOS Local",
    "bus_host": "127.0.0.1",
    "bus_port": 8181
  },
  "judge": {
    "plugin": "ovos-solver-openai-plugin",
    "prompt": "Test the weather skill. Try current weather, forecasts, and weather in specific cities.",
    "lang": "en-us",
    "max_rounds": 20,
    "timeout": 30
  }
}
```

### GitHub Actions

```yaml
- name: Run ovos-judge QA
  run: |
    pip install ovos-judge ovos-solver-openai-plugin
    ovos-judge --config test/qa/weather_skill.json
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## Web UI and REST API

The web server starts on `http://0.0.0.0:8888` by default.

```bash
ovos-judge --port 8080 --host 127.0.0.1 --data-dir /srv/judge
```

Session results are persisted automatically to `~/.local/share/ovos-judge/sessions/`
(`SessionStore` — `store.py:1`). Results survive server restarts.

### REST endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/session` | Create and start a session |
| `GET` | `/api/session/{id}` | Session state, all exchanges |
| `POST` | `/api/session/{id}/stop` | Stop a running session |
| `GET` | `/api/session/{id}/export?format=json\|html` | Download results |
| `GET` | `/api/sessions` | List all sessions, newest first |
| `DELETE` | `/api/session/{id}` | Delete a session |
| `GET` | `/api/plugins` | List installed chat plugins and bundled personas |
| `WS` | `/ws/{id}` | Real-time session events |

### Real-time WebSocket messages

| Type | Direction | Key fields |
|---|---|---|
| `judge_utterance` | server → client | `utterance`, `test_description`, `round` |
| `persona_response` | server → client | `spoken`, `response_time`, `skill_id`, `intent`, `intent_failed` |
| `judge_eval` | server → client | `pass`, `reasoning`, `severity` |
| `session_done` | server → client | `total`, `passed`, `failed`, `summary` |

---

## BusEventCollector

`BusEventCollector` — `persona_client.py:44` — subscribes to five MessageBus event types when
using the OVOS Local persona:

| Event | Captured field |
|---|---|
| `mycroft.skill.handler.start` | `skill_id`, `intent_type` |
| `intent_failure` / `complete_intent_failure` | `intent_failed: true` |
| `speak` | Full spoken text |

The collector is fault-tolerant: if `ovos-bus-client` is not installed or the bus is
unreachable, the session continues without bus metadata.

---

## Cross-References

- [Personas](150-personas.md) — persona format that ovos-judge uses as test targets
- [Agent Engine Types](154-agent-plugins.md) — OPM chat plugins usable as judge LLMs
- [MessageBus](100-bus_service.md) — bus event reference
- [HiveMind Agents](152-hivemind-agents.md) — testing skills deployed to remote HiveMind nodes

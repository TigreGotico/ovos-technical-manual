# Bus Session Management

Sessions represent a single conversational context. Every `Message` carries a serialized `Session` in `message.context["session"]`, allowing different clients (local mic, remote satellite, HiveMind node) to each maintain independent state.

---

## Session

**Module:** `ovos_bus_client.session.Session`

### Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `session_id` | `str` | `uuid4()` | Unique identifier. `"default"` is reserved for the local microphone. |
| `lang` | `str` | config | BCP-47 language for this session |
| `expiration_seconds` | `int` | config (`-1`) | TTL in seconds; `-1` = never expires |
| `active_skills` | `list` | `[]` | `[[skill_id, timestamp], …]` — ordered converse priority |
| `pipeline` | `list` | config | Ordered list of pipeline stage IDs |
| `context` | `IntentContextManager` | new | Conversational context (Adapt entities) |
| `site_id` | `str` | config | Physical location identifier |
| `location_prefs` | `dict` | config | Location, timezone, etc. |
| `system_unit` | `str` | config | `"metric"` / `"imperial"` |
| `time_format` | `str` | config | `"half"` / `"full"` |
| `date_format` | `str` | config | `"DMY"` / `"MDY"` / `"YMD"` |
| `blacklisted_skills` | `list` | config | Skill IDs blocked for this session |
| `blacklisted_intents` | `list` | config | Intent names blocked for this session |
| `persona_id` | `str` | `None` | Active persona for this session |

### Key Methods

```python
# Lifecycle
sess.touch()              # update timestamp, call SessionManager.update
sess.expired()            # True if TTL elapsed
sess.clear()              # remove all active skills

# Active skills (converse priority list)
sess.activate_skill("my-skill-id")    # move to front of list
sess.deactivate_skill("my-skill-id")  # remove from list
sess.is_active("my-skill-id")         # bool

# Response mode (get_response)
sess.enable_response_mode("my-skill-id")   # mark skill as awaiting user input
sess.disable_response_mode("my-skill-id")  # back to normal intent mode

# Serialization
d = sess.serialize()             # → dict (safe for JSON)
sess2 = Session.deserialize(d)   # → Session

# From a Message
sess = Session.from_message(message)  # extracts session from context, or returns default
```

### Properties

| Property | Type | Description |
|---|---|---|
| `active` | `bool` | True if any skills are in the active list |
| `timezone` | `str` | Timezone code from location preferences |

---

## SessionManager

`SessionManager` is a class-level (static) registry of all known sessions.

**Module:** `ovos_bus_client.session.SessionManager`

### Class Attributes

| Attribute | Description |
|---|---|
| `default_session` | The local mic's session (`session_id="default"`) |
| `sessions` | `{session_id: Session}` dict of all known sessions |
| `bus` | Bus connection (set by `connect_to_bus`) |

### Methods

```python
# Get the session for a message (or default)
sess = SessionManager.get(message)        # preferred API
sess = SessionManager.get()               # → default_session

# Update a session in the registry
SessionManager.update(sess)
SessionManager.update(sess, make_default=True)  # also set as default

# Sync default session to all bus clients
SessionManager.sync(message)             # emits ovos.session.update_default

# Reset the default session (new UUID, fresh state)
SessionManager.reset_default_session()

# Remove expired sessions
SessionManager.prune_sessions()
```

### Session Sync Protocol

When a `MessageBusClient` connects it emits `ovos.session.sync`. `SessionManager` responds with `ovos.session.update_default` carrying the current default session. All clients update their local `default_session`.

```
client → ovos.session.sync
core   → ovos.session.update_default  {session_data: {...}}
```

`ovos-core` calls `SessionManager.connect_to_bus(bus)` during `IntentService` startup, which registers listeners for recording/speaking state events and syncs the default session.

### Utility Methods

```python
SessionManager.is_speaking(session)      # bool — TTS is playing
SessionManager.wait_while_speaking(timeout=15, session=None)  # block until done
```

---

## IntentContextManager

Tracks Adapt context entities across turns in a conversation. Scoped per-`Session` and serialized with it.

**Module:** `ovos_bus_client.session.IntentContextManager`

### Configuration

```json
{
  "context": {
    "timeout": 2,
    "max_frames": 3,
    "greedy": false,
    "keywords": []
  }
}
```

| Key | Default | Description |
|---|---|---|
| `timeout` | `2` | Minutes before a context frame expires |
| `max_frames` | `3` | Max frames of context to keep |
| `greedy` | `false` | If true, inject all entities (not just tracked keywords) |
| `keywords` | `[]` | Adapt keyword names to automatically track as context |

### Key Methods

```python
ctx = IntentContextManager()

# Add entity to context
ctx.inject_context({"data": [("London", "City")], "key": "London",
                    "confidence": 1.0, "origin": "my-skill"})

# Get entities for use in Adapt matching
entities = ctx.get_context(max_frames=2, missing_entities=["City"])

# Modify context
ctx.remove_context("City")
ctx.clear_context()

# Serialization
d    = ctx.serialize()
ctx2 = IntentContextManager.deserialize(d)
```

### Context Frame Stack

Context is stored as a stack of `IntentContextManagerFrame` objects, each with a timestamp. Entities from older frames are assigned lower confidence scores during matching.

---

## UtteranceState

Enum tracking whether a skill is in intent-matching or `get_response` mode:

```python
from ovos_bus_client.session import UtteranceState

UtteranceState.INTENT    # "intent"   — normal intent processing
UtteranceState.RESPONSE  # "response" — waiting for get_response input
```

Stored per skill in `Session.utterance_states: Dict[skill_id, UtteranceState]`.

---

## Session in the Pipeline

Session state flows through every bus message via `context["session"]`. Each pipeline stage may read and modify the session. `IntentService` calls `sess.activate_skill(skill_id)` after a successful match. The updated session is serialized into the reply message and all subsequent messages in that turn.

### Per-session Pipeline Override

Each session has its own `pipeline` list. HiveMind clients and individual users can have different intent pipelines:

```python
from ovos_bus_client.session import Session

sess = Session(session_id="remote-user")
sess.pipeline = ["converse", "padatious_high", "fallback_medium"]
```

### Per-session Skill/Intent Blacklists

```python
sess.blacklisted_skills = ["ovos-skill-timer.openvoiceos"]
sess.blacklisted_intents = ["HelloWorldSkill:hello_intent"]
```

Blacklisted skills and intents are skipped during pipeline matching for that session only.

---

## Connection Configuration

```json
{
  "websocket": {
    "host": "127.0.0.1",
    "port": 8181,
    "route": "/core",
    "ssl": false,
    "secret_key": null,
    "allow_unencrypted": true
  },
  "session": {
    "ttl": -1
  }
}
```

| Key | Default | Description |
|---|---|---|
| `session.ttl` | `-1` | Session TTL in seconds. `-1` = never expires. |

---

## Related Pages

- [Bus Client](900-bus_client.md) — `MessageBusClient`, `Message`, and client API
- [Bus Service](100-bus_service.md) — `ovos-messagebus` WebSocket server
- [ovos-core](102-core.md) — `IntentService` session handling
- [Converse Pipeline](converse_pipeline.md) — how active skills in sessions participate in converse

# Pydantic Message Models

`ovos-pydantic-models` provides typed [Pydantic v2](https://docs.pydantic.dev/latest/) models for every message that flows over the OVOS MessageBus. This package is the machine-readable specification of the OVOS bus protocol — covering 545+ message types organized by subsystem.

> **Beta** — Message models are semi-automatically generated and under active review. Some subsystems are deprecated but documented here for historical reference. Do not treat this as a stable API contract.

---

## Why use this library?

The raw OVOS MessageBus API uses `ovos_bus_client.message.Message` — essentially a dict wrapper with no type checking:

```python
# Untyped — any typo silently produces a wrong message
msg = Message("speak", {"utterence": "hello"})  # typo in key, no error
```

With pydantic models:

```python
from ovos_pydantic_models.audio.playback import SpeakMessage, SpeakData

# Validated at construction — typo raises ValidationError immediately
msg = SpeakMessage(data=SpeakData(utterance="hello"))
```

Benefits:

- **Catch errors early** — wrong field names and wrong types raise `ValidationError` at construction
- **IDE autocomplete** — field names and types are known
- **Self-documenting** — the model is the schema
- **Serialization roundtrip** — `model_dump()` / `model_validate()` for free
- **Test fixtures** — build expected messages with validation instead of plain dicts

---

## Installation

```bash
pip install ovos-pydantic-models
```

No OVOS runtime is required. This is a pure Pydantic v2 library.

---

## How Messages Work

Every OVOS bus message follows this structure:

```json
{
  "type": "speak",
  "data": {"utterance": "Hello world", "expect_response": false},
  "context": {"source": "skill-weather.mycroft", "session": {...}}
}
```

`type` is modelled as `message_type` on all subclasses of `OpenVoiceOSMessage`. The `data` field is typed per message class. The `context` field is always a `MessageContext` (which embeds an optional `Session`).

---

## Core Models

### OpenVoiceOSMessage

**Module:** `ovos_pydantic_models.message.OpenVoiceOSMessage`

Base class for all bus messages.

| Field | Type | Required | Description |
|---|---|---|---|
| `message_type` | `str` | yes | The bus message type string (e.g. `"speak"`) |
| `data` | `dict` | no | Message payload. Subclasses replace this with a typed model. |
| `context` | `MessageContext` | no | Routing/session context. Defaults to empty context. |

```python
from ovos_pydantic_models.message import OpenVoiceOSMessage

msg = OpenVoiceOSMessage(message_type="my.custom.event")
raw = msg.model_dump()
restored = OpenVoiceOSMessage.model_validate(raw)
```

### MessageContext

**Module:** `ovos_pydantic_models.message.MessageContext`

Routing context attached to every message. Allows extra fields (open model).

| Field | Type | Default | Description |
|---|---|---|---|
| `source` | `str \| None` | `None` | Origin of the message |
| `destination` | `str \| list[str] \| None` | `None` | Target(s). `None` = broadcast to all. |
| `session` | `Session \| None` | `None` | Embedded session context |

Extra fields are allowed — the bus adds arbitrary keys like `skill_id`, `ident`, etc., which are preserved on deserialization.

### Session

**Module:** `ovos_pydantic_models.session.Session`

| Field | Type | Default | Description |
|---|---|---|---|
| `session_id` | `str` | `"default"` | Unique session identifier |
| `expiration_seconds` | `int` | `-1` | TTL in seconds (-1 = no expiry) |
| `active_skills` | `list[tuple[str, float]]` | `[]` | Skills currently active with last-activation timestamp |
| `utterance_states` | `dict[str, UtteranceState]` | `{}` | Per-skill utterance state |
| `lang` | `str` | `"en-us"` | Session language |
| `context` | `IntentContextManager` | — | Conversational context frame stack |
| `site_id` | `str` | `"unknown"` | Physical location / device identifier |
| `pipeline` | `list[str]` | default pipeline | Ordered intent pipeline stages |
| `system_unit` | `str` | `"metric"` | `"metric"` or `"imperial"` |
| `is_speaking` | `bool` | `False` | Device is currently speaking |
| `is_recording` | `bool` | `False` | Device is currently recording |
| `blacklisted_intents` | `list[str]` | `[]` | Intents blocked for this session |
| `blacklisted_skills` | `list[str]` | `[]` | Skills blocked for this session |

```python
from ovos_pydantic_models.session import Session, UtteranceState
from ovos_pydantic_models.message import MessageContext

session = Session(
    session_id="user-abc",
    lang="de-de",
    utterance_states={"skill-weather.mycroft": UtteranceState.RESPONSE},
)
ctx = MessageContext(source="skills", session=session)
```

---

## Quick Start

```python
from ovos_pydantic_models.audio.playback import SpeakMessage, SpeakData

msg = SpeakMessage(data=SpeakData(utterance="Hello world"))
print(msg.message_type)   # "speak"
print(msg.model_dump())   # {"message_type": "speak", "data": {...}, "context": {...}}
```

Validation at construction:

```python
from pydantic import ValidationError
from ovos_pydantic_models.intents.core import CompleteIntentFailureData, CompleteIntentFailureMessage

try:
    msg = CompleteIntentFailureMessage(data=CompleteIntentFailureData())  # missing utterance
except ValidationError as e:
    print(e)  # "utterance: Field required"
```

Dynamic message types (skill-id prefix):

```python
from ovos_pydantic_models.intents.converse import SkillConversePingMessage, SkillConversePingData

msg = SkillConversePingMessage(
    message_type="my-skill.converse.ping",
    data=SkillConversePingData(skill_id="my-skill", utterances=["hello"], lang="en-us"),
)
```

---

## Bridge to ovos-bus-client

`ovos_bus_client.message.Message` and `OpenVoiceOSMessage` share the same three-field structure. Convert between them:

```python
from ovos_bus_client.message import Message
from ovos_pydantic_models.message import OpenVoiceOSMessage


def to_bus_message(pydantic_msg: OpenVoiceOSMessage) -> Message:
    d = pydantic_msg.model_dump()
    return Message(d["message_type"], d["data"], d["context"])


def from_bus_message(bus_msg: Message, model: type[OpenVoiceOSMessage]) -> OpenVoiceOSMessage:
    return model.model_validate({
        "message_type": bus_msg.msg_type,
        "data": bus_msg.data,
        "context": bus_msg.context,
    })
```

---

## Subsystem Coverage

### Audio / TTS

```python
from ovos_pydantic_models.audio.playback import SpeakMessage, SpeakData

# TTS request
msg = SpeakMessage(data=SpeakData(utterance="Hello, world!", lang="en-us"))
```

| Message type | Class | Description |
|---|---|---|
| `speak` | `SpeakMessage` | Primary TTS request |
| `speak:b64_audio` | `SpeakB64AudioMessage` | Request base64-encoded audio without playing |
| `mycroft.audio.queue` | `MycroftAudioQueueMessage` | Queue a pre-synthesized audio chunk |
| `mycroft.audio.play_sound` | `MycroftAudioPlaySoundMessage` | Play a sound immediately |
| `mycroft.audio.speech.stop` | `MycroftSpeechStopMessage` | Stop current TTS speech |

### Intent Pipeline

```python
from ovos_pydantic_models.intents.core import (
    CompleteIntentFailureMessage,
    IntentServiceIntentGetMessage, IntentServiceIntentGetData,
)

# Query without triggering
request = IntentServiceIntentGetMessage(
    data=IntentServiceIntentGetData(utterance="what time is it", lang="en-us")
)
```

| Message type | Class | Description |
|---|---|---|
| `ovos.utterance.handled` | `OvosUtteranceHandledMessage` | Utterance successfully handled |
| `complete_intent_failure` | `CompleteIntentFailureMessage` | No intent matched |
| `intent.service.intent.get` | `IntentServiceIntentGetMessage` | Query pipeline without executing |
| `intent.service.pipelines.reload` | `IntentServicePipelinesReloadMessage` | Reload pipeline plugins |

### Converse Protocol

```python
from ovos_pydantic_models.intents.converse import (
    ConverseMode, ConverseActivationMode,
    SkillConverseRequestMessage, SkillConverseResponseMessage,
)
```

**`ConverseMode`**: `ACCEPT_ALL`, `BLACKLIST`, `WHITELIST`

**`ConverseActivationMode`**: `ACCEPT_ALL`, `PRIORITY`, `BLACKLIST`, `WHITELIST`

| Message type | Class | Key fields |
|---|---|---|
| `intent.service.skills.activate` | `IntentServiceSkillsActivateMessage` | `skill_id`, `timeout` |
| `{skill_id}.converse.ping` | `SkillConversePingMessage` | `skill_id`, `utterances`, `lang` |
| `{skill_id}.converse.request` | `SkillConverseRequestMessage` | `skill_id`, `utterances`, `lang` |
| `skill.converse.response` | `SkillConverseResponseMessage` | `skill_id`, `result: bool` |
| `skill.converse.get_response.enable` | `SkillConverseGetResponseEnableMessage` | — |
| `skill.converse.get_response.disable` | `SkillConverseGetResponseDisableMessage` | — |

### Fallback Protocol

```python
from ovos_pydantic_models.intents.fallbacks import (
    FallbackMode,
    OvosSkillsFallbackRegisterMessage, OvosSkillsFallbackRegisterData,
)
```

**`FallbackMode`**: `ACCEPT_ALL`, `BLACKLIST`, `WHITELIST`

| Message type | Class | Key fields |
|---|---|---|
| `ovos.skills.fallback.register` | `OvosSkillsFallbackRegisterMessage` | `skill_id`, `priority` |
| `ovos.skills.fallback.deregister` | `OvosSkillsFallbackDeregisterMessage` | `skill_id` |
| `ovos.skills.fallback.ping` | `OvosSkillsFallbackPingMessage` | `utterances`, `lang`, `range` |

### Stop Protocol

| Message type | Class | Key fields |
|---|---|---|
| `mycroft.stop` | `MycroftStopMessage` | — |
| `mycroft.stop.handled` | `MycroftStopHandledMessage` | `by: str` |
| `mycroft.audio.speech.stop` | `MycroftAudioSpeechStopMessage` | `skill_id \| None` |
| `mycroft.skills.abort_execution` | `MycroftSkillsAbortExecutionMessage` | `skill_id` (used by `@killable_intent`) |

### Skill Manager

```python
from ovos_pydantic_models.core.skill_manager import (
    MycroftSkillsInitializedMessage,
    MycroftSkillsErrorMessage, MycroftSkillsErrorData,
)
```

| Message type | Class | Description |
|---|---|---|
| `mycroft.ready` | `MycroftReadyMessage` | All core services ready |
| `mycroft.skills.initialized` | `MycroftSkillsInitializedMessage` | Skills service initialized |
| `mycroft.skills.trained` | `MycroftSkillsTrainedMessage` | Training complete |
| `skillmanager.list` | `SkillManagerListMessage` | Request skill list |
| `mycroft.skills.list` | `MycroftSkillsListMessage` | Reply with loaded skills |

### Skill Installer

```python
from ovos_pydantic_models.core.skill_installer import (
    InstallError,
    OvosSkillsInstallMessage, OvosPipInstallMessage, OvosPipInstallData,
)

msg = OvosPipInstallMessage(
    data=OvosPipInstallData(packages=["requests", "beautifulsoup4"])
)
```

**`InstallError`**: `DISABLED`, `PIP_ERROR`, `BAD_URL`, `NO_PKGS`

| Message type | Class | Key field |
|---|---|---|
| `ovos.skills.install` | `OvosSkillsInstallMessage` | `url: str` |
| `ovos.pip.install` | `OvosPipInstallMessage` | `packages: list[str]` |
| `ovos.pip.uninstall` | `OvosPipUninstallMessage` | `packages: list[str]` |

### Skill Settings

```python
from ovos_pydantic_models.core.skill_settings import SkillSettingsChangeMessage, SkillSettingsChangeData

msg = SkillSettingsChangeMessage(
    data=SkillSettingsChangeData(
        skill_id="skill-weather.mycroft",
        settings={"units": "metric", "location": "London"},
    )
)
```

### Session Synchronization

```python
from ovos_pydantic_models.core.session import OvosSessionSyncMessage, OvosSessionUpdateDefaultMessage

# Client emits this on connect
sync = OvosSessionSyncMessage()
```

| Message type | Class | Description |
|---|---|---|
| `ovos.session.sync` | `OvosSessionSyncMessage` | Request the current default session |
| `ovos.session.update_default` | `OvosSessionUpdateDefaultMessage` | Broadcast updated default session |

---

## Use in Skills

### Emitting typed messages

```python
from ovos_workshop.skills import OVOSSkill
from ovos_pydantic_models.audio.playback import SpeakMessage, SpeakData

class MySkill(OVOSSkill):
    def handle_hello(self, message):
        typed = SpeakMessage(data=SpeakData(utterance="Hello!"))
        self.bus.emit(to_bus_message(typed))
```

### Parsing received messages

```python
from ovos_pydantic_models.intents.core import RecognizerLoopUtteranceMessage

def handle_utterance(self, message):
    typed = from_bus_message(message, RecognizerLoopUtteranceMessage)
    utterances = typed.data.utterances  # list[str], validated
    lang = typed.data.lang              # str, validated
```

---

## Use in Tests (ovoscope / pytest)

```python
from ovos_bus_client.session import Session
from ovos_pydantic_models.audio.playback import SpeakMessage, SpeakData

# Build typed source message
utterance = to_bus_message(
    RecognizerLoopUtteranceMessage(
        data=RecognizerLoopUtteranceData(utterances=["what time is it"], lang="en-us")
    )
)
session = Session("test-123")
utterance.context["session"] = session.serialize()

# Assert on received messages
speak_msgs = [m for m in messages if m.msg_type == "speak"]
typed_speak = from_bus_message(speak_msgs[0], SpeakMessage)
assert "3pm" in typed_speak.data.utterance
assert typed_speak.data.expect_response is False
```

---

## When NOT to use Pydantic Models

- **Ephemeral fire-and-forget messages with no data** — just use `self.bus.emit(Message("my.event"))`.
- **Skills using the OVOSSkill API directly** — `self.speak()`, `self.ask_yesno()`, etc. already produce the right messages. Use models only when you need lower-level control or test assertions.
- **Skill settings** — managed by `ovos-workshop` settings system.

---

## Subsystem Status

| Badge | Meaning |
|---|---|
| ⚠ deprecated | Backing plugin/package archived — documented for reference only |
| β beta | Actively developed, not yet officially released |
| ↩ legacy | Functional but superseded by a better alternative |

**Deprecated:**
- `phal.configuration_provider`, `phal.wifi_setup` — backing packages archived
- `gui.homescreen`, `gui.widgets`, `gui.media_player`, `gui.notifications` — superseded by GUI rewrite

**Beta:**
- `gui.namespace` — GUI protocol unstable during ongoing rewrite
- `audio.video_service`, `audio.web_service` — ovos-media not yet officially launched

**Legacy:**
- `audio.audioservice` — being superseded by OCP for media playback
- `intents.adapt` — superseded by Padacioso / ML-based pipeline plugins
- `intents.padatious` — superseded by Padacioso

---

## Interactive Reference

`docs/index.html` is a searchable, filterable web UI with all 545+ message types:

```bash
python -m http.server 8080 --directory docs
# open http://localhost:8080
```

---

## Related Pages

- [Bus Client](900-bus_client.md) — `Message`, `MessageBusClient`
- [Bus Session](901-bus-session.md) — `Session`, `SessionManager`
- [ovos-core](102-core.md) — intent pipeline, skill manager
- [Skill Classes](412-skill-classes.md) — skill base classes that emit/handle these messages

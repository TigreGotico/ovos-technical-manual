# ovoscope Advanced Testing

This page covers advanced ovoscope testing scenarios beyond the core skill pipeline:
audio service testing, OCP media testing, PHAL plugin testing, listener pipeline testing,
pipeline plugin isolation, pydantic model integration, and the CLI.

See [450-skill-testing.md](450-skill-testing.md) for architecture and
[451-ovoscope-usage.md](451-ovoscope-usage.md) for standard usage patterns.

---

## Audio Service Testing

`ovoscope.audio` provides harnesses for testing `ovos-audio` services against a
`FakeBus` with a `MockAudioBackend` and `MockTTS`.

Install the audio extra:

```bash
pip install ovoscope[audio]
```

### AudioServiceHarness

Use `AudioServiceHarness` when testing the audio routing layer: backend selection by
URI scheme, volume ducking on speech events, the 1-second stop guard, or
session-source validation.

```python
from ovoscope.audio import AudioServiceHarness
from ovos_bus_client.message import Message

with AudioServiceHarness() as h:
    h.play(["http://example.com/track.mp3"])
    h.assert_playing()

    # Duck volume when OVOS starts speaking
    h.bus.emit(Message("recognizer_loop:audio_output_start"))
    h.assert_volume_lowered()
```

**Stop guard**: `AudioService._stop()` silently ignores stop commands issued within
1 second of `play()`. Tests that call `stop()` must wait at least 1.1 seconds:

```python
import time

with AudioServiceHarness() as h:
    h.play(["http://example.com/song.mp3"])
    time.sleep(1.1)   # bypass stop guard
    h.stop()
    h.assert_stopped()
```

**`AudioServiceHarness` assertion methods:**

| Method | Description |
|--------|-------------|
| `assert_playing()` | Raise if backend is not playing |
| `assert_paused()` | Raise if backend is not paused |
| `assert_stopped()` | Raise if backend is playing or paused |
| `assert_volume_lowered()` | Raise if `lower_volume()` was never called |
| `assert_volume_restored()` | Raise if `restore_volume()` was never called |

### PlaybackServiceHarness

Use `PlaybackServiceHarness` when testing TTS execution flow: `speak` messages, the
`recognizer_loop:audio_output_start/end` lifecycle, and mic-listen triggers after speech.

```python
from ovoscope.audio import PlaybackServiceHarness

with PlaybackServiceHarness() as h:
    h.speak("hello world")
    h.assert_spoke("hello world")
    h.assert_audio_output_ended()
```

`PlaybackServiceHarness` patches `ovos_audio.playback.play_audio` to return a mock
`Popen`-like object — keeping tests fast and independent of the host audio stack.

### AudioCaptureSession

`AudioCaptureSession` captures `mycroft.audio.*` and `recognizer_loop:audio_output*`
messages during a test and provides sequence assertion:

```python
from ovoscope.audio import AudioCaptureSession, AudioServiceHarness

with AudioServiceHarness() as h:
    with AudioCaptureSession(h.bus) as cap:
        h.play(["http://example.com/track.mp3"])
    cap.assert_sequence("mycroft.audio.service.play")
```

---

## OCP / Common Play Testing

`ovoscope.ocp` provides `OCPTest` for testing OCP (OpenVoiceOS Common Play) skills
that respond to media queries.

The OCP message flow:

```
recognizer_loop:utterance
  → ovos.common_play.query           (broadcast to all OCP skills)
  → ovos.common_play.query.response  (skill replies with MediaEntry list)
  → ovos.common_play.start           (selected track)
```

### Declarative Style with OCPTest

```python
from ovoscope.ocp import OCPTest

result = OCPTest(
    skill_ids=["ovos-skill-youtube.openvoiceos"],
    utterance="play lofi hip hop",
    mock_responses={
        "youtube.com": {"items": [{"title": "Lofi Radio", "url": "..."}]},
    },
    expected_media=[{"title": "Lofi Radio"}],
    lang="en-US",
    timeout=20.0,
).execute()
```

HTTP calls are intercepted via `unittest.mock.patch` on `requests.Session.get` and
`requests.get`. For skills using non-standard HTTP clients, pass additional patch
targets:

```python
OCPTest(
    skill_ids=["..."],
    utterance="play jazz",
    mock_responses={"api.example.com": {"results": [...]}},
    patch_targets=["my_skill.http.aiohttp.ClientSession.get"],
).execute()
```

**`OCPTest` fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `skill_ids` | `List[str]` | required | OCP skill IDs to load |
| `utterance` | `str` | required | User utterance |
| `mock_responses` | `Dict[str, Any]` | `{}` | URL-substring to JSON response |
| `expected_media` | `List[Dict]` | `[]` | Partial dicts matched against `media_list` |
| `expected_stream_url` | `Optional[str]` | `None` | Substring expected in stream URI |
| `lang` | `str` | `"en-US"` | Language tag |
| `timeout` | `float` | `20.0` | Max wait in seconds |
| `patch_targets` | `List[str]` | `[]` | Additional HTTP modules to patch |

### Lower-Level Assertion

```python
from ovoscope.ocp import assert_ocp_query_response

assert_ocp_query_response(
    messages,
    min_results=1,
    media_type="audio",
    expected_media=[{"title": "My Song"}],
    stream_url_contains="cdn.example.com",
)
```

---

## PHAL Plugin Testing

`ovoscope.phal` provides `MiniPHAL` and `PHALTest` for testing PHAL (Plugin Hardware
Abstraction Layer) plugins without physical hardware.

PHAL plugins communicate exclusively via the MessageBus, accepting a `bus` argument in
their constructors. `MiniPHAL` injects a `FakeBus` so plugin behaviour is identical to
a real deployment.

**Testable plugins (no hardware required):**

| Plugin | Trigger | Expected Response |
|--------|---------|-------------------|
| `ovos-PHAL-plugin-connectivity-events` | `network.connected` | `mycroft.internet.connected` |
| `ovos-PHAL-plugin-oauth` | auth-flow messages | auth-result messages |
| `ovos-PHAL-plugin-ipgeo` | `mycroft.internet.connected` | `mycroft.location.update` |
| `ovos-PHAL-plugin-system` | `system.reboot` | `system.reboot.confirmed` |

**Hardware-dependent plugins** (ALSA, Mark 1, dotstar LEDs) require hardware-in-the-loop
integration tests and are out of scope for ovoscope.

### Context Manager Style

```python
from ovos_utils.messagebus import Message
from ovoscope.phal import MiniPHAL

with MiniPHAL(
    plugin_ids=["ovos-PHAL-plugin-connectivity-events.openvoiceos"],
) as phal:
    phal.emit(Message("network.connected"))
    msg = phal.assert_emitted("mycroft.internet.connected", timeout=2.0)
    assert msg.data.get("connected") is True
```

### Declarative Style

```python
from ovos_utils.messagebus import Message
from ovoscope.phal import PHALTest

PHALTest(
    plugin_ids=["ovos-PHAL-plugin-system.openvoiceos"],
    trigger_message=Message("system.reboot"),
    expected_types=["system.reboot.confirmed"],
    forbidden_types=["system.shutdown.confirmed"],
    timeout=5.0,
).execute()
```

**`MiniPHAL` methods:**

| Method | Description |
|--------|-------------|
| `emit(msg, wait=0.05)` | Emit a message and briefly wait for handlers |
| `assert_emitted(msg_type, timeout=2.0)` | Assert type was emitted; return the `Message` |
| `assert_not_emitted(msg_type, wait=0.2)` | Assert type was NOT emitted |
| `clear_captured()` | Clear the captured message list |

---

## Listener Pipeline Testing

`ovoscope.listener` provides `MiniListener` and `ListenerTest` for testing audio
transformer plugins — the plugins that process raw audio before it reaches the intent
engine.

`MiniListener` wraps `AudioTransformersService` on a `FakeBus`. Rather than injecting
a `recognizer_loop:utterance`, it feeds **raw audio bytes** through the transformer
pipeline and captures all resulting bus messages.

### Audio Transformer Testing

```python
import types, sys
from unittest.mock import MagicMock

# Stub native extension before importing the plugin
_stub = types.ModuleType("ggwave")
_stub.init = MagicMock(return_value=MagicMock())
_stub.free = MagicMock()
_stub.decode = MagicMock(return_value=b"UTT:turn on the lights")
sys.modules.setdefault("ggwave", _stub)

from ovos_audio_transformer_plugin_ggwave import GGWavePlugin
from ovoscope.listener import get_mini_listener

plugin = GGWavePlugin(config={"start_enabled": True})
listener = get_mini_listener(
    plugin_instances={"ovos-audio-transformer-plugin-ggwave": plugin}
)
msgs = listener.feed_audio(b"\x00" * 1024)
assert any(m.msg_type == "recognizer_loop:utterance" for m in msgs)
listener.shutdown()
```

### Full Pipeline Testing (Audio → STT → Utterance)

```python
from unittest.mock import MagicMock
from ovoscope.listener import get_mini_listener

stt = MagicMock()
stt.execute.return_value = "ask not what your country can do for you"

listener = get_mini_listener()
msgs = listener.listen("path/to/jfk.wav", language="en-us", stt_instance=stt)
utt = next(m for m in msgs if m.msg_type == "recognizer_loop:utterance")
assert utt.data["lang"] == "en-us"
assert "ask not" in utt.data["utterances"][0]
listener.shutdown()
```

### `ListenerTest` — Declarative Style

```python
from ovoscope.listener import ListenerTest

ListenerTest(
    plugin_instances={"my-transformer": plugin},
    audio_input=b"\x00" * 1024,
    feed_method="feed_audio",
    expected_types=["recognizer_loop:utterance"],
    forbidden_types=["mycroft.mic.listen"],
).execute()
```

**What `MiniListener` does NOT cover**: VAD, wake-word detection, real STT model loading,
the full `DinkumVoiceLoop` state machine, or real hardware audio. For VAD and wake-word,
use `FakeBus` unit tests directly.

---

## Pipeline Plugin Testing

`ovoscope.pipeline` provides `PipelineHarness` for testing intent pipeline plugins
(Adapt, Padatious, Padacioso, OCP, etc.) in complete isolation — no skill is needed.

```python
from ovoscope.pipeline import PipelineHarness

with PipelineHarness(
    pipeline=["ovos-adapt-pipeline-plugin.openvoiceos"],
    lang="en-US",
) as harness:
    msg = harness.assert_matches("turn on the kitchen lights")
    harness.assert_no_match("garbled nonsense xyz 123")
```

`PipelineHarness` creates a `MiniCroft` with `skill_ids=[]` and the specified pipeline
stages. Intent-matched messages are captured via a `threading.Event` subscription on
`intent.service.skills.activated`.

**`PipelineHarness` methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `match(utterance, timeout=5.0)` | `Optional[Message]` | Return matched message or `None` |
| `assert_matches(utterance, intent_type=None, timeout=5.0)` | `Message` | Assert match; optionally check intent type substring |
| `assert_no_match(utterance, timeout=2.0)` | `None` | Assert utterance is NOT matched |

---

## Pydantic Model Integration

`ovoscope.pydantic_helpers` bridges `ovos_bus_client.message.Message` with
`ovos-pydantic-models` typed message models. Install the optional extra:

```bash
pip install ovoscope[pydantic]
```

### Typed Source Messages

```python
from ovoscope import End2EndTest
from ovos_bus_client.session import Session
from ovos_pydantic_models import RecognizerLoopUtteranceMessage, RecognizerLoopUtteranceData
from ovoscope.pydantic_helpers import to_bus_message

utterance_model = RecognizerLoopUtteranceMessage(
    data=RecognizerLoopUtteranceData(utterances=["what is the weather?"], lang="en-us"),
)
session = Session("test-123")
bus_msg = to_bus_message(utterance_model)
bus_msg.context["session"] = session.serialize()
bus_msg.context["source"] = "A"
bus_msg.context["destination"] = "B"

End2EndTest(
    skill_ids=["skill-weather.openvoiceos"],
    source_message=bus_msg,
    expected_messages=[...],
).execute()
```

Pydantic validation runs at construction time — a misspelled field name like
`"utterance"` instead of `"utterances"` raises `ValidationError` immediately rather
than producing a silent wrong test.

### Typed Assertions on Received Messages

```python
from ovoscope import get_minicroft, CaptureSession
from ovos_pydantic_models import SpeakMessage
from ovoscope.pydantic_helpers import from_bus_message

croft = get_minicroft(["skill-weather.openvoiceos"])
capture = CaptureSession(croft)
capture.capture(bus_msg, timeout=10)
messages = capture.finish()
croft.stop()

speak_msgs = [m for m in messages if m.msg_type == "speak"]
typed_speak = from_bus_message(speak_msgs[0], SpeakMessage)
assert "london" in typed_speak.data.utterance.lower()
assert typed_speak.data.expect_response is False
```

### Type-Safe Test Helpers

```python
from ovoscope.pydantic_helpers import from_bus_message, to_bus_message
from ovos_bus_client.message import Message
from ovos_pydantic_models import SpeakMessage, RecognizerLoopUtteranceMessage, RecognizerLoopUtteranceData
from ovos_bus_client.session import Session

def assert_speak(received_msg: Message, expected_utterance: str | None = None) -> SpeakMessage:
    """Assert a received message is a valid speak message."""
    typed = from_bus_message(received_msg, SpeakMessage)
    if expected_utterance is not None:
        assert typed.data.utterance == expected_utterance
    return typed

def make_utterance(text: str, lang: str = "en-us", session: Session | None = None) -> Message:
    """Build a typed recognizer_loop:utterance message."""
    model = RecognizerLoopUtteranceMessage(
        data=RecognizerLoopUtteranceData(utterances=[text], lang=lang)
    )
    msg = to_bus_message(model)
    if session:
        msg.context["session"] = session.serialize()
    return msg
```

### Fixture Schema Validation

```bash
ovoscope validate test/fixtures/*.json
```

`validate_fixture` from `ovoscope.pydantic_helpers` provides clear errors on malformed
fixture JSON rather than cryptic assertion failures.

---

## Multilingual Testing

`MiniCroft` supports multilingual intent registration via `secondary_langs`:

```python
from ovoscope import get_minicroft

croft = get_minicroft(
    ["my-skill.openvoiceos"],
    lang="pt-PT",
    secondary_langs=["en-US", "de-DE"],
)
```

This patches `Configuration()["secondary_langs"]` before `IntentService` initializes,
so Adapt creates per-language engines and registers vocab from all locale directories.
All overrides are restored in `MiniCroft.stop()`.

---

## Pipeline Config Overrides

Use `pipeline_config` to override per-plugin configuration reproducibly, regardless
of the developer's local `mycroft.conf`:

```python
from ovoscope import get_minicroft

croft = get_minicroft(
    ["my-skill.openvoiceos"],
    pipeline_config={
        "ovos_m2v_pipeline": {
            "model": "Jarbas/ovos-model2vec-intents-distiluse-base-multilingual-cased-v2",
        }
    },
)
```

The key must match the plugin's config key under `Configuration()["intents"]`.
All overrides are restored in `MiniCroft.stop()`.

---

## See Also

- [450-skill-testing.md](450-skill-testing.md) — architecture overview
- [451-ovoscope-usage.md](451-ovoscope-usage.md) — standard usage patterns
- [452-ovoscope-ci.md](452-ovoscope-ci.md) — CI/CD integration
- [ovoscope: audio-testing.md](../ovoscope/docs/audio-testing.md) — full `AudioServiceHarness` API
- [ovoscope: listener.md](../ovoscope/docs/listener.md) — full `MiniListener` API
- [ovoscope: ocp.md](../ovoscope/docs/ocp.md) — full `OCPTest` API
- [ovoscope: phal.md](../ovoscope/docs/phal.md) — full `MiniPHAL` / `PHALTest` API
- [ovoscope: pipeline.md](../ovoscope/docs/pipeline.md) — full `PipelineHarness` API
- [ovoscope: pydantic-integration.md](../ovoscope/docs/pydantic-integration.md) — pydantic bridge functions

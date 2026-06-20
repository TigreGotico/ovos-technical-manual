# Audio Testing with ovoscope

This page tests the **`ovos-audio` services** — the `AudioService` (media
playback / ducking) and the `PlaybackService` (TTS speak lifecycle) — using the
mock backends and context-manager harnesses in `ovoscope.audio`. It is the
counterpart to [Skill Testing](skill-testing.md), which stops at the
`recognizer_loop:utterance` level and never touches TTS or audio output.

## Your first audio test

If you just want to assert that something gets *spoken*, you do not need the
audio service at all — the skill-level `End2EndTest.assert_spoke()` is simpler.
Reach for the harnesses on this page when you need to verify the **audio
service plumbing itself**: backend selection, volume ducking, the speak
lifecycle events, or mic re-listen after a prompt.

```python
from ovoscope.audio import PlaybackServiceHarness

with PlaybackServiceHarness() as h:
    h.speak("hello world")
    h.assert_spoke("hello world")
```

> **Prerequisite — the `audio` extra.** The harnesses import `ovos_audio` lazily
> on `__enter__`, so `from ovoscope.audio import ...` succeeds without it, but
> using a harness raises `ImportError` unless `ovos-audio` is installed. Install
> the extra:
>
> ```bash
> uv pip install "ovoscope[audio]"
> ```
>
> The `audio` extra pulls `ovos-audio>=1.2.0`. (A separate `tts` extra adds
> `jiwer` + a reference STT plugin for TTS *intelligibility* scoring — that is a
> different harness, not needed here.) These classes are also re-exported at the
> top level (`from ovoscope import PlaybackServiceHarness`), but only when
> `ovos_audio` is importable; they are silently absent otherwise, so importing
> straight from `ovoscope.audio` is the reliable form.

## When to Use Which Harness

| Scenario | Harness |
|---|---|
| Testing AudioService backend selection, ducking, stop-guard, session validation | `AudioServiceHarness` |
| Testing PlaybackService TTS synthesis, queuing, speak lifecycle events | `PlaybackServiceHarness` |
| Capturing and asserting bus message sequences during audio interactions | `AudioCaptureSession` |

### AudioServiceHarness

`AudioServiceHarness` — `ovoscope/audio.py`

Wraps `AudioService` (from `ovos_audio.audio`) with a `MockAudioBackend` on a
`FakeBus`. Use it when your test exercises the audio routing layer — backend
selection by URI scheme, volume ducking on speech events, the 1-second stop
guard, or session-source validation.

```python
from ovoscope.audio import AudioServiceHarness
from ovos_bus_client.message import Message

with AudioServiceHarness() as h:
    h.play(["http://example.com/track.mp3"])
    h.assert_playing()
    # Duck the volume as OVOS starts speaking
    h.bus.emit(Message("recognizer_loop:audio_output_start"))
    h.assert_volume_lowered()

```

### PlaybackServiceHarness

`PlaybackServiceHarness` — `ovoscope/audio.py`

Wraps `PlaybackService` (from `ovos_audio.service`) with a `MockTTS` on a
`FakeBus`. Use it when testing TTS execution flow: `speak` messages, the
`recognizer_loop:audio_output_start/end` lifecycle, and optional mic-listen
triggers after speech.

```python
from ovoscope.audio import PlaybackServiceHarness

with PlaybackServiceHarness() as h:
    h.speak("hello world")
    h.assert_spoke("hello world")
    h.assert_audio_output_ended()

```

## Stop Guard Pitfall

`AudioService._stop()` — `ovos-audio/ovos_audio/audio.py` — ignores a stop that
arrives within ~1 second of `play()` (it compares `time.monotonic()` against
`self.play_start_time`). If your test calls `stop()` immediately after `play()`,
the stop is silently dropped and `assert_stopped()` fails.

Sleeping 1.1 s works but is slow. The canonical, instant bypass is to backdate
the service's `play_start_time` so the guard sees an old playback:

```python
import time
from ovoscope.audio import AudioServiceHarness

with AudioServiceHarness() as h:
    h.play(["http://example.com/song.mp3"])
    h.service.play_start_time = time.monotonic() - 2.0   # bypass the stop guard
    h.stop()
    h.assert_stopped()

```

## play_audio Patch Rationale

`PlaybackThread._play()` — `ovos-audio/ovos_audio/playback.py` — calls
`play_audio(data)` then waits on the returned process object. Without patching,
this would invoke a real audio player binary (sox, aplay, paplay, mpg123).

`PlaybackServiceHarness` patches `ovos_audio.playback.play_audio` to return a
mock `Popen`-like object whose `communicate()` and `wait()` are no-ops. This
keeps tests fast and independent of the host audio stack.

## FakeBus wait_for_response Limitation

`FakeBus.wait_for_response()` uses a real WebSocket-style round-trip expectation
that does not work for synchronous in-process handlers. When a service handler
emits a reply synchronously (before `wait_for_response` sets up its internal
listener), the reply is lost.

Use the subscribe-emit-wait pattern instead:

```python
import threading
from ovoscope.audio import AudioServiceHarness
from ovos_bus_client.message import Message

reply_data = {}
done = threading.Event()

def _on_reply(msg):
    reply_data.update(msg.data)
    done.set()

with AudioServiceHarness() as h:
    h.bus.on("mycroft.audio.service.track_info_reply", _on_reply)
    h.bus.emit(Message("mycroft.audio.service.track_info"))
    done.wait(timeout=2)
    h.bus.remove("mycroft.audio.service.track_info_reply", _on_reply)

```

`AudioServiceHarness.get_track_info()` and `list_backends()` already implement
this pattern internally — `ovoscope/audio.py`.

## API Reference

### MockAudioBackend

`MockAudioBackend` — `ovoscope/audio.py`

| Attribute / Method | Type | Description |
|---|---|---|
| `played_tracks` | `List[str]` | All URIs passed to `add_list()` |
| `is_playing` | `bool` | True after `play()`, False after `stop()` |
| `is_paused` | `bool` | True after `pause()`, False after `resume()` |
| `current_track` | `Optional[str]` | First URI from last `add_list()` call |
| `lower_volume_calls` | `int` | Number of times `lower_volume()` was called |
| `restore_volume_calls` | `int` | Number of times `restore_volume()` was called |
| `stop()` | `bool` | Always returns `True` (required by AudioService) |
| `reset()` | `None` | Clears all state back to initial values |

### AudioServiceHarness

`AudioServiceHarness` — `ovoscope/audio.py`

| Method | Description |
|---|---|
| `play(tracks, backend=None, repeat=False)` | Emit play message and sleep briefly |
| `pause()` | Emit pause message |
| `resume()` | Emit resume message |
| `stop()` | Emit stop message |
| `queue(tracks)` | Emit queue message |
| `get_track_info(timeout=2.0)` | Subscribe, emit, wait; return reply data dict or `None` on timeout |
| `list_backends(timeout=2.0)` | Subscribe, emit, wait; return reply data dict or `None` on timeout |
| `assert_playing()` | Raise if backend.is_playing is False |
| `assert_paused()` | Raise if backend.is_paused is False |
| `assert_stopped()` | Raise if is_playing or is_paused is True |
| `assert_volume_lowered()` | Raise if lower_volume_calls == 0 |
| `assert_volume_restored()` | Raise if restore_volume_calls == 0 |

Constructor: `AudioServiceHarness(backend_name="mock", validate_source=False,
disable_ocp=True)`. Set `validate_source=True` to exercise session-source
validation; leave `disable_ocp=True` so no real OCP plugin is discovered. The
injected `MockAudioBackend` is reachable as `h.backend` and the live
`AudioService` as `h.service`.

### MockTTS

`MockTTS` — `ovoscope/audio.py`

| Attribute / Method | Description |
|---|---|
| `spoken_utterances` | List of sentences passed to `get_tts()` |
| `SILENT_WAV` | 44-byte valid WAV class constant |
| `get_tts(sentence, wav_file, ...)` | Write silent WAV, record utterance |
| `reset()` | Clear `spoken_utterances` |

### PlaybackServiceHarness

`PlaybackServiceHarness` — `ovoscope/audio.py`

| Method | Description |
|---|---|
| `speak(utterance, expect_response=False, timeout=10.0)` | Emit `speak`, wait for `recognizer_loop:audio_output_end`; raises `TimeoutError` if playback never finishes |
| `stop()` | Emit `mycroft.stop` |
| `assert_spoke(text)` | Raise if `text` not in `mock_tts.spoken_utterances` |
| `assert_audio_output_started(timeout=3.0)` | Raise if `recognizer_loop:audio_output_start` not fired |
| `assert_audio_output_ended(timeout=3.0)` | Raise if `recognizer_loop:audio_output_end` not fired |
| `assert_mic_listen(timeout=3.0)` | Raise if `mycroft.mic.listen` not fired |

The constructor is `PlaybackServiceHarness(validate_source=False,
disable_ocp=True, tts=None)`. Pass a real `TTS` plugin as `tts=` to synthesise
actual audio — the rendered WAV path of each utterance is then captured in
`h.captured_wavs`; with the default `MockTTS` a silent 44-byte WAV is written
and only the sentence text is recorded.

### AudioCaptureSession

`AudioCaptureSession` — `ovoscope/audio.py`

| Method / Property | Description |
|---|---|
| `start()` / `stop()` | Subscribe/unsubscribe from FakeBus |
| `__enter__` / `__exit__` | Context manager interface |
| `messages` | List of captured `Message` objects |
| `message_types` | List of captured `msg_type` strings |
| `assert_sequence(*types)` | Assert types appear in order as a subsequence |

Default `track_prefixes` captures: `"mycroft.audio."`,
`"recognizer_loop:audio_output"`, `"mycroft.mic.listen"`.

## Cross-References

- `AudioService` — `ovos-audio/ovos_audio/audio.py`


- `PlaybackService` — `ovos-audio/ovos_audio/service.py`


- `PlaybackThread` — `ovos-audio/ovos_audio/playback.py`


- `AudioBackend` (base class) — `ovos_plugin_manager.templates.audio.AudioBackend`


- `TTS` (base class) — `ovos_plugin_manager.templates.tts.TTS`


- End-to-end tests — `ovos-audio/test/end2end/`

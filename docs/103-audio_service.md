# Audio Service (ovos-audio)

The audio service handles TTS synthesis, sound playback, and media backend routing.
It is implemented as `PlaybackService` — `ovos_audio/service.py` — a `Thread` subclass that owns:

1. The primary and fallback TTS plugins
2. The `PlaybackThread` for serialised audio output
3. `DialogTransformersService` for pre-TTS text rewriting
4. `TTSTransformersService` for post-TTS audio post-processing
5. The optional legacy `AudioService` for media playback backends

---

## PlaybackService

```python
PlaybackService(
    ready_hook=on_ready,
    error_hook=on_error,
    stopping_hook=on_stopping,
    alive_hook=on_alive,
    started_hook=on_started,
    watchdog=lambda: None,
    bus=None,
    disable_ocp=None,
    validate_source=True,
    tts=None,
    disable_fallback=False
)
```

| Parameter | Description |
|---|---|
| `bus` | `MessageBusClient` instance; created automatically if `None` |
| `disable_ocp` | Disable OCP inside `AudioService`; reads `disable_ocp` from config if `None` |
| `validate_source` | If `True`, only handle audio from sessions with `session_id == "default"` (local mic only) |
| `tts` | Pre-created `TTS` instance; if provided, auto-reload on config change is disabled |
| `disable_fallback` | If `True`, never load or use the fallback TTS plugin |

`ProcessStatus` lifecycle:

| State | When |
|---|---|
| `started` | Constructor finished |
| `alive` | `run()` called |
| `ready` | TTS is loaded |
| `error` | TTS failed to load |
| `stopping` | `shutdown()` called |

---

## TTS

Two TTS plugins may be loaded at once. If the primary plugin fails for some reason, the second plugin will be used. This allows you to have a lower-quality offline voice as fallback to account for internet outages, ensuring the device can always give feedback.

```json
{
  "tts": {
    "pulse_duck": false,
    "module": "ovos-tts-plugin-server",
    "fallback_module": "ovos-tts-plugin-mimic",
    "ovos-tts-plugin-server": {
      "host": "https://tts.smartgic.io/piper",
      "v2": true,
      "verify_ssl": true
    }
  }
}
```

### TTS Loading and Reload

On startup, `_maybe_reload_tts()` loads the configured TTS plugin. It is also registered as a
config watcher — if `mycroft.conf` changes and the TTS config hash changes, the old TTS instance
is shut down and a new one is created. If `tts` is passed as a constructor argument, auto-reload
is disabled.

### Fallback TTS

If the primary TTS plugin raises an exception during `execute_tts()`, `execute_fallback_tts()` is called.

- Loaded at startup if `preload_fallback: true` (default) and `fallback_module` is set
- Lazy-loaded on first failure otherwise
- Skipped if `disable_fallback=True` or if `fallback_module` equals `module`

### TTSFactory

`TTSFactory.create()` resolves `config["tts"]["module"]` to an installed TTS plugin entry point
(OPM entry point group: `opm.tts`) and instantiates it. After creation, call `tts.init(bus, playback)`.

### Skill Methods

Skills interact with `ovos-audio` via:

```python
def speak(self, utterance: str, expect_response: bool = False, wait: Union[bool, int] = False):
    """Speak a sentence. Emits `speak` bus event."""

def speak_dialog(self, key: str, data: Optional[dict] = None,
                 expect_response: bool = False, wait: Union[bool, int] = False):
    """Speak a random sentence from a dialog file."""

def play_audio(self, filename: str, instant: bool = False):
    """Queue an audio file for playback."""

def acknowledge(self):
    """Play a short sound to acknowledge a request without speaking."""
```

To play sounds via bus messages, emit `"mycroft.audio.play_sound"` or `"mycroft.audio.queue"` with
data `{"uri": "path/sound.mp3"}`.

---

## PlaybackThread

`PlaybackThread` — `ovos_audio/playback.py` — is a daemon thread that consumes entries from
`TTS.queue` (a `Queue`) and plays them sequentially. All TTS output and queued sounds pass
through this thread to ensure they never overlap.

### Queue Entry Format

```python
(audio_path: str, visemes: list, listen: bool, tts_id: str, message: Message)
```

- `audio_path` — path to the synthesized WAV/MP3 file
- `visemes` — list of `(phoneme, timestamp)` pairs for mouth animation; `None` if unavailable
- `listen` — `True` if the microphone should be activated after playback
- `tts_id` — identifier of the TTS plugin; `"sounds"` for queued sound files
- `message` — originating `speak` message for context forwarding

### Playback Lifecycle

```
PlaybackThread.run()
  └── loop:
        dequeue entry → _play()
            ├── on_start()         → begin_audio()  → emit recognizer_loop:audio_output_start
            ├── TTSTransformersService.transform()   (post-process wav)
            ├── emit recognizer_loop:utterance_start
            ├── play_audio(path)   (subprocess via ovos_utils.sound)
            ├── show_visemes()     (if enclosure set)
            └── on_end(listen)     → end_audio()    → emit recognizer_loop:audio_output_end
                                                    → emit mycroft.mic.listen  (if listen=True)
```

### OCP Integration

| Config key | `begin_audio` emits | `end_audio` emits |
|---|---|---|
| `ocp_cork: true` | `ovos.common_play.cork` | `ovos.common_play.uncork` |
| `ocp_duck: true` | `ovos.common_play.duck` | `ovos.common_play.unduck` |

If `pulse_duck: true`, ducking is handled at the OS PulseAudio level — no bus events are emitted.

### G2P Integration

If a G2P (Grapheme-to-Phoneme) plugin is configured (`g2p.module` in `mycroft.conf`),
`PlaybackThread` loads it at startup. When viseme data is not provided by the TTS plugin,
the G2P plugin generates visemes from the utterance text for mouth animations.

```json
{
  "g2p": {
    "module": "ovos-g2p-plugin-mimic"
  }
}
```

### Sound Configuration

```json
{
  "sounds": {
    "start_listening": "snd/start_listening.wav",
    "end_listening": "snd/end_listening.wav",
    "acknowledge": "snd/acknowledge.mp3",
    "error": "snd/error.mp3"
  },
  "play_wav_cmdline": "paplay %1 --stream-name=mycroft-voice",
  "play_mp3_cmdline": "mpg123 %1",
  "play_ogg_cmdline": "ogg123 -q %1"
}
```

By default, OVOS will try to detect the best way to play a sound automatically.

### Key Methods

| Method | Description |
|---|---|
| `set_bus(bus)` | Attach a bus instance |
| `clear_queue()` | Drain the queue and terminate any playing subprocess |
| `pause()` | Stop current playback and block the queue |
| `resume()` | Resume a paused playback |
| `stop()` | Terminate thread and clear queue |
| `show_visemes(pairs)` | Send viseme data to enclosure |

---

## Transformer Plugins

`ovos-audio` runs two transformer pipelines around TTS synthesis:

```
speak event
    │
    ▼
DialogTransformersService    ← rewrite text before sending to TTS
    │
    ▼
TTS plugin (synthesis)
    │
    ▼
TTSTransformersService       ← post-process wav file after synthesis
    │
    ▼
PlaybackThread (play audio)
```

### Dialog Transformers

`DialogTransformersService` rewrites dialog text before it is sent to the TTS engine.
Examples of use: pronunciation corrections, language-specific rewrites, censoring.

Entry point group: `opm.dialog_transformer`

```json
{
  "dialog_transformers": {
    "ovos-dialog-translation-plugin": {},
    "ovos-dialog-transformer-openai-plugin": {
      "rewrite_prompt": "rewrite the text as if you were explaining it to a 5 year old"
    }
  }
}
```

Plugins are called in descending priority order (highest number first). The default blacklisted
skills (never transformed): `["skill-ovos-icanhazdadjokes.openvoiceos"]`.

### TTS Transformers

`TTSTransformersService` post-processes the synthesized WAV file after TTS output and before playback.
Examples of use: audio normalization, speed adjustment, noise reduction.

> **NOTE**: Does not work with StreamingTTS.

Entry point group: `opm.tts_transformer`

```json
{
  "tts_transformers": {
    "ovos-tts-transformer-sox-plugin": {
      "default_effects": {
        "speed": {"factor": 1.1}
      }
    }
  }
}
```

### Common Transformer Behaviour

| Behaviour | Detail |
|---|---|
| Plugin discovery | Via OPM entry point groups |
| Activation | Config key must exist; `"active": false` disables |
| Priority | Higher number → runs first |
| Error handling | Exceptions in individual plugins are logged and skipped |
| Shutdown | `shutdown()` calls `module.shutdown()` on each loaded plugin |

---

## Legacy AudioService

`AudioService` — `ovos_audio/audio.py` — manages a set of audio playback backend plugins (VLC, MPV, etc.)
and exposes media playback control over the bus via the `mycroft.audio.service.*` event namespace.

> **Deprecation notice:** `AudioService` and its backend plugin system are being superseded by `ovos-media`.
> New deployments should migrate to `ovos-media`. The legacy audio service can be disabled with
> `"enable_old_audioservice": false` in `mycroft.conf`.

### Backend Loading

`load_services()` uses OPM to discover installed audio backend plugins (entry point group: `mycroft.plugin.audioservice`). OCP (`ovos_common_play`) is explicitly excluded from the general plugin scan and loaded separately via `find_ocp()`.

### Audio Ducking

`AudioService` automatically lowers playback volume during speech and microphone recording:

| Bus Event | Action |
|---|---|
| `recognizer_loop:audio_output_start` | Lower volume (TTS speaking) |
| `recognizer_loop:audio_output_end` | Restore volume |
| `recognizer_loop:record_begin` | Lower volume (mic active) |
| `recognizer_loop:record_end` | Restore volume (with 8 s speech-detection grace period) |
| `ovos.utterance.handled` | Restore volume if not currently speaking |

### Legacy AudioService Configuration

```json
{
  "enable_old_audioservice": true,
  "disable_ocp": false,
  "Audio": {
    "default-backend": "vlc",
    "backends": {
      "OCP": {},
      "vlc": {"active": true}
    }
  }
}
```

---

## Bus Events

### Emitted by `PlaybackThread`

| Event | When |
|---|---|
| `recognizer_loop:audio_output_start` | Playback of a batch of queued audio begins |
| `recognizer_loop:audio_output_end` | Playback of a batch of queued audio ends |
| `recognizer_loop:utterance_start` | Each individual utterance starts playing |
| `mycroft.mic.listen` | After speech ends when `listen=True` |
| `ovos.common_play.cork` | Before speech if `ocp_cork=True` |
| `ovos.common_play.uncork` | After speech if `ocp_cork=True` |
| `ovos.common_play.duck` | Before speech if `ocp_duck=True` |
| `ovos.common_play.unduck` | After speech if `ocp_duck=True` |

### Handled by `PlaybackService`

| Event | Handler | Description |
|---|---|---|
| `speak` | `handle_speak` | Synthesize and play TTS |
| `speak:b64_audio` | `handle_b64_audio` | Synthesize and return as base64 |
| `mycroft.stop` | `handle_stop` | Stop current TTS playback |
| `mycroft.audio.speech.stop` | `handle_stop` | Stop current TTS playback |
| `mycroft.audio.speak.status` | `handle_speak_status` | Reply with `{"speaking": bool}` |
| `mycroft.audio.queue` | `handle_queue_audio` | Queue sound file in TTS thread |
| `mycroft.audio.play_sound` | `handle_instant_play` | Play sound immediately |
| `ovos.languages.tts` | `handle_get_languages_tts` | Reply with supported TTS languages |
| `opm.tts.query` | `handle_opm_tts_query` | Reply with TTS plugin metadata |
| `opm.g2p.query` | `handle_opm_g2p_query` | Reply with G2P plugin metadata |

### Emitted by `PlaybackService`

| Event | When |
|---|---|
| `mycroft.stop.handled` | After TTS queue is cleared on stop |
| `mycroft.audio.is_speaking` | In reply to `mycroft.audio.speak.status` |

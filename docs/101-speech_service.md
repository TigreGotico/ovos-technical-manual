# Listener Service (ovos-dinkum-listener)

`ovos-dinkum-listener` is the voice input daemon for OpenVoiceOS. It continuously reads audio from
the microphone, runs it through a deterministic finite-state machine
(wakeword → VAD → STT → utterance), and emits bus events that drive the intent pipeline.

Different implementations of the listener service have existed over the years:

- [mycroft-classic-listener](https://github.com/OpenVoiceOS/mycroft-classic-listener) — the original Mycroft Mark 1 listener, extracted to a standalone component — **archived**
- [ovos-listener](https://github.com/OpenVoiceOS/ovos-listener) — updated version with VAD plugins and multiple hotword support — **deprecated** in `ovos-core` **0.0.8**
- [ovos-dinkum-listener](https://github.com/OpenVoiceOS/ovos-dinkum-listener) — a rewrite based on [mycroft-dinkum](https://github.com/MycroftAI/mycroft-dinkum) — **current** implementation since `ovos-core` **0.0.8**

---

## Architecture

```
OVOSDinkumVoiceService (Thread)             service.py:84
    │
    ├── Microphone plugin               OVOSMicrophoneFactory.create()
    ├── HotwordContainer                voice_loop/hotwords.py:102
    │     ├── listen_words   (WW)
    │     ├── wakeup_words
    │     ├── stop_words
    │     └── hot_words
    ├── VADEngine plugin                OVOSVADFactory.create()
    ├── StreamingSTT + fallback STT     plugins.py
    ├── AudioTransformersService        transformers.py
    │
    └── DinkumVoiceLoop (FSM)           voice_loop/voice_loop.py:106
            │
            ├── PRE_WAKE_VAD        ← gate wakeword on speech presence (optional)
            ├── DETECT_WAKEWORD     ← feed audio to hotword engines
            ├── WAITING_CMD         ← continuous mode: accumulate audio until speech
            ├── CONFIRMATION        ← playing listen sound; no STT buffering yet
            ├── BEFORE_COMMAND      ← waiting for VAD to confirm speech started
            ├── IN_COMMAND          ← VAD confirmed; streaming audio to STT
            ├── AFTER_COMMAND       ← silence end: finalise STT, fire callbacks
            ├── RECORDING           ← free recording mode (stop-word or max-silence exits)
            ├── SLEEPING            ← suppressed; wakeup-word only
            └── CHECK_WAKE_UP       ← heard WW while sleeping; waiting for wakeup word
```

The service is a `Thread` subclass — `service.py:84`. All sub-components (mic, hotwords, VAD, STT,
transformers, voice loop) are created and started in `run()`. The service reports lifecycle state
via `ProcessStatus` and emits `mycroft.ready` when all components are loaded.

---

## Data Flow

```
mic.read_chunk()
       │
       ▼
DinkumVoiceLoop.run()                       voice_loop.py:205
       │
       ├─[PRE_WAKE_VAD]─── vad.is_silence() ──► transformers.feed_audio()
       │                         │ speech
       ├─[DETECT_WAKEWORD]─ hotwords.update() + found()
       │                       │ WW detected
       │                  listenword_audio_callback, wake_callback
       │                       │
       ├─[CONFIRMATION]─── wait for sound duration, then → BEFORE_COMMAND
       │
       ├─[BEFORE_COMMAND]─ vad.is_silence() ──► stt.stream_data()
       │                         │ speech_seconds elapsed
       ├─[IN_COMMAND]───── vad.is_silence() ──► stt.stream_data()
       │                       │ silence_seconds elapsed
       ├─[AFTER_COMMAND]── transformers.transform()
       │                   stt.transcribe()   [+ fallback]
       │                   stt_audio_callback, text_callback
       │                   ▼
       └──────────────── DETECT_WAKEWORD  (or WAITING_CMD in continuous/hybrid)
```

---

## Voice Loop FSM

### `ListeningMode` — `voice_loop.py:49`

Global operating mode. Controls which FSM states are reachable.

| Value | Config trigger | Description |
|---|---|---|
| `WAKEWORD` | default | Only listen after a wake word is detected |
| `CONTINUOUS` | `listener.continuous_listen: true` | Always listen; no wake word required |
| `HYBRID` | `listener.hybrid_listen: true` | Always listen but also detect hotwords |
| `SLEEPING` | programmatic | Suppressed; only wakeup words are checked |

### `ListeningState` — `voice_loop.py:32`

Internal FSM state. Transitions on every audio chunk.

| State | String value | Description |
|---|---|---|
| `PRE_WAKE_VAD` | `"pre_wake_vad"` | Gate wakeword detection on VAD speech presence |
| `DETECT_WAKEWORD` | `"wakeword"` | Feed audio to hotword engines waiting for a listen word |
| `WAITING_CMD` | `"continuous"` | Continuous mode: accumulate audio until speech begins |
| `CONFIRMATION` | `"confirmation"` | Playing listen sound; no STT buffering yet |
| `BEFORE_COMMAND` | `"before_cmd"` | Waiting for VAD to confirm speech started |
| `IN_COMMAND` | `"in_cmd"` | VAD confirmed speech; streaming audio to STT |
| `AFTER_COMMAND` | `"after_cmd"` | Silence end detected; finalise STT and fire callbacks |
| `RECORDING` | `"recording"` | Free recording mode; exits on stop word or max silence |
| `SLEEPING` | `"sleeping"` | Suppressed; only wakeup words are active |
| `CHECK_WAKE_UP` | `"wake_up"` | Wake word heard while sleeping; waiting for wakeup word |

### Wake Word mode

![imagem](https://github.com/OpenVoiceOS/ovos-dinkum-listener/assets/33701864/c55388dc-a7fb-4857-9c35-f4a4223c4145)

### Sleep mode

Can be used via [Naptime skill](https://github.com/OpenVoiceOS/skill-ovos-naptime)

![imagem](https://github.com/OpenVoiceOS/ovos-dinkum-listener/assets/33701864/24835210-2116-4080-8c2b-fc18eecd923a)

### Continuous mode

**EXPERIMENTAL**

![imagem](https://github.com/OpenVoiceOS/ovos-dinkum-listener/assets/33701864/c8820161-9cb8-433f-9380-6d07965c7fa5)

### Hybrid mode

**EXPERIMENTAL**

![imagem](https://github.com/OpenVoiceOS/ovos-dinkum-listener/assets/33701864/b9012663-4f00-47a9-bac4-8b08392da12c)

### Recording mode

**EXPERIMENTAL**

Can be used via [Recording skill](https://github.com/OpenVoiceOS/skill-ovos-audio-recording)

![imagem](https://github.com/OpenVoiceOS/ovos-dinkum-listener/assets/33701864/0337b499-3175-4031-a83f-eda352d2197f)

---

## OVOSDinkumVoiceService

**Class:** `OVOSDinkumVoiceService` — `service.py:84`

```python
OVOSDinkumVoiceService(
    on_ready=None, on_error=None, on_stopping=None, on_alive=None, on_started=None,
    watchdog=lambda: None,
    mic=None,
    bus=None,
    validate_source=True,
    stt=None,
    fallback_stt=None,
    vad=None,
    hotwords=None,
    disable_fallback=False
)
```

| Parameter | Description |
|---|---|
| `on_ready` / `on_error` / `on_stopping` / `on_alive` / `on_started` | `ProcessStatus` lifecycle callbacks |
| `watchdog` | Called every 0.5 s for systemd watchdog keepalive |
| `mic` | Pre-created `Microphone`; loaded via `OVOSMicrophoneFactory` if `None` |
| `bus` | `MessageBusClient`; created automatically if `None` |
| `validate_source` | If `True`, only handle `mycroft.mic.listen` from native audio destinations |
| `stt` | Pre-created `StreamingSTT`; disables auto-reload on config change if provided |
| `fallback_stt` | Pre-created fallback `StreamingSTT` |
| `vad` | Pre-created `VADEngine`; loaded via `OVOSVADFactory` if `None` |
| `hotwords` | Pre-created `HotwordContainer`; disables auto-reload on config change if provided |
| `disable_fallback` | If `True`, never load the fallback STT plugin |

### Configuration Reload

`reload_configuration()` is triggered on `configuration.updated` bus events. It computes MD5
hashes of four config sections and only reloads components whose hash changed:

| Config section | Effect |
|---|---|
| listener loop config | Rebuild `DinkumVoiceLoop` |
| hotwords config | Reload hotword engines |
| STT config | Reload primary STT plugin |
| fallback STT config | Reload fallback STT plugin |

### Hallucination Filtering

After STT, transcripts are filtered using a block list. Enabled by `filter_hallucinations: true`
(default: `true`). Additional strings can be added via `hallucination_list` in config.

- `WAKEWORD` mode: empty result emits `recognizer_loop:speech.recognition.unknown`
- `CONTINUOUS` mode: empty result is silently ignored

### Fake Barge-In

When `listener.fake_barge_in: true`:
1. Speaker volume is lowered to `listener.barge_in_volume` (default: `30`) at `record_begin`
2. Volume is restored at `record_end`

`listener.mute_during_output: true` mutes the mic entirely during TTS playback.

### Audio Saving

When `listener.save_utterances: true`, utterance audio + JSON metadata is saved to
`{save_path}/utterances/`. When `listener.record_wake_words: true`, hotword audio is saved to
`{save_path}/wake_words/`. Free recording audio goes to `{save_path}/recordings/`.

---

## Hotwords

`HotwordContainer` — `voice_loop/hotwords.py:102` — manages all loaded hotword/wake-word engines and
routes audio to the appropriate subset based on the current `HotwordState`.

### Hotword Types

| Type | Config key | Effect when detected |
|---|---|---|
| **Listen word** | `listen: true` or matches `listener.wake_word` | Starts VAD/STT recording pipeline |
| **Wakeup word** | `wakeup: true` or matches `listener.stand_up_word` | Exits sleep mode |
| **Stop word** | `stopword: true` | Ends free `RECORDING` mode |
| **Hotword** | `active: true`, none of the above | Plays sound and/or emits bus event |

### `HotwordState`

Controls which engine subset receives audio in `update()` — `hotwords.py:312`:

| State | Active engines | Use case |
|---|---|---|
| `LISTEN` | `listen_words` | Default WW detection |
| `HOTWORD` | `hot_words` | Continuous/hybrid mode |
| `RECORDING` | `stop_words` | During free recording |
| `WAKEUP` | `wakeup_words` | While sleeping |

### Auto-enable Rules — `hotwords.py:158`

When `active` is `null`/`None` in the hotword config:
- The main wake word (`listener.wake_word`) → enabled
- The stand-up word (`listener.stand_up_word`) → enabled
- All other hotwords → disabled

### `CyclicAudioBuffer` — `hotwords.py:22`

A fixed-size sliding window of audio bytes used by hotword plugins. New data is appended; oldest
data is dropped when capacity is exceeded.

```python
from ovos_dinkum_listener.voice_loop.hotwords import CyclicAudioBuffer

buf = CyclicAudioBuffer(duration=0.98, sample_rate=16000, sample_width=2)
buf.append(chunk)
audio = buf.get()
```

### Hotword Configuration Reference

```json
{
  "hotwords": {
    "hey_mycroft": {
      "module": "ovos-ww-plugin-precise-lite",
      "listen": true,
      "sound": "snd/start_listening.wav",
      "active": null
    },
    "wake_up": {
      "module": "ovos-ww-plugin-vosk",
      "wakeup": true,
      "active": null
    },
    "stop_recording": {
      "module": "ovos-ww-plugin-vosk",
      "stopword": true,
      "active": true
    },
    "hey_computer": {
      "module": "ovos-ww-plugin-precise-lite",
      "bus_event": "my.custom.event",
      "sound": "snd/ding.wav",
      "active": true
    },
    "hola_mycroft": {
      "module": "ovos-ww-plugin-precise-lite",
      "listen": true,
      "stt_lang": "es-es",
      "active": true
    }
  }
}
```

| Key | Type | Default | Description |
|---|---|---|---|
| `module` | `str` | — | OPM entry point name for the hotword plugin |
| `active` | `bool\|null` | `null` | `true` to load; auto-enabled for main WW and stand-up word |
| `listen` | `bool` | `false` | Triggers the VAD/STT recording pipeline |
| `wakeup` | `bool` | `false` | Exits sleep mode |
| `stopword` | `bool` | `false` | Ends free recording mode |
| `sound` | `str\|list` | — | Sound file played on detection |
| `bus_event` | `str` | — | Bus message type emitted on detection |
| `utterance` | `str` | — | Hard-coded utterance bypassing STT |
| `stt_lang` | `str` | global lang | Override STT language for the following command |

### Sound Classifiers

Hotwords can be used as generic sound classifiers that emit bus events:

```json
{
  "hotwords": {
    "cough": {
      "module": "ovos-ww-plugin-precise",
      "model": "https://github.com/MycroftAI/precise-data/blob/models-dev/cough.tar.gz",
      "listen": false,
      "active": true,
      "bus_event": "cough.detected"
    }
  }
}
```

### Multilingual Hotwords

A wake word can be configured per language, assigning an STT language per wake word:

```json
{
  "listener": { "wake_word": "hey mycroft" },
  "hotwords": {
    "hey_mycroft": {"module": "...", "listen": true},
    "android": {
      "module": "...",
      "active": true,
      "listen": true,
      "stt_lang": "pt-pt"
    }
  }
}
```

### Fallback Wake Words

Hotword definitions can include `"fallback_ww"` — an alternative config loaded if the primary fails:

```json
{
  "hotwords": {
    "hey_mycroft": {
      "module": "ovos-ww-plugin-precise-lite",
      "listen": true,
      "fallback_ww": "hey_mycroft_vosk"
    },
    "hey_mycroft_vosk": {
      "module": "ovos-ww-plugin-vosk",
      "samples": ["hey mycroft"],
      "rule": "fuzzy",
      "listen": true
    }
  }
}
```

---

## Microphone

Microphone plugins feed raw audio to the listener:

```json
{
  "listener": {
    "microphone": {
      "module": "ovos-microphone-plugin-alsa"
    }
  }
}
```

Default: `ovos-microphone-plugin-alsa`. Entry point group: `opm.microphone`.

---

## VAD (Voice Activity Detection)

VAD plugins serve several functions:
- Detect when the user finished speaking
- Remove silence before sending audio to STT (when `remove_silence: true`)
- Detect when the user is speaking during continuous mode

```json
{
  "listener": {
    "remove_silence": true,
    "VAD": {
      "module": "ovos-vad-plugin-silero",
      "ovos-vad-plugin-silero": {"threshold": 0.2},
      "ovos-vad-plugin-webrtcvad": {"vad_mode": 3}
    }
  }
}
```

### VAD Pre-Wake Feature

When `listener.vad_pre_wake_enabled: true` — `voice_loop.py:215`:

1. Loop starts in `PRE_WAKE_VAD`
2. Each chunk is sent to `transformers.feed_audio()` unless VAD detects speech
3. On speech: chunk appended to `hotword_chunks`, state → `DETECT_WAKEWORD`
4. If no wake word detected within 5 seconds of VAD activation → back to `PRE_WAKE_VAD`

This reduces CPU usage from hotword engines when the environment is silent.

---

## STT

Two STT plugins may be loaded at once. If the primary plugin fails, the fallback is used:

```json
{
  "stt": {
    "module": "ovos-stt-plugin-server",
    "fallback_module": "ovos-stt-plugin-vosk",
    "ovos-stt-plugin-server": {"url": "https://stt.openvoiceos.com/stt"}
  }
}
```

### STT Loading — `plugins.py`

`load_stt_module()` — `plugins.py:81` — loads the primary STT plugin. Non-streaming plugins are
automatically wrapped by `FakeStreamingSTT` — `plugins.py:47` — to adapt them to the streaming
interface required by `DinkumVoiceLoop`.

`load_fallback_stt()` — `plugins.py:102` — loads the fallback STT. Returns `None` if not configured.

### STT Transcription Flow

```
_after_cmd()                                    voice_loop.py:818
 ├─ transformers.transform()        → stt_context dict with injected metadata
 ├─ _vad_remove_silence()           → (if FakeStreamingSTT + remove_silence)
 ├─ _get_tx(stt_context)            → voice_loop.py:739
 │    ├─ _validate_lang(stt_context["stt_lang"])
 │    ├─ stt.transcribe(lang)        → [(text, conf), ...]
 │    ├─ fallback_stt.transcribe()   → (if primary returned nothing)
 │    ├─ filter by min_stt_confidence (keep at least 1)
 │    └─ truncate to max_transcripts
 ├─ stt_audio_callback(bytes, ctx)
 ├─ record_end_callback()
 └─ text_callback(utts, ctx)
```

### `FakeStreamingSTT` — `plugins.py:47`

Adapter that wraps a regular (non-streaming) `STT` plugin inside the `StreamingSTT` interface.
All audio chunks are buffered internally; the underlying plugin is invoked once at transcription time.

---

## Audio Transformers

`AudioTransformersService` — `transformers.py:34` — manages a prioritised pipeline of audio
transformer plugins. Plugins can inspect and modify raw audio before and during STT processing, and
can inject metadata into the utterance context that is merged into `recognizer_loop:utterance`.

![imagem](https://github.com/OpenVoiceOS/ovos-technical-manual/assets/33701864/ae428a90-fc7e-4ca7-81d5-fa1d9bbfb885)

Entry point group: `opm.audio_transformer`

### Feed Methods

| Method | Called in states | Description |
|---|---|---|
| `feed_audio(chunk)` | `DETECT_WAKEWORD`, `WAITING_CMD`, `PRE_WAKE_VAD`, `BEFORE_COMMAND`, `CONFIRMATION` | Ambient audio |
| `feed_hotword(chunk)` | WW detection moment | The chunk in which a WW was detected |
| `feed_speech(chunk)` | `IN_COMMAND`, `RECORDING` | Active speech |
| `transform(chunk)` | `AFTER_COMMAND` | Complete utterance — returns `(bytes, context_dict)` |

Context keys that plugins may inject:

| Key | Description |
|---|---|
| `stt_lang` | Override STT language for this utterance |
| `detected_lang` | Language identified by a classifier plugin |
| `request_lang` | Language volunteered by the source device |

Default context initialised at the start of `transform()` — `transformers.py:117`:

```python
{
    "client_name": "ovos_dinkum_listener",
    "source": "audio",
    "destination": ["skills"]
}
```

### Plugin API

```python
class MyAudioTransformer:
    priority: int  # higher = runs first

    def feed_audio_chunk(self, chunk: bytes) -> None: ...
    def feed_hotword_chunk(self, chunk: bytes) -> None: ...
    def feed_speech_chunk(self, chunk: bytes) -> None: ...
    def feed_speech_utterance(self, chunk: bytes) -> None: ...
    def transform(self, chunk: bytes) -> tuple[bytes, dict]: ...
```

Configuration:

```json
{
  "listener": {
    "audio_transformers": {
      "ovos-audio-transformer-example": {
        "active": true,
        "priority": 50
      }
    }
  }
}
```

---

## Service Bus Events

### Emitted by `OVOSDinkumVoiceService`

| Event | When |
|---|---|
| `recognizer_loop:record_begin` | Recording starts (wakeword or programmatic listen) |
| `recognizer_loop:record_end` | Recording ends |
| `recognizer_loop:wakeword` | Listen word detected (`listen: true`) |
| `recognizer_loop:hotword` | Non-listen hotword detected |
| `recognizer_loop:wakeupword` | Wakeup word detected while sleeping |
| `recognizer_loop:stopword` | Stop word detected during recording |
| `recognizer_loop:utterance` | STT complete — `{"utterances": [...], "lang": "..."}` |
| `recognizer_loop:speech.recognition.unknown` | STT returned empty (WAKEWORD mode) |
| `mycroft.awoken` | Voice loop exited sleep mode |
| `mycroft.audio.play_sound` | Play the listen-start confirmation sound |
| `mycroft.volume.set` | Lower/restore volume for fake barge-in |

### Handled by `OVOSDinkumVoiceService`

| Event | Effect |
|---|---|
| `mycroft.mic.listen` | Programmatic listen (bypasses wakeword) |
| `mycroft.mic.mute` / `unmute` / `mute.toggle` | Soft mute control |
| `recognizer_loop:sleep` | Enter sleep mode |
| `recognizer_loop:wake_up` | Exit sleep mode |
| `recognizer_loop:state.set` | Set listening state and/or mode |
| `recognizer_loop:state.get` | Reply with current state and mode |
| `recognizer_loop:record_stop` | Stop free recording mode |
| `recognizer_loop:b64_audio` | Inject base64-encoded audio as if from mic |
| `recognizer_loop:b64_transcribe` | Transcribe audio and return result on bus |
| `opm.stt.query` | Reply with installed STT plugin metadata |
| `opm.ww.query` | Reply with installed wake word plugin metadata |
| `opm.vad.query` | Reply with installed VAD plugin metadata |
| `ovos.languages.stt` | Reply with supported STT languages |

---

## Configuration Reference

### Listening Mode

| Key | Type | Default | Description |
|---|---|---|---|
| `listener.wake_word` | `str` | `"hey_mycroft"` | Primary wake word name (must match a key in `hotwords`) |
| `listener.stand_up_word` | `str` | `"wake_up"` | Word to exit sleep mode |
| `listener.continuous_listen` | `bool` | `false` | Enable continuous listening mode |
| `listener.hybrid_listen` | `bool` | `false` | Listen continuously but also recognise hotwords |
| `listener.vad_pre_wake_enabled` | `bool` | `false` | Only activate wakeword engines when VAD detects speech |

### Timing

| Key | Type | Default | Description |
|---|---|---|---|
| `listener.speech_begin` | `float` | `0.3` | Seconds of VAD-confirmed speech before recording is active |
| `listener.silence_end` | `float` | `0.7` | Seconds of VAD-confirmed silence to end recording |
| `listener.recording_timeout` | `float` | `10.0` | Max total recording seconds |
| `listener.recording_timeout_with_silence` | `float` | `5.0` | Max pre-speech silence seconds after wakeword |
| `listener.recording_mode_max_silence` | `float` | `30.0` | Max silence seconds in free recording mode |

### STT Quality

| Key | Type | Default | Description |
|---|---|---|---|
| `listener.min_stt_confidence` | `float` | `0.6` | Minimum confidence to accept a transcript |
| `listener.max_transcripts` | `int` | `1` | Maximum alternative transcripts to emit |
| `listener.remove_silence` | `bool` | `false` | Use VAD to strip silence before STT finalisation |
| `listener.instant_listen` | `bool` | `true` | Skip confirmation sound delay before recording |

### Audio Saving

| Key | Type | Default | Description |
|---|---|---|---|
| `listener.save_utterances` | `bool` | `false` | Save STT audio + JSON metadata to disk |
| `listener.record_wake_words` | `bool` | `false` | Save hotword audio + JSON metadata to disk |
| `listener.save_path` | `str` | XDG data dir | Base directory for saved audio |
| `listener.utterance_filename` | `str` | `"{md5}-{uuid4}"` | Filename template for saved utterances |

### Confirmation Sound

| Key | Type | Default | Description |
|---|---|---|---|
| `confirm_listening` | `bool` | `false` | Play a sound when wake word is detected |
| `sounds.start_listening` | `str` | — | Path or name of the listen-start sound |
| `sounds.end_listening` | `str` | — | Sound played when recording mode ends |

### Miscellaneous

| Key | Type | Default | Description |
|---|---|---|---|
| `listener.fake_barge_in` | `bool` | `false` | Lower speaker volume during recording |
| `listener.barge_in_volume` | `int` | `30` | Volume (0–100) during fake barge-in |
| `listener.mute_during_output` | `bool` | `false` | Mute mic while audio is playing |
| `filter_hallucinations` | `bool` | `true` | Remove known STT hallucinations from transcripts |
| `secondary_langs` | `list[str]` | `[]` | Additional language codes accepted from language-detection transformers |

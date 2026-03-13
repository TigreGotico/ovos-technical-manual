# Wyoming Bridges

[Wyoming](https://github.com/rhasspy/wyoming) is a simple TCP-based peer-to-peer protocol
for voice assistant components, originally developed for Home Assistant's voice pipeline.
It defines a small set of typed events that flow over a socket connection, covering the
three main voice pipeline stages: wake word detection, speech-to-text, and text-to-speech.

OVOS provides three Wyoming bridge packages that expose any installed OVOS plugin as a
Wyoming-compatible server. This allows Home Assistant, Rhasspy, and other Wyoming clients
to use OVOS engines without knowing anything about the OVOS plugin system.

| Bridge | Package | Default port | OVOS plugin type |
|---|---|---|---|
| `wyoming-ovos-stt` | `wyoming-ovos-stt` | 7891 | `opm.plugin.stt` |
| `wyoming-ovos-tts` | `wyoming-ovos-tts` | 7892 | `opm.plugin.tts` |
| `wyoming-ovos-wakeword` | `wyoming-ovos-wakeword` | 7893 | `opm.plugin.wake_word` |

All three bridges:

- Are installed via `pip install <package-name>`


- Read plugin configuration from `mycroft.conf` (standard OVOS config file)


- Run as standalone async TCP servers using the `wyoming` library

---

## STT Bridge (`wyoming-ovos-stt`)

Exposes any OVOS STT plugin as a Wyoming ASR server.

### Architecture

```
Wyoming client                    wyoming-ovos-stt                 OVOS plugin layer
(Home Assistant,           ┌─────────────────────────────┐
 rhasspy, etc.)            │  AsyncServer (wyoming lib)   │
                           │                             │
 AudioChunk* ─────────────►  STTAPIEventHandler          │
 AudioStop   ─────────────►    .handle_audio_chunk()     │
 Transcript  ◄─────────────    .handle_stt()  ──────────►  STT.execute(AudioData)
                           │    .handle_audio_end()       │  (OVOSSTTFactory)
 Describe    ─────────────►    → write Info event         │
                           └─────────────────────────────┘

```

**`STTAPIEventHandler`** (`wyoming_ovos_stt/handler.py`)

One instance per client connection. Accumulates incoming audio chunks (converted to
16 kHz / 16-bit / mono via `AudioChunkConverter`), then on `AudioStop` calls
`STT.execute(AudioData)` and sends a `Transcript` event.

| Event type | Action |
|---|---|
| `AudioChunk` | Convert to 16 kHz/16-bit/mono, append to `self.audio` |
| `AudioStop` | Call `STT.execute()`, send `Transcript`, reset accumulator |
| `Transcribe` | Acknowledge (no-op; signals start of a new request) |
| `Describe` | Send `Info` advertising the loaded plugin as an ASR model |

Plugin loading happens once at startup. The plugin instance is shared across all connections.

### Running

```bash
pip install wyoming-ovos-stt
wyoming-ovos-stt --plugin-name <ovos-stt-plugin-name> --uri tcp://0.0.0.0:7891

```

| Argument | Required | Default | Description |
|---|---|---|---|
| `--plugin-name` | Yes | — | OVOS STT plugin module name (e.g. `ovos-stt-plugin-whisper`) |
| `--uri` | Yes | — | `tcp://HOST:PORT` or `unix:///path/to/socket` |
| `--debug` | No | `False` | Enable DEBUG log level |

Examples:

```bash

# OVOS public STT server proxy
wyoming-ovos-stt --uri tcp://0.0.0.0:7891 --plugin-name ovos-stt-plugin-server

# Whisper locally
wyoming-ovos-stt --uri tcp://0.0.0.0:7891 --plugin-name ovos-stt-plugin-whisper

# Unix socket
wyoming-ovos-stt --uri unix:///run/wyoming-stt.sock --plugin-name ovos-stt-plugin-vosk

```

### Configuration

Plugin configuration is read from `mycroft.conf["stt"][<plugin-name>]`.
Language is taken from `cfg["lang"]` if present, otherwise from `mycroft.conf["lang"]`.

```json
{
  "lang": "en-US",
  "stt": {
    "ovos-stt-plugin-server": {
      "url": "https://stt.openvoiceos.com/stt"
    },
    "ovos-stt-plugin-whisper": {
      "model": "base"
    }
  }
}

```

### Wyoming message flow

```
Client → AudioChunk (rate=16000, width=2, channels=1, PCM bytes)
       → AudioChunk ...
       → AudioStop
Server → Transcript (text="hello world")

Client → Describe
Server → Info(asr=[AsrProgram(name=plugin_name, models=[AsrModel(...)])])

```

Audio must be 16 kHz / 16-bit / mono PCM. The bridge converts incoming audio automatically.

---

## TTS Bridge (`wyoming-ovos-tts`)

Exposes any OVOS TTS plugin as a Wyoming TTS server.

### Architecture

```
Wyoming client                    wyoming-ovos-tts                  OVOS plugin layer
(Home Assistant,           ┌──────────────────────────────┐
 rhasspy, etc.)            │  AsyncServer (wyoming lib)    │
                           │                              │
 Describe    ─────────────►  OVOSTTSEventHandler           │
 Info        ◄─────────────   .handle_event()             │
                           │                              │
 Synthesize  ─────────────►   .handle_synth()  ───────────►  TTS.synth(text)
 AudioStart  ◄─────────────   wav_to_chunks()             │  (OVOSTTSFactory)
 AudioChunk* ◄─────────────                               │
 AudioStop   ◄─────────────                               │
                           └──────────────────────────────┘

```

**`OVOSTTSEventHandler`**

One instance per client connection. On `Synthesize`, calls `TTS.synth(text)` which returns
a path to a WAV file. The WAV is split into chunks of 1024 samples and streamed back as
`AudioStart` + `AudioChunk`* + `AudioStop`.

| Event type | Action |
|---|---|
| `Describe` | Send `Info` advertising the loaded plugin as a TTS voice |
| `Synthesize` | Call `TTS.synth()`, stream WAV chunks |

### Running

```bash
pip install wyoming-ovos-tts
wyoming-ovos-tts --plugin-name <ovos-tts-plugin-name> --uri tcp://0.0.0.0:7892

```

| Argument | Required | Default | Description |
|---|---|---|---|
| `--plugin-name` | Yes | — | OVOS TTS plugin module name (e.g. `ovos-tts-plugin-piper`) |
| `--uri` | No | `stdio://` | `tcp://HOST:PORT` or `unix:///path/to/socket` |
| `--debug` | No | `False` | Enable DEBUG log level |

Examples:

```bash

# OVOS public TTS server proxy
wyoming-ovos-tts --uri tcp://0.0.0.0:7892 --plugin-name ovos-tts-plugin-server

# Piper locally
wyoming-ovos-tts --uri tcp://0.0.0.0:7892 --plugin-name ovos-tts-plugin-piper

# Unix socket
wyoming-ovos-tts --uri unix:///run/wyoming-tts.sock --plugin-name ovos-tts-plugin-espeak

```

### Configuration

Plugin configuration is read from `mycroft.conf["tts"][<plugin-name>]`.

```json
{
  "lang": "en-US",
  "tts": {
    "ovos-tts-plugin-server": {
      "host": "https://pipertts.ziggyai.online"
    },
    "ovos-tts-plugin-piper": {
      "voice": "en_US-lessac-medium"
    }
  }
}

```

### Wyoming message flow

```
Client → Synthesize(text="Hello world", voice=VoiceSettings(...))
Server → AudioStart(rate=22050, width=2, channels=1)
       → AudioChunk (1024 samples)
       → AudioChunk ...
       → AudioStop

Client → Describe
Server → Info(tts=[TtsProgram(name=plugin_name, voices=[TtsVoice(...)])])

```

---

## Wake Word Bridge (`wyoming-ovos-wakeword`)

Exposes any OVOS wake word plugin as a Wyoming wake word detection server.
Supports **multiple simultaneous wake word models** loaded on demand per client session.

### Architecture

```
Wyoming client                   wyoming-ovos-wakeword              OVOS plugin layer
(Home Assistant,           ┌────────────────────────────────┐
 rhasspy, etc.)            │  AsyncServer (wyoming lib)      │
                           │                                │
 Describe    ─────────────►  OVOSWakeWordEventHandler        │
 Info        ◄─────────────   ._get_info()                  │
                           │                                │
 Detect([names]) ─────────►   .active_detectors = names     │
                           │   .load_wakewords(names) ──────►  OVOSWakeWordFactory
                           │                                │  .create_hotword(name, cfg)
 AudioStart  ─────────────►   reset all active models       │
 AudioChunk* ─────────────►   HotWordEngine.update(chunk)   │
                           │   HotWordEngine.found_wake_word()│
 Detection   ◄─────────────   (if detected)                 │
 AudioStop   ─────────────►   (if no detection)             │
 NotDetected ◄─────────────   send NotDetected              │
                           └────────────────────────────────┘

```

**`OVOSWakeWordEventHandler`**

One instance per client connection. Maintains a dict of loaded `HotWordEngine` instances,
keyed by hotword name (lazy-loaded on first use). The connection is persistent — the
handler keeps running (`return True`) for continuous detection.

| Event type | Action |
|---|---|
| `Describe` | Send `Info` with all configured hotwords from `mycroft.conf["hotwords"]` |
| `Detect` | Update `active_detectors`, lazy-load requested models |
| `AudioStart` | Reset `_detection = False`, call `model.reset()` on all active models |
| `AudioChunk` | Convert audio, feed to each active `HotWordEngine.update()`, check `found_wake_word()`, send `Detection` if triggered |
| `AudioStop` | If no detection occurred, send `NotDetected` |

### Lazy model loading

Models are loaded the first time they are requested. Once loaded, they are cached for
the lifetime of the connection. All hotwords in `mycroft.conf["hotwords"]` are available;
clients select which to activate via the `Detect` event.

### Running

```bash
pip install wyoming-ovos-wakeword
wyoming-ovos-wakeword --uri tcp://0.0.0.0:7893

```

| Argument | Required | Default | Description |
|---|---|---|---|
| `--uri` | No | `stdio://` | `tcp://HOST:PORT` or `unix:///path/to/socket` |
| `--zeroconf` | No | disabled | Enable mDNS/zeroconf service discovery (optional: service name) |
| `--debug` | No | `False` | Enable DEBUG log level |

Examples:

```bash

# Standard TCP server
wyoming-ovos-wakeword --uri tcp://0.0.0.0:7893

# With zeroconf mDNS discovery (default service name)
wyoming-ovos-wakeword --uri tcp://0.0.0.0:7893 --zeroconf

# With custom zeroconf service name
wyoming-ovos-wakeword --uri tcp://0.0.0.0:7893 --zeroconf my-ovos-wakeword

```

> Zeroconf requires a `tcp://` URI.

### Configuration

Configuration is read entirely from `mycroft.conf`:

- `mycroft.conf["listener"]["wake_word"]` — default active wake word name (if no `Detect` event is sent)


- `mycroft.conf["hotwords"]` — dict of all configured hotword definitions

```json
{
  "listener": {
    "wake_word": "hey_mycroft"
  },
  "hotwords": {
    "hey_mycroft": {
      "module": "ovos-ww-plugin-precise-lite",
      "model": "https://github.com/OpenVoiceOS/precise-lite-models/raw/master/wakewords/en/hey_mycroft.tflite",
      "expected_duration": 3,
      "trigger_level": 3,
      "sensitivity": 0.5,
      "listen": true
    },
    "hey_mycroft_vosk": {
      "module": "ovos-ww-plugin-vosk",
      "samples": ["hey mycroft"],
      "rule": "fuzzy",
      "listen": true
    },
    "wake_up": {
      "module": "ovos-ww-plugin-vosk",
      "rule": "fuzzy",
      "samples": ["wake up"],
      "lang": "en-us",
      "wakeup": true
    }
  }
}

```

All configured hotwords are advertised via `Describe`/`Info` and are selectable by name.

### Wyoming message flow

```
Client → Describe
Server → Info(wake=[WakeProgram(models=[WakeModel(name="hey_mycroft", phrase="Hey Mycroft"), ...])])

Client → Detect(names=["hey_mycroft"])
Client → AudioStart(rate=16000, width=2, channels=1)
       → AudioChunk (raw PCM bytes)
       → AudioChunk ...
       → AudioStop
Server → Detection(name="hey_mycroft")   ← if detected

       | NotDetected                      ← if not detected

```

### Zeroconf / mDNS Discovery

When `--zeroconf` is passed, the bridge calls
`wyoming.zeroconf.register_server(name, port, host)` to announce itself on the local
network. Home Assistant and other Wyoming clients can discover the service automatically
without manual IP configuration.

---

## OVOS Plugin Types Used

| Bridge | Entry point group | Base class | Factory |
|---|---|---|---|
| STT | `opm.plugin.stt` | `ovos_plugin_manager.templates.stt.STT` | `OVOSSTTFactory` |
| TTS | `opm.plugin.tts` | `ovos_plugin_manager.templates.tts.TTS` | `OVOSTTSFactory` |
| Wake word | `opm.plugin.wake_word` | `ovos_plugin_manager.templates.hotwords.HotWordEngine` | `OVOSWakeWordFactory` |

All three bridges use `OVOSSTTFactory` / `OVOSTTSFactory` / `OVOSWakeWordFactory` from
`ovos-plugin-manager` for plugin discovery and instantiation. See
[Plugin Manager](plugin-manager.md) for the plugin packaging reference.

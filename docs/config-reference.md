# Configuration Reference

!!! abstract "In a nutshell"
    This is the settings catalog for OVOS — a lookup table of the main options you can adjust (your language, units, microphone, wake word, which speech and voice engines to use, and so on), with each option's default value and a short note on what it does. You don't need to set most of them; reach for this page when you want to find the name of a particular setting and what it controls. For how to actually apply these settings, see [Configuration Management](config.md); for unfamiliar terms see the [Glossary](glossary.md).

This page provides a comprehensive reference for the core configuration options in OpenVoiceOS. OVOS uses a layered configuration system, typically stored in `mycroft.conf`.

---

## 1. Core Settings

| Key | Default | Description |
|---|---|---|
| `lang` | `"en-us"` | Primary BCP-47 language code for STT and TTS. |
| `secondary_langs` | `[]` | Extra languages whose resource files are loaded; intents are only matched when the utterance is tagged with that lang at STT. |
| `system_unit` | `"metric"` | Measurement units (`metric` or `imperial`). |
| `temperature_unit`| `"celsius"`| Temperature units (`celsius` or `fahrenheit`). |
| `date_format` | `"MDY"` | Date format for display and parsing. |
| `time_format` | `"half"` | Clock format for display (`half` = 12-hour, `full` = 24-hour). |
| `confirm_listening`| `true` | Play a beep when the system starts listening. |

---

## 2. Intent Pipeline

The `intents.pipeline` defines the order in which matchers are evaluated.

```json
"intents": {
  "pipeline": [
    "ovos-stop-pipeline-plugin-high",
    "ovos-converse-pipeline-plugin",
    "ovos-ocp-pipeline-plugin-high",
    "ovos-padatious-pipeline-plugin-high",
    "ovos-adapt-pipeline-plugin-high",
    "ovos-m2v-pipeline-high",
    "ovos-fallback-pipeline-plugin-high"
  ]
}

```

### Adapt Settings

- `conf_high`: 0.65


- `conf_med`: 0.45


- `conf_low`: 0.25

### Padatious Settings

- `stem`: `false` (Use snowball stemmer)


- `cast_to_ascii`: `false` (Normalize to ASCII)

---

## 3. Listener & Microphone

All of these live under the top-level `listener` key:

| Key | Default | Description |
|---|---|---|
| `listener.sample_rate` | `16000` | Audio sampling rate in Hz. |
| `listener.fake_barge_in` | `true` | Mute output during recording. |
| `listener.recording_timeout`| `10.0` | Max seconds for a single recording. |
| `listener.remove_silence` | `true` | Strip leading/trailing silence before sending audio to STT. |
| `listener.wake_word` | `"hey_mycroft"` | Default hotword (matches an entry under `hotwords`). |

### Microphone Plugin

The microphone plugin is nested under `listener.microphone`:

```json
"listener": {
  "microphone": {
    "module": "ovos-microphone-plugin-alsa"
  }
}

```

---

## 4. Speech Activity (VAD)

The timing thresholds actually read by `ovos-dinkum-listener` to decide when a command
starts and ends are top-level `listener` keys (not nested under `VAD`):

| Key | Default | Description |
|---|---|---|
| `listener.speech_begin` | `0.3` | Seconds of detected speech before a command is considered started. |
| `listener.silence_end` | `0.7` | Seconds of silence before a command is considered ended. |

The shipped config also carries a `listener.VAD` block (`silence_method`, `speech_seconds`,
`silence_seconds`, plus a per-VAD-plugin `module`/fallback chain such as
`ovos-vad-plugin-silero` → `ovos-vad-plugin-precise` → `ovos-vad-plugin-webrtcvad` →
`ovos-vad-plugin-noise`) used to select and configure the [VAD plugin](vad-plugins.md)
itself — a separate concern from the `speech_begin`/`silence_end` timing above.

---

## 5. Plugin Selection

### STT (Speech-to-Text)

```json
"stt": {
  "module": "ovos-stt-plugin-server",
  "fallback_module": ""
}

```

### TTS (Text-to-Speech)

```json
"tts": {
  "module": "ovos-tts-plugin-server",
  "ovos-tts-plugin-mimic": {
    "voice": "ap"
  }
}

```

---

## 6. MessageBus (Websocket)

| Key | Default | Description |
|---|---|---|
| `host` | `"127.0.0.1"` | Host for the core MessageBus. |
| `port` | `8181` | Port for the core MessageBus. |
| `shared_connection`| `true` | If true, all skills share one websocket. |

---

*Source code: [OpenVoiceOS/ovos-config](https://github.com/OpenVoiceOS/ovos-config).*

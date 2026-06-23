# Configuration Reference

!!! abstract "In a nutshell"
    This is the settings catalog for OVOS — a lookup table of the main options you can adjust (your language, units, microphone, wake word, which speech and voice engines to use, and so on), with each option's default value and a short note on what it does. You don't need to set most of them; reach for this page when you want to find the name of a particular setting and what it controls. For how to actually apply these settings, see [Configuration Management](config.md); for unfamiliar terms see the [Glossary](glossary.md).

This page provides a comprehensive reference for the core configuration options in OpenVoiceOS. OVOS uses a layered configuration system, typically stored in `mycroft.conf`.

---

## 1. Core Settings

| Key | Default | Description |
|---|---|---|
| `lang` | `"en-US"` | Primary BCP-47 language code for STT and TTS. |
| `secondary_langs` | `[]` | Extra languages whose resource files are loaded; intents are only matched when the utterance is tagged with that lang at STT. |
| `system_unit` | `"metric"` | Measurement units (`metric` or `imperial`). |
| `temperature_unit`| `"celsius"`| Temperature units (`celsius` or `fahrenheit`). |
| `date_format` | `"MDY"` | Date format for display and parsing. |
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

| Key | Default | Description |
|---|---|---|
| `sample_rate` | `16000` | Audio sampling rate in Hz. |
| `fake_barge_in` | `true` | Mute output during recording. |
| `recording_timeout`| `10.0` | Max seconds for a single recording. |
| `remove_silence` | `true` | Strip leading/trailing silence before sending audio to STT. |
| `wake_word` | `"hey_mycroft"` | Default hotword (matches an entry under `hotwords`). |

### Microphone Plugin

```json
"microphone": {
  "module": "ovos-microphone-plugin-alsa"
}

```

---

## 4. Speech Activity (VAD)

| Key | Default | Description |
|---|---|---|
| `silence_method` | `"vad_and_ratio"` | VAD strategy (`VAD_ONLY`, `ALL`, etc.). |
| `speech_seconds` | `0.1` | Seconds of speech to trigger command start. |
| `silence_seconds`| `0.5` | Seconds of silence to trigger command end. |

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

# Wake Word Verifier Plugins

The wake word verifier framework lets one or more secondary plugins inspect the audio captured during a wake-word detection event and veto false triggers. This is separate from the detection plugin itself and runs as a post-detection gate.

OPM interface: [OpenVoiceOS/ovos-plugin-manager#341](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/341) (merged).  
Listener integration: [OpenVoiceOS/ovos-dinkum-listener#191](https://github.com/OpenVoiceOS/ovos-dinkum-listener/pull/191) (open).

---

## Pre-Wake VAD

Before the wake word detector even fires, an optional VAD gate can filter frames that are clearly silent, reducing the detection surface for false activations.

Source: [OpenVoiceOS/ovos-dinkum-listener#189](https://github.com/OpenVoiceOS/ovos-dinkum-listener/pull/189) (merged).

```json
{
  "listener": {
    "vad_pre_wake_enabled": true
  }
}
```

When enabled, audio frames pass through the configured VAD plugin before reaching the wake word model. A 5-second fallback returns the listener to the pre-wake VAD state if no wake word is detected.

---

## Verifier Configuration

```json
{
  "listener": {
    "ww_verifiers": {
      "ovos-ww-verifier-silero": {"threshold": 0.1}
    },
    "vad_pre_wake_enabled": false
  }
}
```

Multiple verifiers can be listed; a detection is accepted only if all verifiers pass. Combine either `ww_verifiers` or `vad_pre_wake_enabled` — enabling both is redundant.

---

## OPM Verifier Interface

```python
from ovos_plugin_manager.templates.hotwords import HotWordVerifier

class MyVerifier(HotWordVerifier):
    def verify(self, audio_data: bytes) -> bool:
        """Return True to accept the detection, False to veto it."""
        ...
```

Plugin entry point group: `opm.ww.verifier`.

```python
# pyproject.toml
[project.entry-points."opm.ww.verifier"]
my-verifier = "my_package:MyVerifier"
```

---

## Silero Verifier

The reference verifier wraps the Silero VAD model to confirm that captured audio contains actual speech, not silence or transient noise:

```json
{
  "listener": {
    "ww_verifiers": {
      "ovos-ww-verifier-silero": {"threshold": 0.1}
    }
  }
}
```

A lower `threshold` accepts quieter speech; raise it to require stronger speech confidence.

---

## Speaker Verification

[TigreGotico/speakeronnx](https://github.com/TigreGotico/speakeronnx) is a pure-`onnxruntime` speaker embedding library (wespeaker resnet34 and ecapa512 models, cc-by-4.0; more model integrations tracked in its issues). The companion plugin `ovos-ww-verifier-plugin-speaker` gates wake-word detections against enrolled household profiles — only recognized household members can activate the assistant; guests are silently ignored. With no profiles enrolled the verifier fails open (everyone allowed).

Enrollment is a one-time CLI step per person:

```bash
ovos-speaker-enroll Alice clip1.wav clip2.wav clip3.wav
```

Profiles are stored as embedding vectors in `~/.local/share/ovos_speaker_verifier/profiles.json` — no audio is retained. Configuration:

```json
{
  "model": "wespeaker-resnet34",
  "threshold": 0.45
}
```

Use case: household authorization — a shared-wake-word deployment where each registered user's voice profile allows or denies activation.

---

## Precise-ONNX Plugin

`ovos-ww-plugin-precise-onnx` provides high-accuracy wake word detection from `.onnx` model files, without TensorFlow Lite dependency.

```json
{
  "hotwords": {
    "hey_mycroft": {
      "module": "ovos-ww-plugin-precise-onnx",
      "model": "https://github.com/OpenVoiceOS/precise-lite-models/raw/master/wakewords/en/hey_mycroft.onnx",
      "trigger_level": 3,
      "sensitivity": 0.5
    }
  }
}
```

---

## microWakeWord Plugin

> **Status:** [TigreGotico/ovos-ww-plugin-microwakeword](https://github.com/TigreGotico/ovos-ww-plugin-microwakeword) — private, in development.

OVOS wake-word plugin wrapping [microWakeWord](https://github.com/kahrendt/microWakeWord) TFLite streaming models from the ESPHome ecosystem. Enables zero-cost sub-1 MB wake word models originally designed for microcontrollers.

---

## Synthetic Dataset Generation and ww-trainer

The [ww-trainer](https://github.com/TigreGotico/ww-trainer) toolkit provides:

- **Synthetic audio generation** — text-to-speech augmentation to bootstrap wake word training data.
- **Single-run training** — train a Precise or microWakeWord compatible model from labeled audio.
- **Genetic hyperparameter search** — automated architecture search.
- **ONNX export** — produce deployment-ready `.onnx` model files compatible with `ovos-ww-plugin-precise-onnx`.
- **Live inference testing** — verify a trained model against the microphone in real time.

---

## Related Pages

- [Wake Word Plugins](wake-word-plugins.md) — detection plugin reference
- [VAD Plugins](vad-plugins.md)
- [Listener / Speech Service](speech-service.md)

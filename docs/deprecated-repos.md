# Deprecated & Archived Repositories

!!! abstract "In a nutshell"
    This page is a reference list of old OVOS code projects that are no longer maintained, together with what replaced each one. It exists so that if you run into an old package name or an out-of-date guide online, you can look it up here, see that it has been retired, and find the current thing to use instead. You do not need to read it top to bottom — treat it as a lookup table. See the [Glossary](glossary.md) for terms.

!!! warning "These repositories are archived"
    The repositories below are **archived** in the [OpenVoiceOS GitHub organization](https://github.com/OpenVoiceOS) — they are read-only and no longer maintained. They are listed here so you can recognise them and find the current replacement. Do **not** start new work against them.

There are roughly **84** archived repositories (the exact count drifts as more get archived). They are grouped by area below; each row gives the reason and the current replacement where one exists.


## Backend services (removed architecture) (5)

*OVOS no longer uses a central backend; these are removed, not replaced.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-backend-client](https://github.com/OpenVoiceOS/ovos-backend-client) | client library for interaction with all compatible ovos-core backend services | Removed — OVOS is backendless |
| [ovos-backend-manager](https://github.com/OpenVoiceOS/ovos-backend-manager) | A simple web UI for personal backend, powered by PyWebIO | Removed — OVOS is backendless |
| [ovos-binary-shop](https://github.com/OpenVoiceOS/ovos-binary-shop) | Wheels and pre-compiled binaries for usage with ovos plugins / images | Removed — wheels are published on PyPI |
| [ovos-personal-backend](https://github.com/OpenVoiceOS/ovos-personal-backend) | personal backend - self-hosted backend to manage multiple OVOS devices | Removed — OVOS is backendless |
| [ovos-stt-plugin-selene](https://github.com/OpenVoiceOS/ovos-stt-plugin-selene) | STT plugin to use selene backend services | Removed — OVOS is backendless |

## Skills (renamed, or folded into pipelines/services) (11)

*Old Mycroft-era skills; most were renamed `skill-ovos-*` → `ovos-skill-*` or folded into core pipelines.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-skill-fallback-chatgpt](https://github.com/OpenVoiceOS/ovos-skill-fallback-chatgpt) | — | [ovos-persona](https://github.com/OpenVoiceOS/ovos-persona) |
| [ovos-skills](https://github.com/OpenVoiceOS/ovos-skills) | ovos-core metapackage for skills daemon | ovos-core (skills run in-process) |
| [skill-homescreen-lite](https://github.com/OpenVoiceOS/skill-homescreen-lite) | Minimal homescreen for remote client devices | [ovos-skill-homescreen](https://github.com/OpenVoiceOS/ovos-skill-homescreen) |
| [skill-ovos-alarm](https://github.com/OpenVoiceOS/skill-ovos-alarm) | Mycroft AI Alarm Skill - Set single and recurring alarms, with a choice of alarm sounds | [ovos-skill-alerts](https://github.com/OpenVoiceOS/ovos-skill-alerts) |
| [skill-ovos-common-play](https://github.com/OpenVoiceOS/skill-ovos-common-play) | Mycroft AI official Playback Control Skill - providing Intents for other Skills to use common playback functionality (via Common Play) | OCP pipeline (ovos-ocp-pipeline-plugin) |
| [skill-ovos-common-query](https://github.com/OpenVoiceOS/skill-ovos-common-query) | Skill Negotiating for the best source for an answer via Common QA | [ovos-common-query-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-common-query-pipeline-plugin) |
| [skill-ovos-mycroftgui](https://github.com/OpenVoiceOS/skill-ovos-mycroftgui) | Mycroft skill to take control of the Mycroft GUI QT application. | GUI rework (ovos-gui) |
| [skill-ovos-settings](https://github.com/OpenVoiceOS/skill-ovos-settings) | Mycroft skill to take control of OpenVoiceOS it's functions and tools. | GUI rework — [pyhtmx-gui-client](https://github.com/OpenVoiceOS/pyhtmx-gui-client) |
| [skill-ovos-setup](https://github.com/OpenVoiceOS/skill-ovos-setup) | OpenVoiceOS Setup Skill - configure your device and optionally connect it to a backend server | Removed — OVOS is backendless; onboarding via ovos-installer |
| [skill-ovos-stop](https://github.com/OpenVoiceOS/skill-ovos-stop) | stop whatever the assistant is doing | Stop pipeline (ovos-stop-pipeline-plugin) |
| [skill-ovos-timer](https://github.com/OpenVoiceOS/skill-ovos-timer) | Timer Skill | [ovos-skill-alerts](https://github.com/OpenVoiceOS/ovos-skill-alerts) |

## STT plugins (5)

*Superseded STT engines.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-stt-plugin-HiTZ](https://github.com/OpenVoiceOS/ovos-stt-plugin-HiTZ) | — | [ovos-stt-plugin-onnx-asr](https://github.com/TigreGotico/ovos-stt-plugin-onnx-asr) |
| [ovos-stt-plugin-fasterwhisper-zuazo](https://github.com/OpenVoiceOS/ovos-stt-plugin-fasterwhisper-zuazo) | — | [ovos-stt-plugin-fasterwhisper](https://github.com/OpenVoiceOS/ovos-stt-plugin-fasterwhisper) |
| [ovos-stt-plugin-mms](https://github.com/OpenVoiceOS/ovos-stt-plugin-mms) | — | [ovos-stt-plugin-wav2vec2](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec2) |
| [ovos-stt-plugin-nos](https://github.com/OpenVoiceOS/ovos-stt-plugin-nos) | — | [ovos-stt-plugin-wav2vec2](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec2) |
| [ovos-stt-plugin-projectAINA-remote](https://github.com/OpenVoiceOS/ovos-stt-plugin-projectAINA-remote) | — | Remote demo server is gone, but it served a Catalan **Whisper** model — run that model locally with [ovos-stt-plugin-fasterwhisper](https://github.com/OpenVoiceOS/ovos-stt-plugin-fasterwhisper) or [ovos-stt-plugin-whisper](https://github.com/OpenVoiceOS/ovos-stt-plugin-whisper) |

## TTS plugins (7)

*Superseded TTS engines.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-tts-plugin-cotovia-remote](https://github.com/OpenVoiceOS/ovos-tts-plugin-cotovia-remote) | — | Removed — unofficial demo server, now gone; no replacement |
| [ovos-tts-plugin-matxa-multispeaker-cat](https://github.com/OpenVoiceOS/ovos-tts-plugin-matxa-multispeaker-cat) | — | [phoonnx](https://github.com/TigreGotico/phoonnx) — runs the same Matxa Catalan models |
| [ovos-tts-plugin-mimic2](https://github.com/OpenVoiceOS/ovos-tts-plugin-mimic2) | — | Removed — proprietary cloud-hosted Tacotron model, never released. The `kusal` voice in [phoonnx](https://github.com/TigreGotico/phoonnx) was trained on the same dataset and can be used instead. |
| [ovos-tts-plugin-mimic3](https://github.com/OpenVoiceOS/ovos-tts-plugin-mimic3) | Text to speech plugin for OVOS using Mimic 3 | [phoonnx](https://github.com/TigreGotico/phoonnx) — directly supports the Mimic3 voices (as it does Larynx and Piper voices) |
| [ovos-tts-plugin-mimic3-server](https://github.com/OpenVoiceOS/ovos-tts-plugin-mimic3-server) | — | The Mimic3 server API is gone, but [phoonnx](https://github.com/TigreGotico/phoonnx) runs the Mimic3 voices directly |
| [ovos-tts-plugin-nos](https://github.com/OpenVoiceOS/ovos-tts-plugin-nos) | Galician TTS | [phoonnx](https://github.com/TigreGotico/phoonnx) — runs the Proxecto Nós Galician voices |
| [ovos-tts-plugin-piper](https://github.com/OpenVoiceOS/ovos-tts-plugin-piper) | — | [phoonnx](https://github.com/TigreGotico/phoonnx) — runs Piper ONNX voices (incl. the `kusal` voice) |

## Wake-word & VAD plugins (9)

*Older wake-word/VAD engines; the Precise family is superseded by the ONNX build.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-vad-plugin-precise](https://github.com/OpenVoiceOS/ovos-vad-plugin-precise) | tflite GRU VAD detector | [ovos-vad-plugin-silero](https://github.com/OpenVoiceOS/ovos-vad-plugin-silero) |
| [ovos-ww-plugin-nyumaya-legacy](https://github.com/OpenVoiceOS/ovos-ww-plugin-nyumaya-legacy) | hotword plugin for mycroft-core | Removed — use [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx) / openWakeWord |
| [ovos-ww-plugin-pocketsphinx](https://github.com/OpenVoiceOS/ovos-ww-plugin-pocketsphinx) | OpenVoiceOS plugin for detecting wakewords with pocketsphinx | [ovos-ww-plugin-vosk](https://github.com/OpenVoiceOS/ovos-ww-plugin-vosk) |
| [ovos-ww-plugin-precise](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise) | mycroft plugin for detecting wake word with precise | [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx) |
| [ovos-ww-plugin-precise-lite](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-lite) | — | [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx) |
| [ovos-ww-plugin-snowboy](https://github.com/OpenVoiceOS/ovos-ww-plugin-snowboy) | snowboy plugin for mycroft | Removed — use [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx) / openWakeWord |
| [precise-lite](https://github.com/OpenVoiceOS/precise-lite) | A lightweight, simple-to-use, RNN wake word listener | [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx) |
| [precise-lite-trainer](https://github.com/OpenVoiceOS/precise-lite-trainer) | train wake word models | [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx) |
| [precise_lite_runner](https://github.com/OpenVoiceOS/precise_lite_runner) | — | [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx) |

## PHAL & GUI plugins (16)

*Hardware/GUI plugins superseded by the current PHAL set or the GUI rework.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ZZZ-ovos_enclosure](https://github.com/OpenVoiceOS/ZZZ-ovos_enclosure) | Enclosure module | [ovos-PHAL](https://github.com/OpenVoiceOS/ovos-PHAL) |
| [mycroft-gui-qt5](https://github.com/OpenVoiceOS/mycroft-gui-qt5) | maintained version of the old QT5 mycroft-gui for OpenVoiceOS | [mycroft-gui-qt6](https://github.com/OpenVoiceOS/mycroft-gui-qt6) |
| [ovos-PHAL-plugin-balena-wifi](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-balena-wifi) | — | [ovos-PHAL-plugin-network-manager](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-network-manager) |
| [ovos-PHAL-plugin-brightness-control-rpi](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-brightness-control-rpi) | — | GUI rework — [pyhtmx-gui-client](https://github.com/OpenVoiceOS/pyhtmx-gui-client) |
| [ovos-PHAL-plugin-color-scheme-manager](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-color-scheme-manager) | OVOS Shell ColorScheme Manager Plugin for OVOS PHAL | GUI rework — [pyhtmx-gui-client](https://github.com/OpenVoiceOS/pyhtmx-gui-client) |
| [ovos-PHAL-plugin-configuration-provider](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-configuration-provider) | PHAL plugin to provide configuration in displayable GUI format | GUI rework — [pyhtmx-gui-client](https://github.com/OpenVoiceOS/pyhtmx-gui-client) |
| [ovos-PHAL-plugin-dashboard](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-dashboard) | Dashboard PHAL plugin to handle Dashboard operations | Removed — community-maintained, no official replacement |
| [ovos-PHAL-plugin-display-manager-ipc](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-display-manager-ipc) | — | Removed — folded into [ovos-gui](https://github.com/OpenVoiceOS/ovos-gui) |
| [ovos-PHAL-plugin-gui-network-client](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-gui-network-client) | A GUI Network Client For PHAL | [ovos-PHAL-plugin-network-manager](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-network-manager) |
| [ovos-PHAL-plugin-homeassistant](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-homeassistant) | HomeAssistant PHAL Plugin for OpenVoice OS | Removed — use a dedicated Home Assistant skill (e.g. OscillateLabsLLC/skill-homeassistant) |
| [ovos-PHAL-plugin-mk2](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk2) | — | [ovos-PHAL-plugin-mk2-v6-fan-control](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk2-v6-fan-control) |
| [ovos-PHAL-plugin-notification-widgets](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-notification-widgets) | Notifications and Widgets PHAL plugin | GUI rework — [pyhtmx-gui-client](https://github.com/OpenVoiceOS/pyhtmx-gui-client) |
| [ovos-PHAL-plugin-wifi-setup](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-wifi-setup) | Central Wifi Setup Plugin for PHAL | [ovos-PHAL-plugin-network-manager](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-network-manager) |
| [ovos-gui-plugin-shell-companion](https://github.com/OpenVoiceOS/ovos-gui-plugin-shell-companion) | — | GUI rework — [pyhtmx-gui-client](https://github.com/OpenVoiceOS/pyhtmx-gui-client) |
| [ovos-media-plugin-qt5](https://github.com/OpenVoiceOS/ovos-media-plugin-qt5) | default GUI implementation for OCP framework | GUI rework (ovos-gui adapters) |
| [ovos-shell](https://github.com/OpenVoiceOS/ovos-shell) | — | GUI rework — [pyhtmx-gui-client](https://github.com/OpenVoiceOS/pyhtmx-gui-client) |

## Core, libraries & tooling (9)

*Old metapackages/utilities, merged elsewhere or retired.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-classifiers](https://github.com/OpenVoiceOS/ovos-classifiers) | — | Removed — split into focused libs (ovos-utterance-normalizer, ovos-lang-detector-*, ovos-*-parser) |
| [ovos-cli-client](https://github.com/OpenVoiceOS/ovos-cli-client) | — | Removed — use messagebus tooling (ovos-busmon) |
| [ovos-listener](https://github.com/OpenVoiceOS/ovos-listener) | ovos-core metapackage for speech daemon | [ovos-dinkum-listener](https://github.com/OpenVoiceOS/ovos-dinkum-listener) |
| [ovos-translate-plugin-deepl](https://github.com/OpenVoiceOS/ovos-translate-plugin-deepl) | — | [ovos-translate-plugin-nllb](https://github.com/OpenVoiceOS/ovos-translate-plugin-nllb) |
| [ovos-translations](https://github.com/OpenVoiceOS/ovos-translations) | — | [ovos-localize](https://github.com/OpenVoiceOS/ovos-localize) |
| [ovos_skill_installer](https://github.com/OpenVoiceOS/ovos_skill_installer) | A package extraction tool for Python | ovos-core / ovos-workshop |
| [ovos_skill_manager](https://github.com/OpenVoiceOS/ovos_skill_manager) | skill installer for OVOS | ovos-core / ovos-workshop |
| [ovos-lingua-franca](https://github.com/OpenVoiceOS/ovos-lingua-franca) | Mycroft's multilingual text parsing and formatting library | Split into focused libraries — [ovos-date-parser](https://github.com/OpenVoiceOS/ovos-date-parser), [ovos-number-parser](https://github.com/OpenVoiceOS/ovos-number-parser), and the other `ovos-*-parser` packages |
| [zzz-old-ovos-utils](https://github.com/OpenVoiceOS/zzz-old-ovos-utils) | collection of simple utilities for use across the mycroft ecosystem | [ovos-utils](https://github.com/OpenVoiceOS/ovos-utils) |

## Datasets, lists & images (8)

*Reference/data repos kept for history.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ZZZ-raspOVOS](https://github.com/OpenVoiceOS/ZZZ-raspOVOS) | Run ovos ontop of RaspberryPiOS | [raspOVOS](https://github.com/OpenVoiceOS/raspOVOS) — the current, actively maintained image |
| [awesome-ocp-skills](https://github.com/OpenVoiceOS/awesome-ocp-skills) | Media skills for OCP, music, movies, radio, audiobooks and more! | [OVOS-skills-store](https://github.com/OpenVoiceOS/OVOS-skills-store) |
| [awesome-ovos-plugins](https://github.com/OpenVoiceOS/awesome-ovos-plugins) | List of ovos-plugin-manager plugins and projects | [OVOS-skills-store](https://github.com/OpenVoiceOS/OVOS-skills-store) |
| [big-tts-cache](https://github.com/OpenVoiceOS/big-tts-cache) | cached utterances from the defunct mimic2 TTS from Mycroft AI | Removed (mimic2 retired) |
| [lang-support-tracker](https://github.com/OpenVoiceOS/lang-support-tracker) | — | [ovos-localize](https://github.com/OpenVoiceOS/ovos-localize) |
| [ovos-gitlocalize-intent-dataset](https://github.com/OpenVoiceOS/ovos-gitlocalize-intent-dataset) | — | [ovos-localize](https://github.com/OpenVoiceOS/ovos-localize) |
| [ovos-ww-auto-synth-dataset](https://github.com/OpenVoiceOS/ovos-ww-auto-synth-dataset) | — | [ovos-ww-community-dataset](https://github.com/OpenVoiceOS/ovos-ww-community-dataset) |
| [raspovos-manual](https://github.com/OpenVoiceOS/raspovos-manual) | User manual for the raspOVOS image | raspOVOS README / ovos-installer |

## Test, template & internal repos (14)

*Scaffolding/test/dummy repos, not user-facing.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [disable-msm-dummy-repo](https://github.com/OpenVoiceOS/disable-msm-dummy-repo) | A repository for sharing and collaboration for third-party Mycroft skills development. | Removed — MSM (Mycroft Skills Manager) test artifact |
| [hardware-mycroft-mark-1](https://github.com/OpenVoiceOS/hardware-mycroft-mark-1) | in-case-of-apocalypse archive of Mycroft Mark 1 repository | historical archive |
| [my-assistant](https://github.com/OpenVoiceOS/my-assistant) | template repo for derivative voice assistants | Removed — old assistant template scaffold |
| [ovos-skills-info](https://github.com/OpenVoiceOS/ovos-skills-info) | Skill information parser support skill | Removed — skill metadata folded into ovos-workshop |
| [ovos-solver-YesNo-plugin](https://github.com/OpenVoiceOS/ovos-solver-YesNo-plugin) | — | [ovos-YesNo-plugin](https://github.com/OpenVoiceOS/ovos-YesNo-plugin) (needs ovos-plugin-manager>=2.4.0) |
| [quiet.py](https://github.com/OpenVoiceOS/quiet.py) | Python Ctypes Bindings for libquiet | Removed — use [ovos-audio-transformer-plugin-ggwave](https://github.com/OpenVoiceOS/ovos-audio-transformer-plugin-ggwave) |
| [skill-abort-test](https://github.com/OpenVoiceOS/skill-abort-test) | internal test skill for an `ovos_utils` change | Removed — internal test skill |
| [skill-balena-wifi-setup](https://github.com/OpenVoiceOS/skill-balena-wifi-setup) | — | [ovos-PHAL-plugin-network-manager](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-network-manager) |
| [skill-monkey-patch-tester](https://github.com/OpenVoiceOS/skill-monkey-patch-tester) | test monkey patches | Removed — internal test skill |
| [skill-monkey-patcher](https://github.com/OpenVoiceOS/skill-monkey-patcher) | apply patches to mycroft-core at runtime | Removed — mycroft-core runtime patcher; no replacement |
| [skill-template-repo](https://github.com/OpenVoiceOS/skill-template-repo) | — | [ovos-skill-hello-world](https://github.com/OpenVoiceOS/ovos-skill-hello-world) |
| [template-package-repo](https://github.com/OpenVoiceOS/template-package-repo) | — | Removed — use [gh-automations](https://github.com/OpenVoiceOS/gh-automations) shared workflows |
| [tskill-ocp-cps](https://github.com/OpenVoiceOS/tskill-ocp-cps) | — | Removed — internal test skill |
| [tskill-osm_parsing](https://github.com/OpenVoiceOS/tskill-osm_parsing) | Repository to test OSM parser testing | Removed — internal test skill |

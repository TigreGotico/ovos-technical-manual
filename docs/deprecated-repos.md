# Deprecated & Archived Repositories

!!! warning "These repositories are archived"
    The repositories below are **archived** in the [OpenVoiceOS GitHub organization](https://github.com/OpenVoiceOS) — they are read-only and no longer maintained. They are listed here so you can recognise them and find the current replacement. Do **not** start new work against them.

There are **83** archived repositories. They are grouped by area below; each row gives the reason and the current replacement where one exists.


## Backend services (removed architecture) (5)

*OVOS no longer uses a central backend; these are removed, not replaced.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-backend-client](https://github.com/OpenVoiceOS/ovos-backend-client) | client library for interaction with all compatible ovos-core backend services | Removed — OVOS is backendless |
| [ovos-backend-manager](https://github.com/OpenVoiceOS/ovos-backend-manager) | A simple web UI for personal backend, powered by PyWebIO | Removed — OVOS is backendless |
| [ovos-binary-shop](https://github.com/OpenVoiceOS/ovos-binary-shop) | Wheels and pre-compiled binaries for usage with ovos plugins / images | — |
| [ovos-personal-backend](https://github.com/OpenVoiceOS/ovos-personal-backend) | personal backend - self-hosted backend to manage multiple OVOS devices | Removed — OVOS is backendless |
| [ovos-stt-plugin-selene](https://github.com/OpenVoiceOS/ovos-stt-plugin-selene) | STT plugin to use selene backend services | Removed — OVOS is backendless |

## Skills (renamed, or folded into pipelines/services) (11)

*Old Mycroft-era skills; most were renamed `skill-ovos-*` → `ovos-skill-*` or folded into core pipelines.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-skill-fallback-chatgpt](https://github.com/OpenVoiceOS/ovos-skill-fallback-chatgpt) | — | — |
| [ovos-skills](https://github.com/OpenVoiceOS/ovos-skills) | ovos-core metapackage for skills daemon | ovos-core (skills run in-process) |
| [skill-homescreen-lite](https://github.com/OpenVoiceOS/skill-homescreen-lite) | Minimal homescreen for remote client devices | [ovos-skill-homescreen](https://github.com/OpenVoiceOS/ovos-skill-homescreen) |
| [skill-ovos-alarm](https://github.com/OpenVoiceOS/skill-ovos-alarm) | Mycroft AI Alarm Skill - Set single and recurring alarms, with a choice of alarm sounds | [ovos-skill-alerts](https://github.com/OpenVoiceOS/ovos-skill-alerts) |
| [skill-ovos-common-play](https://github.com/OpenVoiceOS/skill-ovos-common-play) | Mycroft AI official Playback Control Skill - providing Intents for other Skills to use common playback functionality (via Common Play) | OCP pipeline (ovos-ocp-pipeline-plugin) |
| [skill-ovos-common-query](https://github.com/OpenVoiceOS/skill-ovos-common-query) | Skill Negotiating for the best source for an answer via Common QA | [ovos-common-query-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-common-query-pipeline-plugin) |
| [skill-ovos-mycroftgui](https://github.com/OpenVoiceOS/skill-ovos-mycroftgui) | Mycroft skill to take control of the Mycroft GUI QT application. | GUI rework (ovos-gui) |
| [skill-ovos-settings](https://github.com/OpenVoiceOS/skill-ovos-settings) | Mycroft skill to take control of OpenVoiceOS it's functions and tools. | — |
| [skill-ovos-setup](https://github.com/OpenVoiceOS/skill-ovos-setup) | OpenVoiceOS Setup Skill - configure your device and optionally connect it to a backend server | — |
| [skill-ovos-stop](https://github.com/OpenVoiceOS/skill-ovos-stop) | stop whatever the assistant is doing | Stop pipeline (ovos-stop-pipeline-plugin) |
| [skill-ovos-timer](https://github.com/OpenVoiceOS/skill-ovos-timer) | Timer Skill | — |

## STT plugins (5)

*Superseded STT engines.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-stt-plugin-HiTZ](https://github.com/OpenVoiceOS/ovos-stt-plugin-HiTZ) | — | — |
| [ovos-stt-plugin-fasterwhisper-zuazo](https://github.com/OpenVoiceOS/ovos-stt-plugin-fasterwhisper-zuazo) | — | [ovos-stt-plugin-fasterwhisper](https://github.com/OpenVoiceOS/ovos-stt-plugin-fasterwhisper) |
| [ovos-stt-plugin-mms](https://github.com/OpenVoiceOS/ovos-stt-plugin-mms) | — | — |
| [ovos-stt-plugin-nos](https://github.com/OpenVoiceOS/ovos-stt-plugin-nos) | — | [ovos-stt-plugin-wav2vec2](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec2) |
| [ovos-stt-plugin-projectAINA-remote](https://github.com/OpenVoiceOS/ovos-stt-plugin-projectAINA-remote) | — | — |

## TTS plugins (7)

*Superseded TTS engines.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-tts-plugin-cotovia-remote](https://github.com/OpenVoiceOS/ovos-tts-plugin-cotovia-remote) | — | — |
| [ovos-tts-plugin-matxa-multispeaker-cat](https://github.com/OpenVoiceOS/ovos-tts-plugin-matxa-multispeaker-cat) | — | — |
| [ovos-tts-plugin-mimic2](https://github.com/OpenVoiceOS/ovos-tts-plugin-mimic2) | — | [ovos-tts-plugin-piper](https://github.com/OpenVoiceOS/ovos-tts-plugin-piper) |
| [ovos-tts-plugin-mimic3](https://github.com/OpenVoiceOS/ovos-tts-plugin-mimic3) | Text to speech plugin for OVOS using Mimic 3 | [ovos-tts-plugin-piper](https://github.com/OpenVoiceOS/ovos-tts-plugin-piper) |
| [ovos-tts-plugin-mimic3-server](https://github.com/OpenVoiceOS/ovos-tts-plugin-mimic3-server) | — | [ovos-tts-plugin-piper](https://github.com/OpenVoiceOS/ovos-tts-plugin-piper) |
| [ovos-tts-plugin-nos](https://github.com/OpenVoiceOS/ovos-tts-plugin-nos) | Galician TTS | — |
| [ovos-tts-plugin-piper](https://github.com/OpenVoiceOS/ovos-tts-plugin-piper) | — | — |

## Wake-word & VAD plugins (9)

*Older wake-word/VAD engines; the Precise family is superseded by the ONNX build.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-vad-plugin-precise](https://github.com/OpenVoiceOS/ovos-vad-plugin-precise) | tflite GRU VAD detector | — |
| [ovos-ww-plugin-nyumaya-legacy](https://github.com/OpenVoiceOS/ovos-ww-plugin-nyumaya-legacy) | hotword plugin for mycroft-core | — |
| [ovos-ww-plugin-pocketsphinx](https://github.com/OpenVoiceOS/ovos-ww-plugin-pocketsphinx) | OpenVoiceOS plugin for detecting wakewords with pocketsphinx | — |
| [ovos-ww-plugin-precise](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise) | mycroft plugin for detecting wake word with precise | [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx) |
| [ovos-ww-plugin-precise-lite](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-lite) | — | [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx) |
| [ovos-ww-plugin-snowboy](https://github.com/OpenVoiceOS/ovos-ww-plugin-snowboy) | snowboy plugin for mycroft | — |
| [precise-lite](https://github.com/OpenVoiceOS/precise-lite) | A lightweight, simple-to-use, RNN wake word listener | [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx) |
| [precise-lite-trainer](https://github.com/OpenVoiceOS/precise-lite-trainer) | train wake word models | [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx) |
| [precise_lite_runner](https://github.com/OpenVoiceOS/precise_lite_runner) | — | [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx) |

## PHAL & GUI plugins (16)

*Hardware/GUI plugins superseded by the current PHAL set or the GUI rework.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ZZZ-ovos_enclosure](https://github.com/OpenVoiceOS/ZZZ-ovos_enclosure) | Enclosure module | [ovos-PHAL](https://github.com/OpenVoiceOS/ovos-PHAL) |
| [mycroft-gui-qt5](https://github.com/OpenVoiceOS/mycroft-gui-qt5) | maintained version of the old QT5 mycroft-gui for OpenVoiceOS | [mycroft-gui-qt6](https://github.com/OpenVoiceOS/mycroft-gui-qt6) |
| [ovos-PHAL-plugin-balena-wifi](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-balena-wifi) | — | — |
| [ovos-PHAL-plugin-brightness-control-rpi](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-brightness-control-rpi) | — | — |
| [ovos-PHAL-plugin-color-scheme-manager](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-color-scheme-manager) | OVOS Shell ColorScheme Manager Plugin for OVOS PHAL | — |
| [ovos-PHAL-plugin-configuration-provider](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-configuration-provider) | PHAL plugin to provide configuration in displayable GUI format | — |
| [ovos-PHAL-plugin-dashboard](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-dashboard) | Dashboard PHAL plugin to handle Dashboard operations | — |
| [ovos-PHAL-plugin-display-manager-ipc](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-display-manager-ipc) | — | — |
| [ovos-PHAL-plugin-gui-network-client](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-gui-network-client) | A GUI Network Client For PHAL | — |
| [ovos-PHAL-plugin-homeassistant](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-homeassistant) | HomeAssistant PHAL Plugin for OpenVoice OS | — |
| [ovos-PHAL-plugin-mk2](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk2) | — | — |
| [ovos-PHAL-plugin-notification-widgets](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-notification-widgets) | Notifications and Widgets PHAL plugin | — |
| [ovos-PHAL-plugin-wifi-setup](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-wifi-setup) | Central Wifi Setup Plugin for PHAL | — |
| [ovos-gui-plugin-shell-companion](https://github.com/OpenVoiceOS/ovos-gui-plugin-shell-companion) | — | — |
| [ovos-media-plugin-qt5](https://github.com/OpenVoiceOS/ovos-media-plugin-qt5) | default GUI implementation for OCP framework | GUI rework (ovos-gui adapters) |
| [ovos-shell](https://github.com/OpenVoiceOS/ovos-shell) | — | — |

## Core, libraries & tooling (8)

*Old metapackages/utilities, merged elsewhere or retired.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-classifiers](https://github.com/OpenVoiceOS/ovos-classifiers) | — | — |
| [ovos-cli-client](https://github.com/OpenVoiceOS/ovos-cli-client) | — | — |
| [ovos-listener](https://github.com/OpenVoiceOS/ovos-listener) | ovos-core metapackage for speech daemon | [ovos-dinkum-listener](https://github.com/OpenVoiceOS/ovos-dinkum-listener) |
| [ovos-translate-plugin-deepl](https://github.com/OpenVoiceOS/ovos-translate-plugin-deepl) | — | — |
| [ovos-translations](https://github.com/OpenVoiceOS/ovos-translations) | — | [ovos-localize](https://github.com/OpenVoiceOS/ovos-localize) |
| [ovos_skill_installer](https://github.com/OpenVoiceOS/ovos_skill_installer) | A package extraction tool for Python | ovos-core / ovos-workshop |
| [ovos_skill_manager](https://github.com/OpenVoiceOS/ovos_skill_manager) | skill installer for OVOS | ovos-core / ovos-workshop |
| [zzz-old-ovos-utils](https://github.com/OpenVoiceOS/zzz-old-ovos-utils) | collection of simple utilities for use across the mycroft ecosystem | [ovos-utils](https://github.com/OpenVoiceOS/ovos-utils) |

## Datasets, lists & images (8)

*Reference/data repos kept for history.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ZZZ-raspOVOS](https://github.com/OpenVoiceOS/ZZZ-raspOVOS) | Run ovos ontop of RaspberryPiOS | raspOVOS (itself now deprecated) |
| [awesome-ocp-skills](https://github.com/OpenVoiceOS/awesome-ocp-skills) | Media skills for OCP, music, movies, radio, audiobooks and more! | — |
| [awesome-ovos-plugins](https://github.com/OpenVoiceOS/awesome-ovos-plugins) | List of ovos-plugin-manager plugins and projects | — |
| [big-tts-cache](https://github.com/OpenVoiceOS/big-tts-cache) | cached utterances from the defunct mimic2 TTS from Mycroft AI | Removed (mimic2 retired) |
| [lang-support-tracker](https://github.com/OpenVoiceOS/lang-support-tracker) | — | [ovos-localize](https://github.com/OpenVoiceOS/ovos-localize) |
| [ovos-gitlocalize-intent-dataset](https://github.com/OpenVoiceOS/ovos-gitlocalize-intent-dataset) | — | [ovos-localize](https://github.com/OpenVoiceOS/ovos-localize) |
| [ovos-ww-auto-synth-dataset](https://github.com/OpenVoiceOS/ovos-ww-auto-synth-dataset) | — | — |
| [raspovos-manual](https://github.com/OpenVoiceOS/raspovos-manual) | User manual for the raspOVOS image | raspOVOS README / ovos-installer |

## Test, template & internal repos (14)

*Scaffolding/test/dummy repos, not user-facing.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [disable-msm-dummy-repo](https://github.com/OpenVoiceOS/disable-msm-dummy-repo) | A repository for sharing and collaboration for third-party Mycroft skills development. | — |
| [hardware-mycroft-mark-1](https://github.com/OpenVoiceOS/hardware-mycroft-mark-1) | in-case-of-apocalypse archive of Mycroft Mark 1 repository | historical archive |
| [my-assistant](https://github.com/OpenVoiceOS/my-assistant) | template repo for derivative voice assistants | — |
| [ovos-skills-info](https://github.com/OpenVoiceOS/ovos-skills-info) | Skill information parser support skill | — |
| [ovos-solver-YesNo-plugin](https://github.com/OpenVoiceOS/ovos-solver-YesNo-plugin) | — | — |
| [quiet.py](https://github.com/OpenVoiceOS/quiet.py) | Python Ctypes Bindings for libquiet | — |
| [skill-abort-test](https://github.com/OpenVoiceOS/skill-abort-test) | test skill for OpenVoiceOS/ovos_utils/pull/34 | — |
| [skill-balena-wifi-setup](https://github.com/OpenVoiceOS/skill-balena-wifi-setup) | — | — |
| [skill-monkey-patch-tester](https://github.com/OpenVoiceOS/skill-monkey-patch-tester) | test monkey patches | — |
| [skill-monkey-patcher](https://github.com/OpenVoiceOS/skill-monkey-patcher) | apply patches to mycroft-core at runtime | — |
| [skill-template-repo](https://github.com/OpenVoiceOS/skill-template-repo) | — | — |
| [template-package-repo](https://github.com/OpenVoiceOS/template-package-repo) | — | — |
| [tskill-ocp-cps](https://github.com/OpenVoiceOS/tskill-ocp-cps) | — | — |
| [tskill-osm_parsing](https://github.com/OpenVoiceOS/tskill-osm_parsing) | Repository to test OSM parser testing | — |

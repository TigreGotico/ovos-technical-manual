# OVOS Repository Index

!!! abstract "In a nutshell"
    OVOS is a large ecosystem of small, focused repositories — core services, plus hundreds of swappable [plugins](plugins-index.md) and [skills](skill-design-guidelines.md). This page is the map: every **public** repository in the [OpenVoiceOS GitHub organization](https://github.com/OpenVoiceOS), grouped by what it does. For each one: why it exists, what it does, and which part of the stack consumes it. Archived repositories are omitted here — see [Deprecated & Legacy Repositories](deprecated-repos.md).

There are roughly **260** public, actively-maintained repositories in the [`OpenVoiceOS`](https://github.com/OpenVoiceOS) organization (the exact count drifts as repos are added or archived). Browse them by category below; click any name to open it on GitHub. Entries marked ⚠️ are experimental or pre-release — read the repository's own README before adopting them.

> Generated from the live organization repository list. If a repository is missing here it is either archived, private, or newly created — check the [organization page](https://github.com/OpenVoiceOS) for the authoritative list.

## Core services & libraries (18)

**[ovos-ui-enclosure-protocol](https://github.com/OpenVoiceOS/ovos-ui-enclosure-protocol)**
:   The consumer/listener half of the legacy Mark 1 hardware-enclosure protocol: it defines `EnclosureProtocolListener`, a mix-in that wires the `enclosure.*` bus messages (LED eyes, mouth/faceplate, system LEDs) to overridable handlers. The producer half (`EnclosureAPI`, used by skills as `self.enclosure`) lives in ovos-gui-api-client; loaded by hardware enclosure plugins such as ovos-PHAL-plugin-mk1.

**[ovos-audio](https://github.com/OpenVoiceOS/ovos-audio)**
:   The "mouth" of the OVOS assistant: it handles text-to-speech generation and audio playback of the resulting speech. Core runtime component of the OVOS stack; other services and skills import it directly or run it as a daemon.

**[ovos-bus-client](https://github.com/OpenVoiceOS/ovos-bus-client)**
:   A Python client for the OVOS messagebus. Connect to OVOS, emit messages, and react to system events. Core runtime component of the OVOS stack; other services and skills import it directly or run it as a daemon.

**[ovos-color-parser](https://github.com/OpenVoiceOS/ovos-color-parser)**
:   Turn natural-language color descriptions into color objects, and color objects back into names, in 23 languages. Pure Python, zero network, no ML model — just bundled wordlists and color math. Core runtime component of the OVOS stack; other services and skills import it directly or run it as a daemon.

**[ovos-config](https://github.com/OpenVoiceOS/ovos-config)**
:   helper package to interact with mycroft config. Core runtime component of the OVOS stack; other services and skills import it directly or run it as a daemon.

**[ovos-core](https://github.com/OpenVoiceOS/ovos-core)**
:   OpenVoiceOS is an open-source platform for smart speakers and other voice-centric devices. Core runtime component of the OVOS stack; other services and skills import it directly or run it as a daemon.

**[ovos-date-parser](https://github.com/OpenVoiceOS/ovos-date-parser)**
:   Multilingual parsing, extraction and formatting of human date, time and duration expressions — a two-way bridge between machine timestamps and the way people actually speak and write about time. Core runtime component of the OVOS stack; other services and skills import it directly or run it as a daemon.

**[ovos-dinkum-listener](https://github.com/OpenVoiceOS/ovos-dinkum-listener)**
:   The OVOS speech-recognition daemon: it owns the microphone, wake-word detection, voice-activity detection and STT, and emits the recognized utterance onto the messagebus for the intent service to handle. Core runtime component of the OVOS stack; other services and skills import it directly or run it as a daemon.

**[ovos-gui](https://github.com/OpenVoiceOS/ovos-gui)**
:   GUI messagebus service, manages GUI state and implements the gui protocol. Core runtime component of the OVOS stack; other services and skills import it directly or run it as a daemon.

**[ovos-gui-api-client](https://github.com/OpenVoiceOS/ovos-gui-api-client)**
:   A template defines what kind of information is being presented, not how it looks. The display layer (Qt/web/terminal/etc.) owns all rendering decisions. Skills own only the semantic data they provide. Core runtime component of the OVOS stack; other services and skills import it directly or run it as a daemon.

**[ovos-lang-parser](https://github.com/OpenVoiceOS/ovos-lang-parser)**
:   Map spoken and written language names to standard IETF/BCP-47 language codes — and back — in many languages, offline, with a two-function API. Core runtime component of the OVOS stack; other services and skills import it directly or run it as a daemon.

**[ovos-messagebus](https://github.com/OpenVoiceOS/ovos-messagebus)**
:   messagebus service, the nervous system of OpenVoiceOS. Core runtime component of the OVOS stack; other services and skills import it directly or run it as a daemon.

**[ovos-number-parser](https://github.com/OpenVoiceOS/ovos-number-parser)**
:   Convert numbers between digits and spoken words, in 40 languages, with one small dependency-light library. Core runtime component of the OVOS stack; other services and skills import it directly or run it as a daemon.

**[ovos-opendata-server](https://github.com/OpenVoiceOS/ovos-opendata-server)**
:   A FastAPI service for collecting anonymized OVOS usage metrics and data with an interactive Streamlit dashboard for visualization. Core runtime component of the OVOS stack; other services and skills import it directly or run it as a daemon.

**[ovos-plugin-manager](https://github.com/OpenVoiceOS/ovos-plugin-manager)**
:   OPM can be used to load and create plugins for the OpenVoiceOS ecosystem! Core runtime component of the OVOS stack; other services and skills import it directly or run it as a daemon.

**[ovos-pydantic-models](https://github.com/OpenVoiceOS/ovos-pydantic-models)**
:   Typed Pydantic v2 models for every message that flows over the OVOS messagebus. Core runtime component of the OVOS stack; other services and skills import it directly or run it as a daemon.

**[ovos-utils](https://github.com/OpenVoiceOS/ovos-utils)**
:   collection of simple utilities for use across the mycroft ecosystem. Core runtime component of the OVOS stack; other services and skills import it directly or run it as a daemon.

**[ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop)**
:   Base classes, decorators, and helpers for building skills and applications for OpenVoiceOS. Core runtime component of the OVOS stack; other services and skills import it directly or run it as a daemon.


## Skills (53)

Every entry below is an installable OVOS skill, loaded by ovos-core's skill loader and dispatched
to by the intent service once installed on a device.

**[ovos-skill-alerts](https://github.com/OpenVoiceOS/ovos-skill-alerts)**
:   A skill to manage alarms, timers, reminders, events and todos and optionally sync them with a CalDAV service.

**[ovos-skill-application-launcher](https://github.com/OpenVoiceOS/ovos-skill-application-launcher)**
:   Application Launcher.

**[ovos-skill-audio-recording](https://github.com/OpenVoiceOS/ovos-skill-audio-recording)**
:   Record audio to file, requires ovos-dinkum-listener.

**[ovos-skill-bandcamp](https://github.com/OpenVoiceOS/ovos-skill-bandcamp)**
:   Bandcamp skill for your hipster music needs.

**[ovos-skill-boot-finished](https://github.com/OpenVoiceOS/ovos-skill-boot-finished)**
:   The Finished Booting skill provides notifications when OpenVoiceOS (OVOS) has fully started and all core services are ready. Notifications can be spoken, played as a sound, or simply logged, based on the user's preferences.

**[ovos-skill-camera](https://github.com/OpenVoiceOS/ovos-skill-camera)**
:   Camera skill for OpenVoiceOS, needs the companion plugin ovos-PHAL-plugin-camera or ovos-PHAL-plugin-termux.

**[ovos-skill-cmd](https://github.com/OpenVoiceOS/ovos-skill-cmd)**
:   A simple OVOS skill for running shell scripts and other commands. The commands execute quietly without requiring confirmation from OVOS.

**[ovos-skill-color-picker](https://github.com/OpenVoiceOS/ovos-skill-color-picker)**
:   Look up colors by voice. Powered by ovos-color-parser.

**[ovos-skill-confucius-quotes](https://github.com/OpenVoiceOS/ovos-skill-confucius-quotes)**
:   Quote from Confucius.

**[ovos-skill-count](https://github.com/OpenVoiceOS/ovos-skill-count)**
:   CountSkill is a simple skill for Open Voice OS (OVOS) that counts from 1 to any user-specified number — or even infinitely — speaking each number aloud. It supports both cardinal and ordinal formats and works offline thanks to ovos-number-parser.

**[ovos-skill-date-time](https://github.com/OpenVoiceOS/ovos-skill-date-time)**
:   Get the time, date, day of the week.

**[ovos-skill-days-in-history](https://github.com/OpenVoiceOS/ovos-skill-days-in-history)**
:   Informs you of historical tidbits about a given calendar day.

**[ovos-skill-ddg](https://github.com/OpenVoiceOS/ovos-skill-ddg)**
:   Answer factual questions using DuckDuckGo Instant Answers.

**[ovos-skill-diagnostics](https://github.com/OpenVoiceOS/ovos-skill-diagnostics)**
:   Retrieve system information such as CPU, memory, and language settings.

**[ovos-skill-dictation](https://github.com/OpenVoiceOS/ovos-skill-dictation)**
:   continuously transcribes user speech to text file while enabled, made for ovos-dinkum-listener.

**[ovos-skill-easter-eggs](https://github.com/OpenVoiceOS/ovos-skill-easter-eggs)**
:   pop culture references skill.

**[ovos-skill-fallback-unknown](https://github.com/OpenVoiceOS/ovos-skill-fallback-unknown)**
:   Capture unrecognized Utterances.

**[ovos-skill-fuster-quotes](https://github.com/OpenVoiceOS/ovos-skill-fuster-quotes)**
:   A skill that answers questions about Joan Fuster, a Valencian essayist, poet, and philosopher known for his work on Catalan culture and identity, providing quotes and biographical facts.

**[ovos-skill-ggwave](https://github.com/OpenVoiceOS/ovos-skill-ggwave)**
:   Voice interface for ggwave plugin.

**[ovos-skill-hello-world](https://github.com/OpenVoiceOS/ovos-skill-hello-world)**
:   Introductory Skill so that Skill Authors can see how an OVOS Skill is put together.

**[ovos-skill-homescreen](https://github.com/OpenVoiceOS/ovos-skill-homescreen)**
:   The home screen is the central place for all your tasks. It is the first thing you will see after completing the onboarding process. It supports a variety of pre-defined widgets which provide you with a quick overview of information you need to know like the current date, time and weather. The home screen contains various features and integrations which you can learn more about in the following sections.

**[ovos-skill-icanhazdadjokes](https://github.com/OpenVoiceOS/ovos-skill-icanhazdadjokes)**
:   A skill that tells dad jokes on request, sourced from the icanhazdadjoke.com API.

**[ovos-skill-ip](https://github.com/OpenVoiceOS/ovos-skill-ip)**
:   Network connection information.

**[ovos-skill-iss-location](https://github.com/OpenVoiceOS/ovos-skill-iss-location)**
:   Track the location of the ISS.

**[ovos-skill-laugh](https://github.com/OpenVoiceOS/ovos-skill-laugh)**
:   Makes your voice assistant laugh like a maniac.

**[ovos-skill-local-media](https://github.com/OpenVoiceOS/ovos-skill-local-media)**
:   File Browser For Open Voice OS.

**[ovos-skill-mark1-ctrl](https://github.com/OpenVoiceOS/ovos-skill-mark1-ctrl)**
:   Controls the enclosure api vocally.

**[ovos-skill-moviemaster](https://github.com/OpenVoiceOS/ovos-skill-moviemaster)**
:   OVOS skill to query IMDB about movies.

**[ovos-skill-naptime](https://github.com/OpenVoiceOS/ovos-skill-naptime)**
:   Put the assistant to sleep when you don't want to be disturbed.

**[ovos-skill-news](https://github.com/OpenVoiceOS/ovos-skill-news)**
:   News Streams catalog.

**[ovos-skill-number-facts](https://github.com/OpenVoiceOS/ovos-skill-number-facts)**
:   Facts about numbers.

**[ovos-skill-parrot](https://github.com/OpenVoiceOS/ovos-skill-parrot)**
:   Turn OpenVoiceOS into a echoing parrot!

**[ovos-skill-personal](https://github.com/OpenVoiceOS/ovos-skill-personal)**
:   Learn history and personality of the assistant.

**[ovos-skill-pokepedia](https://github.com/OpenVoiceOS/ovos-skill-pokepedia)**
:   A child-friendly OpenVoiceOS (OVOS) skill that allows users to query Pokémon data via voice commands. The skill interfaces with the public PokeAPI to retrieve stats, types, moves, and abilities, and provides simplified battle predictions.

**[ovos-skill-pyradios](https://github.com/OpenVoiceOS/ovos-skill-pyradios)**
:   OCP skill for Pyradios, a client for the Radio Browser API.

**[ovos-skill-randomness](https://github.com/OpenVoiceOS/ovos-skill-randomness)**
:   A skill for all kinds of chance - make a choice, roll a die, flip a coin, pick between two choices, etc.

**[ovos-skill-screenshot](https://github.com/OpenVoiceOS/ovos-skill-screenshot)**
:   Take screenshots by voice.

**[ovos-skill-somafm](https://github.com/OpenVoiceOS/ovos-skill-somafm)**
:   OCP skill for SomaFM.

**[ovos-skill-soundcloud](https://github.com/OpenVoiceOS/ovos-skill-soundcloud)**
:   soundcloud skill for OCP.

**[ovos-skill-speedtest](https://github.com/OpenVoiceOS/ovos-skill-speedtest)**
:   Ask OVOS to run a simple speedtest.

**[ovos-skill-spelling](https://github.com/OpenVoiceOS/ovos-skill-spelling)**
:   Let OVOS help you spell words.

**[ovos-skill-spotify](https://github.com/OpenVoiceOS/ovos-skill-spotify)**
:   OCP skill for spotify.

**[ovos-skill-tunein](https://github.com/OpenVoiceOS/ovos-skill-tunein)**
:   OCP skill for TuneIn.

**[ovos-skill-volume](https://github.com/OpenVoiceOS/ovos-skill-volume)**
:   Control the volume of your system.

**[ovos-skill-wallpapers](https://github.com/OpenVoiceOS/ovos-skill-wallpapers)**
:   Skill that fetches and sets desktop wallpapers from wallhaven.cc by voice command.

**[ovos-skill-weather](https://github.com/OpenVoiceOS/ovos-skill-weather)**
:   Weather conditions and forecasts.

**[ovos-skill-wikihow](https://github.com/OpenVoiceOS/ovos-skill-wikihow)**
:   How to do nearly everything.

**[ovos-skill-wikipedia](https://github.com/OpenVoiceOS/ovos-skill-wikipedia)**
:   Wikipedia skill for OpenVoiceOS. Adds a voice interface on top of ovos-wikipedia-plugin, which handles all Wikipedia search and retrieval.

**[ovos-skill-wolfie](https://github.com/OpenVoiceOS/ovos-skill-wolfie)**
:   Wolfram Alpha skill for OpenVoiceOS. Adds a voice interface on top of ovos-wolfram-alpha-plugin, which handles all Wolfram Alpha queries.

**[ovos-skill-word-of-the-day](https://github.com/OpenVoiceOS/ovos-skill-word-of-the-day)**
:   Get Word of the Day from Dictionary.com., Dicionário Priberam, Portal das Palabras or RodaMots.cat.

**[ovos-skill-wordnet](https://github.com/OpenVoiceOS/ovos-skill-wordnet)**
:   WordNet skill for OpenVoiceOS. Adds a voice interface on top of ovos-wordnet-plugin, which handles all WordNet lookups, intent detection, and translation.

**[ovos-skill-youtube](https://github.com/OpenVoiceOS/ovos-skill-youtube)**
:   simple youtube skill for better-cps.

**[ovos-skill-youtube-music](https://github.com/OpenVoiceOS/ovos-skill-youtube-music)**
:   Youtube Music OCP Skill.


## STT plugins (11)

Each registers under the `opm.stt` entry-point group and is loaded by ovos-dinkum-listener (or ovos-stt-server) when selected as the active speech-to-text engine, unless noted otherwise.

**[ovos-stt-plugin-azure](https://github.com/OpenVoiceOS/ovos-stt-plugin-azure)**
:   OpenVoiceOS plugin for Microsoft Azure.

**[ovos-stt-plugin-chromium](https://github.com/OpenVoiceOS/ovos-stt-plugin-chromium)**
:   A stt plugin for mycroft using the google chrome browser api.

**[ovos-stt-plugin-citrinet](https://github.com/OpenVoiceOS/ovos-stt-plugin-citrinet)**
:   OpenVoiceOS STT plugin for Nemo Citrinet.

**[ovos-stt-plugin-fasterwhisper](https://github.com/OpenVoiceOS/ovos-stt-plugin-fasterwhisper)**
:   OpenVoiceOS STT plugin for Faster Whisper.

**[ovos-stt-plugin-nemo](https://github.com/OpenVoiceOS/ovos-stt-plugin-nemo)**
:   OpenVoiceOS STT plugin for Nemo, GPU is strongly recommended.

**[ovos-stt-plugin-vosk](https://github.com/OpenVoiceOS/ovos-stt-plugin-vosk)**
:   Mycroft STT plugin for Vosk.

**[ovos-stt-plugin-wav2vec2](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec2)**
:   OVOS plugin for Wav2Vec2.

**[ovos-stt-plugin-whisper-lm](https://github.com/OpenVoiceOS/ovos-stt-plugin-whisper-lm)**
:   OpenVoiceOS STT plugin for Whisper-LM-transformers, KenLM and Large language model integration with Whisper ASR models implemented in Hugging Face library.

**[ovos-stt-plugin-whispercpp](https://github.com/OpenVoiceOS/ovos-stt-plugin-whispercpp)**
:   OpenVoiceOS STT plugin for whispercpp.

**[ovos-stt-server](https://github.com/OpenVoiceOS/ovos-stt-server)**
:   Wraps any OVOS STT plugin as a standalone HTTP microservice for speech-to-text and spoken-language detection, so STT can run off-device. Called over HTTP by ovos-stt-server-plugin (or any client speaking its API) instead of loading an STT plugin in-process.

**[ovos-stt-server-plugin](https://github.com/OpenVoiceOS/ovos-stt-server-plugin)**
:   A client-side STT plugin that forwards audio to a remote ovos-stt-server instance over HTTP instead of running recognition locally. Registers under the `opm.stt` entry-point group; loaded by ovos-dinkum-listener when configured to use a remote STT server.


## TTS plugins (18)

Most register under the `opm.tts` entry-point group and are loaded by ovos-audio (or ovos-tts-server) when selected as the active text-to-speech engine, unless noted otherwise.

**[ovos-tts-plugin-omnivoice](https://github.com/OpenVoiceOS/ovos-tts-plugin-omnivoice)**
:   ⚠️ No packaged release yet — a TTS plugin wrapping OmniVoice, a massively multilingual (600+ language) zero-shot text-to-speech model with no fixed speaker catalog, supporting auto voice selection, free-text voice design, and short-clip voice cloning. Registers under `opm.tts`; loaded by ovos-audio when selected as the active TTS engine.

**[ovos-tts-plugin-SAM](https://github.com/OpenVoiceOS/ovos-tts-plugin-SAM)**
:   OpenVoiceOS TTS plugin for S.A.M - Software Automatic Mouth.

**[ovos-tts-plugin-ahotts](https://github.com/OpenVoiceOS/ovos-tts-plugin-ahotts)**
:   OVOS TTS plugin for AhoTTS.

**[ovos-tts-plugin-azure](https://github.com/OpenVoiceOS/ovos-tts-plugin-azure)**
:   This TTS service for OpenVoiceOS requires a subscription to Microsoft Azure and the creation of a Speech resource (.

**[ovos-tts-plugin-beepspeak](https://github.com/OpenVoiceOS/ovos-tts-plugin-beepspeak)**
:   OpenVoiceOS R2D2 TTS plugin.

**[ovos-tts-plugin-coqui](https://github.com/OpenVoiceOS/ovos-tts-plugin-coqui)**
:   OVOS TTS plugin for Coqui TTS.

**[ovos-tts-plugin-cotovia](https://github.com/OpenVoiceOS/ovos-tts-plugin-cotovia)**
:   OVOS TTS plugin for Cotovia TTS.

**[ovos-tts-plugin-edge-tts](https://github.com/OpenVoiceOS/ovos-tts-plugin-edge-tts)**
:   TTS plugin for OVOS based on Edge-TTS.

**[ovos-tts-plugin-espeakNG](https://github.com/OpenVoiceOS/ovos-tts-plugin-espeakNG)**
:   OpenVoiceOS TTS plugin for espeak-ng.

**[ovos-tts-plugin-google-tx](https://github.com/OpenVoiceOS/ovos-tts-plugin-google-tx)**
:   OVOS TTS plugin for gTTS.

**[ovos-tts-plugin-lux](https://github.com/OpenVoiceOS/ovos-tts-plugin-lux)**
:   LuxTTS plugin for OpenVoiceOS voice assistant platform.

**[ovos-tts-plugin-marytts](https://github.com/OpenVoiceOS/ovos-tts-plugin-marytts)**
:   TTS Plugin for MaryTTS.

**[ovos-tts-plugin-mimic](https://github.com/OpenVoiceOS/ovos-tts-plugin-mimic)**
:   OVOS TTS plugin for Mimic.

**[ovos-tts-plugin-pico](https://github.com/OpenVoiceOS/ovos-tts-plugin-pico)**
:   OpenVoiceOS TTS plugin for PicoTTS.

**[ovos-tts-plugin-polly](https://github.com/OpenVoiceOS/ovos-tts-plugin-polly)**
:   Requires Amazon access key.

**[ovos-tts-server](https://github.com/OpenVoiceOS/ovos-tts-server)**
:   Wraps any OVOS TTS plugin as a standalone microservice — a small, stateless FastAPI app that exposes text-to-speech over HTTP, so TTS can run off-device. Called over HTTP by ovos-tts-server-plugin (or any client speaking its API) instead of loading a TTS plugin in-process.

**[ovos-tts-server-plugin](https://github.com/OpenVoiceOS/ovos-tts-server-plugin)**
:   A client-side TTS plugin that forwards text to a remote ovos-tts-server instance over HTTP instead of synthesizing speech locally. Registers under the `opm.tts` entry-point group; loaded by ovos-audio when configured to use a remote TTS server.

**[ovos-tts-transformer-sox-plugin](https://github.com/OpenVoiceOS/ovos-tts-transformer-sox-plugin)**
:   This repository contains a Python package for a Text-to-Speech (TTS) transformer that utilizes SoX (Sound eXchange) for audio processing. The transformer applies various effects to the generated audio before playback.


## Wake Word plugins (7)

**[ovos-ww-plugin-microwakeword](https://github.com/OpenVoiceOS/ovos-ww-plugin-microwakeword)**
:   OVOS wake-word plugin wrapping microWakeWord TFLite streaming models from the ESPHome ecosystem. Registers under `opm.wake_word`; loaded by ovos-dinkum-listener when configured as the active wake-word engine.

**[ovos-ww-plugin-openWakeWord](https://github.com/OpenVoiceOS/ovos-ww-plugin-openWakeWord)**
:   This is an OVOS plugin for openWakeWord, an open-source wake word or phrase detection system. It has competitive performance compared to Mycroft Precise or Picovoice Porcupine, can be trained on 100% synthetic data, and can run on a single Raspberry Pi 3 core. Registers under `opm.wake_word`; loaded by ovos-dinkum-listener when configured as the active wake-word engine.

**[ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx)**
:   OpenVoiceOS wake-word plugin for Precise using onnxruntime instead of tflite, paired with pre-trained models from precise-lite-models. Registers under `opm.wake_word`; loaded by ovos-dinkum-listener when configured as the active wake-word engine.

**[ovos-ww-plugin-vosk](https://github.com/OpenVoiceOS/ovos-ww-plugin-vosk)**
:   Mycroft wake word plugin for Vosk. Registers under `opm.wake_word`; loaded by ovos-dinkum-listener when configured as the active wake-word engine.

**[ovos-ww-plugin-wakewordlab](https://github.com/OpenVoiceOS/ovos-ww-plugin-wakewordlab)**
:   OVOS wake word plugin using wakewordlab — compact neural wake word detection with Silero VAD pre-filtering. Registers under `opm.wake_word`; loaded by ovos-dinkum-listener when configured as the active wake-word engine.

**[precise-lite-models](https://github.com/OpenVoiceOS/precise-lite-models)**
:   Free models for usage with precise-lite. Registers under `opm.wake_word`; loaded by ovos-dinkum-listener when configured as the active wake-word engine.

**[wyoming-ovos-wakeword](https://github.com/OpenVoiceOS/wyoming-ovos-wakeword)**
:   expose OVOS wake word plugins via wyoming for usage with the voice pee. Registers under `opm.wake_word`; loaded by ovos-dinkum-listener when configured as the active wake-word engine.


## VAD plugins (3)

**[ovos-vad-plugin-noise](https://github.com/OpenVoiceOS/ovos-vad-plugin-noise)**
:   simple VAD plugin extracted from the old ovos-listener. Registers under `opm.VAD`; loaded by ovos-dinkum-listener to decide when speech starts and stops.

**[ovos-vad-plugin-silero](https://github.com/OpenVoiceOS/ovos-vad-plugin-silero)**
:   Silero Voice Activity Detection (VAD) plugin. Registers under `opm.VAD`; loaded by ovos-dinkum-listener to decide when speech starts and stops.

**[ovos-vad-plugin-webrtcvad](https://github.com/OpenVoiceOS/ovos-vad-plugin-webrtcvad)**
:   WebRTC VAD plugin for OpenVoiceOS. Registers under `opm.VAD`; loaded by ovos-dinkum-listener to decide when speech starts and stops.


## Microphone plugins (4)

**[ovos-microphone-plugin-alsa](https://github.com/OpenVoiceOS/ovos-microphone-plugin-alsa)**
:   OpenVoiceOS Microphone plugin. Registers under `opm.microphone`; loaded by ovos-dinkum-listener as the audio input source.

**[ovos-microphone-plugin-files](https://github.com/OpenVoiceOS/ovos-microphone-plugin-files)**
:   OpenVoiceOS Microphone Files plugin. Registers under `opm.microphone`; loaded by ovos-dinkum-listener as the audio input source.

**[ovos-microphone-plugin-pyaudio](https://github.com/OpenVoiceOS/ovos-microphone-plugin-pyaudio)**
:   OpenVoiceOS Microphone plugin. Registers under `opm.microphone`; loaded by ovos-dinkum-listener as the audio input source.

**[ovos-microphone-plugin-sounddevice](https://github.com/OpenVoiceOS/ovos-microphone-plugin-sounddevice)**
:   Open Voice OS microphone plugin for python-sounddevice library. Registers under `opm.microphone`; loaded by ovos-dinkum-listener as the audio input source.


## Solver / Agent plugins (8)

**[ovos-a2a-agent-plugin](https://github.com/OpenVoiceOS/ovos-a2a-agent-plugin)**
:   An OVOS ChatEngine plugin that lets an ovos-persona delegate its reasoning to any external agent that speaks the Agent2Agent (A2A) protocol. Used by ovos-persona and the Common Query/fallback pipelines (via Agent Engines) to answer free-form questions or drive agentic behavior.

**[ovos-agentic-loop](https://github.com/OpenVoiceOS/ovos-agentic-loop)**
:   Agent-loop ChatEngine plugins for OVOS. Implements seven agentic reasoning patterns (ReAct, Plan-and-Execute, Reflexion, Self-Ask, Chain-of-Thought, CRITIC, Tree-of-Thoughts), five built-in toolboxes, SKILL.md integration, and AGENTS.md context management — all as standard OPM plugins. Used by ovos-persona and the Common Query/fallback pipelines (via Agent Engines) to answer free-form questions or drive agentic behavior.

**[ovos-memory-plugins](https://github.com/OpenVoiceOS/ovos-memory-plugins)**
:   Give your OpenVoiceOS persona a memory. Used by ovos-persona and the Common Query/fallback pipelines (via Agent Engines) to answer free-form questions or drive agentic behavior.

**[ovos-persona](https://github.com/OpenVoiceOS/ovos-persona)**
:   The PersonaPipeline brings multi-persona management to OpenVoiceOS (OVOS), enabling interactive conversations with virtual assistants. 🎙️ With personas, you can customize how queries are handled by assigning specific solvers to each persona. Used by ovos-persona and the Common Query/fallback pipelines (via Agent Engines) to answer free-form questions or drive agentic behavior.

**[ovos-persona-server](https://github.com/OpenVoiceOS/ovos-persona-server)**
:   A single HTTP server that exposes one OVOS Persona as eight concurrent API surfaces — so any LLM client (OpenAI SDK, LangChain, Ollama tools, Anthropic SDK, Google Gemini SDK, Cohere SDK, HuggingFace TGI client, AWS Bedrock client, or any A2A agent) can talk to your OVOS persona without changes. Used by ovos-persona and the Common Query/fallback pipelines (via Agent Engines) to answer free-form questions or drive agentic behavior.

**[ovos-solver-failure-plugin](https://github.com/OpenVoiceOS/ovos-solver-failure-plugin)**
:   Extreme fallback, just complains it does not have a brain. Used by ovos-persona and the Common Query/fallback pipelines (via Agent Engines) to answer free-form questions or drive agentic behavior.

**[ovos-solver-plugin-aiml](https://github.com/OpenVoiceOS/ovos-solver-plugin-aiml)**
:   A rule-based chatbot answer engine for OVOS, using AIML pattern matching. Used by ovos-persona and the Common Query/fallback pipelines (via Agent Engines) to answer free-form questions or drive agentic behavior.

**[ovos-solver-plugin-rivescript](https://github.com/OpenVoiceOS/ovos-solver-plugin-rivescript)**
:   A rule-based chatbot answer engine for OVOS, using RiveScript pattern matching. Used by ovos-persona and the Common Query/fallback pipelines (via Agent Engines) to answer free-form questions or drive agentic behavior.


## PHAL plugins (18)

Each is a PHAL (Platform/Hardware Abstraction Layer) plugin, loaded by ovos-PHAL to bridge hardware or OS-level events onto the messagebus.

**[ovos-PHAL](https://github.com/OpenVoiceOS/ovos-PHAL)**
:   Plugin based Hardware Abstraction Layer.

**[ovos-PHAL-plugin-alsa](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-alsa)**
:   controls system volume with alsa.

**[ovos-PHAL-plugin-app-launcher](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-app-launcher)**
:   PHAL plugin for OpenVoiceOS that handles OS-level desktop application management on behalf of ovos-skill-application-launcher (or any other bus client).

**[ovos-PHAL-plugin-camera](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-camera)**
:   This plugin allows users to interact with cameras using OpenCV or libcamera, take snapshots, and serve video streams over HTTP. It also provides methods for handling camera operations via messagebus events.

**[ovos-PHAL-plugin-connectivity-events](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-connectivity-events)**
:   Monitors network state and exposes it via messagebus.

**[ovos-PHAL-plugin-dotstar](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-dotstar)**
:   PHAL plugin driving DotStar-type LEDs on ReSpeaker 2/4/6/8-mic HATs and the Adafruit VoiceBonnet.

**[ovos-PHAL-plugin-gpsd](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-gpsd)**
:   Exposes location readings from the `gpsd` daemon (USB/serial GPS receivers) to the assistant.

**[ovos-PHAL-plugin-hotkeys](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-hotkeys)**
:   plugin for Keyboard hotkeys, define key combos to trigger bus events.

**[ovos-PHAL-plugin-ipgeo](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-ipgeo)**
:   Autoconfigure default location based on ip address via ip-api.com.

**[ovos-PHAL-plugin-mk1](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk1)**
:   handles integration with the Mycroft Mark1 hardware.

**[ovos-PHAL-plugin-mk2-v6-fan-control](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk2-v6-fan-control)**
:   PHAL plugin controlling the cooling fan on the Mycroft Mark II v6 development kit.

**[ovos-PHAL-plugin-network-manager](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-network-manager)**
:   Provides the network-management interface for NetworkManager-based systems, using `nmcli` for all communication with NetworkManager.

**[ovos-PHAL-plugin-oauth](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-oauth)**
:   ⚠️ Early-stage — bridges the `oauth.*` bus messages so a skill can register an OAuth application and have the OVOS shell drive the authorization flow, storing the resulting credentials.

**[ovos-PHAL-plugin-pulseaudio](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-pulseaudio)**
:   controls system volume with pulseaudio.

**[ovos-PHAL-plugin-system](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-system)**
:   Provides system specific commands to OVOS. The dbus interface for this plugin is not yet established.

**[ovos-PHAL-plugin-tools](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-tools)**
:   A PHAL (Platform / Hardware Abstraction Layer) service provider that exposes all installed OPM ToolBox plugins (opm.agents.toolbox entry-point group) as a unified bus API.

**[ovos-PHAL-plugin-wallpaper-manager](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-wallpaper-manager)**
:   This PHAL plugin provides a central wallpaper management interface for homescreens and other desktops.

**[ovos-PHAL-sensors](https://github.com/OpenVoiceOS/ovos-PHAL-sensors)**
:   Expose sensor data from your OVOS device to various systems.


## Media / OCP plugins (17)

**[ovos-media-classifier](https://github.com/OpenVoiceOS/ovos-media-classifier)**
:   ⚠️ Work in progress, not yet deployed in OVOS — a self-describing, pluggable media-intent classifier that decides what kind of media a request wants ("play some music", "watch an anime") so the OCP pipeline can route it to the right provider. Intended to register under an OCP classifier entry point once stable; loaded by ovos-media's OCP pipeline when adopted.

**[ovos-media-plugin-mpv](https://github.com/OpenVoiceOS/ovos-media-plugin-mpv)**
:   An audio/video backend plugin that drives the MPV media player, with play/pause/stop/seek controls and volume management. Loaded by ovos-media (or the legacy ovos-audio service) when MPV is configured as the active playback backend.

**[ovos-media-plugin-ffplay](https://github.com/OpenVoiceOS/ovos-media-plugin-ffplay)**
:   A playback backend plugin wrapping ffplay (the FFmpeg player). Loaded by ovos-media (or the legacy ovos-audio service) when ffplay is configured as the active playback backend.

**[ovos-media-plugin-cli](https://github.com/OpenVoiceOS/ovos-media-plugin-cli)**
:   A generic command-line playback backend: it shells out to any CLI media player, or auto-detects the best available one (sox, mpg123, paplay, aplay, afplay) per platform. Loaded by ovos-media (or the legacy ovos-audio service) as a fallback or explicit backend.

**[ovos-media](https://github.com/OpenVoiceOS/ovos-media)**
:   ⚠️ **Work in progress** — pre-release software, under active development and not yet deployed in OpenVoiceOS; APIs may change without notice. Published in the open for transparency; do not depend on it in production yet. Part of the OVOS Common Play (OCP) media stack; loaded by ovos-media (or the legacy ovos-audio service) to resolve or play a given media type.

**[ovos-media-plugin-chromecast](https://github.com/OpenVoiceOS/ovos-media-plugin-chromecast)**
:   chromecast plugin for ovos-audio and ovos-media. Part of the OVOS Common Play (OCP) media stack; loaded by ovos-media (or the legacy ovos-audio service) to resolve or play a given media type.

**[ovos-media-plugin-mplayer](https://github.com/OpenVoiceOS/ovos-media-plugin-mplayer)**
:   Mplayer plugin for ovos-media. Part of the OVOS Common Play (OCP) media stack; loaded by ovos-media (or the legacy ovos-audio service) to resolve or play a given media type.

**[ovos-media-plugin-spotify](https://github.com/OpenVoiceOS/ovos-media-plugin-spotify)**
:   spotify plugin for ovos-audio and ovos-media. Part of the OVOS Common Play (OCP) media stack; loaded by ovos-media (or the legacy ovos-audio service) to resolve or play a given media type.

**[ovos-media-plugin-vlc](https://github.com/OpenVoiceOS/ovos-media-plugin-vlc)**
:   vlc plugin for ovos-media. Part of the OVOS Common Play (OCP) media stack; loaded by ovos-media (or the legacy ovos-audio service) to resolve or play a given media type.

**[ovos-ocp-audio-plugin](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin)**
:   OVOS Common Play is a full-fledged voice media player packaged as a mycroft audio plugin. Part of the OVOS Common Play (OCP) media stack; loaded by ovos-media (or the legacy ovos-audio service) to resolve or play a given media type.

**[ovos-ocp-bandcamp-plugin](https://github.com/OpenVoiceOS/ovos-ocp-bandcamp-plugin)**
:   allows OCP to play bandcamp urls, streams will be extracted at playback time. Part of the OVOS Common Play (OCP) media stack; loaded by ovos-media (or the legacy ovos-audio service) to resolve or play a given media type.

**[ovos-ocp-files-plugin](https://github.com/OpenVoiceOS/ovos-ocp-files-plugin)**
:   Packaging of the audio-metadata library for OVOS, adding MP4 support and a maintained PyPI release; used to read audio file tags. Part of the OVOS Common Play (OCP) media stack; loaded by ovos-media (or the legacy ovos-audio service) to resolve or play a given media type.

**[ovos-ocp-m3u-plugin](https://github.com/OpenVoiceOS/ovos-ocp-m3u-plugin)**
:   allows OCP to play .pls and .m3u urls as playlists. Part of the OVOS Common Play (OCP) media stack; loaded by ovos-media (or the legacy ovos-audio service) to resolve or play a given media type.

**[ovos-ocp-news-plugin](https://github.com/OpenVoiceOS/ovos-ocp-news-plugin)**
:   allows OCP to play urls for some news providers, this plugin will extract the real stream at playback time. Part of the OVOS Common Play (OCP) media stack; loaded by ovos-media (or the legacy ovos-audio service) to resolve or play a given media type.

**[ovos-ocp-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-ocp-pipeline-plugin)**
:   OVOS plugin for specialized media handling. Part of the OVOS Common Play (OCP) media stack; loaded by ovos-media (or the legacy ovos-audio service) to resolve or play a given media type.

**[ovos-ocp-rss-plugin](https://github.com/OpenVoiceOS/ovos-ocp-rss-plugin)**
:   allows OCP to play rss feeds, the plugin will extract the first playable stream. Part of the OVOS Common Play (OCP) media stack; loaded by ovos-media (or the legacy ovos-audio service) to resolve or play a given media type.

**[ovos-ocp-youtube-plugin](https://github.com/OpenVoiceOS/ovos-ocp-youtube-plugin)**
:   allows OCP to play youtube urls. Part of the OVOS Common Play (OCP) media stack; loaded by ovos-media (or the legacy ovos-audio service) to resolve or play a given media type.


## Translation plugins (6)

**[ovos-google-translate-plugin](https://github.com/OpenVoiceOS/ovos-google-translate-plugin)**
:   The plugin is used in a wider context to translate utterances/texts on demand (e.g. from solvers and ovos-bidirectional-translation-plugin). Registers under `opm.lang.translate` / `opm.lang.detect`; used wherever OVOS needs to detect or translate free text, including skills and transformer plugins.

**[ovos-lang-detector-classics-plugin](https://github.com/OpenVoiceOS/ovos-lang-detector-classics-plugin)**
:   Provides plugins for the following packages:. Registers under `opm.lang.translate` / `opm.lang.detect`; used wherever OVOS needs to detect or translate free text, including skills and transformer plugins.

**[ovos-lang-detector-fasttext-plugin](https://github.com/OpenVoiceOS/ovos-lang-detector-fasttext-plugin)**
:   fasttext-language-identification is the companion language detector for the NLLB model. Registers under `opm.lang.translate` / `opm.lang.detect`; used wherever OVOS needs to detect or translate free text, including skills and transformer plugins.

**[ovos-translate-plugin-nllb](https://github.com/OpenVoiceOS/ovos-translate-plugin-nllb)**
:   Language Plugin for NLLB200 language translator. Registers under `opm.lang.translate` / `opm.lang.detect`; used wherever OVOS needs to detect or translate free text, including skills and transformer plugins.

**[ovos-translate-server](https://github.com/OpenVoiceOS/ovos-translate-server)**
:   Wraps any OVOS translation/language-detection plugin as a standalone HTTP microservice. Called over HTTP by ovos-translate-server-plugin (or any client speaking its API) instead of loading a translation plugin in-process.

**[ovos-translate-server-plugin](https://github.com/OpenVoiceOS/ovos-translate-server-plugin)**
:   A client-side translation/language-detection plugin that forwards text to a remote ovos-translate-server instance over HTTP. Registers under `opm.lang.translate` / `opm.lang.detect`; used wherever OVOS needs to detect or translate free text via a remote server.


## Pipeline / Intent plugins (10)

**[ovos-markov-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-markov-pipeline-plugin)**
:   An intent pipeline plugin that trains one word-level Markov chain per intent and picks the intent whose model has the lowest perplexity for a given utterance, sitting between pattern-matchers (Adapt, padacioso) and trained classifiers (Padatious) in modeling approach. Registers under `opm.pipeline`; loaded by ovos-core's intent service.

**[intent-test-set](https://github.com/OpenVoiceOS/intent-test-set)**
:   A curated dataset of labeled utterances for benchmarking intent pipeline plugins against each other. Consumed by benchmarking pipelines and test suites; not loaded at runtime.

**[ovos-adapt-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-adapt-pipeline-plugin)**
:   The Adapt Intent Parser is a flexible and extensible intent definition and determination framework. It is intended to parse natural language text into a structured intent that can then be invoked programatically. Registers under `opm.pipeline`; loaded by ovos-core's intent service to match utterances to skills.

**[ovos-common-query-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-common-query-pipeline-plugin)**
:   The OVOS Common Query Framework is designed to answer questions by gathering answers from several skills and selecting the best one. Registers under `opm.pipeline`; loaded by ovos-core's intent service to match utterances to skills.

**[ovos-hierarchical-knn-pipeline](https://github.com/OpenVoiceOS/ovos-hierarchical-knn-pipeline)**
:   An intent matching pipeline for OpenVoiceOS (OVOS), powered by a two-stage hierarchical k-NN classifier backed by IBM Granite embeddings and a FAISS index. Registers under `opm.pipeline`; loaded by ovos-core's intent service to match utterances to skills.

**[ovos-hivemind-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-hivemind-pipeline-plugin)**
:   When in doubt, ask a smarter OVOS install. Registers under `opm.pipeline`; loaded by ovos-core's intent service to match utterances to skills.

**[ovos-m2v-pipeline](https://github.com/OpenVoiceOS/ovos-m2v-pipeline)**
:   An intent matching pipeline for OpenVoiceOS (OVOS), powered by the Model2Vec model for intent classification. Registers under `opm.pipeline`; loaded by ovos-core's intent service to match utterances to skills.

**[ovos-padatious-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-padatious-pipeline-plugin)**
:   An efficient and agile neural network intent parser, implemented in pure numpy with a FANN-compatible model format. Registers under `opm.pipeline`; loaded by ovos-core's intent service to match utterances to skills.

**[ovos-tool-adapters](https://github.com/OpenVoiceOS/ovos-tool-adapters)**
:   Bridges MCP (Model Context Protocol) and UTCP (Universal Tool Calling Protocol) servers into the OVOS agentic loop as standard ToolBox plugins. Registers under `opm.pipeline`; loaded by ovos-core's intent service to match utterances to skills.

**[padatious_cache](https://github.com/OpenVoiceOS/padatious_cache)**
:   Pre-trained Padatious intent classifiers to significantly accelerate the first boot and skill loading of OpenVoiceOS. Registers under `opm.pipeline`; loaded by ovos-core's intent service to match utterances to skills.


## Transformer plugins (6)

**[ovos-audio-transformer-plugin-bandpass](https://github.com/OpenVoiceOS/ovos-audio-transformer-plugin-bandpass)**
:   An audio transformer that band-pass filters captured speech before STT, attenuating energy outside a configurable range (the telephone band, 300–3400 Hz, by default) to strip non-phonetic rumble and hiss. Registers under `opm.transformer.audio`; loaded by ovos-dinkum-listener before the STT stage.

**[ovos-tts-transformer-audiosr](https://github.com/OpenVoiceOS/ovos-tts-transformer-audiosr)**
:   An engine-agnostic TTS transformer that upscales the waveform from any TTS plugin to 48 kHz just before playback, recovering high-frequency detail lost by low-sample-rate voices without retraining. Registers under `opm.transformer.tts`; loaded by ovos-audio after the TTS stage and before playback.

**[ovos-audio-transformer-plugin-ggwave](https://github.com/OpenVoiceOS/ovos-audio-transformer-plugin-ggwave)**
:   Audio transformer plugin wrapping ggwave (data-over-sound) so OVOS can receive audio QR codes such as Wi-Fi setup credentials spoken through a speaker. Registers under `opm.transformer.*`; loaded by ovos-core or ovos-audio to hook into the text, metadata, dialog, or TTS-audio stage of the pipeline.

**[ovos-audio-transformer-plugin-speechbrain-langdetect](https://github.com/OpenVoiceOS/ovos-audio-transformer-plugin-speechbrain-langdetect)**
:   spoken language detector for ovos. Registers under `opm.transformer.*`; loaded by ovos-core or ovos-audio to hook into the text, metadata, dialog, or TTS-audio stage of the pipeline.

**[ovos_tts_transformer_FlashSR](https://github.com/OpenVoiceOS/ovos_tts_transformer_FlashSR)**
:   Audio super-resolution for OpenVoiceOS speech synthesis. FlashSR upsamples the audio produced by any TTS plugin from 16 kHz to 48 kHz just before playback, recovering high-frequency detail that low-sample-rate voices discard. The result is brighter, less muffled speech without retraining or replacing your existing voice. Registers under `opm.transformer.*`; loaded by ovos-core or ovos-audio to hook into the text, metadata, dialog, or TTS-audio stage of the pipeline.

**[ovos_tts_transformer_NovaSR](https://github.com/OpenVoiceOS/ovos_tts_transformer_NovaSR)**
:   Audio super-resolution for OpenVoiceOS speech synthesis. NovaSR upsamples the audio produced by any TTS plugin from 16 kHz to 48 kHz just before playback, recovering high-frequency detail that low-sample-rate voices discard. The result is brighter, less muffled speech without retraining or replacing your existing voice. Registers under `opm.transformer.*`; loaded by ovos-core or ovos-audio to hook into the text, metadata, dialog, or TTS-audio stage of the pipeline.


## Hardware / OS images (10)

**[buildroot](https://github.com/OpenVoiceOS/buildroot)**
:   Buildroot is a simple, efficient and easy-to-use tool to generate embedded Linux systems through cross-compilation. Consumed by device images and build tooling (raspOVOS, ovos-buildroot) rather than by the runtime software stack directly.

**[mycroft-mark1-firmware](https://github.com/OpenVoiceOS/mycroft-mark1-firmware)**
:   This repository holds the code run on the Arduino within a Mycroft unit. It manages the eyes, the mouth, and the button. The code is written entirely in C++ with Arduino's standard library. Consumed by device images and build tooling (raspOVOS, ovos-buildroot) rather than by the runtime software stack directly.

**[ovos-buildroot](https://github.com/OpenVoiceOS/ovos-buildroot)**
:   A minimalistic Linux OS bringing the open source voice assistant ovos-core to embedded, low-spec headless and/or small (touch)screen devices. Consumed by device images and build tooling (raspOVOS, ovos-buildroot) rather than by the runtime software stack directly.

**[ovos-hardware-helpers](https://github.com/OpenVoiceOS/ovos-hardware-helpers)**
:   A small library to help with specific hardware. Consumed by device images and build tooling (raspOVOS, ovos-buildroot) rather than by the runtime software stack directly.

**[ovos-i2c-detection](https://github.com/OpenVoiceOS/ovos-i2c-detection)**
:   A small repo containing auto-detection scripts for i2c devices. Consumed by device images and build tooling (raspOVOS, ovos-buildroot) rather than by the runtime software stack directly.

**[ovos-i2csound](https://github.com/OpenVoiceOS/ovos-i2csound)**
:   Script for i2c HAT detection and configuration on a Raspberry Pi. Consumed by device images and build tooling (raspOVOS, ovos-buildroot) rather than by the runtime software stack directly.

**[ovos-mark1-utils](https://github.com/OpenVoiceOS/ovos-mark1-utils)**
:   small library to interact with a Mycroft Mark1 faceplate via the messagebus. Consumed by device images and build tooling (raspOVOS, ovos-buildroot) rather than by the runtime software stack directly.

**[ovos-systemd](https://github.com/OpenVoiceOS/ovos-systemd)**
:   A legacy, unmaintained set of example systemd unit files written for the old `mycroft-core`
    stack (predating OVOS's own systemd packaging). It is not wired into the current OVOS
    install paths — the [`ovos-installer`](ovos-installer.md) and [raspOVOS](install-raspovos.md)
    each ship their own current systemd units instead; see
    [Production Operations](production-operations.md#keep-services-running-systemd-units) for
    real, current examples.

**[raspOVOS](https://github.com/OpenVoiceOS/raspOVOS)**
:   raspOVOS is the flagship OpenVoiceOS experience for the Raspberry Pi: ready-to-flash images that turn a Pi into a voice assistant. Consumed by device images and build tooling (raspOVOS, ovos-buildroot) rather than by the runtime software stack directly.

**[raspovos-audio-setup](https://github.com/OpenVoiceOS/raspovos-audio-setup)**
:   Automatic audio configuration for Raspberry Pi devices running OpenVoiceOS. Consumed by device images and build tooling (raspOVOS, ovos-buildroot) rather than by the runtime software stack directly.


## Tooling & CI (14)

**[gh-automations](https://github.com/OpenVoiceOS/gh-automations)**
:   Reusable GitHub Actions workflows and Python scripts for the OpenVoiceOS ecosystem. A standalone developer or operator tool; not a runtime dependency of the OVOS stack.

**[ovos-busmon](https://github.com/OpenVoiceOS/ovos-busmon)**
:   Live monitor, capture, and injection tool for the OpenVoiceOS messagebus. Stream every bus message to a browser, filter by type (glob), inspect payloads, export captures as JSONL, and inject messages directly from the UI. A standalone developer or operator tool; not a runtime dependency of the OVOS stack.

**[ovos-docker](https://github.com/OpenVoiceOS/ovos-docker)**
:   Please follow the dedicated documentation. A standalone developer or operator tool; not a runtime dependency of the OVOS stack.

**[ovos-docker-stt](https://github.com/OpenVoiceOS/ovos-docker-stt)**
:   Docker/Podman compose files that run an OVOS STT plugin as a standalone speech-to-text container service. A standalone developer or operator tool; not a runtime dependency of the OVOS stack.

**[ovos-docker-tts](https://github.com/OpenVoiceOS/ovos-docker-tts)**
:   Docker/Podman compose files that run an OVOS TTS plugin as a standalone text-to-speech container service. A standalone developer or operator tool; not a runtime dependency of the OVOS stack.

**[ovos-docker-tx](https://github.com/OpenVoiceOS/ovos-docker-tx)**
:   Docker/Podman compose files that run an OVOS translation plugin as a standalone translation container service. A standalone developer or operator tool; not a runtime dependency of the OVOS stack.

**[ovos-docs-viewer](https://github.com/OpenVoiceOS/ovos-docs-viewer)**
:   in terminal docs viewer. A standalone developer or operator tool; not a runtime dependency of the OVOS stack.

**[ovos-installer](https://github.com/OpenVoiceOS/ovos-installer)**
:   Installer for Open Voice OS (OVOS) and HiveMind on Linux and macOS. Supports interactive installs, scenario-based automation, and optional container deployment. A standalone developer or operator tool; not a runtime dependency of the OVOS stack.

**[ovos-spec-tools](https://github.com/OpenVoiceOS/ovos-spec-tools)**
:   Reference implementation of the OVOS [formal specifications](architecture-specs.md) — the low-level, dependency-light primitives those specifications describe. A standalone developer or operator tool; not a runtime dependency of the OVOS stack.

**[ovos-tools](https://github.com/OpenVoiceOS/ovos-tools)**
:   A grab-bag of helper scripts for developing, testing, and administering OVOS devices. A standalone developer or operator tool; not a runtime dependency of the OVOS stack.

**[ovos-wyoming-docker](https://github.com/OpenVoiceOS/ovos-wyoming-docker)**
:   A collection of Docker images for running OVOS services using the Wyoming Protocol. A standalone developer or operator tool; not a runtime dependency of the OVOS stack.

**[ovos-yaml-editor](https://github.com/OpenVoiceOS/ovos-yaml-editor)**
:   The OpenVoiceOS Config Editor is a web-based application for managing and editing the configuration files of OpenVoiceOS, supporting YAML and JSON formats. It provides an easy-to-use interface for modifying and saving configuration data, making it simple for users to adjust system settings. A standalone developer or operator tool; not a runtime dependency of the OVOS stack.

**[wyoming-ovos-stt](https://github.com/OpenVoiceOS/wyoming-ovos-stt)**
:   expose OVOS STT plugins via wyoming for usage with the voice pee. A standalone developer or operator tool; not a runtime dependency of the OVOS stack.

**[wyoming-ovos-tts](https://github.com/OpenVoiceOS/wyoming-ovos-tts)**
:   expose OVOS TTS plugins via wyoming for usage with the voice pee. A standalone developer or operator tool; not a runtime dependency of the OVOS stack.


## Datasets & Models (3)

**[ovos-datasets](https://github.com/OpenVoiceOS/ovos-datasets)**
:   All datasets released under the Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) license. Consumed by training or benchmarking pipelines and plugin test suites; not loaded at runtime.

**[ovos-ww-community-dataset](https://github.com/OpenVoiceOS/ovos-ww-community-dataset)**
:   Wake Word training data provided by the OpenVoiceOS/Mycroft Community. Consumed by training or benchmarking pipelines and plugin test suites; not loaded at runtime.

**[voices_demo](https://github.com/OpenVoiceOS/voices_demo)**
:   Audio samples demonstrating available TTS voices, for comparing options before configuring one. Consumed by training or benchmarking pipelines and plugin test suites; not loaded at runtime.


## Project infrastructure (web/blog) (4)

**[ovos-blogs](https://github.com/OpenVoiceOS/ovos-blogs)**
:   This is the existing blog-starter plus TypeScript. Public-facing website or blog infrastructure for the project; not part of the runtime software stack.

**[ovos-landing-page](https://github.com/OpenVoiceOS/ovos-landing-page)**
:   A community-driven, open-source AI voice platform. Public-facing website or blog infrastructure for the project; not part of the runtime software stack.

**[ovos-org-website](https://github.com/OpenVoiceOS/ovos-org-website)**
:   Test repo for ovos webpage. Public-facing website or blog infrastructure for the project; not part of the runtime software stack.

**[ovos-technical-manual](https://github.com/OpenVoiceOS/ovos-technical-manual)**
:   the OVOS project documentation is written and maintained by users just like you! Public-facing website or blog infrastructure for the project; not part of the runtime software stack.


## Meta & infrastructure / other components (46)

Repositories that do not fit a single functional category above: organization-wide
templates, legacy/reference components, standalone libraries the ecosystem depends
on, and assets used across projects.

**[.github](https://github.com/OpenVoiceOS/.github)**
:   The organization-wide `.github` repository: issue/PR templates and the profile README shown on the [OpenVoiceOS](https://github.com/OpenVoiceOS) organization page. Read by GitHub itself, not by any OVOS service.

**[DrQA](https://github.com/OpenVoiceOS/DrQA)**
:   A PyTorch implementation of the "Reading Wikipedia to Answer Open-Domain Questions" paper, mirrored for reference. Not consumed by any current OVOS component; kept as a historical reference for open-domain question answering research.

**[OVOS-skills-store](https://github.com/OpenVoiceOS/OVOS-skills-store)**
:   The community skill store: a curated list where OVOS developers submit and discover third-party skills. Read by skill-installer tooling and the skill-store GUI to populate the list of installable skills.

**[OpenVoiceOS](https://github.com/OpenVoiceOS/OpenVoiceOS)**
:   The organization's release tracker — high-level release notes across the ecosystem's many repositories. Reference only; no runtime component consumes it.

**[VocalFusionDriver](https://github.com/OpenVoiceOS/VocalFusionDriver)**
:   A Linux kernel driver for the XMOS VocalFusion microphone array, built for kernel 5.10. Used when building custom kernels for XMOS-based microphone hardware; not needed for standard installs.

**[architecture](https://github.com/OpenVoiceOS/architecture)**
:   Formal, implementation-agnostic specifications for the voice-OS application binary interface — intent template grammar, locale resource formats, and the interfaces skills and pipelines must honor. Consumed as the reference spec by [ovos-spec-tools](https://github.com/OpenVoiceOS/ovos-spec-tools) and by pipeline/skill authors checking conformance.

**[kw-template-matcher](https://github.com/OpenVoiceOS/kw-template-matcher)**
:   A standalone template-expansion and fuzzy-matching utility: it expands templates with slots, optional phrases, and alternatives, then matches free text against them with confidence scoring. Used for prototyping NLU/intent grammars; not itself wired into an OVOS pipeline entry point.

**[linha-fina](https://github.com/OpenVoiceOS/linha-fina)**
:   An SVM-based intent engine that can add or remove intents at runtime without retraining from scratch. Used as a benchmarking baseline for pipeline plugins rather than a production matcher.

**[message_spec](https://github.com/OpenVoiceOS/message_spec)**
:   Reference material describing OVOS messagebus message shapes. Superseded in practice by [ovos-pydantic-models](https://github.com/OpenVoiceOS/ovos-pydantic-models), which is the actively maintained, machine-readable version of the same specification.

**[mycroft-classic-listener](https://github.com/OpenVoiceOS/mycroft-classic-listener)**
:   The original Mycroft-core listener, updated to run on top of current OVOS packages. Kept as a simpler alternative to ovos-dinkum-listener and as a historical reference to the classic Mark 1 implementation; not the default listener.

**[mycroft-gui-qt6](https://github.com/OpenVoiceOS/mycroft-gui-qt6)**
:   A Qt6 port of the Qt5 Mycroft GUI client, aiming for full feature parity. Acts as a GUI client that connects to ovos-gui over the [GUI protocol](gui-protocol.md); used on devices such as the Mycroft Mark II that render a native Qt interface.

**[mycroft-legacy](https://github.com/OpenVoiceOS/mycroft-legacy)**
:   Restores select deprecated mycroft-core functionality that was dropped from modern OVOS packages, for installs that still depend on it. Consumed only by legacy setups migrating off classic mycroft-core.

**[nebulento](https://github.com/OpenVoiceOS/nebulento)**
:   A lightweight fuzzy-matching intent parser built on rapidfuzz. Available as an alternative intent-matching engine; not wired into the default OVOS pipeline stack.

**[ovos-YesNo-plugin](https://github.com/OpenVoiceOS/ovos-YesNo-plugin)**
:   A heuristic yes/no answer classifier for OpenVoiceOS. Used by skills that need to interpret a freeform confirmation response (skills call it directly rather than through an OPM entry-point group).

**[ovos-audio-plugin-mpv](https://github.com/OpenVoiceOS/ovos-audio-plugin-mpv)**
:   An MPV-based audio backend for the legacy `ovos-audio` playback service (predates the newer [ovos-media-plugin-mpv](https://github.com/OpenVoiceOS/ovos-media-plugin-mpv)). Loaded by `ovos-audio` when configured as the active audio backend.

**[ovos-bidirectional-translation-plugin](https://github.com/OpenVoiceOS/ovos-bidirectional-translation-plugin)**
:   ⚠️ Early-stage — bundles an utterance-transformer and a dialog-transformer plugin that together let OVOS understand a request in one language and reply in the user's own language. Registers under `opm.transformer.text` / `opm.transformer.dialog`; loaded by ovos-core's transformer pipeline when enabled. See [Bidirectional Translation](bidirectional-translation.md) for the design.

**[ovos-chromadb-embeddings-plugin](https://github.com/OpenVoiceOS/ovos-chromadb-embeddings-plugin)**
:   A ChromaDB-backed vector-store plugin implementing the `EmbeddingsDB` interface. Loaded by persona/memory components (such as ovos-memory-plugins' RAG backend) that need a persistent embeddings store.

**[ovos-ddg-plugin](https://github.com/OpenVoiceOS/ovos-ddg-plugin)**
:   A DuckDuckGo Instant Answers solver plugin. Registers as a common-query / solver plugin, used by ovos-persona and the common-query pipeline to answer general-knowledge questions.

**[ovos-dialog-normalizer-plugin](https://github.com/OpenVoiceOS/ovos-dialog-normalizer-plugin)**
:   A dialog-transformer plugin that normalizes the text OVOS is about to speak (expanding abbreviations, numbers, etc.) before it reaches TTS. Registers under `opm.transformer.dialog`; loaded by ovos-core's dialog-transformer pipeline stage.

**[ovos-gguf-plugin](https://github.com/OpenVoiceOS/ovos-gguf-plugin)**
:   A unified GGUF/llama-cpp-python wrapper providing chat, summarization, dialog rewriting, translation, language detection, and text embeddings from quantized local models. Registers multiple `opm.*` plugin types (solver, transformer, embeddings) backed by the same GGUF runtime, so it can be loaded by ovos-persona, the transformer pipeline, or memory backends depending on which capability is configured.

**[ovos-legacy-mycroft-gui-plugin](https://github.com/OpenVoiceOS/ovos-legacy-mycroft-gui-plugin)**
:   A compatibility shim exposing the classic mycroft-core GUI plugin interface on top of modern ovos-gui. Used only by GUI clients written against the old mycroft-core API.

**[ovos-localize](https://github.com/OpenVoiceOS/ovos-localize)**
:   A GitHub-native localization platform purpose-built for OVOS skill and plugin locale files, replacing GitLocalize. Used by maintainers and translators to manage translations; see [Machine-Translation Boundary](ovos-localize-tutorial.md) if present, or the localization workflow docs.

**[ovos-machine-translations](https://github.com/OpenVoiceOS/ovos-machine-translations)**
:   Temporary machine-translated resource files produced while skills and plugins waited for GitLocalize-based human translation. Historical/staging resource, not imported by runtime code.

**[ovos-messagebus-chat-plugin](https://github.com/OpenVoiceOS/ovos-messagebus-chat-plugin)**
:   A ChatEngine agent plugin (`opm.agents.chat`) that proxies chat turns through a connected OVOS messagebus, sending each utterance through the OVOS pipeline and collecting the synthesized reply. Loaded by chat-style agent front-ends that want to drive OVOS as their backend rather than talking to it directly.

**[ovos-openai-plugin](https://github.com/OpenVoiceOS/ovos-openai-plugin)**
:   Provides OpenAI-Chat-Completions-compatible solver/persona plugins, usable against OpenAI itself or any server implementing the same `/chat/completions` contract (ollama, llama.cpp, vLLM, LocalAI). Loaded by ovos-persona when a persona is configured to use an OpenAI-compatible model.

**[ovos-option-matcher-fuzzy-plugin](https://github.com/OpenVoiceOS/ovos-option-matcher-fuzzy-plugin)**
:   A fuzzy-matching `OptionMatcherEngine` plugin, used to pick the closest matching item from a list of options a skill offers (e.g. disambiguating "the second one" or a near-miss name). Loaded by skills that use the OptionMatcher helper from ovos-workshop.

**[ovos-qdrant-embeddings-plugin](https://github.com/OpenVoiceOS/ovos-qdrant-embeddings-plugin)**
:   A Qdrant-backed vector-store plugin implementing the `EmbeddingsDB` interface, an alternative to ovos-chromadb-embeddings-plugin. Loaded by persona/memory components that need a persistent embeddings store backed by Qdrant.

**[ovos-utterance-corrections-plugin](https://github.com/OpenVoiceOS/ovos-utterance-corrections-plugin)**
:   An utterance-transformer plugin that applies user-defined find/replace corrections to STT output before intent matching, to fix recurring misrecognitions. Registers under `opm.transformer.text`; loaded by ovos-core's utterance-transformer pipeline stage.

**[ovos-utterance-normalizer](https://github.com/OpenVoiceOS/ovos-utterance-normalizer)**
:   An utterance-transformer plugin that normalizes recognized text (casing, punctuation, contractions) before it reaches intent matchers. Registers under `opm.transformer.text`; loaded by ovos-core's utterance-transformer pipeline stage.

**[ovos-utterance-plugin-cancel](https://github.com/OpenVoiceOS/ovos-utterance-plugin-cancel)**
:   An utterance-transformer plugin that cancels an in-progress utterance when the user appends a cancel/nevermind phrase. Registers under `opm.transformer.text`; loaded by ovos-core's utterance-transformer pipeline stage.

**[ovos-wikipedia-plugin](https://github.com/OpenVoiceOS/ovos-wikipedia-plugin)**
:   Wikipedia integration exposing both a retrieval engine for RAG pipelines and a tool-use toolbox for agentic personas. Loaded by ovos-persona (as a solver/tool) or by RAG-based memory backends that need a Wikipedia retriever.

**[ovos-wolfram-alpha-plugin](https://github.com/OpenVoiceOS/ovos-wolfram-alpha-plugin)**
:   ⚠️ Marked alpha upstream — Wolfram Alpha integration providing a retrieval engine and an agent toolbox, the same dual-role pattern as ovos-wikipedia-plugin. Loaded by ovos-persona when Wolfram Alpha is configured as a solver or tool.

**[ovos-wordnet-plugin](https://github.com/OpenVoiceOS/ovos-wordnet-plugin)**
:   Exposes WordNet as a retrieval engine and an agent toolbox with lookup tools (definitions, synonyms). Loaded by ovos-persona when WordNet is configured as a solver or tool.

**[ovos-ww-verifier-plugin-speaker](https://github.com/OpenVoiceOS/ovos-ww-verifier-plugin-speaker)**
:   A wake-word verifier plugin that rejects wake-word triggers from voices that are not enrolled household members. Registers under `opm.wake_word.verifier`; loaded by ovos-dinkum-listener as a second-stage check after the wake-word engine fires.

**[ovos_assets](https://github.com/OpenVoiceOS/ovos_assets)**
:   Shared images, icons, and artwork used across OpenVoiceOS repositories and documentation. Referenced (linked or copied) by websites, GUI themes, and READMEs across the organization; not imported by running code.

**[ovoscope](https://github.com/OpenVoiceOS/ovoscope)**
:   An end-to-end testing framework for OVOS skills: it runs a full ovos-core pipeline in-process against a `FakeBus`, with no server, audio stack, or network required. Used by skill authors and CI to load real skill plugins, emit a test utterance, and assert on the resulting bus messages; see the [ovoscope skill](ovoscope-overview.md) docs.

**[padacioso](https://github.com/OpenVoiceOS/padacioso)**
:   A lightweight, dependency-light regex-based intent parser, file-format compatible with Padatious. Registers under `opm.pipeline`; loaded by ovos-core's intent service as a low-footprint alternative to the neural Padatious engine.

**[palavreado](https://github.com/OpenVoiceOS/palavreado)**
:   A dead-simple keyword-based intent parser positioned as a drop-in replacement for Adapt. Registers under `opm.pipeline`; loaded by ovos-core's intent service when configured as the keyword-matching pipeline stage.

**[pi-gen](https://github.com/OpenVoiceOS/pi-gen)**
:   A mirror of the official tool used to build Raspberry Pi OS images (formerly Raspbian). Used by the raspOVOS build process to produce bootable Raspberry Pi images; not a runtime dependency.

**[pyhtmx-gui-client](https://github.com/OpenVoiceOS/pyhtmx-gui-client)**
:   A GUI client for OpenVoiceOS built with HTMX, TailwindCSS, and daisyUI instead of Qt. Connects to ovos-gui over the [GUI protocol](gui-protocol.md); an alternative renderer for devices that prefer a web-based interface.

**[quebra_frases](https://github.com/OpenVoiceOS/quebra_frases)**
:   A small utility library that chunks strings into byte-sized pieces (sentences, words, numbers) for text processing. Imported directly as a library by several parser packages, including [ovos-date-parser](date-parser.md) and [ovos-number-parser](https://github.com/OpenVoiceOS/ovos-number-parser).

**[renovate-config](https://github.com/OpenVoiceOS/renovate-config)**
:   Shared Renovate bot configuration for dependency-update pull requests across OpenVoiceOS repositories. Read by the Renovate GitHub App, not by any OVOS service.

**[rpi-linux](https://github.com/OpenVoiceOS/rpi-linux)**
:   A mirror of the Raspberry Pi Foundation's Linux kernel source tree. Used to build the kernel for Raspberry Pi-based OVOS images; unrelated kernel issues should be reported upstream, not against this mirror.

**[scripts](https://github.com/OpenVoiceOS/scripts)**
:   A grab-bag of small helper scripts for OVOS maintenance tasks, such as quickly navigating logs and slicing out error contexts. Standalone operator tooling; not imported by any package.

**[status](https://github.com/OpenVoiceOS/status)**
:   The open-source uptime monitor and public status page for OpenVoiceOS-hosted services, powered by Upptime. Standalone monitoring infrastructure; not part of the runtime stack.

**[wallpaper_changer](https://github.com/OpenVoiceOS/wallpaper_changer)**
:   A Python library that changes the desktop wallpaper programmatically across several Linux desktop environments. Used as a library by [ovos-skill-wallpapers](https://github.com/OpenVoiceOS/ovos-skill-wallpapers) to apply the wallpaper it fetches.


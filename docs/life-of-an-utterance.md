# The Life of an Utterance

This guide provides a technical, step-by-step walkthrough of how a voice command is processed by OpenVoiceOS, from the moment sound hits the microphone to the final spoken response.

---

## 1. Capture and [Wake Word](wake-word-plugins.md) Detection
**Service:** `ovos-dinkum-listener` (or similar)
**Input:** Raw audio from the microphone plugin.

The listener service is always active, monitoring a stream of audio.

-   **[VAD](vad-plugins.md) Plugin**: Continuously checks if someone is speaking.


-   **Wake Word Plugin**: Monitors the audio stream for the configured wake word (e.g., "Hey Mycroft").


-   **Trigger**: Once the wake word is detected, the listener begins recording the subsequent audio as a potential command.

---

## 2. [Speech-to-Text](stt-plugins.md) ([STT](stt-plugins.md))
**Service:** `ovos-dinkum-listener`
**Output:** `recognizer_loop:utterance` ([MessageBus](bus-service.md))

Once the user stops speaking (detected by the VAD plugin), the recorded audio buffer is sent to the **STT Plugin**.

-   The STT engine (e.g., Whisper, Google, Vosk) transcribes the audio into text.


-   The listener emits a `recognizer_loop:utterance` message to the bus, containing the transcription in its `data` field.

---

## 3. Utterance and Metadata Transformation
**Service:** `ovos-core` ([Intent Service](intent-service.md))
**Bus Event:** `recognizer_loop:utterance`

The `IntentService` within `ovos-core` picks up the transcription. Before matching it to an intent, it passes it through the **[Transformer](transformer-plugins.md) Pipeline**:

-   **Utterance Transformers**: These can normalize the text (e.g., "42" -> "forty-two"), fix common STT errors, or expand abbreviations.


-   **Metadata Transformers**: These can enrich the message context with information like the user's emotion or the current environmental noise level.

---

## 4. Intent Pipeline Matching
**Service:** `ovos-core` (Intent Service)
**Process:** Ordered evaluation of matchers.

The (potentially modified) utterance is now evaluated against the **Intent Pipeline**. Each matcher is tried in order until a high-confidence match is found:

1.  **[Converse](converse-pipeline.md)**: Active skills are given a chance to intercept the utterance first (e.g., for multi-turn questions).


2.  **[Adapt](adapt-pipeline.md)**: High-confidence keyword matching for simple, direct commands.


3.  **[Padatious](padatious-pipeline.md)**: Expression-based matching for more natural language.


4.  **[Common Play](ocp-pipeline.md) ([OCP](ocp-pipeline.md))**: If the utterance sounds like a media request (e.g., "Play some jazz"), it's routed to OCP.


5.  **[Common Query](cq-pipeline.md)**: If no direct match is found, OVOS queries various skills for general knowledge (e.g., "Who is Einstein?").


6.  **[Fallback](fallback-pipeline.md)**: As a last resort, fallback skills (like LLM-based solvers) can attempt to handle the utterance.

---

## 5. [Skill](skill-design-guidelines.md) Execution
**Service:** A specific Skill (running in `ovos-core`)
**Bus Event:** `{skill_id}:activate` and the specific intent message.

Once a match is found, `ovos-core` emits a message specifically for the winning skill.

-   The skill's **intent handler** is triggered.


-   The skill performs its logic (e.g., querying an API, controlling a device).


-   If the skill needs to respond, it calls `self.speak()` or `self.speak_dialog()`.

---

## 6. [Text-to-Speech](tts-plugins.md) ([TTS](tts-plugins.md))
**Service:** `ovos-audio`
**Bus Event:** `speak`

The skill emits a `speak` message containing the response text.

-   The `ovos-audio` service receives the `speak` message.


-   It sends the text to the **TTS Plugin** (e.g., Piper, Mimic, Coqui) to generate a WAV file.


-   It also requests **Visemes** (for lip-sync) from a **G2P Plugin**.

---

## 7. Audio Playback and GUI Updates
**Service:** `ovos-audio` and `ovos-gui`
**Output:** Sound from speakers and visuals on screen.

-   **Playback**: `ovos-audio` plays the generated WAV file through the configured audio output (e.g., ALSA, PulseAudio).


-   **GUI**: If the skill provided a UI (via `self.gui.show_page()`), the `ovos-gui` service renders the [QML](qt5-gui.md)/HTML view on the screen, often synchronized with the spoken response.

---

## 8. [Session](session.md) Wrap-up
**Service:** `ovos-core` (Session Manager)

The conversation state is updated. If the skill requested a follow-up question (e.g., `expect_response=True`), the listener is reactivated immediately, and the cycle begins again at Step 1, but with the current **Session** context preserved.

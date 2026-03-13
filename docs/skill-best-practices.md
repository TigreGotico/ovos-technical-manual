# Skill Design Best Practices

Creating a high-quality OVOS skill is not just about writing code; it's about designing a user experience that is intuitive, robust, and respects the user's intent. This guide outlines the best practices for developing skills that feel "native" to the OVOS ecosystem.

---

## 1. Intent Design

### Favor [Padatious](padatious-pipeline.md) for Natural Language
While [Adapt](adapt-pipeline.md) is great for simple keyword commands, Padatious should be your primary tool for most intents. It allows for more natural, varied utterances and handles variations in user speech much better than strict keyword matching.

### Use Entities for Variation
Instead of writing dozens of similar `.intent` lines, use entities to capture specific variables:

-   **Bad:** "What's the weather in London?", "What's the weather in New York?"


-   **Good:** "What's the weather in {location}" (with a `location.entity` file).

---

## 2. Conversation Flow

### Use `self.speak_dialog()`
Never hardcode strings in your Python code. Always use `.dialog` files. This ensures your skill is easily translatable and provides variety in responses.

### Respect the `stop()` Method
A well-behaved skill must implement the `stop()` method to terminate any active processes (like music playback or timers) when the user says "Stop".

### Handle Context Correcty
If your skill asks a follow-up question (using `expect_response=True`), make sure you are prepared to handle the user's answer in a `converse()` method or a specific intent.

---

## 3. Performance and Efficiency

### Keep `initialize()` Lightweight
Avoid doing heavy processing (like downloading large datasets) inside the `initialize()` method. This can slow down the startup of the entire OVOS system. Use background threads or lazy-loading where possible.

### Declare Runtime Requirements
Be explicit about what your skill needs (e.g., internet access, a GUI). This allows the [Skill Manager](skill-manager.md) to only load your skill when its requirements are met, saving system resources.

---

## 4. Error Handling

### Be Graceful with Failures
If an API call fails or a resource is unavailable, provide a clear, helpful response to the user instead of simply failing silently.

-   **Bad:** (Silence)


-   **Good:** "I'm sorry, I couldn't reach the weather service right now. Please try again later."

### Log Informatively
Use `self.log` to provide useful information for debugging, but avoid logging sensitive user data or being overly "spammy".

---

## 5. GUI and Visuals

### Design for Multiple Screens
If your skill has a GUI, test it on both horizontal and vertical screens. Use [Kirigami](qt5-gui.md)'s responsive components to ensure it looks good on everything from a small smart speaker to a large TV.

### Sync Visuals with Speech
When using `self.gui.show_page()`, try to synchronize the visual information with the spoken response. Don't overwhelm the user with too much text on the screen while the assistant is speaking.

# Skill Design Best Practices

!!! abstract "In a nutshell"
    A "skill" is an add-on that teaches OVOS to do something, like answering a question or setting a timer. This guide collects hard-won advice on making a skill that feels natural and reliable to talk to, not just one that technically works. It is written for skill makers. See [Skill Examples](skill-examples.md) and the [Glossary](glossary.md).

Creating a high-quality OVOS skill is not just about writing code; it's about designing a user experience that is intuitive, robust, and respects the user's intent. This guide outlines the best practices for developing skills that feel "native" to the OVOS ecosystem.

!!! note "Scope: code-level practices"
    This page is about **how to write the code** of a skill — which API to call, which method to implement, how to structure error handling. For guidance on **how to design the voice interaction itself** (when to ask for confirmation, how to phrase prompts, how much to say), see [Skill Design Guidelines](skill-design-guidelines.md).

---

## 1. Intent Design

### Favor [Padatious](padatious-pipeline.md) for Natural Language
While [Adapt](adapt-pipeline.md) is great for simple keyword commands, Padatious should be your primary tool for most intents. It allows for more natural, varied utterances and handles variations in user speech much better than strict keyword matching.

### Use Entities for Variation
Instead of writing dozens of similar `.intent` lines, use entities to capture specific variables:

-   **Bad:** "What's the weather in London?", "What's the weather in New York?"


-   **Good:** "What's the weather in {location}" (with a `location.entity` file).

```python
from ovos_workshop.decorators import intent_handler
from ovos_workshop.intents import IntentBuilder

class WeatherSkill(OVOSSkill):
    @intent_handler(IntentBuilder("WeatherIntent").require("Weather").require("location"))
    def handle_weather_intent(self, message):
        location = message.data.get("location")
        self.speak_dialog("weather", {"location": location})
```

---

## 2. Conversation Flow

### Use `self.speak_dialog()`
Never hardcode strings in your Python code. Always use `.dialog` files. This ensures your skill is easily translatable and provides variety in responses.

```python
# locale/en-us/weather.dialog contains one line per variant, e.g.:
#   It's {temperature} degrees in {location}.
self.speak_dialog("weather", {"temperature": 21, "location": "Lisbon"})
```

### Respect the `stop()` Method
A well-behaved skill must implement the `stop()` method to terminate any active processes (like music playback or timers) when the user says "Stop".

```python
def stop(self):
    if self.timer_thread and self.timer_thread.is_alive():
        self.timer_active = False
        return True
    return False
```

### Handle Context Correcty
If your skill asks a follow-up question (using `expect_response=True`), make sure you are prepared to handle the user's answer in a `converse()` method or a specific intent.

```python
def handle_ask_name_intent(self, message):
    self.speak_dialog("ask_name", expect_response=True)

def converse(self, message=None):
    utterances = message.data.get("utterances", [])
    if utterances:
        self.speak_dialog("hello", {"name": utterances[0]})
        return True
    return False
```

---

## 3. Performance and Efficiency

### Keep `initialize()` Lightweight
Avoid doing heavy processing (like downloading large datasets) inside the `initialize()` method. This can slow down the startup of the entire OVOS system. Use background threads or lazy-loading where possible.

```python
from threading import Thread

def initialize(self):
    # register intents / events here, keep it fast
    Thread(target=self._load_large_dataset, daemon=True).start()
```

### Declare Runtime Requirements
Be explicit about what your skill needs (e.g., internet access, a GUI). This allows the [Skill Manager](skill-manager.md) to only load your skill when its requirements are met, saving system resources.

```python
from ovos_utils.process_utils import RuntimeRequirements

class WeatherSkill(OVOSSkill):
    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(requires_internet=True, requires_gui=False)
```

---

## 4. Error Handling

### Be Graceful with Failures
If an API call fails or a resource is unavailable, provide a clear, helpful response to the user instead of simply failing silently.

-   **Bad:** (Silence)


-   **Good:** "I'm sorry, I couldn't reach the weather service right now. Please try again later."

```python
def handle_weather_intent(self, message):
    try:
        data = self.get_weather()
    except ConnectionError:
        self.speak_dialog("weather.error")
        return
    self.speak_dialog("weather", data)
```

### Log Informatively
Use `self.log` to provide useful information for debugging, but avoid logging sensitive user data or being overly "spammy".

```python
self.log.debug(f"fetching weather for {location}")
self.log.error("weather API request failed", exc_info=True)
```

---

## 5. GUI and Visuals

### Design for Multiple Screens
If your skill has a GUI, test it on both horizontal and vertical screens. Use [Kirigami](qt5-gui.md)'s responsive components to ensure it looks good on everything from a small smart speaker to a large TV.

### Sync Visuals with Speech
When using `self.gui.show_page()`, try to synchronize the visual information with the spoken response. Don't overwhelm the user with too much text on the screen while the assistant is speaking.

```python
def handle_weather_intent(self, message):
    self.gui["temperature"] = "21°C"
    self.gui.show_page("weather.qml", override_idle=60)
    self.speak_dialog("weather", {"temperature": 21})
```

---

*Source code: [OpenVoiceOS/ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop).*

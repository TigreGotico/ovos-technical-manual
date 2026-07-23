# Developer FAQ

!!! abstract "In a nutshell"
    Short answers to specific "how do I…?" questions that come up while writing a skill. Skim
    it when you hit one of these; it assumes you've already built a basic skill (start with
    [Your First Skill](first-skill.md) if not). If you don't write skills, you can skip this page.

## How do I know if a screen / GUI client is available?

`ovos_utils.gui` exposes helper functions to query GUI availability. Use these to decide whether to show a page or fall back to voice-only behavior.

```python
from ovos_utils.gui import can_display, is_gui_installed, is_gui_connected
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler


class MySkill(OVOSSkill):

    @intent_handler("gui.status.intent")
    def handle_status_intent(self, message):
        print("device has a screen:", can_display())
        print("mycroft-gui installed:", is_gui_installed())
        print("gui client connected:", is_gui_connected(self.bus))
        if is_gui_connected(self.bus):
            self.gui.show_text("Hello from the GUI!")
        else:
            self.speak("I have nothing to show, no screen is connected")
```

> The legacy `GUITracker` class has been **removed** from `ovos_utils.gui`. Use the standalone `can_display()`, `is_gui_installed()`, and `is_gui_connected(bus)` functions instead. To react to GUI lifecycle events, listen to the relevant `gui.*` messagebus messages with `self.add_event(...)`.

## How do I stop an intent mid execution?

Sometimes you want to abort a running intent immediately, the stop method may not be enough in some circumstances
we provide a `killable_intent` decorator in `ovos_workshop` that can be used to abort a running intent immediately

a common use case is for GUI interfaces where the same action may be done by voice or clicking buttons, in this case you may need to abort a running `get_response` loop

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import killable_intent, intent_handler
from time import sleep


class Test(OVOSSkill):
    """
    send "mycroft.skills.abort_question" and confirm only get_response is aborted
    send "mycroft.skills.abort_execution" and confirm the full intent is aborted, except intent3
    send "my.own.abort.msg" and confirm intent3 is aborted
    say "stop" and confirm all intents are aborted
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_special_var = "default"

    def handle_intent_aborted(self):
        self.speak("I am dead")
        # handle any cleanup the skill might need, since intent was killed
        # at an arbitrary place of code execution some variables etc. might
        # end up in unexpected states
        self.my_special_var = "default"

    @killable_intent(callback=handle_intent_aborted)
    @intent_handler("test.intent")
    def handle_test_abort_intent(self, message):
        self.my_special_var = "changed"
        while True:
            sleep(1)
            self.speak("still here")

    @intent_handler("test2.intent")
    @killable_intent(callback=handle_intent_aborted)
    def handle_test_get_response_intent(self, message):
        self.my_special_var = "CHANGED"
        ans = self.get_response("question", num_retries=99999)
        self.log.debug("get_response returned: " + str(ans))
        if ans is None:
            self.speak("question aborted")

    @killable_intent(msg="my.own.abort.msg", callback=handle_intent_aborted)
    @intent_handler("test3.intent")
    def handle_test_msg_intent(self, message):
        if self.my_special_var != "default":
            self.speak("someone forgot to cleanup")
        while True:
            sleep(1)
            self.speak("you can't abort me")

```

## How do I send files over the bus?

Sometimes you may want to send files or binary data over the messagebus, `ovos_utils` provides some tools to make this easy

Sending a file

```python
from ovos_bus_client.util import send_binary_file_message, decode_binary_message
from ovos_workshop.skills import OVOSSkill


class MySkill(OVOSSkill): 
    def initialize(self):
        self.add_event("mycroft.binary.file", self.receive_file)
    
    def receive_file(self, message):
        print("Receiving file")
        path = message.data["path"]  # file path, extract filename if needed
        binary_data = decode_binary_message(message)
        # Insert logic to process the data
        
    def send_file(self, my_file_path):
        # pass self.bus explicitly — otherwise a brand new bus connection is
        # opened and closed just for this one message
        send_binary_file_message(my_file_path, bus=self.bus)

```

Sending binary data directly

```python
from ovos_bus_client.util import send_binary_data_message, decode_binary_message
from ovos_workshop.skills import OVOSSkill


class MySkill(OVOSSkill):
    def initialize(self):
        self.add_event("mycroft.binary.data", self.receive_binary)
    
    def send_data(self, binary_data):
        # pass self.bus explicitly — otherwise a brand new bus connection is
        # opened and closed just for this one message
        send_binary_data_message(binary_data, bus=self.bus)

    def receive_binary(self, message):
        print("Receiving binary data")
        binary_data = decode_binary_message(message)
         # Insert logic to process the data

```

---

Didn't find your question here? Ask in the
[skills channel on OVOS Chat](https://matrix.to/#/#openvoiceos-skills:matrix.org).


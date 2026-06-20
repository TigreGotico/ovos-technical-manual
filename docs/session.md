# Session Aware Skills

> Specification: [OVOS-SESSION-1](https://github.com/OpenVoiceOS/architecture/blob/dev/ovos-session-1.md) (Session wire shape) and [OVOS-SESSION-2](https://github.com/OpenVoiceOS/architecture/blob/dev/ovos-session-2.md) (Session lifecycle & state ownership)

**What / why (beginners):** a single OVOS device can be talking to many clients at once — your phone, a kitchen satellite, a HiveMind node. Each request arrives carrying a `Session` that identifies *who* is asking and *in what language*. If your skill stores any state (a chat history, a game in progress, a "current selection"), you must key that state by `session_id` instead of stashing it in a single instance variable — otherwise two users would clobber each other.

If you want your skills to handle simultaneous users you need to make them [Session](session.md) aware

Each remote client, usually a [voice satellite](https://jarbashivemind.github.io/HiveMind-community-docs/07_voicesat/), will send a `Session` with the `Message`

Your skill should keep track of any Session specific state separately, eg, a chat history

> **WARNING**: Stateful Skills need to be Session Aware to play well with [HiveMind](https://jarbashivemind.github.io/HiveMind-community-docs/)

## SessionManager

You can access the `Session` in a `Message` object via the `SessionManager` class

```python
from ovos_bus_client.session import SessionManager, Session

class MySkill(OVOSSkill):

    def on_something(self, message):
        sess = SessionManager.get(message)
        print(sess.session_id)

```

If the message originated in the device itself, the `session_id` is always equal to `"default"`, if it comes from an external client then it will be a unique uuid

## Magic Properties

Skills have some "magic properties", these will always reflect the value in the current `Session`

```python
    # magic properties -> depend on message.context / Session
    @property
    def lang(self) -> str:
        """
        Get the current language as a BCP-47 language code. This will consider
        current session data if available, else Configuration.
        """
        
    @property
    def location(self) -> dict:
        """
        Get the JSON data struction holding location information.
        This info can come from Session
        """

    @property
    def location_pretty(self) -> Optional[str]:
        """
        Get a speakable city from the location config if available
        This info can come from Session
        """

    @property
    def location_timezone(self) -> Optional[str]:
        """
        Get the timezone code, such as 'America/Los_Angeles'
        This info can come from Session
        """
        
    @property
    def dialog_renderer(self) -> Optional[MustacheDialogRenderer]:
        """
        Get a dialog renderer for this skill. Language will be determined by
        message context to match the language associated with the current
        session or else from Configuration.
        """

    @property
    def resources(self) -> SkillResources:
        """
        Get a SkillResources object for the current language. Objects are
        initialized for the current Session language as needed.
        """

```

## Per User Interactions

Let's consider a skill that keeps track of a chat history, how would such a skill keep track of `Sessions`?

```python
from ovos_bus_client.session import SessionManager, Session
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill


class UtteranceRepeaterSkill(OVOSSkill):

    def initialize(self):
        self.chat_sessions = {}
        self.add_event('recognizer_loop:utterance', self.on_utterance)

    # keep chat history per session
    def on_utterance(self, message):
        utt = message.data['utterances'][0]
        sess = SessionManager.get(message)
        if sess.session_id not in self.chat_sessions:
            self.chat_sessions[sess.session_id] = {"current_stt": ""}
        self.chat_sessions[sess.session_id]["prev_stt"] = self.chat_sessions[sess.session_id]["current_stt"]
        self.chat_sessions[sess.session_id]["current_stt"] = utt

    # retrieve previous STT per session
    @intent_handler('repeat.stt.intent')
    def handle_repeat_stt(self, message):
        sess = SessionManager.get(message)
        if sess.session_id not in self.chat_sessions:
            utt = self.resources.render_dialog('nothing')
        else:
            utt = self.chat_sessions[sess.session_id]["prev_stt"]
        self.speak_dialog('repeat.stt', {"stt": utt})
            
    # session specific stop event 
    # if this method returns True then self.stop will NOT be called
    def stop_session(self, session: Session):
        if session.session_id in self.chat_sessions:
            self.chat_sessions.pop(session.session_id)
            return True
        return False

```

A full example can be found in the [parrot skill](https://github.com/OpenVoiceOS/skill-ovos-parrot)

# Session Aware Skills

!!! abstract "In a nutshell"
    One OVOS device can talk to several people at once: your phone, a kitchen speaker, and other connected devices may all be asking it things at the same time. A *session* is simply the information that says who is asking and in what language. If your skill remembers anything between requests, like a running game or a chat history, it needs to keep each person's information separate so two users don't get each other's answers, much like separate tables at a restaurant. This page shows how to make a skill session aware. New terms are explained in the [Glossary](glossary.md).

!!! info "📐 Formal specification"
    The session's wire shape and field registry are specified by **[OVOS-SESSION-1 — Session Carrier](https://github.com/OpenVoiceOS/architecture/blob/dev/session-1.md)**; who owns and may mutate session state, and the reserved `"default"` device-local session, by **[OVOS-SESSION-2 — Session Lifecycle & State Ownership](https://github.com/OpenVoiceOS/architecture/blob/dev/session-2.md)**; and the decaying per-session `intent_context` that gates which intents may match across turns by **[OVOS-CONTEXT-1 — Intent Context](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-context.md)**. See also the [spec index](architecture-specs.md). SESSION-1 is the field registry; other specs *claim* fields into it (e.g. `intent_context` → CONTEXT-1, the transformer-chain lists → OVOS-TRANSFORM-1).

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

If the message originated in the device itself, the `session_id` is always equal to the reserved value `"default"`; if it comes from an external client then it will be a unique uuid. The `"default"` session is special: it is the device-local session whose state the orchestrator holds and persists in-process, rather than receiving it from a client on every message (OVOS-SESSION-2 §5).

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

A full example can be found in the [parrot skill](https://github.com/OpenVoiceOS/ovos-skill-parrot)

# Intent Layers

!!! abstract "In a nutshell"
    Normally a skill listens for all of its commands at once. Intent Layers let a skill turn commands on and off as a conversation progresses, so only the choices that make sense right now are available — much like a "choose your own adventure" book where each page unlocks the next set of options. This is handy for step-by-step flows, games, or anything that should react differently depending on what the user just did. For the broader picture, see the [Glossary](glossary.md).

??? info "📐 Formal specification"
    `IntentLayer` gating is implemented through the session's **intent context** — each layer is a session context token its intents require. The mechanism is specified by **[OVOS-CONTEXT-1 — Intent Context](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-context.md)** (see [Context](context.md) and the [spec index](architecture-specs.md)).

!!! tip "`IntentLayers` are per-session"
    `IntentLayer` state lives in the **session**, so layered skills are concurrency-safe across [HiveMind](https://jarbashivemind.github.io/HiveMind-community-docs/) satellites — two satellites can be in different layers at the same time. (The lower-level `enable_intent` / `disable_intent` calls in the next section still change the **global** intent set, so prefer layers for per-session flows.)

!!! note "Not the same as skill permissions"
    Intent layers switch groups of *intents* on and off inside one already-active skill. Whether a skill is even allowed to participate in converse at all (whitelists, blacklists, `ConverseMode`) is a separate, coarser gate — see [Permissions & Activation Control](permissions.md).

## Managing Intents

Sometimes you might want to manually enable or disable an intent, in OVOSSkills you can do this explicitly to create stateful interactions

```python
class RotatingIntentsSkill(OVOSSkill):

    def initialize(self):
        # NOTE: this must be done in initialize, not in __init__
        self.disable_intent("B.intent")
        self.disable_intent("C.intent")
        
    @intent_handler("A.intent")
    def handle_A_intent(self, message):
        # do stuff
        self.enable_intent("B.intent")
        self.disable_intent("A.intent")

    @intent_handler("B.intent")
    def handle_B_intent(self, message):
        # do stuff
        self.enable_intent("C.intent")
        self.disable_intent("B.intent")
        
    @intent_handler("C.intent")
    def handle_C_intent(self, message):
        # do stuff
        self.enable_intent("A.intent")
        self.disable_intent("C.intent")

```

> **NOTE**: `enable_intent` / `disable_intent` change the **global** intent set — these states are shared across [Sessions](session.md). For per-session gating, use [Intent Layers](#decorators) (which gate via intent context) instead.


## State Machines

Another utils provided by `ovos-workshop` is `IntentLayers`, to manage groups of intent together

`IntentLayers` lend themselves well to implement state machines.

### The Manual way

In this example we implement the [Konami Code](https://en.wikipedia.org/wiki/Konami_Code), doing everything the manual way instead of using decorators

![State diagram of the Konami Code intent layers: up1 and up2 lead to down1 and down2, then left1/right1, left2/right2, and finally the B and A layers before resetting](https://github.com/OpenVoiceOS/ovos-technical-manual/assets/33701864/13b9de20-1f8d-44b3-9b65-c13a79a41b1e)

```python
class KonamiCodeSkill(OVOSSkill):
    def initialize(self):
        self.counter = 0
        self.top_fails = 3
        
        up_intent = IntentBuilder('KonamiUpIntent').require("KonamiUpKeyword").build()
        down_intent = IntentBuilder('KonamiDownIntent').require("KonamiDownKeyword").build()
        left_intent = IntentBuilder('KonamiLeftIntent').require("KonamiLeftKeyword").build()
        right_intent = IntentBuilder('KonamiRightIntent').require("KonamiRightKeyword").build()
        b_intent = IntentBuilder('KonamiBIntent').require("KonamiBKeyword").build()
        a_intent = IntentBuilder('KonamiAIntent').require("KonamiAKeyword").build()

        self.register_intent(up_intent, self.handle_up_intent)
        self.register_intent(down_intent, self.handle_down_intent)
        self.register_intent(left_intent, self.handle_left_intent)
        self.register_intent(right_intent, self.handle_right_intent)
        self.register_intent(b_intent, self.handle_b_intent)
        self.register_intent(a_intent, self.handle_a_intent)

    def build_intent_layers(self):
        self.intent_layers.update_layer("up1", ["KonamiUpIntent"])
        self.intent_layers.update_layer("up2", ["KonamiUpIntent"])
        self.intent_layers.update_layer("down1", ["KonamiDownIntent"])
        self.intent_layers.update_layer("down2", ["KonamiDownIntent"])
        self.intent_layers.update_layer("left1", ["KonamiLeftIntent"])
        self.intent_layers.update_layer("right1",["KonamiRightIntent"])
        self.intent_layers.update_layer("left2", ["KonamiLeftIntent"])
        self.intent_layers.update_layer("right2",["KonamiRightIntent"])
        self.intent_layers.update_layer("B",["KonamiBIntent"])
        self.intent_layers.update_layer("A",["KonamiAIntent"])
        
        self.intent_layers.activate_layer("up1")

    def reset(self):
        self.active = False
        self.counter = 0
        self.intent_layers.disable()
        self.intent_layers.activate_layer("up1")
        
    def handle_up_intent(self, message):
        if self.intent_layers.is_active("up1"):
            self.intent_layers.deactivate_layer("up1")
            self.intent_layers.activate_layer("up2")
        else:
            self.intent_layers.activate_layer("down1")
            self.intent_layers.deactivate_layer("up2")
        self.acknowledge()

    def handle_down_intent(self, message):        
        if self.intent_layers.is_active("down1"):
            self.intent_layers.deactivate_layer("down1")
            self.intent_layers.activate_layer("down2")
        else:
            self.intent_layers.activate_layer("left1")
            self.intent_layers.deactivate_layer("down2")
        self.acknowledge()

    # handle_left_intent, handle_right_intent, and handle_b_intent follow the
    # same pattern: check which layer of the pair is active, deactivate it,
    # and activate the next layer in the sequence (left1/left2, then
    # right1/right2, then "B", then "A")

    def handle_a_intent(self, message):
        self.play_audio(self.find_resource("power_up.mp3", "snd"))
        self.reset()

    def stop(self):
        if self.active:
            self.reset()

    def converse(self, message):
        if self.active:
            if not any(self.voc_match(utt, kw) for kw in ["KonamiUpKeyword", 
                                                          "KonamiDownKeyword", 
                                                          "KonamiLeftKeyword", 
                                                          "KonamiRightKeyword", 
                                                          "KonamiBKeyword", 
                                                          "KonamiAKeyword"]):
                self.counter += 1
                if self.counter > self.top_fails:
                    self.speak("Wrong cheat code")
                    self.reset()
                else:
                    self.speak("Wrong! Try again")
                return True
        return False

```

### Decorators

When you have many complex chained intents `IntentLayers` often makes your life easier, a layer is a named group of intents that you can manage at once.

Slightly more complex than the previous example, we may want to offer several "forks" on the intent execution, enabling different intent groups depending on previous interactions

[skill-moon-game](https://github.com/JarbasSkills/skill-moon-game/) is an example full voice game implemented this way

An excerpt from the game to illustrate usage of `IntentLayer` decorators

> **NOTE**: `IntentLayers` are **per-session** — gated via [intent context](context.md) ([OVOS-CONTEXT-1](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-context.md)), so each [voice satellite](https://jarbashivemind.github.io/HiveMind-community-docs/07_voicesat/) keeps its own layer state instead of all joining the same game.

```python
from ovos_workshop.decorators.layers import layer_intent, enables_layer, \
    disables_layer, resets_layers


class Apollo11GameSkill(OVOSSkill):

    def initialize(self):
        # start with all game states disabled
        self.intent_layers.disable()

    @intent_handler(IntentBuilder("StartApollo11Intent"). \
                    optionally("startKeyword"). \
                    require("MoonGameKeyword"))
    def handle_start_intent(self, message=None):
        if not self.playing:
            self.playing = True
            self.speak_dialog("start.game")
            self.handle_intro()
        else:
            self.speak_dialog("already.started")

    @layer_intent(IntentBuilder("StopApollo11Intent"). \
                  require("stopKeyword"). \
                  optionally("MoonGameKeyword"),
                  layer_name="stop_game")
    @resets_layers()
    def handle_game_over(self, message=None):
        if self.playing:
            self.speak_dialog("stop.game")

    @enables_layer(layer_name="guard")
    @enables_layer(layer_name="stop_game")
    def handle_intro(self):
        self.speak_dialog("reach_gate")
        self.speak_dialog("guard")
        self.speak_dialog("present_id", expect_response=True)

    @layer_intent(IntentBuilder("Yes1Apollo11Intent").require("yesKeyword"),
                  layer_name="guard")
    def handle_yes1(self, message=None):
        self.speak_dialog("guard_yes")
        self.briefing_question1()

    @layer_intent(IntentBuilder("No1Apollo11Intent").require("noKeyword"),
                  layer_name="guard")
    @enables_layer(layer_name="guard2")
    @disables_layer(layer_name="guard")
    def handle_no1(self, message=None):
        self.speak_dialog("guard_no")
        self.speak_dialog("present_id", expect_response=True)
        
    # (...) more intent layers
    
    def converse(self, message):
        if not self.playing:
            return False
        # (...)
        # take corrective action when no intent matched
        if self.intent_layers.is_active("guard") or \
                self.intent_layers.is_active("guard2"):
            self.speak_dialog("guard_dead")
            self.handle_game_over()
        # (...)
        else:
            self.speak_dialog("invalid.command", expect_response=True)
        return True

```

### Under the hood

`self.intent_layers` is an instance of `IntentLayers`
(`ovos_workshop.decorators.layers.IntentLayers`), created lazily the first time a layer
decorator or `layer_intent` runs and bound to the skill instance.

A layer is **not** a separate matching mechanism — it's a named group of intents mapped to a
single synthetic [intent context](context.md) token (`layer_<name>`, prefixed internally with
the skill id). Every intent registered under that layer is set to *require* the token, so:

- `activate_layer("guard")` calls `self.set_context(...)` for the layer's token — the layer's
  intents become matchable.
- `deactivate_layer("guard")` calls `self.remove_context(...)` — they stop matching again.
- The intents themselves stay registered with the intent service for the skill's whole
  lifetime; only whether their required context is present changes. There's no
  detach/re-attach churn.

Because layer state rides on intent context, and intent context is per-session, each
[voice satellite](https://jarbashivemind.github.io/HiveMind-community-docs/07_voicesat/)
talking to a shared skill keeps its own independent set of active layers.

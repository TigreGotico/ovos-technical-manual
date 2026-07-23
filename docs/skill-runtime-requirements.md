# Runtime Requirements in OVOS

!!! warning "Deprecated — legacy reference"
    `RuntimeRequirements` is a deprecated mechanism, kept documented here for existing skills
    that already declare it. There is currently no successor mechanism in `ovos-utils`/
    `ovos-workshop`. New skills should not be built around it.

!!! abstract "In a nutshell"
    Some skills only make sense under certain conditions — a weather skill needs internet, a smart-home skill needs the local network, a picture skill needs a screen. "Runtime requirements" is a legacy declaration where a skill states what it needs, so OVOS can optionally defer loading it until those things are available. For where this fits in a skill's lifecycle see [Skill Classes](skill-classes.md); for term definitions see the [Glossary](glossary.md).

`RuntimeRequirements` lets a skill declare, up front, what conditions (internet, network, GUI) it needs — historically intended to let OVOS defer loading a skill until the system is ready for it, and to skip premature activation on offline, headless, or GUI-enabled setups.

---

## Usage Guide

### Step 1: Customize `ready_settings` (boot-finished skill)

The `mycroft.ready` message — signalling that the device has finished booting — is
not emitted by `ovos-core` itself. It comes from the `ovos-skill-boot-finished`
skill, which polls the other services and emits `mycroft.ready` once they all
report ready. Configure what it waits for through **that skill's own settings**
(`ready_settings`), not a global core config key:

```json
{
  "ready_settings": [
    "skills",
    "network_skills",
    "internet_skills",
    "audio",
    "speech"
  ]
}

```

This is the skill's `settings.json` (see [Skill Settings](skill-settings.md)),
not `mycroft.conf`. In this example, boot-finished is configured to wait for
network and internet connectivity, plus the audio and speech services, before
emitting `mycroft.ready`. Each setup can customize this list based on its
needs — an offline install won't want to wait on internet-dependent skills, a
headless server won't want to wait on an audio stack, etc. If `ready_settings`
is not set, the skill defaults to waiting for `skills` plus every currently
installed skill_id.

### Step 2: Define `RuntimeRequirements` in your skill

Use the `runtime_requirements` class property to control when and how your skill should load based on system resources like internet, network, or GUI.

Example:

```python
from ovos_utils import classproperty
from ovos_workshop.skills import OVOSSkill
from ovos_utils.process_utils import RuntimeRequirements

class MySkill(OVOSSkill):

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(
            requires_internet=True
        )

```

---

## Technical Explanation

### `ready_settings`

`ready_settings` is a setting on the `ovos-skill-boot-finished` skill; it controls when that skill emits `mycroft.ready`, which signals that the system is ready for use. Each entry in the list waits for a different component:

- **"skills"** – Waits for `ovos-core` to report ready.


- **"network_skills"** / **"network"** – Waits for the system to detect a network connection (`mycroft.network.connected`).


- **"internet_skills"** / **"internet"** – Waits for an internet connection (`mycroft.internet.connected`).


- **"gui_connected"** – Waits for a GUI client to connect over the GUI socket.


- **"voice"** – Waits for `ovos-dinkum-listener` to report ready.


- **"audio"** – Waits for `ovos-audio` to report ready.


- **"gui"** – Waits for the `ovos-gui` websocket to report ready.


- **"PHAL"** – Waits for PHAL to report ready.


- **{skill_id}** – Waits for a specific skill to be available.

Any other name is treated generically: the skill waits for a `mycroft.<name>.is_ready` response, so third-party services can plug into the same mechanism.

> ⚠️ **Note**: If `ready_settings` is not configured, the skill defaults to
> waiting for `skills` plus every currently installed skill_id. Because OVOS
> supports dynamic skill loading (skills can load and unload after startup),
> timing can impact anything that depends on the `mycroft.ready` message.

---

## Deferred Loading (before-load gating only)

`ovos-core`'s `SkillManager` can defer loading a skill until its declared requirements are
met — a skill with `internet_before_load=True` is not instantiated until the internet
connection event fires, and likewise for `network_before_load` and `gui_before_load`. This
gating is **opt-in**: it only applies when `skills.use_deferred_loading` is set to `true` in
config. With the default configuration (`use_deferred_loading` unset/`false`), all installed
skills load unconditionally at startup regardless of their declared requirements.

```json
{
  "skills": {
    "use_deferred_loading": true
  }
}

```

### Benefits (when deferred loading is enabled):

- Reduces memory and CPU usage.


- Avoids unnecessary skill activations.


- Simplifies skill logic (e.g., no need to check for connectivity manually before doing network I/O in `initialize()`).

`requires_internet`, `requires_network`, and `requires_gui` are also present on
`RuntimeRequirements`, but they do not currently trigger an unload — `SkillManager`'s
connection-loss handlers exist as no-op placeholders, so a running skill is **not** unloaded
when a required resource disappears. Only the before-load gate above is active.

---

## RuntimeRequirements (`@classproperty`)

The `RuntimeRequirements` class property lets a skill declare its connectivity/GUI needs.

> ⚠️ Replaces the older, now-removed `"priority_skills"` config option.

### Key fields:

| Field                 | Description |
|----------------------|-------------|
| `internet_before_load` | Wait for internet before loading (requires `skills.use_deferred_loading: true`) |
| `requires_internet`     | Declares the skill needs internet to work |
| `no_internet_fallback` | Declares the skill can keep working without internet |
| `network_before_load`  | Wait for network before loading (requires `skills.use_deferred_loading: true`) |
| `requires_network`     | Declares the skill needs network to work |
| `gui_before_load`      | Wait for GUI before loading (requires `skills.use_deferred_loading: true`) |
| `requires_gui`         | Declares the skill needs a GUI to work |
| `no_gui_fallback`      | Declares the skill can keep working without a GUI |

> 🧠 Uses `@classproperty` so the system can evaluate the requirements without loading the skill.

---

## Examples

### 1. Fully Offline [Skill](skill-design-guidelines.md)

In this example, a fully offline skill is defined. The skill does not require internet or network connectivity during
loading or runtime. If the network or internet is unavailable, the skill can still operate.

Defining this documents that your skill has no connectivity needs; with `skills.use_deferred_loading: true` it also ensures the skill loads as soon as possible instead of waiting on internet.

```python
from ovos_utils import classproperty
from ovos_workshop.skills import OVOSSkill
from ovos_utils.process_utils import RuntimeRequirements


class MyOfflineSkill(OVOSSkill):

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(internet_before_load=False,
                                   network_before_load=False,
                                   requires_internet=False,
                                   requires_network=False,
                                   no_internet_fallback=True,
                                   no_network_fallback=True)

```
Documents that the skill needs neither internet nor network.

---

### 2. Internet-Dependent Skill (with fallback)

In this example, an online search skill with a local cache is defined. The skill declares that it requires internet
connectivity to work. With `skills.use_deferred_loading: true`, it also won't load until internet is available.

Our skill keeps a cache of previous results, so it declares `no_internet_fallback=True` to document that it can
tolerate internet outages once running.

```python
from ovos_utils import classproperty
from ovos_workshop.skills import OVOSSkill
from ovos_utils.process_utils import RuntimeRequirements


class MyInternetSkill(OVOSSkill):

    @classproperty
    def runtime_requirements(self):
        # our skill can answer cached results when the internet goes down
        return RuntimeRequirements(
            internet_before_load=True,  # only load once we have internet (needs deferred loading)
            requires_internet=True,  # indicate we need internet to work
            no_internet_fallback=True  # documents that a cached fallback exists
        )

    def initialize(self):
        ...  # do something that requires internet connectivity

```
With `skills.use_deferred_loading: true`, loads only once internet is available.

---

### 3. LAN-Controlled IOT Skill

Consider a skill that should only load once we have a network connection.
By specifying that requirement (with `skills.use_deferred_loading: true`), we can ensure the
skill is only loaded once the network is available, and it is safe to utilize network
resources on initialization.

In this example, an IOT skill controlling devices via LAN is defined.

`no_network_fallback=False` documents that the skill cannot cope without network.

```python
from ovos_utils import classproperty
from ovos_workshop.skills import OVOSSkill
from ovos_utils.process_utils import RuntimeRequirements


class MyIOTSkill(OVOSSkill):

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(
            network_before_load=True,  # only load once network available (needs deferred loading)
            requires_network=True,  # we need network to work
            no_network_fallback=False  # documents that no fallback exists without network
        )

    def initialize(self):
        ...  # do something that needs LAN connectivity

```
With `skills.use_deferred_loading: true`, loads once the local network is connected.

---

### 4. GUI + Internet Skill

Consider a skill with both graphical user interface (GUI) and internet dependencies.

The skill declares both GUI and internet requirements — with `skills.use_deferred_loading: true`,
loading waits until both are available.

If the user asks "show me the picture of the day" and we have both internet and a GUI, our skill will match the intent. If we do not have internet but have a GUI, the skill can still operate using a cached picture — that's what `no_internet_fallback=True` documents.

```python
from ovos_utils import classproperty
from ovos_workshop.skills import OVOSSkill
from ovos_utils.process_utils import RuntimeRequirements


class MyGUIAndInternetSkill(OVOSSkill):

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(
            gui_before_load=True,  # only load if GUI is available (needs deferred loading)
            requires_gui=True,  # documents the skill needs a GUI to work
            internet_before_load=True,  # only load if internet is available (needs deferred loading)
            requires_internet=True,  # documents the skill needs internet to work
            no_gui_fallback=False,  # documents that no fallback exists without a GUI
            no_internet_fallback=True  # documents that a cached fallback exists without internet
        )

    def initialize(self):
        ...  # do something that requires both GUI and internet connectivity

```
With `skills.use_deferred_loading: true`, requires both GUI and internet to load.

---

## Tips and Caveats

- If `runtime_requirements` is not defined, OVOS assumes **internet is required** but **GUI is optional**.


- You can combine different requirements to handle a wide range of usage patterns (e.g., headless servers, embedded devices, smart displays).


- Before-load gating only takes effect with `skills.use_deferred_loading: true`; otherwise
  `RuntimeRequirements` is documentation only and every skill loads unconditionally at startup.

---

*Source code: [OpenVoiceOS/ovos-utils](https://github.com/OpenVoiceOS/ovos-utils).*

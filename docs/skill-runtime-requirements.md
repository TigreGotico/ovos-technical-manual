# Runtime Requirements in OVOS

!!! abstract "In a nutshell"
    Some skills only make sense under certain conditions — a weather skill needs internet, a smart-home skill needs the local network, a picture skill needs a screen. "Runtime requirements" are a short declaration where a skill states what it needs, so OVOS only switches it on when those things are available and quietly switches it off when they're not. This saves resources and avoids odd behavior, a bit like an appliance that won't turn on until it's plugged in. For where this fits in a skill's lifecycle see [Skill Classes](skill-classes.md); for term definitions see the [Glossary](glossary.md).

OVOS (OpenVoiceOS) introduces advanced runtime management to ensure skills are only loaded and active when the system is ready. This improves performance, avoids premature skill activation, and enables greater flexibility across different system setups (offline, headless, GUI-enabled, etc.), controlling when OVOS declares readiness and how dynamic skill loading works.

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

## Dynamic Loading and Unloading

`ovos-core`'s dynamic skill management improves system performance and reliability by **only loading skills once their requirements are met** — a skill with `internet_before_load=True` simply is not instantiated until the internet connection event fires, and likewise for `network_before_load` and `gui_before_load`.

### Benefits:

- Reduces memory and CPU usage.


- Avoids unnecessary skill activations.


- Simplifies skill logic (e.g., no need to check for connectivity manually before doing network I/O in `initialize()`).

Skills are loaded only when their specific requirements are met. This optimization prevents unnecessary loading, conserving system resources and ensuring a more efficient skill environment.

`requires_internet`, `requires_network`, and `requires_gui` describe both
sides of the skill's lifecycle: the **before-load** gate (deferring load
until the resource is available) and the matching **unload** behavior once
the skill is running. When a required resource disappears, `ovos-core`'s
`SkillManager` unloads the skill (`_unload_on_internet_disconnect`,
`_unload_on_network_disconnect`, `_unload_on_gui_disconnect`), unless the
skill has declared the corresponding `no_*_fallback` flag to keep running
without it.

---

## RuntimeRequirements (`@classproperty`)

The `RuntimeRequirements` class property allows skill developers to declare when a skill should be loaded or unloaded based on runtime conditions.

> ⚠️ Replaces the older, now-removed `"priority_skills"` config option.

### Key fields:

| Field                 | Description |
|----------------------|-------------|
| `internet_before_load` | Wait for internet before loading |
| `requires_internet`     | Declares the skill needs internet to work (unloaded if internet is lost, unless `no_internet_fallback` is set) |
| `no_internet_fallback` | Declares the skill can keep working without internet |
| `network_before_load`  | Wait for network before loading |
| `requires_network`     | Declares the skill needs network to work (unloaded if network is lost, unless `no_network_fallback` is set) |
| `gui_before_load`      | Wait for GUI before loading |
| `requires_gui`         | Declares the skill needs a GUI to work (unloaded if the GUI is lost, unless `no_gui_fallback` is set) |
| `no_gui_fallback`      | Declares the skill can keep working without a GUI |

> 🧠 Uses `@classproperty` so the system can evaluate the requirements without loading the skill.

---

## Examples

### 1. Fully Offline [Skill](skill-design-guidelines.md)

In this example, a fully offline skill is defined. The skill does not require internet or network connectivity during
loading or runtime. If the network or internet is unavailable, the skill can still operate.

Defining this will ensure your skill loads as soon as possible; otherwise, the `SkillManager` will wait for internet before loading the skill.

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
Loads immediately, runs without internet or network.

---

### 2. Internet-Dependent Skill (with fallback)

In this example, an online search skill with a local cache is defined. The skill requires internet connectivity during
both loading and runtime. If the internet is not available, the skill won't load. Once loaded, the skill continues to
require internet connectivity.

Our skill keeps a cache of previous results, so it declares it can handle internet outages via `no_internet_fallback=True` — this keeps the skill loaded (rather than unloaded) if internet later goes away.

```python
from ovos_utils import classproperty
from ovos_workshop.skills import OVOSSkill
from ovos_utils.process_utils import RuntimeRequirements


class MyInternetSkill(OVOSSkill):

    @classproperty
    def runtime_requirements(self):
        # our skill can answer cached results when the internet goes down
        return RuntimeRequirements(
            internet_before_load=True,  # only load once we have internet
            requires_internet=True,  # indicate we need internet to work
            no_internet_fallback=True  # do NOT unload if internet goes down
        )

    def initialize(self):
        ...  # do something that requires internet connectivity

```
Loads only when internet is available.

---

### 3. LAN-Controlled IOT Skill

Consider a skill that should only load once we have a network connection.
By specifying that requirement, we can ensure that the skill is only loaded once the requirements are met, and it is
safe to utilize network resources on initialization.

In this example, an IOT skill controlling devices via LAN is defined. The skill requires network connectivity during
loading, and if the network is not available, it won't load.

`no_network_fallback=False` states the skill cannot cope without network, so it will be unloaded if network connectivity is lost.

```python
from ovos_utils import classproperty
from ovos_workshop.skills import OVOSSkill
from ovos_utils.process_utils import RuntimeRequirements


class MyIOTSkill(OVOSSkill):

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(
            network_before_load=True,  # only load once network available
            requires_network=True,  # we need network to work
            no_network_fallback=False  # unload if network goes down
        )

    def initialize(self):
        ...  # do something that needs LAN connectivity

```
Loads when the local network is connected.

---

### 4. GUI + Internet Skill

Consider a skill with both graphical user interface (GUI) and internet dependencies.

The skill requires both GUI availability and internet connectivity during loading — if either is not available, the skill won't load.

If the user asks "show me the picture of the day" and we have both internet and a GUI, our skill will match the intent. If we do not have internet but have a GUI, the skill can still operate using a cached picture — that's what `no_internet_fallback=True` communicates: the skill stays loaded rather than being unloaded when internet later disappears.

```python
from ovos_utils import classproperty
from ovos_workshop.skills import OVOSSkill
from ovos_utils.process_utils import RuntimeRequirements


class MyGUIAndInternetSkill(OVOSSkill):

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(
            gui_before_load=True,  # only load if GUI is available
            requires_gui=True,  # continue requiring GUI once loaded
            internet_before_load=True,  # only load if internet is available
            requires_internet=True,  # continue requiring internet once loaded
            no_gui_fallback=False,  # unload if GUI becomes unavailable
            no_internet_fallback=True  # do NOT unload if internet becomes unavailable, use cached picture
        )

    def initialize(self):
        ...  # do something that requires both GUI and internet connectivity

```
Requires both GUI and internet to load.

---

## Tips and Caveats

- If `runtime_requirements` is not defined, OVOS assumes **internet is required** but **GUI is optional**.


- You can combine different requirements to handle a wide range of usage patterns (e.g., headless servers, embedded devices, smart displays).


- Consider defining graceful fallbacks to avoid unnecessary unloading.

---

*Source code: [OpenVoiceOS/ovos-utils](https://github.com/OpenVoiceOS/ovos-utils).*

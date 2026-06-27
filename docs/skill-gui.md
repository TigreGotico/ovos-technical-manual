# GUI Skills (GUIInterface)

!!! abstract "In a nutshell"
    When an OVOS device has a screen, a skill can show things on it — text, images, a page of results — not just speak. This page describes the small Python toolkit a skill author uses to push data to the screen and ask for a page to be displayed. It is a developer topic, and the screen system is being rebuilt (see [GUI Adapters](gui-adapters.md)), so voice should stay the main way you interact while the screen support is treated as a bonus. See the [Glossary](glossary.md) for terms.

!!! danger "The OVOS GUI is deprecated — assume it is not usable today"
    The current **"legacy" OVOS GUI** stack is **deprecated** and should be treated as
    **broken**: **there is no generally usable OVOS GUI right now**. A ground-up replacement
    (the [GUI rework](gui-adapters.md), spec **OVOS-GUI-1**) is actively being built but is
    **not yet ready**. Adding screen support to a skill today only benefits **Mark 2**
    devices, where the [`ovos-installer`](ovos-installer.md) keeps the legacy GUI running
    until the replacement lands. This page documents the legacy API for reference and Mark 2
    maintenance — voice should remain the primary interface.

!!! info "📐 Formal specification"
    The **forward** model a skill targets is **[OVOS-GUI-1 — GUI Display Subsystem](https://github.com/OpenVoiceOS/architecture/blob/dev/gui-1.md)** (a formal [architecture spec](architecture-specs.md)). Under it, `self.gui` declares display intent by naming a template from the **closed `SYSTEM_*` vocabulary** (`SYSTEM_text`, `SYSTEM_image`, `SYSTEM_list`, `SYSTEM_weather`, `SYSTEM_confirm`, …) and pushing flat session-data; interchangeable **render backends** draw it, routed by `session_id`. Two rules matter for skill authors: a skill **MUST NOT** invent template names or ship its own home/resting screen (the resting display is owned entirely by the backend, §6.9), and image keys carry an `http(s)` URL or `data:` URI — **never a local filesystem path**. The `show_*` helpers below map onto these templates; the custom-`.qml` path is legacy and unsupported under OVOS-GUI-1. Where this page and the spec differ, the spec is the canonical target.

Many OVOS devices have a screen. A skill can drive that screen the same way it
speaks: through a small Python API. You set some values, ask for a page to be
shown, and any connected GUI client (Qt shell, web, terminal, ...) renders it.

**In plain terms:** `self.gui` is a dict-like object. You put data in it
(`self.gui["name"] = "OVOS"`), then call a `show_*` method to display a page.

Under the hood, `self.gui` is a `SkillGUI` instance (a subclass of `GUIInterface`)
created automatically for every `OVOSSkill`. On current `ovos-workshop` v8 the base class
lives in `ovos_bus_client.apis.gui.GUIInterface`; the skill wrapper is
`ovos_workshop.skills.ovos.SkillGUI`, namespaced to your `skill_id`.

!!! warning "Upcoming — unreleased"
    [OpenVoiceOS/ovos-workshop#420](https://github.com/OpenVoiceOS/ovos-workshop/pull/420)
    (`feat!: bind OVOSSkill.gui to ovos-gui-api-client`) rebinds `self.gui` to a
    `GUIInterface` from the standalone **`ovos-gui-api-client`** package (instead of
    `ovos_bus_client.apis.gui`) and drops the `ui_directories` constructor argument, since
    skills under the [GUI rework](gui-service.md) no longer ship QML. This is **not** on a
    released `ovos-workshop`; on stable installs `self.gui` is still the
    `ovos_bus_client.apis.gui.GUIInterface`-based `SkillGUI` described above.

## Quick start

```python
def handle_hello(self, message):
    self.gui["name"] = "OpenVoiceOS"
    self.gui.show_text("Hello from OVOS!")
```

`self.gui` behaves like a dictionary — values you set are synced to the active
page whenever it (re)renders. The keys you set are visible to the page under the
skill's namespace.

---

## Standard page templates

To get a unified look and feel without writing any UI code, `GUIInterface`
provides ready-made `SYSTEM_*` page templates. You call a helper, it sets the
needed values and shows the matching template. These render on every GUI client
according to its local capabilities.

#### Text

Display simple strings of text (auto-paginated).

```python
gui.show_text(text, title=None, override_idle=None, override_animations=False)
```

#### Static Image

Display a static image such as a jpeg or png.

```python
gui.show_image(url, caption=None, title=None, fill=None,
               background_color=None, override_idle=None,
               override_animations=False)
```

`fill` accepts `"PreserveAspectFit"`, `"PreserveAspectCrop"`, or `"Stretch"`.
`url` may be a local file path or an `http(s)` URL; missing local files are
logged and the call returns without showing anything.

#### Animated Image

Display an animated image such as a gif (same arguments as `show_image`).

```python
gui.show_animated_image(url, caption=None, title=None, fill=None,
                        background_color=None, override_idle=None,
                        override_animations=False)
```

#### HTML Snippet

Display a local HTML snippet. Complex JavaScript may not be supported by all
clients.

```python
gui.show_html(html, resource_url=None, override_idle=None,
              override_animations=False)
```

#### Remote URL

Display a webpage. Only supported by clients with a full browser engine.

```python
gui.show_url(url, override_idle=None, override_animations=False)
```

#### Input Box

Show a fullscreen text-entry UI with confirm/cancel buttons.

```python
gui.show_input_box(title=None, placeholder=None, confirm_text=None,
                   exit_text=None, override_idle=None,
                   override_animations=False)
```

#### Notifications

```python
gui.show_notification(content, duration=10, action=None,
                      noticetype="transient", style="info", callback_data=None)
gui.show_controlled_notification(content, style="info")
gui.remove_controlled_notification()
```

`style` is one of `info`, `warning`, `success`, `error`; `noticetype` is
`transient` (auto-timeout) or `sticky`.

!!! note "`override_idle`"
    `override_idle=True` keeps your page up indefinitely; an `int` delays the
    return to the idle/home screen for that many seconds. `override_animations=True`
    disables platform transition animations for the page.

---

## Custom pages

Templates cover common cases, but you can also ship your own pages. Place a
`gui/` folder in your skill with your UI files and request them by name:

```python
def handle_food_places(self, message):
    self.gui["foodPlaces"] = results
    self.gui.show_page("foodplaces")   # resolves your gui/ resource
```

For the Qt/QML client, custom pages are `.qml` files; see
[Mycroft-GUI QT5](qt5-gui.md) for the QML component reference, theming, event
handling, and resting faces. Other clients resolve the same logical page name to
their own format.

Useful page-control methods:

```python
gui.show_pages(page_names, index=0, override_idle=None,
               override_animations=False, remove_others=False)
gui.remove_page(page)
gui.remove_pages(page_names)
gui.clear()     # reset values + pages (does NOT close the screen)
gui.release()   # tell the platform the skill is done with the screen
```

---

## Usage in Skills

`self.gui` provides a `GUIInterface` under the `self.skill_id` namespace, so two
skills setting `self.gui["name"]` never collide.

```python
def handle_hello(self, message):
    self.gui["name"] = "OpenVoiceOS"
    self.gui.show_text("Hello from OVOS!")
```

To react to clicks/events coming back from the page, register a bus handler:

```python
def initialize(self):
    self.gui.register_handler("skill.foo.event", self.handle_foo_event)

def handle_foo_event(self, message):
    self.speak(message.data["string"])
```

For OCP media players and idle/home screens see the
[GUI Service Reference](gui-service.md).

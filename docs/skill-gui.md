# GUI Skills (GUIInterface)

!!! info "NEW IN 2026: THE TEMPLATE-ONLY REFACTOR"
    As of **The Great GUI Refactor (March 2026)**, OVOS has moved to a **template-only architecture**. 
    Skills should no longer provide their own `.qml` or `.html` files for the core GUI service. 
    Instead, skills use a standardized set of **21 templates** (`SYSTEM_*`) that are rendered 
    automatically by any connected GUI adapter (Qt, Web/HTMX, Terminal, etc.).

Any component wanting to implement a GUI for OpenVoiceOS can do so via the `GUIInterface` class
from [ovos-gui-api-client](https://github.com/OpenVoiceOS/ovos-gui-api-client).

!!! warning "DEPRECATION NOTICE"
    `self.gui` in `OVOSSkill` is deprecated as a default property (scheduled for removal in 9.0.0). 
    Skills requiring a GUI should initialize `GUIInterface` explicitly or use specialized mixins.

## Page Templates

To have a unified look and feel, and to allow simple UIs to be integrated into skills without UI framework knowledge, the `GUIInterface` provides **standardized page templates**.

A page template is a semantic UI layout (e.g., `SYSTEM_weather`) that is rendered by gui clients according to their local capabilities.

Skills should only use the provided templates. Providing custom pages is now considered a **Legacy Feature** and is only supported for [Legacy QT5/6 GUI clients](qt5-gui.md).

---

## All Standard Templates

The following methods are available via `GUIInterface`. All arguments follow a standardized schema to ensure they look great on all devices.

#### Text
Display simple strings of text.

```python
gui.show_text(text, title=None, override_idle=None)

```

#### Static Image
Display a static image such as a jpeg or png.

```python
gui.show_image(url, caption=None, title=None, fill="fit")

```

#### Animated Image
Display an animated image such as a gif.

```python
gui.show_animated_image(url, caption=None, title=None)

```

#### HTML Page
Display a local HTML snippet. Note that complex JavaScript may not be supported by all adapters.

```python
gui.show_html(html, resource_url=None)

```

#### Remote URL
Display a webpage. Only supported by adapters with a full browser engine.

```python
gui.show_url(url)

```

---

## Usage in Skills

In OVOS Skills, `self.gui` (via the `ovos-workshop` mixin) provides a `GUIInterface` under the `self.skill_id` namespace.

```python
def handle_hello(self, message):
    self.gui['name'] = "OpenVoiceOS"
    self.gui.show_text("Hello from the new template-only GUI!")

```

For more advanced templates like **Weather**, **Media Players**, or **Clock**, see the [GUI Service Reference](gui-service.md).

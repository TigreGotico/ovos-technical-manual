# Mycroft Mark 1 Hardware

!!! abstract "In a nutshell"
    The **Mark 1** was the original Mycroft smart speaker, recognizable by its little face: a grid of LEDs that forms a scrolling "mouth" and two colored "eyes". This developer page explains how OVOS lets skills control that faceplate — showing text or images on the mouth, and changing the eyes' color, blinking, and animations. It covers both a simple high-level interface and a lower-level library for fine-grained, pixel-by-pixel effects. See the [Glossary](glossary.md) for unfamiliar terms.

The **Mycroft Mark 1** was the first official hardware for Mycroft AI. It features a distinctive faceplate with a 32x8 LED "mouth" and two RGB LED "eyes". OpenVoiceOS provides full support for the Mark 1 hardware, including both a high-level `EnclosureAPI` for common tasks and a low-level `ovos-mark1-utils` library for fine-grained control.

---

## Enclosure API

!!! warning "`self.enclosure` is leaving the skill base class"
    `self.enclosure` will **no longer be a built-in `OVOSSkill` property** — the same direction
    [`self.gui`](skill-gui.md) is going. The `EnclosureAPI` itself is
    **not going away**: it moves into the **[`ovos-mark1-utils`](https://github.com/OpenVoiceOS/ovos-mark1-utils)**
    library, so code that needs it imports it from there rather than reaching for `self.enclosure`.

    In the [GUI rework](gui-adapters.md), the Mark 1 **faceplate** (LED "mouth" + "eyes") is
    remodelled as **one of the new GUI plugins**: the faceplate's bus **event listeners** move
    into that GUI plugin, which renders the standard display events onto the faceplate. Other
    Mark 1 hardware may be handled by a dedicated **mk1 PHAL plugin** (still being decided). This
    page documents the current API for existing Mark 1 skills.

The `EnclosureAPI` is an abstraction over the "body" of the device. It provides a standard way for skills to interact with hardware features like displays and LEDs without needing to know the low-level details of the hardware transport.

```python
from ovos_bus_client.apis.enclosure import EnclosureAPI

api = EnclosureAPI(bus)

```

In a standard `OVOSSkill`, the `EnclosureAPI` is available as `self.enclosure`.

### Drawing to the Mouth Display

The mouth display is a grid of 32x8 pixels. You can send text, which will scroll if it's too long, or draw custom images.

**Displaying Text:**

```python
self.enclosure.mouth_text('The meaning of life, the universe and everything is 42')

```

**Displaying Images (Code):**
Images can be encoded as a string where each character represents 4 pixels.

```python
self.enclosure.mouth_display(img_code="HIAAAAAAAAAAAAAA", refresh=False)

```

**Displaying Images (PNG):**
You can also display 32x8 PNG images.

```python
self.enclosure.mouth_display_png('/path/to/image.png', threshold=70, invert=False, x=0, y=0, refresh=True)

```

---

## Mark 1 Utilities (`ovos-mark1-utils`)

For more advanced control, such as pixel-by-pixel eye manipulation or complex faceplate
animations, use the [ovos-mark1-utils](https://github.com/OpenVoiceOS/ovos-mark1-utils)
library (import name `ovos_mark1`, `pip install ovos-mark1-utils`). It interacts with the
faceplate over the [message bus](bus-service.md) (see the
[PHAL Mark 1 message spec](https://openvoiceos.github.io/message_spec/phal_mk1/)) and offers
three layers:

- **`Mark1EnclosureAPI`** — the high-level enclosure API (mouth text, mouth animations, eye
  colour, system reset). It subclasses the standard `EnclosureAPI` and is what
  `self.enclosure` resolves to on Mark 1 hardware.
- **`Eyes`** — fine-grained eye control (colour, brightness, blink, spins).
- **`FaceplateGrid` / `BlackScreen`** — pixel-level drawing on the 32×8 mouth display, plus
  ready-made icons and animations.

```python
from ovos_mark1 import Mark1EnclosureAPI
from ovos_bus_client.util import get_mycroft_bus

bus = get_mycroft_bus()
enclosure = Mark1EnclosureAPI(bus)
enclosure.mouth_text("hello")
enclosure.eyes_color(255, 0, 0)   # red eyes
```

### Animating the Eyes

```python
from ovos_mark1.eyes import Eyes
from ovos_bus_client.util import get_mycroft_bus

bus = get_mycroft_bus()
eyes = Eyes(bus)
eyes.change_color("blue")  # named colour
eyes.blink()               # blink both eyes
eyes.hue_spin()            # cycle the hue
eyes.on(); eyes.off()      # raw on / off
```

The `Eyes` API also exposes `set_hue` / `set_saturation` / `set_luminance` and their animated
`hue_spin` / `saturation_spin` / `luminance_spin` variants.

### Faceplate Icons

You can define icons using a simple string grid:

```python
from ovos_mark1.faceplate import BlackScreen

class MusicIcon(BlackScreen):
    str_grid = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXX     XXXXXXXXXXXXX
XXXXXXXXXXXXXX     XXXXXXXXXXXXX
XXXXXXXXXXXXXX XXX XXXXXXXXXXXXX
XXXXXXXXXXXXXX XXX XXXXXXXXXXXXX
XXXXXXXXXXXXX  XX  XXXXXXXXXXXXX
XXXXXXXXXXXX   X   XXXXXXXXXXXXX
XXXXXXXXXXXXX XXX XXXXXXXXXXXXXX
"""
    
icon = MusicIcon()
icon.display()  # show in mark1

```

### Faceplate Animations

The library includes base classes for creating dynamic animations, such as cellular automata or particle systems.

```python
from ovos_mark1.faceplate.cellular_automaton import Rule110
from ovos_bus_client.util import get_mycroft_bus
from time import sleep

bus = get_mycroft_bus()
a = Rule110(bus=bus)

for grid in a:
    grid.display(invert=False)
    sleep(0.5)

```

---

## Related Resources

- **[Message Bus Spec - PHAL Mark 1](https://openvoiceos.github.io/message_spec/phal_mk1/)**: Detailed reference for the bus messages used by the Mark 1 enclosure.


- **[ovos-mark1-utils GitHub](https://github.com/OpenVoiceOS/ovos-mark1-utils)**: Source code and additional examples.

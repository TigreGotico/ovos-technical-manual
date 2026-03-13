# Mycroft Mark 1 Hardware

The **Mycroft Mark 1** was the first official hardware for Mycroft AI. It features a distinctive faceplate with a 32x8 LED "mouth" and two RGB LED "eyes". OpenVoiceOS provides full support for the Mark 1 hardware, including both a high-level `EnclosureAPI` for common tasks and a low-level `ovos-mark1-utils` library for fine-grained control.

---

## Enclosure API

The `EnclosureAPI` is an abstraction over the "body" of the device. It provides a standard way for skills to interact with hardware features like displays and LEDs without needing to know the low-level details of the hardware transport.

```python
from ovos_bus_client.apis.enclosure import EnclosureApi

api = EnclosureApi(bus)

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
self.mouth_display_png('/path/to/image.png', threshold=70, invert=False, x=0, y=0, refresh=True)

```

---

## Mark 1 Utilities (`ovos-mark1-utils`)

For more advanced control, such as pixel-by-pixel eye manipulation or complex faceplate animations, use the [ovos-mark1-utils](https://github.com/OpenVoiceOS/ovos-mark1-utils) library.

### Animating the Eyes

```python
from ovos_mark1.eyes import Eyes
from ovos_bus_client.utils import get_mycroft_bus

bus = get_mycroft_bus()
eyes = Eyes(bus)
eyes.hue_spin()

```

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
from ovos_bus_client.utils import get_mycroft_bus
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

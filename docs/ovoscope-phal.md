# PHAL Plugin Testing

!!! abstract "In a nutshell"
    PHAL is the layer of add-ons that lets the assistant talk to physical hardware
    and the operating system, such as adjusting the volume, reading a battery
    level, or controlling a screen. This page is a developer tool for testing
    those add-ons on an ordinary computer, pretending the hardware is there so no
    real device is needed. See the [Glossary](glossary.md).

`ovoscope.phal` provides `MiniPHAL` and `PHALTest` for testing PHAL
(Platform Hardware Abstraction Layer) plugins without physical hardware.

## Why PHAL is Testable

PHAL plugins communicate **exclusively via the MessageBus**, accepting a
`bus` argument in their constructors. `MiniPHAL` injects a `FakeBus` so
plugins behave identically to a real deployment, but no hardware or OS
device access is required.

## Testable Plugins (No Hardware Required)

| Plugin | Trigger | Expected Response |
|--------|---------|-------------------|
| `ovos-PHAL-plugin-connectivity-events` | `network.connected` | `mycroft.internet.connected` |
| `ovos-PHAL-plugin-oauth` | auth-flow messages | auth-result messages |
| `ovos-PHAL-plugin-ipgeo` | `mycroft.internet.connected` | `mycroft.location.update` |
| `ovos-PHAL-plugin-system` | `system.reboot` / `system.shutdown` | confirmation messages |

## Hardware-Dependent Plugins (Out of Scope)

Plugins that require physical hardware are **not suitable** for in-process
testing and should use hardware-in-the-loop integration tests instead:

- `ovos-PHAL-plugin-alsa` — requires ALSA audio subsystem


- `ovos-PHAL-plugin-mk1` — requires Mark 1 hardware


- `ovos-PHAL-plugin-dotstar` — requires APA102 LED ring

## `MiniPHAL` — Context Manager

`MiniPHAL` — `ovoscope/phal.py:43`

```python
from ovos_bus_client.message import Message
from ovoscope.phal import MiniPHAL

with MiniPHAL(
    plugin_ids=["ovos-PHAL-plugin-connectivity-events.openvoiceos"],
) as phal:
    phal.emit(Message("network.connected"))
    msg = phal.assert_emitted("mycroft.internet.connected", timeout=2.0)
    assert msg.data.get("connected") is True

```

### Constructor Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `plugin_ids` | `Optional[List[str]]` | `None` (→ `[]`) | OPM entry-point IDs to load. |
| `plugin_instances` | `Optional[Dict[str, Any]]` | `None` (→ `{}`) | Pre-built plugin instances keyed by `plugin_id`. The instance must already be wired to the harness `FakeBus`, so this only works when you can build the plugin against an externally-supplied bus. |
| `plugin_factories` | `Optional[Dict[str, Callable[[FakeBus], Any]]]` | `None` (→ `{}`) | Callables `(bus) -> plugin` keyed by `plugin_id`, invoked inside `__enter__` so the plugin is always constructed with the harness `FakeBus`. Takes precedence over `plugin_instances` for the same `plugin_id`. |
| `config` | `Optional[Dict[str, Dict[str, Any]]]` | `None` (→ `{}`) | Per-plugin config overrides keyed by `plugin_id`. |

> **`plugin_instances` vs `plugin_factories`.** Pre-built `plugin_instances` are
> handy for injecting mocks, but they are constructed *before* the harness exists,
> so they hold a different bus than the one `MiniPHAL` captures on. Prefer
> `plugin_factories` whenever the plugin needs the harness bus:
>
> ```python
> from ovos_phal_plugin_tools import OVOSToolsPHALPlugin
> from ovoscope.phal import MiniPHAL
> from ovos_bus_client.message import Message
>
> with MiniPHAL(
>     plugin_ids=["ovos-phal-plugin-tools"],
>     plugin_factories={
>         "ovos-phal-plugin-tools": lambda bus: OVOSToolsPHALPlugin(bus=bus),
>     },
> ) as phal:
>     phal.emit(Message("ovos.tools.list", {}))
>     phal.assert_emitted("ovos.tools.list.response")
> ```

### Methods

`MiniPHAL.emit` — `ovoscope/phal.py:146`

| Method | Description |
|--------|-------------|
| `emit(msg, wait=0.05)` | Emit `msg` on the internal bus then sleep `wait` seconds so async handlers have time to fire before the next assertion. Set `wait=0` to disable the sleep. |
| `assert_emitted(msg_type, timeout=2.0)` | Poll captured messages up to `timeout` seconds; return the first matching `Message`. Raises `AssertionError` on timeout. — `ovoscope/phal.py:157` |
| `assert_not_emitted(msg_type, wait=0.2)` | Sleep `wait` seconds then assert no captured message has `msg_type`. Raises `AssertionError` if one was captured. — `ovoscope/phal.py:184` |
| `clear_captured()` | Clear the captured message list. Useful between sequential assertions in the same `with` block. — `ovoscope/phal.py:203` |

#### `emit(wait=...)` — settling delay

The `wait` parameter (default `0.05` s) controls how long `MiniPHAL` sleeps
after calling `bus.emit()`. PHAL plugin handlers may run on a background thread,
so a short settle time is necessary before asserting on results. Increase `wait`
for plugins with higher latency; set `wait=0` to suppress the sleep entirely when
the handler is known to be synchronous.

```python

# Default — 50 ms settle time
phal.emit(Message("network.connected"))

# Custom settle time (slower plugin)
phal.emit(Message("system.reboot"), wait=0.5)

# No sleep (synchronous handler)
phal.emit(Message("config.get"), wait=0)

```

## `PHALTest` — Declarative Style

`PHALTest` — `phal.py:PHALTest`

```python
from ovos_bus_client.message import Message
from ovoscope.phal import PHALTest

PHALTest(
    plugin_ids=["ovos-PHAL-plugin-system.openvoiceos"],
    trigger_message=Message("system.reboot"),
    expected_types=["system.reboot.confirmed"],
    forbidden_types=["system.shutdown.confirmed"],
    timeout=5.0,
).execute()

```

`execute()` returns the full `List[Message]` captured during the run. Internally it
emits `trigger_message`, then asserts each `expected_types` entry was emitted within
`timeout` seconds and each `forbidden_types` entry was *not* emitted; any miss raises
`AssertionError`.

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `plugin_ids` | `List[str]` | **required** | Plugins to load. |
| `trigger_message` | `Message` | **required** | Message to emit as stimulus. |
| `expected_types` | `List[str]` | `[]` | Types that MUST appear. |
| `forbidden_types` | `List[str]` | `[]` | Types that MUST NOT appear. |
| `plugin_instances` | `Dict[str, Any]` | `{}` | Pre-built instances keyed by `plugin_id`. |
| `plugin_factories` | `Dict[str, Callable[[FakeBus], Any]]` | `{}` | `(bus) -> plugin` factories keyed by `plugin_id`; built against the harness bus. Use this when the plugin must be constructed with the harness bus. |
| `config` | `Dict[str, Dict]` | `{}` | Per-plugin config. |
| `timeout` | `float` | `5.0` | Per-expectation wait timeout in seconds. |

---

*Source code: [OpenVoiceOS/ovoscope](https://github.com/OpenVoiceOS/ovoscope).*

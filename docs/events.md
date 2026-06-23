# Events

!!! abstract "In a nutshell"
    OVOS components react to "events" — little announcements like "the user said something" or "a timer went off" that travel between the parts of the system. This developer reference covers the helper tools that let a skill listen for those announcements, tidy them all up when it shuts down, and schedule things to happen later. It is for people writing skills or plugins. See the [Glossary](glossary.md).

**Module:** `ovos_utils.events`

`ovos_utils.events` provides the bookkeeping that skills use around message bus handlers: `EventContainer` tracks every handler a skill registers so they can all be cleanly removed on shutdown, and the handler wrappers add the standard start/stop/error reporting and skill-ID unmunging that intent handlers rely on. `EventSchedulerInterface` (now moved to `ovos-bus-client`) schedules timed and repeating events over the bus.

---

## `EventContainer`

Tracks message bus handlers registered by a skill or plugin, allowing clean unregistration on shutdown.

```python
from ovos_utils.events import EventContainer

container = EventContainer(bus)

container.add("my.event", handler)
container.add("my.once", handler, once=True)

# Later:
container.remove("my.event")
container.clear()  # remove all

```

### Methods

| Method | Description |
|---|---|
| `set_bus(bus)` | Attach a message bus |
| `add(name, handler, once=False)` | Register a handler. If `once=True`, automatically unregisters after first call |
| `remove(name) → bool` | Remove all handlers for `name`. Returns `True` if any were found |
| `clear()` | Unregister and clear all tracked handlers |
| `__iter__` | Iterate over `(name, handler)` pairs |

> **Note on `remove()`:** Due to wrapper functions, `bus.remove(name, handler)` may not find the actual registered callable. `EventContainer.remove()` therefore calls `bus.remove_all_listeners(name)` to reliably clear all handlers for a given event name.

---

## Handler Wrappers

### `create_wrapper(handler, skill_id, on_start, on_end, on_error)`

Creates a wrapped handler for skill intent handlers. The wrapper:

1. Calls `unmunge_message(message, skill_id)` to strip the skill ID prefix from intent entity keys


2. Calls `on_start(message)` if provided


3. Calls `handler()` or `handler(message)` depending on signature


4. Calls `on_error(e)` or `on_error(e, message)` on exception


5. Always calls `on_end(message)` in the `finally` block

### `create_basic_wrapper(handler, on_error)`

Simpler wrapper that calls `handler()` or `handler(message)` and calls `on_error(e)` on exception. Used by `EventSchedulerInterface` for scheduled events.

### `unmunge_message(message, skill_id)`

Strips the letterified skill ID prefix from intent entity keys in `message.data`. For example, key `myskillMyentity` becomes `Myentity` for skill `my.skill`.

### `get_handler_name(handler) → str`

Returns a human-readable name for a handler function, including the owner object's name if available.

---

## `EventSchedulerInterface`

> **Deprecated.** Moved to `ovos_bus_client.apis.events.EventSchedulerInterface`.

Interface for scheduling events via the OVOS message bus scheduler. Emits `mycroft.scheduler.*` messages.

```python

# Preferred import:
from ovos_bus_client.apis.events import EventSchedulerInterface

```

### Methods

| Method | Description |
|---|---|
| `schedule_event(handler, when, data, name, context)` | Schedule a one-time event |
| `schedule_repeating_event(handler, when, interval, data, name, context)` | Schedule a repeating event |
| `update_scheduled_event(name, data)` | Update event data |
| `cancel_scheduled_event(name)` | Cancel a pending event |
| `get_scheduled_event_status(name) → int` | Seconds until next trigger |
| `cancel_all_repeating_events()` | Cancel all repeating events |
| `shutdown()` | Cancel repeating events and clear all registered handlers |

`when` may be a `datetime`, or a positive `int`/`float` representing seconds from now.

---

*Source code: [OpenVoiceOS/ovos-utils](https://github.com/OpenVoiceOS/ovos-utils).*

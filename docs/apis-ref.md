# High-Level APIs

`ovos_bus_client.apis` provides ready-made interfaces for the most common interactions with OVOS services. Skills and applications use these instead of emitting raw bus messages.

---

## GUIInterface

**Module:** `ovos_bus_client.apis.gui.GUIInterface`

Interface to the `ovos-gui` display service. Values set on the interface are synced to QML via the `sessionData` mechanism. Used as `self.gui` inside skills.

```python
from ovos_bus_client.apis.gui import GUIInterface

gui = GUIInterface(skill_id="my-skill", bus=bus)

```

### Data Sync

```python

# Set a value — automatically synced to all connected GUI clients
gui["temperature"] = 22
gui["city"] = "Paris"

# Read a value
temp = gui.get("temperature")

# Remove a value
del gui["temperature"]

```

Values become available in QML as `sessionData.temperature`.

### Showing Pages

Pages are `PageTemplates` enum values corresponding to pre-built OVOS system QML pages:

```python
from ovos_bus_client.apis.gui import PageTemplates

gui.show_page(PageTemplates.TEXT)        # SYSTEM_text
gui.show_page(PageTemplates.IMAGE)       # SYSTEM_image
gui.show_page(PageTemplates.URL)         # SYSTEM_url
gui.show_page(PageTemplates.LOADING)     # SYSTEM_loading

```

Available templates:

| Template | Description |
|---|---|
| `IDLE` | Default idle/homescreen state |
| `LOADING` | Loading spinner |
| `STATUS` | Status message |
| `TEXT` | Plain text display |
| `ERROR` | Error message |
| `IMAGE` | Static image |
| `ANIMATED_IMAGE` | Animated/GIF image |
| `HTML` | Inline HTML |
| `URL` | Web URL in a browser frame |
| `WEATHER` | Weather widget |
| `CLOCK` | Clock widget |
| `FACE` | Avatar face |

### GUI Events (from QML → skill)

```python

# Register a handler for events triggered by QML via triggerEvent()
gui.register_handler("button.pressed", self.on_button_pressed)

# listens for "{skill_id}.button.pressed"

# Callback when any GUI value is changed from the QML side
gui.set_on_gui_changed(self.on_gui_changed)

```

### Properties

| Property | Type | Description |
|---|---|---|
| `connected` | `bool` | True if at least one GUI client is connected |
| `gui_disabled` | `bool` | True if GUI is disabled in config |
| `page` | `PageTemplates` | Currently active page |
| `pages` | `list` | All active pages for this skill |
| `skill_id` | `str` | Namespace used for GUI events |

---

## EventSchedulerInterface

**Module:** `ovos_bus_client.apis.events.EventSchedulerInterface`

Schedule future and repeating bus events. Used as `self.event_scheduler` inside skills.

```python
from ovos_bus_client.apis.events import EventSchedulerInterface
from datetime import datetime, timedelta

scheduler = EventSchedulerInterface(bus=bus, skill_id="my-skill")

```

### Scheduling

```python

# Single-shot — call handler in 10 seconds
scheduler.schedule_event(
    handler=self.on_timer,
    when=10,                  # seconds from now (or datetime)
    data={"msg": "hi"},
    name="my_timer"
)

# Repeating — call every 60 seconds starting in 5 seconds
scheduler.schedule_repeating_event(
    handler=self.on_tick,
    when=5,
    interval=60,
    name="my_tick"
)

# Update data on a scheduled event
scheduler.update_scheduled_event("my_timer", {"msg": "updated"})

# Cancel
scheduler.cancel_scheduled_event("my_timer")
scheduler.cancel_all_repeating_events()

# Check next scheduled time
when = scheduler.get_scheduled_event_status("my_timer")

```

### Notes

- Event names are scoped as `{skill_id}:{name}` to avoid collisions.


- The `when` parameter accepts: `datetime` (timezone-aware or naive), `int`/`float` seconds from now.


- Naive datetimes are assigned the system timezone from config.


- Repeated events skip past occurrences if the system was offline — they fire at the next future time.


- The bus-side daemon that fires events is `EventScheduler` in `ovos_bus_client.util.scheduler`, managed by `ovos-core`.

### Bus Events Used Internally

| Event | Direction | Description |
|---|---|---|
| `mycroft.scheduler.schedule_event` | → scheduler | Add an event |
| `mycroft.schedule.update_event` | → scheduler | Update event data |
| `mycroft.scheduler.remove_event` | → scheduler | Cancel an event |
| `mycroft.scheduler.get_event` | → scheduler | Query next execution time |
| `{skill_id}:{name}` | scheduler → skill | Fires when event is due |

---

## OCPInterface

**Module:** `ovos_bus_client.apis.ocp.OCPInterface`

Interface to OCP (OpenVoiceOS Common Play) — the media playback service. Used as `self.audio_service` inside skills.

```python
from ovos_bus_client.apis.ocp import OCPInterface

ocp = OCPInterface(bus=bus)

```

### Playback Control

```python
ocp.play(tracks=["https://example.com/song.mp3"])
ocp.play(tracks=[("https://example.com/song.mp3", "audio/mpeg")])
ocp.queue(tracks=["https://example.com/song2.mp3"])
ocp.stop()
ocp.next()
ocp.prev()
ocp.pause()
ocp.resume()

```

Tracks can be:

- A string URI: `"https://example.com/song.mp3"`


- A `(uri, mime_type)` tuple: `("https://example.com/song.mp3", "audio/mpeg")`


- Plain file paths are automatically converted to `file://` URIs

All methods accept an optional `source_message` kwarg. If omitted, `dig_for_message` is used to recover the triggering message from the call stack so that proper context/routing is preserved.

### `ClassicAudioServiceInterface` (deprecated)

The old `mycroft.audio.*` namespace is no longer supported in `ovos-audio`. Use `OCPInterface` instead.

---

## EnclosureAPI

**Module:** `ovos_bus_client.apis.enclosure.EnclosureAPI`

Legacy interface for controlling Mycroft Mark 1 hardware (eyes, mouth, system). This class is being deprecated and will eventually move to a PHAL plugin. New skills should not use it.

```python

# Available via self.enclosure in OVOSSkill
self.enclosure.reset()
self.enclosure.system_mute()
self.enclosure.system_unmute()

```

---

## EventScheduler (Server-Side Daemon)

**Module:** `ovos_bus_client.util.scheduler.EventScheduler`

This is the server-side daemon that actually stores and fires scheduled events. It is started by `ovos-core` (when `enable_event_scheduler=True`) and is not used directly by skills.

It persists pending events to disk (XDG data directory) so scheduled events survive restarts.

```python
from ovos_bus_client.util.scheduler import EventScheduler

scheduler = EventScheduler(bus, schedule_file="schedule.json")
scheduler.daemon = True
scheduler.start()

```

Bus events handled:

| Event | Handler |
|---|---|
| `mycroft.scheduler.schedule_event` | Add/update a scheduled event |
| `mycroft.scheduler.remove_event` | Remove an event |
| `mycroft.schedule.update_event` | Update event payload |
| `mycroft.scheduler.get_event` | Return next execution time |

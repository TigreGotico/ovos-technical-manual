
# ovos-bus-client Documentation

`ovos-bus-client` provides the WebSocket client, `Message` objects, `Session` management, and high-level API interfaces for communicating with the OVOS [MessageBus](bus-service.md).

## Contents

| Document | Description |
|---|---|
| [message.md](message-ref.md) | `Message`, `CollectionMessage`, `GUIMessage`, `dig_for_message` |
| [client.md](client-ref.md) | `MessageBusClient` — connect, emit, listen, wait, collect |
| [async_client.md](async-client.md) | `AsyncMessageBusClient` — asyncio client, benchmarks, API reference |
| [session.md](session.md) | `Session`, `SessionManager`, `IntentContextManager` |
| [apis.md](apis-ref.md) | `GUIInterface`, `EventSchedulerInterface`, `OCPInterface`, `EnclosureAPI` |
| [configuration.md](configuration-ref.md) | Connection config, defaults, encryption |

## Quick Start

```python
from ovos_bus_client import MessageBusClient
from ovos_bus_client.message import Message

bus = MessageBusClient()
bus.run_in_thread()
bus.connected_event.wait()

# Listen for an event
bus.on("recognizer_loop:utterance", lambda msg: print(msg.data))

# Send a message
bus.emit(Message("speak", {"utterance": "Hello world"}))

# Request/response
response = bus.wait_for_response(
    Message("intent.service.intent.get", {"utterance": "what time is it"}),
    reply_type="intent.service.intent.reply",
    timeout=5
)

```

## Package Layout

```
ovos_bus_client/
├── message.py          # Message, CollectionMessage, GUIMessage, dig_for_message
├── session.py          # Session, SessionManager, IntentContextManager
├── client/
│   ├── client.py       # MessageBusClient, GUIWebsocketClient  (sync, thread-based)
│   ├── async_client.py # AsyncMessageBusClient, AsyncMessageWaiter, AsyncMessageCollector
│   ├── collector.py    # MessageCollector (used by collect_responses)
│   └── waiter.py       # MessageWaiter (used by wait_for_response)
├── apis/
│   ├── events.py       # EventSchedulerInterface
│   ├── gui.py          # GUIInterface, PageTemplates
│   ├── ocp.py          # OCPInterface, ClassicAudioServiceInterface (deprecated)
│   └── enclosure.py    # EnclosureAPI (legacy, being deprecated)
├── util/
│   ├── __init__.py     # get_mycroft_bus, get_message_lang
│   └── scheduler.py    # EventScheduler (server-side daemon thread)
└── conf.py             # load_message_bus_config, load_gui_message_bus_config

```

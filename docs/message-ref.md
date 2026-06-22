# Message

!!! abstract "In a nutshell"
    Every time one part of the assistant tells another part something, it sends a
    "Message" — the basic note they pass back and forth. This is a developer
    reference for what those notes look like and how to work with them. If you are
    not building on the system internals, you can skip this. See the
    [Glossary](glossary.md) and [ovos-bus-client overview](bus-client-overview.md).

**Module:** `ovos_bus_client.message`

`Message` is the fundamental unit of communication across the OVOS MessageBus. Every event sent or received is a `Message`.

## Structure

```python
Message(
    msg_type: str,    # event name, e.g. "recognizer_loop:utterance"
    data: dict = {},  # payload
    context: dict = {}  # metadata (routing, session, skill_id, lang, …)
)

```

Wire format (JSON):

```json
{"type": "speak", "data": {"utterance": "Hello"}, "context": {"skill_id": "my-skill"}}

```

## Constructing Messages

```python
from ovos_bus_client.message import Message

msg = Message("speak", {"utterance": "Hi!"}, {"skill_id": "my-skill"})

```

## Serialization

```python
json_str = msg.serialize()           # → plain JSON string
msg2     = Message.deserialize(json_str)  # → Message
d        = msg.as_dict               # → plain dict

```

The `Message` envelope is re-exported unchanged from
[`ovos_spec_tools.message`](https://github.com/OpenVoiceOS/ovos-spec-tools)
(the OVOS-MSG-1 spec). `serialize` / `deserialize` produce and consume **plain
JSON** with no transport concerns mixed in — encryption is **not** a `Message`
responsibility (see [Encryption](#encryption) below).

The same module also defines `MalformedMessage` (a `ValueError`/`AssertionError`
raised by the constructor and `deserialize` on an invalid message) and the
constant `DEFAULT_SESSION_ID = "default"` — the reserved session id used when a
message carries no session (the interaction is treated as originating from the
local device).

## Routing Methods

These are used to construct related messages while preserving context:

### `forward(msg_type, data=None)`

Copy the existing `context` verbatim. Used to relay a message as-is under a new type.

```python
relay = message.forward("my.new.event", {"key": "value"})

# relay.context == message.context

```

### `reply(msg_type, data=None, context=None)`

Construct a reply: copies context, swaps `source` ↔ `destination`, and merges any extra context.

```python
reply = message.reply("speak", {"utterance": "Done"})

```

### `response(data=None, context=None)`

Shorthand for `reply(self.msg_type + ".response", ...)`. Matches the convention used by `wait_for_response`.

```python
ack = message.response({"status": "ok"})

# ack.msg_type == "my.event.response"

```

### `publish(msg_type, data, context=None)` — deprecated

Copy context without a `target` key, used for broadcast messages. **Deprecated** —
it emits a `DeprecationWarning` and is not part of OVOS-MSG-1. Use
[`forward`](#forwardmsg_type-datanone) instead.

## Encryption

Encryption is **not** a `Message` feature and is **deprecated**. The optional
layer-2 AES-GCM scheme lives at the transport edge —
`MessageBusClient.emit` / `on_message` call internal `_maybe_encrypt` /
`_maybe_decrypt` helpers — and only engages when `websocket.secret_key` is set in
`mycroft.conf`. Because its key-setup / key-exchange half was never implemented,
the client emits a `DeprecationWarning` whenever it encrypts or decrypts.

```json
{
  "websocket": {
    "secret_key": "my-secret",
    "allow_unencrypted": false
  }
}

```

If `allow_unencrypted` is `false`, the client raises a `RuntimeError` when it
receives a plaintext message. The `encrypt_as_dict` / `decrypt_from_dict` helpers
remain importable from `ovos_bus_client.message` for any consumer that used them
directly, but new code should not rely on this scheme.

---

## `dig_for_message`

```python
from ovos_bus_client.message import dig_for_message

msg = dig_for_message(max_records=10)

```

Walks the call stack looking for a `Message` argument passed to any function in the current call chain. Used internally by skills and APIs to recover the originating message without threading it explicitly through every call. Returns `None` if no message is found.

---

## `CollectionMessage`

**Module:** `ovos_bus_client.message.CollectionMessage`

Extension of `Message` for use with `bus.collect_responses` / `bus.on_collect`. Provides helper methods for multi-handler collect patterns.

```python

# In a collect handler (registered with bus.on_collect):
def my_handler(msg: CollectionMessage):
    # ... do work ...
    if success:
        self.bus.emit(msg.success({"result": "data"}))
    else:
        self.bus.emit(msg.failure())

    # To extend the timeout while processing:
    self.bus.emit(msg.extend(timeout=5))

```

| Method | Effect |
|---|---|
| `success(data, context)` | Reply as `{msg_type}.response` with `succeeded: True` |
| `failure()` | Reply as `{msg_type}.response` with `succeeded: False` |
| `extend(timeout)` | Reply as `{msg_type}.handling` to extend caller's timeout |

---

## `GUIMessage`

A `Message` subclass for the GUI WebSocket channel. Serializes differently — data fields are spread at the top level alongside `type`:

```json
{"type": "gui.event", "key1": "val1", "key2": "val2"}

```

Used internally by `GUIWebsocketClient`. Skills should not construct these directly.

---

## Common `context` Keys

| Key | Set by | Meaning |
|---|---|---|
| `skill_id` | Skill | Which skill emitted this message |
| `session` | Core/client | Serialized `Session` object |
| `lang` | STT / transformer | Language of the utterance |
| `stt_lang` | STT | Language used to transcribe |
| `detected_lang` | Transformer | Language detected by classifier |
| `request_lang` | Source | Language volunteered by source |
| `source` | Bus routing | Origin of the message |
| `destination` | Bus routing | Target of the message |
| `cancel_word` | STT | The cancel word that was detected |
| `valid_langs` | Core | Languages enabled for this request |

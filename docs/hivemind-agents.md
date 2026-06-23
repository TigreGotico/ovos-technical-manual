# Remote Agents with HiveMind

!!! abstract "In a nutshell"
    OpenVoiceOS runs **local-first**, but sometimes you want one capable machine to do the
    thinking and a fleet of small devices ("satellites") to do the listening and speaking — or
    you want to reach your assistant securely from off-device. **HiveMind** is the companion
    project that makes that possible: it exposes an OVOS install (or a single persona) over an
    authenticated, encrypted protocol that satellites and clients connect to.

!!! info "HiveMind lives under its own org"
    The HiveMind packages referenced here are maintained in the **[JarbasHiveMind](https://github.com/JarbasHiveMind)**
    GitHub organization (not `OpenVoiceOS`). The full guide is the
    [HiveMind community docs](https://jarbashivemind.github.io/HiveMind-community-docs/); this
    page covers how HiveMind relates to OVOS.

---

## The pieces

| Piece | Role |
|---|---|
| **`hivemind-core`** | The server. Listens for connections, authenticates clients, enforces permissions, and routes messages to an **agent**. |
| **Agent** | What actually answers — either a full [ovos-core](core.md) install (`hivemind-ovos-agent-plugin`) or a single [persona](personas.md) (`hivemind-persona-agent-plugin`). |
| **Satellites / clients** | The devices and apps that connect to `hivemind-core` (mic satellites, CLI clients, your own code). |

`hivemind-core` is **pluggable** via the **HiveMind Plugin Manager (HPM)** across four axes, so
you can swap implementations without touching the rest:

- **Agent protocol** — what brain answers (OVOS / persona / others).
- **Network protocol** — how clients connect (WebSocket is the reference implementation).
- **Database** — where client credentials live (JSON / SQLite / Redis).
- **Binary data handler** — how binary payloads (e.g. audio) move over the mesh.

![](img/satellites.png)

---

## Quickstart: expose an OVOS install

```bash
pip install hivemind-core
```

**1. Provision a client.** Every satellite/client needs an access key issued by the server:

```bash
hivemind-core add-client       # prints an access key + password for one client
```

This writes the client to the server's credentials database (under
`xdg_data_home()/hivemind-core`), separate from the server config at
`~/.config/hivemind-core/server.json`.

**2. Start the server:**

```bash
hivemind-core listen           # start listening for HiveMind connections
```

By default it serves the local `ovos-core` via `hivemind-ovos-agent-plugin` (configured under
`agent_protocol` in `server.json`).

**3. Give a client its identity, then connect.** On the *client* device, persist the access key
issued in step 1 (this is the step that makes everything else work):

```bash
pip install hivemind-websocket-client
hivemind-client set-identity    # stores the access key / host for this node
```

After `set-identity`, clients (and the [solver](#using-hivemind-as-a-solver) below) can connect
without being handed connection details each time.

---

## Choosing the agent: full OVOS vs a single persona

The agent is selected by the `agent_protocol.module` key in `~/.config/hivemind-core/server.json`.

### Full OVOS — `hivemind-ovos-agent-plugin`

The default. Bridges HiveMind to a running [ovos-core](core.md) over its messagebus, so remote
clients get the **whole** assistant (skills, pipelines, OCP, etc.).

### A single persona — `hivemind-persona-agent-plugin`

Exposes just one [persona](personas.md) — no `ovos-core`, no messagebus — so the attack surface
is minimal. It answers straight from the configured persona.

```json
{
  "agent_protocol": {
    "module": "hivemind-persona-agent-plugin",
    "hivemind-persona-agent-plugin": {
      "persona": {
        "name": "Llama",
        "solvers": ["ovos-solver-openai-plugin"],
        "ovos-solver-openai-plugin": {
          "api_url": "https://llama.smartgic.io/v1",
          "key": "sk-xxxx",
          "system_prompt": "You are helpful, creative, clever, and very friendly."
        }
      }
    }
  }
}
```

The `persona` value may be an inline config dict (above) or a path to an
[ovos-persona](https://github.com/OpenVoiceOS/ovos-persona) JSON file (`~` is expanded). The
`"module"` value must equal the plugin's entry-point name, and that same string is reused as the
key holding its config.

---

## Satellites & clients

A server is only useful once something connects to it. On the client side:

- **[`hivemind-websocket-client`](https://github.com/JarbasHiveMind/hivemind-websocket-client)** — the client library and the `hivemind-client` CLI (`set-identity`, send utterances, etc.).
- **[`hivemind-mic-satellite`](https://github.com/JarbasHiveMind/hivemind-mic-satellite)** — a thin device that only does wake-word + microphone capture; STT/TTS run server-side.
- **[`hivemind-listener`](https://github.com/JarbasHiveMind/hivemind-listener)** — the server-side audio entrypoint that performs STT/TTS for audio satellites (binary audio over the mesh).

This split is the real "voice satellite" story: cheap devices listen and speak, the server thinks.

---

## Permissions & access control

HiveMind is **deny-by-default**: a client may only do what it has been explicitly granted.
`hivemind-core` exposes admin CLI commands to manage this, including:

- `add-client` / `list-clients` / `revoke` — manage who may connect.
- `allow-msg` / `blacklist-msg` — whitelist or block specific bus message types per client.
- `make-admin` / `revoke-admin`, `allow-escalate` / `allow-propagate` — elevate or restrict a client.
- `blacklist-skill` / `blacklist-intent` — stop a client from reaching specific skills/intents.

This is what makes HiveMind safe to expose to satellites or other users, unlike the plain
[persona-server](persona-server.md) (HTTP, no auth).

!!! tip "Web admin UI"
    [`hivemind-admin-panel`](https://github.com/JarbasHiveMind/hivemind-admin-panel) is a web UI
    for managing clients, permissions, plugins and personas instead of the CLI.

---

## Using HiveMind as a solver

Want your *local* assistant to ask a *remote* HiveMind agent when it's stuck? Install the
**[`ovos-solver-hivemind-plugin`](https://github.com/JarbasHiveMind/ovos-solver-hivemind-plugin)**
(class `HiveMindSolver`, import `ovos_hivemind_solver`) and add it to a persona. It is a normal
[solver](agent-plugins.md), so it slots into a mixture-of-solvers chain — handy for delegating
hard questions, surviving local outages, or collaborative setups.

```json
{
  "name": "HiveMind Agent",
  "solvers": ["ovos-solver-hivemind-plugin"],
  "ovos-solver-hivemind-plugin": {"autoconnect": true}
}
```

Or from your own code (the node identity must already be set with `hivemind-client set-identity`):

```python
from ovos_hivemind_solver import HiveMindSolver

bot = HiveMindSolver()          # reads the identity provisioned via `hivemind-client set-identity`
bot.connect()
print(bot.spoken_answer("what is the speed of light?"))
```

### As an intent-pipeline stage

There is also a pipeline-plugin form,
**[`ovos-hivemind-pipeline-plugin`](https://github.com/JarbasHiveMind/ovos-hivemind-pipeline-plugin)**
(entry point `opm.pipeline`, class `HiveMindPipeline`). Instead of living inside a persona, it
slots directly into the [intent pipeline](pipelines-overview.md) — *"when in doubt, ask a smarter
OVOS install."* Add it to `intents.pipeline` and configure it under `mycroft.conf`:

```json
{
  "intents": {
    "pipeline": ["...", "ovos-hivemind-pipeline-plugin", "..."],
    "ovos-hivemind-pipeline-plugin": {
      "name": "Hive Mind",
      "confirmation": true,
      "slave_mode": false
    }
  }
}
```

Use the **solver** form to delegate inside a persona's reasoning; use the **pipeline** form to
delegate at the intent-matching stage (e.g. as a late, catch-all matcher).

---

## Deployment patterns

HiveMind and the [persona-server](persona-server.md) cover different trust boundaries:

| Use case | Tools | Secure? | Notes |
|---|---|---|---|
| Local interface + persona | `ovos-persona-server` + `persona.json` | ❌ | OpenAI-compatible HTTP, no auth — quick setups only |
| Local interface + OpenVoiceOS | `ovos-persona-server` + the `ovos-messagebus` handler | ❌ | Exposes the OVOS bus to the persona server; HTTP, no auth |
| Local interface + remote HiveMind agent | `ovos-persona-server` + `ovos-solver-hivemind-plugin` | ❌ | HTTP front, but the agent itself is remote |
| Secure remote OpenVoiceOS agent | `hivemind-core` + `hivemind-ovos-agent-plugin` + `ovos-core` | ✅ | Auth, encryption, granular permissions |
| Secure remote persona agent | `hivemind-core` + `hivemind-persona-agent-plugin` + `persona.json` | ✅ | Same, persona-only (minimal surface) |

The HTTP rows are useful for wiring a persona into local tools (Home Assistant's Ollama
integration, OpenWebUI, …) on a trusted network. The HiveMind rows are what you expose to
satellites or untrusted networks.

> ⚠️ The plain [`persona-server`](persona-server.md) is **HTTP only — not encrypted or
> authenticated**. Keep it on a trusted local network; use HiveMind for anything remote.

---

## Further reading

- [HiveMind community docs](https://jarbashivemind.github.io/HiveMind-community-docs/)
- [OVOS & HiveMind in the Manufacturing Industry](https://blog.openvoiceos.org/posts/2026-01-14-OVOS-hivemind-industry) — OVOS blog

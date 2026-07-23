# Running OVOS in Production

!!! abstract "In a nutshell"
    A single OVOS assistant on your desk needs almost no care and feeding. Running many of
    them — a fleet of kiosks, a house full of satellite devices, a product built on top of
    OVOS — is a different job: you need services that restart themselves when they crash,
    a way to know the assistant is actually ready before you rely on it, logs you can ship
    somewhere central, and a safe way to upgrade a device (and undo the upgrade if it goes
    wrong) without physically touching it. This page collects the real, verified pieces for
    that job: systemd units, a readiness probe, log locations, staged upgrades with
    rollback, and how to run one shared speech backend for many thin clients. It assumes you
    are already comfortable with [installing OVOS](ovos-installer.md) and the
    [release channels](release-channels.md) page.

---

## Keep services running: systemd units

OVOS itself does not manage process supervision — that is left to the OS. The
[`ovos-installer`](ovos-installer.md) and the [raspOVOS](install-raspovos.md) image both use
**systemd user units** for this. The examples below are adapted from the units raspOVOS
actually ships (`overlays/base_ovos/home/ovos/.config/systemd/user/` in the
[raspOVOS](https://github.com/OpenVoiceOS/raspOVOS) repository).

A top-level dummy target groups all the OVOS services so you can start/stop/enable the whole
stack as one unit:

```ini title="~/.config/systemd/user/ovos.service"
[Unit]
Description=OVOS A.I. Software stack.

[Service]
Type=oneshot
Group=ovos
ExecStart=/bin/true
RemainAfterExit=yes

[Install]
WantedBy=default.target
```

Each real service is `PartOf=ovos.service` and `WantedBy=ovos.service`, so `systemctl --user
restart ovos.service` cascades to all of them, but each can also be restarted individually
without disturbing its siblings:

```ini title="~/.config/systemd/user/ovos-messagebus.service"
[Unit]
Description=OVOS Messagebus (Rust)
PartOf=ovos.service
After=ovos.service

[Service]
Group=ovos
UMask=002
ExecStart=/usr/local/bin/ovos_rust_messagebus
Restart=on-failure

[Install]
WantedBy=ovos.service
```

```ini title="~/.config/systemd/user/ovos-skills.service"
[Unit]
Description=OVOS Skills
PartOf=ovos.service
After=ovos.service
After=ovos-messagebus.service

[Service]
Type=notify
Group=ovos
UMask=002
ExecStart=%h/.venvs/ovos/bin/python /usr/libexec/ovos-systemd-skills
TimeoutStartSec=10m
TimeoutStopSec=1m
Restart=on-failure
StartLimitInterval=5min
StartLimitBurst=4

[Install]
WantedBy=ovos.service
```

If you are writing your own unit for a custom service (a skill runner, a persona server, a
thin-client bridge), the pattern worth keeping is:

- `Restart=on-failure` — restart on crash, not on a clean stop.
- `StartLimitInterval=` / `StartLimitBurst=` — give up (rather than loop forever) after
  repeated failures in a short window, so a broken deploy doesn't spin your CPU.
- `PartOf=`/`After=` the messagebus unit for anything that needs a live bus connection at
  startup.

```bash
systemctl --user daemon-reload
systemctl --user enable --now ovos.service
systemctl --user status ovos-skills.service
journalctl --user -u ovos-skills.service -f
```

!!! note "System vs user units"
    The units above are **user** units (`~/.config/systemd/user/`), matching how raspOVOS and
    the installer run OVOS as the `ovos` user. If you need OVOS to start before any user logs
    in (a headless kiosk), install the same unit files under `/etc/systemd/system/` instead and
    use `systemctl enable --now` (no `--user`); you will also need
    `loginctl enable-linger ovos` if you keep user units but want them running without an
    active login session.

---

## Knowing when the assistant is actually ready

Services report a rolling status (`started` → `ready` → `error`/`stopping`) over the bus, and
the [`ovos-skill-boot-finished`](https://github.com/OpenVoiceOS/ovos-skill-boot-finished) skill
polls each one and emits a single `mycroft.ready` message once every service it is configured to
wait on has reported ready. This is the signal to use in health checks, readiness probes, or an
`ExecStartPost` step — not "is the process running", which says nothing about whether the
voice pipeline can actually hear and answer you yet.

!!! note "Requires the boot-finished skill to be installed"
    `mycroft.ready` is emitted by a skill, not by `ovos-core` itself. It is pulled in by the
    `skills-audio` [extra](release-channels.md#what-are-ovos-extras)
    (`ovos-core[skills-audio]`) and is installed by default on most full setups, but a
    from-scratch, headless, or minimal install must include it explicitly for the readiness
    probe below to ever get a response.

A minimal readiness probe using [`ovos-bus-client`](bus-service.md):

```python
from ovos_bus_client import MessageBusClient
from ovos_bus_client.message import Message

bus = MessageBusClient()
bus.run_in_thread()
response = bus.wait_for_response(
    Message("mycroft.ready.check"), reply_type="mycroft.ready", timeout=30
)
bus.close()
if response is None:
    raise SystemExit("OVOS did not report ready within 30s")
print("OVOS is ready")
```

Save that as `/usr/local/bin/ovos-ready-probe` and wire it into a unit as a post-start check:

```ini
ExecStartPost=/usr/local/bin/ovos-ready-probe
```

!!! warning "Timeout, not certainty"
    `wait_for_response` returns `None` on timeout, it does not raise. Always check for `None`
    — a bare `response.data` on a timed-out call raises `AttributeError`, not a clean failure.

### Headless devices: choosing what "ready" means

[`ovos-skill-boot-finished`](https://github.com/OpenVoiceOS/ovos-skill-boot-finished) is the
skill that actually answers `mycroft.ready.check` and decides what to wait for, via its
`ready_settings` setting. By default it waits for `skills` plus every installed skill to
register; for a server or a device with no GUI/audio you usually want to name only the
services that actually apply:

```yaml title="settings.json for ovos-skill-boot-finished"
ready_settings:
  - skills     # ovos-core skill loader reported ready
  - voice      # ovos-dinkum-listener reported ready (omit on a text-only/server node)
  - audio      # ovos-audio reported ready (omit if there is no speaker)
speak_ready: false   # don't speak a "ready" dialog on a headless box
ready_sound: false   # don't play a ready chime either
```

`network`/`internet`/`gui_connected` are also accepted `ready_settings` entries, and any
service exposing an OVOS `ProcessStatus` (including `PHAL`) can be named by its status key.

!!! note "Upcoming — a bundled health check script"
    A ready-to-use OVOS health check script for the `ovos-installer` is in progress
    ([ovos-installer#542](https://github.com/OpenVoiceOS/ovos-installer/pull/542)), covering
    the same "is the assistant actually ready" question as the readiness probe above without
    writing your own.

---

## Log locations and shipping them out

OVOS logs to stdout by default; every real deployment (systemd, raspOVOS, the installer) sets
a `logging` section in `mycroft.conf` so each service writes its own rotating file instead:

```json
{
  "logging": {
    "path": "~/.local/state/mycroft/",
    "max_bytes": 50000000,
    "backup_count": 6
  }
}
```

Without that section, `ovos-utils`' logger still defaults to a file under
`$XDG_STATE_HOME/mycroft/<service>.log` (typically `~/.local/state/mycroft/`) rather than pure
stdout — check that directory first if you can't find a log file. Each service gets its own
file named after it (`skills.log`, `bus.log`, `audio.log`, `voice.log`, `gui.log`, ...).

`ovos-utils` also ships a small CLI, `ovos-logs`, for navigating those files without hunting
through each one by hand:

```bash
ovos-logs show -l skills            # page through skills.log (uses $PAGER/less)
ovos-logs slice -l bus -l skills -f ~/incident.log   # extract bus+skills since service start
ovos-logs slice -s "01-12-2023" -u "01-12-2023 17:00" # slice a specific window
ovos-logs reduce -s 1000000         # trim every log down to ~1MB (keep the tail)
```

For centralized log shipping (many devices → one place), point a standard log-forwarding
agent (Vector, Fluent Bit, Promtail, `rsyslog`) at the log directory, or redirect the systemd
unit's stdout to the journal (the default) and ship `journalctl` output instead — OVOS itself
does not include a log-shipping client.

---

## Staged upgrades and rollback

[Release channels](release-channels.md) covers `stable`/`testing`/`alpha` constraints files.
For a fleet, the same mechanism gives you a controlled, reversible upgrade path:

```bash
# 1. Freeze exactly what's currently installed, in case you need to go back
uv pip freeze > /etc/ovos/known-good-$(date +%F).txt

# 2. Upgrade against a pinned constraints file (stays within one release channel)
uv pip install --upgrade ovos-core[mycroft] \
    -c https://raw.githubusercontent.com/OpenVoiceOS/ovos-releases/refs/heads/main/constraints-stable.txt

# 3. Restart and re-run the readiness probe above before declaring success
systemctl --user restart ovos.service
```

If the upgrade misbehaves, roll back to the frozen set:

```bash
uv pip install --force-reinstall -r /etc/ovos/known-good-2026-07-01.txt
systemctl --user restart ovos.service
```

`--force-reinstall` is needed on rollback because a plain `pip install` treats "already
satisfies requirement" as nothing to do — it will not downgrade a package back to an older
pinned version on its own.

!!! tip "Stage it on one device first"
    Constraints files are a moving target upstream. Roll an upgrade out to one canary device,
    confirm the readiness probe and a couple of real voice interactions succeed, then repeat
    the same `uv pip install -c ...` command across the rest of the fleet.

---

## One config for many devices: the system config layer

OVOS reads configuration from several layered files, [merged in order](config.md) so that a
more specific file overrides a more general one. The layer meant for fleet-wide, admin-managed
settings is the **system config**, at a fixed path:

```text
/etc/mycroft/mycroft.conf
```

This file sits below each user's own `~/.config/mycroft/mycroft.conf`, so per-device
overrides still win, but anything you don't override there comes from the system file. This
is the layer to drop settings into via configuration management (Ansible, a Debian package
postinst, a golden image) rather than hand-editing every device's user config — for example,
pinning the same wake word, STT/TTS servers, or `ready_settings` across an entire fleet.

---

## Thin clients + a shared speech backend

A common fleet topology is several low-power "thin" devices that only run the bus, listener
and audio services, all pointed at one shared, more capable machine that does the actual
speech-to-text and text-to-speech work over HTTP (see [STT server](stt-server.md) and
[TTS server](tts-server.md)). A sketch, based on the real container images published by
[`ovos-docker`](https://github.com/OpenVoiceOS/ovos-docker):

```yaml title="docker-compose.yml — central speech backend"
services:
  ovos_stt_server:
    image: docker.io/smartgic/ovos-stt-server:${VERSION}   # or your own build, see stt-server.md
    ports: ["8080:8080"]

  ovos_tts_server:
    image: docker.io/smartgic/ovos-tts-server:${VERSION}   # or your own build, see tts-server.md
    ports: ["9666:9666"]
```

```yaml title="docker-compose.yml — thin client (per device)"
services:
  ovos_messagebus:
    image: docker.io/smartgic/ovos-messagebus:${VERSION}
    network_mode: host

  ovos_listener:
    image: docker.io/smartgic/ovos-listener:${VERSION}
    network_mode: host
    depends_on: [ovos_messagebus]
    # configure stt.module = ovos-stt-plugin-server, urls -> the central STT server above

  ovos_audio:
    image: docker.io/smartgic/ovos-audio:${VERSION}
    network_mode: host
    depends_on: [ovos_messagebus]
    # configure tts.module = ovos-tts-plugin-server, host -> the central TTS server above

  ovos_core:
    image: docker.io/smartgic/ovos-core:${VERSION}
    network_mode: host
    depends_on: [ovos_messagebus]
```

Each thin client still runs its own bus, listener, audio and core — only the heavy STT/TTS
inference is centralized. This is the same pattern as
[Wyoming bridges](wyoming-bridges.md) and [HiveMind](hivemind-agents.md), just wired directly
through the companion server plugins instead of a satellite protocol; see
[Composable Deployments](composable-deployments.md) for the general principle of splitting
OVOS across machines.

---

## Observability: what exists and what doesn't

!!! warning "There is no built-in metrics endpoint"
    OVOS does not expose a Prometheus-style `/metrics` endpoint or any built-in dashboard. The
    closest thing is usage-metric uploads, and those are **explicitly opt-in**: disabled by
    default, with nothing sent anywhere unless you deliberately configure an endpoint (see the
    commented-out `opendataConfig`-style keys in the default `mycroft.conf`, and
    [`ovos-opendata-server`](ecosystem-index.md) if you want to run your own collector). That
    is a telemetry pipeline you opt into, not an operational metrics/monitoring system.

For day-to-day, per-device debugging, use:

- **`ovos-busmon`** — a terminal UI that shows the live message traffic on a device's bus in
  real time; the fastest way to see whether wake word → STT → intent → TTS is actually firing.
- **`ovos-logs`** (above) for historical logs.
- The [readiness probe](#knowing-when-the-assistant-is-actually-ready) as a synthetic check you
  can run from outside the device (cron, a monitoring agent, a CI job) on a schedule.

There is no supported way to scrape per-request latency or error rates across a fleet today;
if you need that, you will need to build it on top of the bus messages yourself.

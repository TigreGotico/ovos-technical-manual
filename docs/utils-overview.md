
# ovos-utils

!!! abstract "In a nutshell"
    `ovos-utils` is a shared toolbox of small helpers that the rest of OVOS reuses, so the same basic jobs do not have to be re-invented in every component. This page is a developer reference listing what is in the toolbox. If you are not writing OVOS code, you do not need it. See the [Glossary](glossary.md).

Shared utility library used by all OVOS components. Provides logging, process lifecycle management, a testing-friendly fake message bus, event scheduling, file utilities, network checks, audio playback, and XDG path helpers.

---

## Module Overview

| Module | Description |
|---|---|
| `ovos_utils.log` | `LOG` — OVOS-wide logging class with optional file rotation |
| `ovos_utils.process_utils` | `ProcessStatus`, `RuntimeRequirements`, `PIDLock`, `MonotonicEvent` |
| `ovos_utils.fakebus` | `FakeBus`, `FakeMessage` — in-process bus for testing without a live WebSocket |
| `ovos_utils.events` | `EventContainer`, `EventSchedulerInterface`, handler wrappers |
| `ovos_utils.file_utils` | Resource resolution, vocab loading, `FileWatcher` |
| `ovos_utils.network_utils` | `get_ip()`, `is_connected_dns()`, `is_connected_http()`, `check_captive_portal()` |
| `ovos_utils.sound` | `play_audio()`, `get_sound_duration()` |
| `ovos_utils.thread_utils` | `create_daemon()`, `create_killable_daemon()`, `wait_for_exit_signal()`, `threaded_timeout` |
| `ovos_utils.xdg_utils` | XDG Base Directory helpers (`xdg_config_home()`, `xdg_data_home()`, etc.) |
| `ovos_utils.bracket_expansion` | Dialog template `{option1\|option2}` expansion |
| `ovos_utils.decorators` | `classproperty`, `timed_lru_cache` |
| `ovos_utils.json_helper` | JSON load/save helpers |
| `ovos_utils.list_utils` | `flatten_list()` and related helpers |
| `ovos_utils.parse` | [Utterance](life-of-an-utterance.md) parsing helpers |
| `ovos_utils.dialog` | Dialog file loading |
| `ovos_utils.lang/` | Language normalization utilities |
| `ovos_utils.ssml` | SSML tag helpers |
| `ovos_utils.time` | Timezone-aware `now_local()`, `get_config_tz()` |
| `ovos_utils.system` | `system_info()` and related helpers |
| `ovos_utils.gui` | GUI interface utilities |
| `ovos_utils.skills` | [Skill](skill-design-guidelines.md) ID helpers |
| `ovos_utils.ocp` | [OCP](ocp-pipeline.md) (media player) helpers |
| `ovos_utils.smtp_utils` | Email-sending utilities |

---

## Installation

```bash
pip install ovos-utils

```

`ovos-utils` is a dependency of `ovos-bus-client`, `ovos-config`, `ovos-workshop`, and virtually every other OVOS package. Most projects get it transitively.

---

## Environment Variables

| Variable | Used by | Description |
|---|---|---|
| `OVOS_DEFAULT_LOG_NAME` | `LOG` | Default logger name (default: `OVOS`) |
| `OVOS_DEFAULT_LOG_LEVEL` | `LOG` | Default log level (default: `INFO`) |
| `OVOS_CONFIG_BASE_FOLDER` | `LOG`, `PIDLock` | XDG base folder name (default: `mycroft`) |

---

## Further Reading

- [Logging](log-ref.md) — `LOG`, `init_service_logger()`, `log_deprecation()`, `deprecated` decorator


- [Process Utilities](process-utils-ref.md) — `ProcessStatus`, `RuntimeRequirements`, `PIDLock`, `MonotonicEvent`


- [FakeBus](fakebus.md) — `FakeBus`, `FakeMessage` — in-process message bus for testing


- [Events](events.md) — `EventContainer`, `EventSchedulerInterface`, handler wrappers


- [Utilities](utilities.md) — file, network, sound, threading, XDG helpers

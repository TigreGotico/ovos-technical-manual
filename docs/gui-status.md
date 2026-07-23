# Screens on OVOS Today

!!! abstract "In a nutshell"
    OVOS is voice-first, but some devices (notably the **Mark 2**) also have a screen.
    The screen software that exists **today** is old, deprecated, and best described as
    "just barely working" — kept alive only so existing Mark 2 devices don't go dark. A
    ground-up replacement is being designed, but it is **Upcoming** and not usable yet.
    This page is the single, honest answer to "what's the state of GUI on OVOS?" — every
    other GUI page links back here instead of repeating the same warning.

## The honest verdict

There is **no generally usable OVOS GUI right now**. The only screen stack that actually
runs is the **legacy Qt5 stack** — [`ovos-shell`](ovos-shell.md) wrapping
[`mycroft-gui-qt5`](qt5-gui.md), talking over the [legacy GUI protocol](gui-protocol.md) to
[`ovos-gui`](gui-service.md) — and that stack is **deprecated upstream** (Qt5 itself is no
longer updated) and treated as **broken** in the sense that no active development happens
on it. It is kept solely so devices that already have it (Mark 2s shipped via the
[`ovos-installer`](ovos-installer.md)) keep a working screen.

A ground-up replacement — the **GUI adapter rework**, formalized as spec
**OVOS-GUI-1** — is being built to fix this properly, but it is **Upcoming**: not merged,
not released, and not something to plan a product around today. See
[GUI Adapter Plugins](gui-adapters.md) for the technical design.

## Practical recommendation

If you are shipping a device with a screen **today**:

- Voice must remain the primary interface — treat any screen as a bonus, never a
  requirement, since the display stack can vanish or be swapped without warning.
- If you need a screen now, use the legacy Mark 2 path: `ovos-shell` +
  `mycroft-gui-qt5`, installed automatically by the [`ovos-installer`](ovos-installer.md).
  Do not invest in new QML pages against this stack — it will not gain new capability.
- Do not build against the adapter/rework APIs yet; they are **Upcoming** and their
  shape can still change before release.
- If a screen is not a hard requirement, skip the GUI entirely. OVOS works fully
  voice-only, and this sidesteps the whole legacy/rework transition.

## Tracked rework

The GUI adapter rework is spread across several repositories. All of the following are
open, in-progress pull requests — nothing here has shipped:

- [ovos-plugin-manager#377](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/377) — `AbstractGUIPlugin` base class
- [ovos-gui#112](https://github.com/OpenVoiceOS/ovos-gui/pull/112) — adapter/template rework landing
- [ovos-gui#117](https://github.com/OpenVoiceOS/ovos-gui/pull/117) — OVOS-GUI-1 service conformance
- [ovos-bus-client#238](https://github.com/OpenVoiceOS/ovos-bus-client/pull/238) — GUI-1-conformant wire shapes
- [ovos-legacy-mycroft-gui-plugin#3](https://github.com/OpenVoiceOS/ovos-legacy-mycroft-gui-plugin/pull/3) — legacy adapter conforming to the session_id-only contract

## GUI generations at a glance

| Generation | Status | What it is | Page |
|---|---|---|---|
| Legacy GUI service | Deprecated, only thing that runs | The `ovos-gui` daemon that tracks GUI state and speaks the legacy protocol | [GUI Service](gui-service.md) |
| Legacy protocol | Deprecated | The Qt-WebSocket messages (`gui.value.set`, `gui.page.show`, …) between skills and screen clients | [GUI Protocol](gui-protocol.md) |
| Qt5/QML client | Deprecated upstream, still the only runnable client | `mycroft-gui-qt5`, the Qt5/QML rendering toolkit | [Qt5 GUI](qt5-gui.md) |
| Shell application | Deprecated, still in use on Mark 2 | `ovos-shell`, the full-screen Kirigami app wrapping the Qt5 client | [OVOS Shell](ovos-shell.md) |
| Home screen | Deprecated, still in use on Mark 2 | The idle/resting screen skill shown when nothing else is displayed | [Home Screen](homescreen.md) |
| Skill GUI API | Legacy API, still what skills use today | `self.gui` / `GUIInterface`, the Python API a skill uses to push data to a screen | [GUI Skills](skill-gui.md) |
| Adapter rework (OVOS-GUI-1) | **Upcoming** — in progress, not usable | Planned replacement: skills declare `SYSTEM_*` templates, interchangeable render backends draw them | [GUI Adapter Plugins](gui-adapters.md) |

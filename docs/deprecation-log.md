# Deprecation Log & Migration Guide

This document tracks deprecated modules, classes, and architectural patterns within the OpenVoiceOS ecosystem. For whole **repositories** that have been archived (and their replacements), see **[Deprecated & Archived Repositories](deprecated-repos.md)**.

Starting with `ovos-core` **0.0.8**, the project strictly follows **Semantic Versioning**:

- `X.0.0`: Major releases containing **breaking changes**.


- `0.X.0`: Minor releases containing **new features**.


- `0.0.X`: Patch releases containing **bug fixes**.

Following the [OVOS Deprecation Policy](architecture-overview.md), deprecated features remain functional for at least one major version before removal to ensure a smooth migration path.

---

## 2026

!!! note "GUI status"
    In `ovos-workshop` v8 `self.gui` (a `SkillGUI`, subclass of
    `GUIInterface` from `ovos_bus_client.apis.gui`) is a live, supported default
    property on every `OVOSSkill`. It is **not** deprecated and is not scheduled
    for removal. Skills may use the built-in `SYSTEM_*` page templates or ship
    their own `.qml`/custom pages via `show_page` — see
    [GUI Skills](skill-gui.md).

!!! warning "Upcoming — unreleased"
    The [GUI rework](gui-service.md) rebinds the skill-side GUI API. Unreleased PR
    [OpenVoiceOS/ovos-workshop#420](https://github.com/OpenVoiceOS/ovos-workshop/pull/420)
    moves `GUIInterface` out of `ovos_bus_client.apis.gui` into the standalone
    **`ovos-gui-api-client`** package and drops the `ui_directories` argument from
    `SkillGUI`. This is a real future direction, not a released change — no published
    `ovos-workshop` ships it yet. The `ovos_bus_client.apis.gui` import remains current on
    stable installs.

### [ovos-media] OVOSAbstractApplication
**Date:** March 2026  
**Status:** **REMOVED** (Stabilization Refactor)

The `OVOSAbstractApplication` mixin has been removed from `OCPMediaPlayer` to decouple media playback from skill lifecycle management.

*   **Impact:** Media players should manage their own state without inheriting from the application base class.


*   **Replacement:** Implement standard OCP integration directly.

### [ovos-gui] Qt-Specific Protocol Documentation
**Date:** March 2026  
**Status:** Deprecated

Documentation and protocol extensions specific to the original Mycroft-Qt implementation are being moved to a legacy section.

*   **Impact:** The core `ovos-gui` protocol is now strictly platform-agnostic.


*   **Reference:** See [GUI Protocol](gui-protocol.md) for the modern, unified specification.

---

## 2025

### [ovos-workshop] Legacy Skill Base Classes
**Date:** November 2025  
**Status:** **DEPRECATED** (Consolidated in `ovos-workshop` 8.0.0)

Older skill base classes imported from `mycroft.skills` or early `ovos-workshop` versions are being consolidated.

*   **Deprecated:** `MycroftSkill` and skill classes imported from `mycroft.skills`


*   **Replacement:** `OVOSSkill` from `ovos_workshop.skills.ovos` (also re-exported from `ovos_workshop.skills`)


*   **Note:** Version 8.0.0 finalized the internal refactor to separate GUI, intent, and resource management into mixins.

### [ovos-utils] Signal-Based Events
**Date:** June 2025  
**Status:** Deprecated

Use of Linux signals for inter-process communication in certain utilities has been deprecated in favor of the MessageBus.

*   **Impact:** Improved cross-platform compatibility (especially Windows support).


*   **Replacement:** Use `ovos_bus_client` for all inter-component communication.

---

## 2024

### [ovos-core] PHAL Extension Entry Points
**Date:** September 2024  
**Status:** Deprecated

The method for registering PHAL (Platform Hardware Abstraction Layer) plugins was standardized.

*   **Deprecated:** `ovos.plugin.phal` (legacy naming)


*   **Replacement:** `ovos.plugin.phal` (standardized entry point group)


*   **Reference:** See [PHAL Documentation](ovoscope-phal.md).

---

## Migration Tips

1.  **Check Logs:** OVOS components emit `DeprecationWarning` when using deprecated features. Run your components with `PYTHONWARNINGS="once"` to identify them.


2.  **Audit Scripts:** Use the `ensure_compliance.py` script (if available in your workspace) to scan your skills for deprecated patterns.


3.  **Docs First:** Always refer to the QUICK_FACTS.md in each repository for the current recommended entry points.

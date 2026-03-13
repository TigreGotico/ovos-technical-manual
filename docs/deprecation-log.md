# Deprecation Log & Migration Guide

This document tracks deprecated modules, classes, and architectural patterns within the OpenVoiceOS ecosystem. 

Starting with `ovos-core` **0.0.8**, the project strictly follows **Semantic Versioning**:

- `X.0.0`: Major releases containing **breaking changes**.


- `0.X.0`: Minor releases containing **new features**.


- `0.0.X`: Patch releases containing **bug fixes**.

Following the [OVOS Deprecation Policy](architecture-overview.md), deprecated features remain functional for at least one major version before removal to ensure a smooth migration path.

---

## 2026

### [ovos-workshop] OVOSSkill.gui Property
**Date:** March 2026  
**Status:** **DEPRECATED** (Scheduled for removal in `ovos-workshop` 9.0.0)

Direct access to `self.gui` within `OVOSSkill` is being phased out as a default property to allow for more flexible GUI initialization and to reduce overhead for headless skills.

*   **Impact:** Skills requiring a GUI should now explicitly initialize their GUI interface or use specific GUI mixins.


*   **Replacement:** The internal `SkillGUI` class is being replaced by the more generic `GUIInterface`.


*   **Migration Path:** Most skills will continue to work via the deprecated property for now, but developers are encouraged to move towards explicit initialization in `initialize()`.

### [ovos-bus-client] GUI APIs
**Date:** March 2026  
**Status:** Deprecated (Scheduled for removal in `ovos-bus-client` 2.0.0)

The legacy GUI interface helpers in `ovos-bus-client.apis.gui` have been deprecated in favor of a standalone, more robust client library.

*   **Deprecated Module:** `ovos_bus_client.apis.gui`


*   **Replacement:** [ovos-gui-api-client](https://github.com/OpenVoiceOS/ovos-gui-api-client)


*   **Impact:** Skill developers should migrate from `self.gui` (when used directly) to the dedicated API client. For `OVOSSkill` users, the internal `self.gui` is being updated to use the new client transparently.

### [ovos-gui] Legacy QML/Page System
**Date:** March 2026  
**Status:** **REMOVED** (Major Release `ovos-gui` 1.0.0)

The legacy QML page-based system, which relied on skills providing `.qml` files to be rendered by a heavy Qt-based GUI service, has been removed.

*   **Impact:** The `ovos-gui` service now implements a **template-only architecture** (HTMX based).


*   **Migration Path:**


    *   **GUIs:** Clients should implement the [formal adapter interface contract (TECH-005)](gui-adapters.md).


    *   **Skills:** Use standardized GUI templates provided by `ovos-workshop` rather than custom QML files. Custom UI logic should be handled via HTMX templates or dedicated Voice Apps.

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

*   **Deprecated:** `MycroftSkill`, `OVOSSkill` (legacy imports)


*   **Replacement:** `OVOSSkill` from `ovos_workshop.skills.ovos`


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

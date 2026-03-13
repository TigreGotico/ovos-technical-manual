
# FAQ — `ovos-technical-manual`

## What is the "Great GUI Refactor" of March 2026?
OpenVoiceOS has moved to a **template-only architecture**. This means the core `ovos-gui` service no longer renders custom QML or HTML files provided by skills. Instead, skills provide data to one of 21 standardized `SYSTEM_*` templates, which are rendered by adapter plugins (Qt, Web/HTMX, Terminal).

## Is `self.gui` deprecated?
Yes, in `OVOSSkill` version 9.0.0, the default `self.gui` property is being phased out. Skills should now explicitly initialize `GUIInterface` from `ovos-gui-api-client` if they require visual output.

## How do I migrate my legacy QML skill?
Instead of calling `self.gui.show_page("MyPage.qml")`, you should use one of the standard template methods, such as `self.gui.show_text()`, `self.gui.show_image()`, or `self.gui.show_list()`. If your skill requires a completely custom UI, consider developing it as a standalone **Voice App**.

## Where is the project history?
See the [Timeline](docs/timeline.md) for a complete history of major milestones from 2015 to the present.

## Where can I find info on deprecated features?
Refer to the [Deprecation Log](docs/deprecation-log.md) for tracking removals and migration guides.

---

## Technical Setup

## How do I install the manual locally?
```bash
pip install ovos-technical-manual
```
Or for development (recommended):
```bash
uv pip install -e ovos-technical-manual/
```

## How do I build the docs?
The manual uses `mkdocs`. You can run a local server to preview changes:
```bash
mkdocs serve
```

## Where do I report documentation errors?
Open an issue on the [ovos-technical-manual](https://github.com/OpenVoiceOS/ovos-technical-manual) repository. Ensure you are targeting the `master` branch for any proposed fixes.

## Why do the docs look different when I build them locally?
To ensure the documentation matches the official theme, you must have `mkdocs-material` and `pymdown-extensions` installed. If you are using the shared workspace environment, they should already be available via `uv`.

```bash
pip install mkdocs-material pymdown-extensions mkdocs-material-extensions
```

## What Python versions are supported?
See `QUICK_FACTS.md` — currently `3.10+` is standard for the workspace.

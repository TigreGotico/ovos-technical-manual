# FAQ — `ovos-technical-manual`

## How does a skill draw on a screen today?

A skill uses `self.gui`, a `SkillGUI` (subclass of `GUIInterface`) that ships in
`ovos-workshop` (currently v8). It is imported from `ovos_bus_client.apis.gui` and
exposes helpers like `self.gui.show_text(...)`, `show_image(...)`, `show_list(...)`,
and `show_page("MyPage.qml")` for custom QML. `self.gui` is **not** deprecated.

## What is the GUI rework I keep hearing about?

A template/adapter rework is in progress but **not yet released**. It is specified in
[OVOS-GUI-1](https://github.com/OpenVoiceOS/architecture/blob/dev/ovos-gui-1.md) (a
closed vocabulary of 22 `SYSTEM_*` templates; `ovos-gui` becomes a pure state/dispatch
hub; `session_id`-only addressing) and lands via these open PRs:

- [ovos-gui#112](https://github.com/OpenVoiceOS/ovos-gui/pull/112) — adapter/template rework
- [ovos-workshop#420](https://github.com/OpenVoiceOS/ovos-workshop/pull/420) — rebinds `self.gui` to the standalone `ovos-gui-api-client`
- [ovos-legacy-mycroft-gui-plugin#3](https://github.com/OpenVoiceOS/ovos-legacy-mycroft-gui-plugin/pull/3) and [pyhtmx-gui-client#1](https://github.com/OpenVoiceOS/pyhtmx-gui-client/pull/1) — `opm.gui_adapter` adapters

Until these merge, build against the current `self.gui` API described in
[GUI Support](docs/skill-gui.md). Pages describing the rework are marked **Upcoming**.

## Where is the project history?

See the [Timeline](docs/timeline.md).

## Where can I find info on deprecated features?

See the [Deprecation Log](docs/deprecation-log.md).

## How do I build the manual locally?

The manual is a MkDocs site, not a PyPI package. Clone it and serve:

```bash
git clone https://github.com/OpenVoiceOS/ovos-technical-manual
cd ovos-technical-manual
uv venv && uv pip install mkdocs mkdocs-material pymdown-extensions pygments==2.18.0
mkdocs serve   # preview at http://127.0.0.1:8000
```

(`pygments` must be pinned `<2.19`; newer pygments crashes `pymdown-extensions`.)

## Where do I report documentation errors?

Open an issue or PR on
[ovos-technical-manual](https://github.com/OpenVoiceOS/ovos-technical-manual);
the site deploys from `master`.

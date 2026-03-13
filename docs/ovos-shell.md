# OVOS Shell

[ovos-shell](https://github.com/OpenVoiceOS/ovos-shell) is the **production Qt5/[Kirigami](qt5-gui.md)
shell application** for OVOS on embedded and desktop devices (Mark 2, Raspberry Pi with
touchscreen, laptop). It wraps the `mycroft-gui-qt5` library (`Mycroft 1.0` [QML](qt5-gui.md) module)
inside a full-screen, frameless Kirigami application window.

It is distinct from the standalone `mycroft-gui-qt5` developer app: `ovos-shell` provides
the production UI chrome — status bar, sliding quick-settings panel, notifications, OSD,
splash screen, shutdown dialog, and homescreen — while delegating all skill rendering to
`Mycroft.SkillView`.

> **Voice First.** The visual interface is always secondary to the voice interface.
> All interactions should be completable with voice alone; touchscreen controls supplement
> but never replace voice.

---

## Architecture

```
ovos-shell/
├── application/             ← Main executable (ovos-shell binary)
│   ├── main.cpp             ← QApplication entry point
│   ├── qml/                 ← Shell QML
│   │   ├── main.qml             ← Root window (Kirigami.AbstractApplicationWindow)
│   │   ├── homescreen/          ← Built-in idle/homescreen
│   │   │   ├── HomescreenController.qml  ← Data broker (bus events → QML properties)
│   │   │   ├── idle.qml                  ← Root idle screen
│   │   │   ├── MainPage.qml, NightTimePage.qml
│   │   │   └── … (17 more sub-components)
│   │   ├── panel/               ← Sliding quick-settings panel
│   │   ├── osd/                 ← On-screen display (volume, etc.)
│   │   ├── StatusIndicator.qml
│   │   ├── ListenerAnimation.qml
│   │   └── …
├── lib/                     ← OVOSPlugin 1.0 QML module (Configuration, PlacesModel)
├── theme/                   ← OVOS Kirigami theme plugin (KF5 ≥ 5.91)
├── theme-legacy/            ← OVOS Kirigami theme plugin (KF5 < 5.91)
└── schemes/                 ← Colour scheme files

```

### Dependencies

| Dependency | Role |
|---|---|
| `mycroft-gui-qt5` | `Mycroft 1.0` QML module — `SkillView`, `MycroftController`, system templates |
| Qt5 (≥ 5.12) | Core, Quick, WebView, Widgets, DBus |
| KF5 Kirigami2 | Application window, theme, layouts |
| KF5 DBusAddons | D-Bus service registration |
| KF5 Config / ConfigWidgets | Settings persistence |

`ovos-shell` does **not** duplicate system templates. It inherits all 21 template QML
files from `mycroft-gui-qt5` (installed to `$prefix/share/mycroft-gui/system-templates/`).

---

## Component Responsibilities

### `main.qml`

- Root `Kirigami.AbstractApplicationWindow` — full screen, frameless


- Monitors `Mycroft.MycroftController.status` to restart GUI/skill service watchers


- Embeds `Mycroft.SkillView` for skill rendering


- Hosts `StatusIndicator`, `ListenerAnimation`, `SlidingPanel`, notification popups, OSD


- Shows `homescreen/idle.qml` via `Loader` when the skill stack is empty:

```qml
Loader {
    id: homescreenLoader
    anchors.fill: parent
    z: 1
    source: "homescreen/idle.qml"
    visible: !mainView.currentItem && serviceWatcher.guiServiceAlive
}

```

### `Mycroft.SkillView` (from `mycroft-gui-qt5`)

- Displays the active namespace stack


- Loads QML pages via `SYSTEM:` URI → local file resolution


- Manages namespace transitions and animations

### `SlidingPanel` / `QuickSettings`

- Swipe-up panel with mute, volume, brightness, wireless, reboot, shutdown controls


- Uses `OVOSPlugin.Configuration` for reading current device state

### `StatusIndicator`

- Subscribes to OVOS status events (`recognizer_loop:wakeword`, `recognizer_loop:record_begin`, etc.)


- Drives the listening animation

---

## Homescreen (Built-In Idle Screen)

The homescreen is built directly into `ovos-shell`. It replaces `ovos-skill-homescreen`,
which is deprecated.

### Architecture

```
ovos-legacy-mycroft-gui-plugin
  HomescreenManager
      │  emits homescreen.data.time, .weather, .wallpaper,
      │         .notifications, .apps, .examples, .connectivity
      │         homescreen.widget.timer, .alarm, .media
      ▼
ovos-shell  application/qml/homescreen/
  HomescreenController.qml
      │  subscribes to homescreen.data.* + homescreen.widget.*
      │  exposes: timeString, weatherCode, applicationsModel, …
      ▼
  idle.qml
      │  root Item; instantiates HomescreenController
      │  provides sessionData shim for sub-components
      ▼
  MainPage.qml, NightTimePage.qml, WeatherArea.qml, …

```

### `HomescreenController.qml`

Subscribes to bus events via `Mycroft.MycroftController.onIntentRecevied` and exposes
**plain QML properties** — no `sessionData`, no SkillView namespace.

| Bus event consumed | QML properties updated |
|---|---|
| `homescreen.data.time` | `timeString`, `dateString`, `weekdayString`, `dayString`, `monthString`, `yearString` |
| `homescreen.data.weather` | `weatherEnabled`, `weatherCode`, `weatherTemp` |
| `homescreen.data.wallpaper` | `wallpaperPath`, `selectedWallpaper` |
| `homescreen.data.notifications` | `notificationCounter`, `notificationModel` |
| `homescreen.data.apps` | `applicationsModel`, `appsEnabled` |
| `homescreen.data.examples` | `skillExamples`, `examplesEnabled`, `examplesPrefix` |
| `homescreen.data.connectivity` | `systemConnectivity` |
| `homescreen.widget.timer` | `timerWidgetData`, `timerWidgetCount` |
| `homescreen.widget.alarm` | `alarmWidgetData`, `alarmWidgetCount` |
| `homescreen.widget.media` | `mediaWidgetEnabled`, `mediaWidgetData`, `mediaWidgetState` |
| `mycroft.device.show.idle` / `ovos.homescreen.displayed` | emits `homescreenRequested()` signal |

`idle.qml` defines a `property QtObject sessionData` shim that maps each `sessionData.xxx`
name to `homescreenController.yyy`, so sub-components (`DayMonthDisplay`, `WeatherArea`,
etc.) continue using `sessionData.xxx` via QML scope lookup without modification.

### Homescreen sub-components

| File | Role |
|---|---|
| `HomescreenController.qml` | Data broker |
| `idle.qml` | Root idle screen; mounts HomescreenController; hosts StackLayout and apps Drawer |
| `MainPage.qml` | Main idle view (clock, weather, examples, widgets) |
| `NightTimePage.qml` | Night-mode clock-only view |
| `HorizontalDisplayLayout.qml` | Landscape two-column layout |
| `VerticalDisplayLayout.qml` | Portrait single-column layout |
| `TimeDisplay.qml` | Large clock label |
| `WeatherArea.qml` | Weather icon + temperature; offline indicator |
| `WidgetsArea.qml` | Timer / alarm / media widget row |
| `MediaWidgetButton.qml` | [OCP](ocp-pipeline.md) playback controls widget |
| `MediaWidgetDisplay.qml` | OCP track info display |
| `AppsBar.qml` | App launcher icons (bottom Drawer) |
| `ExamplesDisplay.qml` | Rotating example utterances bar |

### Data source: `HomescreenManager`

All homescreen data is produced by `HomescreenManager` in `ovos-legacy-mycroft-gui-plugin`.
It subscribes to:

- Datetime via `ovos_date_parser.get_date_strings()` (every 10 s)


- Weather via `skill-ovos-weather.openvoiceos.weather.request` / `.response` (every 900 s)


- Wallpaper via `homescreen.wallpaper.set` ([PHAL](ovoscope-phal.md) wallpaper manager)


- Notifications via `ovos.notification.update_counter` / `ovos.notification.update_storage_model`


- Apps via `homescreen.register.app` / `detach_skill`


- Examples via `homescreen.register.examples` / `detach_skill` (every 900 s refresh)


- Connectivity via `mycroft.network.connected`, `mycroft.internet.connected`, `enclosure.notify.no_internet`


- Timer/alarm widgets via `ovos.widgets.timer.*` / `ovos.widgets.alarm.*`


- OCP media via `gui.player.media.service.sync.status` / `ovos.common_play.track_info.response`

### Deprecated: `ovos-skill-homescreen`

| Was in skill | Now in |
|---|---|
| `gui/qt5/*.qml` | `ovos-shell/application/qml/homescreen/` |
| Python data coordination | `ovos-legacy-mycroft-gui-plugin` `HomescreenManager` |
| `@resting_screen_handler` | Not needed — homescreen is shown when stack is empty |

The skill now contains only a stub `handle_idle` that emits `ovos.homescreen.displayed`
and will be archived once all deployments have updated.

---

## Configuration

### Theme / Colour (`OvosTheme` KConfig)

The `OVOSPlugin.Configuration` QML singleton reads and writes `~/.config/OvosTheme`
(standard KConfig format).

```ini
[ColorScheme]
primaryColor=#313131
secondaryColor=#F70D1A
textColor=#F1F1F1
themeStyle=dark

[SelectedScheme]
name=default
path=/usr/share/OVOS/ColorSchemes/default.json

```

| Group | Key | Default | Description |
|---|---|---|---|
| `ColorScheme` | `primaryColor` | `#313131` | Primary UI background colour (ARGB hex) |
| `ColorScheme` | `secondaryColor` | `#F70D1A` | Accent colour (OVOS red) |
| `ColorScheme` | `textColor` | `#F1F1F1` | Primary text colour |
| `ColorScheme` | `themeStyle` | `dark` | Kirigami theme style: `dark` or `light` |
| `SelectedScheme` | `name` | `default` | Display name of the active colour scheme |
| `SelectedScheme` | `path` | `default` | Filesystem path to the active scheme's `.json` file |

When individual colours are set via the quick-settings panel, `SelectedScheme` is set to
`name=custom`, `path=custom`.

### Colour Scheme Files

Scheme `.json` files are loaded from (in priority order):

1. `/usr/local/share/OVOS/ColorSchemes/*.json`


2. `/usr/share/OVOS/ColorSchemes/*.json`


3. `$XDG_DATA_HOME/OVOS/ColorSchemes/` (typically `~/.local/share/OVOS/ColorSchemes/`)

Minimum required keys:

```json
{
  "name": "My Scheme",
  "primaryColor": "#FF1a1a2e",
  "secondaryColor": "#FFe94560",
  "textColor": "#FFffffff"
}

```

Colors must include an alpha prefix (e.g. `FF` for fully opaque).

The `Configuration` class watches all three directories with `QFileSystemWatcher` and
emits `schemeListChanged()` when files are added or removed.

### System Template Override (`OVOS_SYSTEM_TEMPLATES`)

Set this environment variable before launching `ovos-shell` to override individual
system-template QML files. Only the templates you want to customise need to be present
in the directory; others fall through to `mycroft-gui-qt5` defaults.

```bash
#!/bin/bash

# /usr/bin/ovos-shell-launch (example wrapper)
export OVOS_SYSTEM_TEMPLATES=/usr/share/ovos-shell/system-templates
exec /usr/bin/ovos-shell "$@"

```

Template resolution order:

1. `$OVOS_SYSTEM_TEMPLATES/<Name>.qml` — if the env var is set **and** the file exists


2. `$MYCROFT_SYSTEM_TEMPLATES_DIR/<Name>.qml` — compiled-in default
   (`/usr/share/mycroft-gui/system-templates/`)

---

## GUI Screenshots

Display settings panel:

![](https://github.com/OpenVoiceOS/ovos_assets/raw/master/Images/shell_settings.gif)

Colour theme editor:

![](https://github.com/OpenVoiceOS/ovos_assets/raw/master/Images/shell_theme.gif)

---

## Companion Plugins

To unlock full functionality, configure `ovos-gui-plugin-shell-companion` in
`mycroft.conf`. This plugin integrates with `ovos-gui` to provide:

- Colour scheme manager


- Notification widgets


- Configuration provider (settings UI)


- Brightness control (night mode, etc.)

```json
{
  "gui": {
    "extension": "ovos-gui-plugin-shell-companion"
  }
}

```

`ovos-shell` is tightly coupled to [PHAL](ovoscope-phal.md). The following PHAL plugins
should also be installed for a fully functional shell:

- `ovos-PHAL-plugin-network-manager`


- `ovos-PHAL-plugin-gui-network-client`


- `ovos-PHAL-plugin-wifi-setup`


- `ovos-PHAL-plugin-alsa`


- `ovos-PHAL-plugin-system`

---

## Building

```bash
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr
make -j$(nproc)
sudo make install

```

The `Mycroft 1.0` QML module (from `mycroft-gui-qt5`) must be installed before building
`ovos-shell`.

---

## Qt Version Policy

This repository targets **Qt5**. A separate `ovos-shell-qt6` repository will target Qt6.
Both link against their respective `mycroft-gui` library versions. Do not introduce
Qt6-only API into this repository.

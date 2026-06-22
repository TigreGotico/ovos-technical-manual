# OVOS Shell

!!! danger "The OVOS GUI is deprecated — assume it is not usable today"
    `ovos-shell` is part of the **legacy** OVOS GUI stack, which is **deprecated** and should
    be treated as **broken**: **there is no generally usable OVOS GUI right now**. A ground-up
    replacement (the [GUI rework](gui-adapters.md), spec **OVOS-GUI-1**) is actively being
    built but is **not yet ready**. On **Mark 2** devices the
    [`ovos-installer`](ovos-installer.md) still installs `ovos-shell` so those devices keep a
    screen until the replacement lands. Kept for reference and Mark 2 maintenance.

[ovos-shell](https://github.com/OpenVoiceOS/ovos-shell) is the **legacy Qt5/[Kirigami](qt5-gui.md)
shell application** for OVOS on embedded and desktop devices (Mark 2, Raspberry Pi with
touchscreen, laptop). It wraps the `mycroft-gui-qt5` library (`Mycroft 1.0` [QML](qt5-gui.md) module)
inside a full-screen, frameless Kirigami application window.

It is distinct from the standalone `mycroft-gui-qt5` developer app: `ovos-shell` provides
the production UI chrome — status indicator, sliding quick-settings panel, notifications,
OSD, splash screen, pairing/OAuth loaders, and shutdown dialog — while delegating all skill
rendering to `Mycroft.SkillView`. The idle screen itself is supplied by a homescreen
skill (see [Home Screen](homescreen.md)), not by the shell.

> **Voice First.** The visual interface is always secondary to the voice interface.
> All interactions should be completable with voice alone; touchscreen controls supplement
> but never replace voice.

---

## Architecture

```
ovos-shell/
├── application/             ← Main executable (ovos-shell binary)
│   ├── main.cpp             ← QApplication entry point
│   ├── plugins/             ← EnvironmentSummary, ResetOperations
│   ├── qml/                 ← Shell QML
│   │   ├── main.qml             ← Root window (Kirigami.AbstractApplicationWindow)
│   │   ├── panel/               ← Sliding quick-settings panel (+ quicksettings/)
│   │   ├── osd/                 ← On-screen display (volume, etc.)
│   │   ├── StatusIndicator.qml, ListenerAnimation.qml
│   │   ├── SplashScreen.qml, ShutdownOptions.qml, ServiceWatcher.qml
│   │   ├── NotificationsSystem.qml, NotificationPop*.qml
│   │   ├── OAuthLoader.qml, OAuthQrCodeLoader.qml, PairingArea.qml
│   │   └── Keyboard.qml, FactoryResetUI.qml, KdeConnect.qml
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

`ovos-shell` does not bundle skill-page QML itself. Skill pages and the built-in
`SYSTEM_*` pages are resolved by the `Mycroft.SkillView` runtime from `mycroft-gui-qt5`.

---

## Component Responsibilities

### `main.qml`

- Root `Kirigami.AbstractApplicationWindow` — full screen, frameless


- Monitors `Mycroft.MycroftController.status` to restart GUI/skill service watchers


- Embeds `Mycroft.SkillView` for skill rendering


- Hosts `StatusIndicator`, `ListenerAnimation`, `SlidingPanel`, notification popups, OSD


- When the skill stack is empty, the shell shows a plain background image; the actual idle
  screen is drawn by a homescreen skill rendered through `Mycroft.SkillView`:

```qml
Image {
    source: "background.png"
    fillMode: Image.PreserveAspectFit
    anchors.fill: parent
    opacity: !mainView.currentItem && serviceWatcher.guiServiceAlive
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

## Homescreen (Idle Screen)

The shell does not draw the idle screen itself. When the namespace stack is empty it shows
a plain background image; the actual homescreen is provided by a skill (default
`skill-ovos-homescreen.openvoiceos`) whose resting-screen page is rendered through
`Mycroft.SkillView`. Skills register idle screens with `@resting_screen_handler`. See
[Home Screen](homescreen.md) for the configuration and the resting-screen API.

!!! warning "Upcoming — unreleased"
    The GUI rework ([OpenVoiceOS/ovos-gui#112](https://github.com/OpenVoiceOS/ovos-gui/pull/112),
    specified by [architecture#63](https://github.com/OpenVoiceOS/architecture/pull/63))
    moves homescreen data coordination into a `HomescreenManager` inside
    `ovos-legacy-mycroft-gui-plugin`
    ([PR #3](https://github.com/OpenVoiceOS/ovos-legacy-mycroft-gui-plugin/pull/3),
    `feat/session-id-contract`), which subscribes to datetime, weather, wallpaper,
    notification, app, example, connectivity, and widget sources and re-emits them as
    `homescreen.data.*` / `homescreen.widget.*` bus messages for a client to render. This
    is **not** in any released shell and the shell itself contains no `homescreen/` QML on
    `master`. The resting-screen skill API (`@resting_screen_handler`, `idle_display_skill`)
    remains the supported mechanism on released OVOS. A Qt6 client successor is in flight at
    [mycroft-gui-qt6#7](https://github.com/OpenVoiceOS/mycroft-gui-qt6/pull/7).

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

The `Configuration` QML singleton (`OVOSPlugin.Configuration`) is implemented in
`lib/configuration.cpp` and exposes these read/write properties to QML.

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

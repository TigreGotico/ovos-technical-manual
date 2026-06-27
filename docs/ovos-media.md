# ovos-media

!!! abstract "In a nutshell"
    `ovos-media` is the planned future replacement for how OVOS plays music, podcasts and videos. Today, stock installs still use the older audio backend; `ovos-media` is an opt-in, work-in-progress rewrite meant to handle audio, video and web playback more cleanly and to support several players at once. If you are not deliberately trying it out, you are not using it yet — this page describes where things are heading. See the [OCP Pipeline](ocp-pipeline.md) for how playback requests are recognised, or the [Glossary](glossary.md) for terms.

!!! info "📐 Formal specification"
    Media playback is specified by two architecture documents:
    **[OVOS-OCP-1 — OVOS Common Playback](https://github.com/OpenVoiceOS/architecture/blob/dev/ocp-1.md)**
    defines the per-session **virtual media player** — the single logical
    player every "play / pause / next / louder / stop" command targets, plus
    the MPRIS bridge to and from the host OS — while
    **[OVOS-AUDIO-1 — Audio Output Service](https://github.com/OpenVoiceOS/architecture/blob/dev/audio-out.md)**
    defines the **output service** that actually renders queued audio. OCP-1
    fixes the *observable control surface*; how a URI becomes bytes on a
    speaker is a backend concern. `ovos-media` is the implementation moving
    toward that contract. For the full set see the
    **[spec index](architecture-specs.md)**.

!!! warning "Upcoming — a refactor that is not the default yet"
    `ovos-media` is the **upcoming** media-playback service for OVOS, still being refactored.
    It is **not enabled by default**. Today, stock installs play media through the **legacy
    audio backend** — the [`ovos-ocp-audio-plugin`](media-plugins.md#ovos-ocp-audio-plugin)
    ("old audio service") inside [`ovos-audio`](audio-service.md), which is **deprecated but
    still shipped**. Switching to `ovos-media` is opt-in (see below) and some parts are still
    coupled (Qt5 GUI, player-as-skill). Treat this page as the *target architecture*.

!!! info "Which media system am I running? (legacy vs. ovos-media)"
    OVOS has **two media-playback backends** that share the same [OCP](ocp-pipeline.md)
    search framework (pipeline + skills + extractors):

    | | Legacy (current default) | ovos-media (upcoming) |
    |---|---|---|
    | **Package** | `ovos-ocp-audio-plugin` in [`ovos-audio`](audio-service.md) | `ovos-media` (standalone daemon) |
    | **Status** | deprecated, still shipped & on by default | opt-in refactor, not default |
    | **Playback** | one bundled audio backend | per-request audio/video/web [media plugins](media-plugins.md) (`opm.media.*`) |
    | **Extras** | — | MPRIS, per-session state, multiple players |
    | **Config** | `enable_old_audioservice: true` (default) | `enable_old_audioservice: false` + run `ovos-media` |

    The OCP **pipeline** and **stream extractors** are unaffected by which backend you use —
    only the *playback* layer differs. (OCP **skills** are a separate, longer-term change —
    see the next note.)

!!! info "Upcoming — MediaProvider plugins replace OCP skills"
    Media catalogs are moving **out of skills and into plugins**: a new **MediaProvider** plugin
    type (`opm.media.provider` / `PluginTypes.MEDIA_PROVIDER`) that the OCP pipeline loads
    **in-process** and calls `search()` on directly, in place of today's
    [OCP skills](ocp-skills.md). This is **upcoming, not released** — in flight in
    [ovos-plugin-manager#405](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/405)
    (Phase 1 of the `ovos-media` migration). OCP skills remain the way to provide media for now.

`ovos-media` is the standalone audio/video daemon for OpenVoiceOS. It is the **upcoming
replacement** for the legacy audio service, providing a more robust and modular media player
built on the OpenVoiceOS [Common Play](ocp-pipeline.md) ([OCP](ocp-pipeline.md)) framework.

**In plain terms:** the old audio service could only play one kind of stream through a thin wrapper. `ovos-media` is a proper media daemon: it has separate audio/video/web players you pick per request, supports MPRIS (so your phone's media controls work), and keeps per-session state so multiple devices can each play their own thing.

To use `ovos-media` you need to disable the old audio service and enable the OCP pipeline in `ovos-core`:

```json
{
  "enable_old_audioservice": false
}

```

```json
{
  "intents": {
    "pipeline": [
      "ovos-converse-pipeline-plugin",
      "ovos-ocp-pipeline-plugin-high",
      "...",
      "ovos-common-query-pipeline-plugin",
      "ovos-ocp-pipeline-plugin-medium",
      "...",
      "ovos-ocp-pipeline-plugin-low",
      "ovos-fallback-pipeline-plugin-low"
    ]
  }
}

```

---

## Architecture

OCP (OVOS Common Play) splits into a **search/match layer** and a **playback layer**. The search
layer — the [`ocp-pipeline`](ocp-pipeline.md), OCP skills (media catalogs), and stream extractors —
is shared regardless of which playback layer you run. The playback layer has two implementations
that currently run in parallel: the legacy ["old audio service"](media-plugins.md#ovos-ocp-audio-plugin)
(`ovos-ocp-audio-plugin` inside [`ovos-audio`](audio-service.md)) and the standalone `ovos-media`
daemon described here, which is the target:

```
[Current / target]
  ovos-core intent pipeline
    └── ocp-pipeline-plugin
          └── Search dispatch → OCP skills → results → ovos-media

  ovos-media (standalone daemon)
    ├── Player state machine (OCPMediaCatalog)
    ├── MPRIS
    ├── Media backend plugins
    └── GUI (still coupled — target: GUI adapter plugins)

```

---

## OCP Pipeline Plugin

**Package:** import name `ocp_pipeline` (PyPI distribution `ovos-ocp-pipeline-plugin`)
**Entry point group:** `opm.pipeline`
**Class:** `OCPPipelineMatcher` (entry point `ovos-ocp-pipeline-plugin`); the legacy bridge is `MycroftCPSLegacyPipeline` (`ovos-ocp-pipeline-plugin-legacy`)

The OCP pipeline plugin is the NLP brain of the media stack. It integrates with `ovos-core`'s
intent pipeline, handles all media query classification, and dispatches search to OCP skills.
It does NOT handle playback.

### What It Does

1. **Classification** — determines the media type (music, podcast, radio, video, audiobook, news, etc.)
   using a trained `AhocorasickNER` classifier and vocabulary files from `ocp_pipeline/locale/`.

2. **Search dispatch** — emits `ovos.common_play.query` on the bus. All registered OCP skills
   respond with `ovos.common_play.query.response`, providing `MediaEntry`/`Playlist` objects scored 0–100.

3. **Result selection** — collects responses up to a timeout, sorts by score, picks the best result.


4. **Playback routing** — emits `ovos.common_play.play` with the selected result to the active player.

### Per-[Session](session.md) Player State

The pipeline plugin tracks one `OCPPlayerProxy` per session — important for [HiveMind](hivemind-agents.md) where each
satellite has its own player:

```python
@dataclass
class OCPPlayerProxy:
    session_id: str
    available_extractors: List[str]
    ocp_available: bool
    player_state: PlayerState = PlayerState.STOPPED
    media_state: MediaState = MediaState.UNKNOWN
    media_type: MediaType = MediaType.GENERIC
    skill_id: Optional[str] = None

```

### Pipeline Configuration

The OCP matcher contributes several confidence-ranked pipeline stages — `ovos-ocp-pipeline-plugin-high`, `-medium`, `-low`, plus `ovos-ocp-pipeline-plugin-legacy` for old-style CommonPlay skills. Place them at the appropriate confidence tier in your pipeline:

```json
{
  "intents": {
    "pipeline": [
      "...",
      "ovos-ocp-pipeline-plugin-high",
      "ovos-ocp-pipeline-plugin-medium",
      "ovos-ocp-pipeline-plugin-low",
      "..."
    ]
  }
}

```

### OCP Skills

OCP skills inherit `OVOSCommonPlaybackSkill` and register by emitting `ovos.common_play.announce`:

```python
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill, MediaType
from ovos_utils.ocp import MediaEntry

class MyMusicSkill(OVOSCommonPlaybackSkill):
    @ocp_search()
    def search_my_service(self, phrase, media_type):
        # Return MediaEntry or Playlist objects scored 0-100
        if media_type == MediaType.MUSIC:
            yield MediaEntry(
                title="My Song",
                uri="https://example.com/song.mp3",
                confidence=85,
                media_type=MediaType.MUSIC,
            )

    @ocp_featured_media()
    def featured_media(self):
        # Optional: return a playlist for the OCP browse UI
        return Playlist(title="My Playlist", media=[...])

```

Skills must NOT handle playback. They must NOT have intents for play/pause/stop/next.

### Bus Messages

#### Inbound (to pipeline from skills / player)

| Message | Description |
|---|---|
| `ovos.common_play.query.response` | OCP skill returning search results |
| `ovos.common_play.announce` | OCP skill announcing presence |
| `ovos.common_play.player.state` | Player state update |
| `ovos.common_play.media.state` | Media state update |
| `ovos.common_play.track.state` | Track state update |

#### Outbound (from pipeline to skills / player)

| Message | Description |
|---|---|
| `ovos.common_play.query` | Dispatch search to all OCP skills |
| `ovos.common_play.play` | Tell player to play selected result |
| `ovos.common_play.pause` | Pause |
| `ovos.common_play.resume` | Resume |
| `ovos.common_play.stop` | Stop |
| `ovos.common_play.next` | Next track |
| `ovos.common_play.prev` | Previous track |

---

## ovos-media Player

**Entry point:** `ovos-media` (runs `ovos_media.__main__:main`)

Key modules:

- `ovos_media/player.py` — `OCPMediaCatalog` (`OVOSCommonPlaybackSkill` subclass); manages playlists, track history, liked songs


- `ovos_media/media_backends/` — `AudioService`, `VideoService`, `WebService` — each manages typed backend plugins


- `ovos_media/player.py` — uses a `GUIInterface` from `ovos-gui-api-client` (`self.gui.show_media_player(...)`) to push player state via the template API (the old `ovos_media/gui.py` / `OCPGUIInterface` is gone)


- `ovos_media/mpris.py` — MPRIS integration

### Available Media Backend Plugins

Media backends are typed: audio players register on the `opm.media.audio` entry-point group,
video players on `opm.media.video`, and web players on `opm.media.web`. They are configured under
`media.audio_players` / `media.video_players` / `media.web_players` (see the config example below).

The table below lists the **pip package** to install; each package registers one entry point per
type it supports, named `ovos-media-<type>-plugin-<name>` (e.g. the `ovos-media-plugin-vlc`
package registers `ovos-media-audio-plugin-vlc` and `ovos-media-video-plugin-vlc`). You configure
the player by its entry-point name.

| Package | Types | Description |
|---|---|---|
| [`ovos-media-plugin-vlc`](https://github.com/OpenVoiceOS/ovos-media-plugin-vlc) | audio, video | VLC instance |
| [`ovos-media-plugin-mplayer`](https://github.com/OpenVoiceOS/ovos-media-plugin-mplayer) | audio, video | mplayer |
| [`ovos-media-plugin-simple`](https://github.com/OpenVoiceOS/ovos-media-plugin-simple) | audio | Minimal audio player (simple fallback) |
| [`ovos-media-plugin-spotify`](https://github.com/OpenVoiceOS/ovos-media-plugin-spotify) | audio | Spotify Connect |
| [`ovos-media-plugin-chromecast`](https://github.com/OpenVoiceOS/ovos-media-plugin-chromecast) | audio, video | Cast to a Chromecast device |
| [`ovos-media-plugin-qt5`](https://github.com/OpenVoiceOS/ovos-media-plugin-qt5) | audio, video, web | Hand off to the [GUI](gui-service.md) player ([ovos-shell](ovos-shell.md)) |

### Stream Extractor Plugins

OCP supports stream extractor plugins (`opm.ocp.extractor` entry-point group; the older
`ovos.ocp.extractor` group is a deprecated alias) that transform non-playable URIs into playable
streams before handing them to the media backend:

- `ovos-ocp-youtube-plugin` — extracts audio stream from YouTube URLs


- `ovos-ocp-m3u-plugin` — parses M3U playlists


- `ovos-ocp-rss-plugin` — parses podcast RSS feeds

---

## Media Intents

Before the regular intent stage, OCP handles these utterances (taking into account current player state):

- `"play {query}"` — always available


- `"previous"` — requires media loaded


- `"next"` — requires media loaded


- `"pause"` — requires media loaded


- `"play"` / `"resume"` — requires media loaded


- `"stop"` — requires media loaded


- `"I like that song"` — requires music playing

---

## MPRIS Integration

OCP integrates with MPRIS, allowing OCP to control and be controlled by external players.
Via MPRIS (and KDEConnect), OCP can display data from external players and control playback
in connected devices.

```json
{
  "media": {
    "enable_mpris": true,
    "dbus_type": "session"
  }
}

```

Confirm OCP is registered with dbus:

```bash
dbus-send --session --dest=org.freedesktop.DBus --type=method_call --print-reply \
  /org/freedesktop/DBus org.freedesktop.DBus.ListNames

# Should show: "org.mpris.MediaPlayer2.OCP"

```

---

## Configuration

```json
{
  "media": {
    "enable_mpris": false,

    "preferred_audio_services": ["gui", "vlc", "mplayer", "cli"],
    "preferred_video_services": ["gui", "vlc"],
    "preferred_web_services": ["gui", "browser"],

    "audio_players": {
      "vlc": {
        "module": "ovos-media-audio-plugin-vlc",
        "aliases": ["VLC"],
        "active": true
      },
      "cli": {
        "module": "ovos-media-audio-plugin-cli",
        "aliases": ["Command Line"],
        "active": true
      },
      "gui": {
        "module": "ovos-media-audio-plugin-gui",
        "aliases": ["GUI", "Graphical User Interface"],
        "active": true
      }
    },

    "video_players": {
      "vlc": {
        "module": "ovos-media-video-plugin-vlc",
        "aliases": ["VLC"],
        "active": true
      },
      "gui": {
        "module": "ovos-media-video-plugin-gui",
        "aliases": ["GUI", "Graphical User Interface"],
        "active": true
      }
    },

    "web_players": {
      "browser": {
        "module": "ovos-media-web-plugin-browser",
        "aliases": ["Browser", "Local Browser", "Default Browser"],
        "active": true
      },
      "gui": {
        "module": "ovos-media-web-plugin-gui",
        "aliases": ["GUI", "Graphical User Interface"],
        "active": true
      }
    }
  }
}

```

---

## Legacy Compatibility

### ClassicAudioServiceInterface

When `ovos-media` is not running (i.e., the system still uses `ovos-ocp-audio-plugin` inside
`ovos-audio`), the pipeline plugin falls back to emitting `mycroft.audio.service.*` bus messages
to control the classic audio service via `ovos_bus_client.apis.ocp.ClassicAudioServiceInterface`.

### LegacyCommonPlay Bridge

For skills that still use the old Mycroft `CommonPlaySkill` base class (pre-OCP), the pipeline
plugin includes a bridge:

- Emits `play:query` instead of `ovos.common_play.query`


- Collects `play:query.response` from old-style skills


- Emits `play:start` to tell the winning skill to handle playback itself

This bridge is marked for removal in `ovos-core 0.1.0`.

---

## Known Coupling Issues

### OCPMediaCatalog is a skill

`ovos_media/player.py` inherits from `OVOSCommonPlaybackSkill`. This registers `ovos-media` as
a skill on the bus and loads skill infrastructure (settings, locale, etc.). It also registers
`@ocp_search()` for liked songs and `@ocp_featured_media()` for the browse view.

### No next/prev in some backends

The Music Assistant audio backend does not implement `next()` or `previous()` through the legacy
`AudioBackend` interface — only through the MA queue API.

---

## Features

### Liked Songs

Like a currently playing song via GUI or the intent "I like that song". Liked songs can be played
via the intent "play my favorite songs" or through the GUI.

### Skills Browse / Featured Media

Some skills provide `@ocp_featured_media()`. These are accessible from the OCP skills menu in the GUI.

### File Browser Integration

Selected files and folders will be played in OCP. Folders are treated as playlists.

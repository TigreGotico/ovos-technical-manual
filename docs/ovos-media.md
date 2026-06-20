# ovos-media

`ovos-media` is the standalone audio/video daemon for OpenVoiceOS. It replaces the legacy audio service with a more robust and modular media player based on the OpenVoiceOS [Common Play](ocp-pipeline.md) ([OCP](ocp-pipeline.md)) framework.

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
      "converse",
      "ocp_high",
      "...",
      "common_qa",
      "ocp_medium",
      "...",
      "ocp_low",
      "fallback_low"
    ]
  }
}

```

---

## Architecture History

OCP (OVOS Common Play) was originally implemented as an `AudioBackend` plugin inside the Mycroft
audio service — a severe misuse of an interface designed for thin wrappers around playback binaries.
The result was `ovos-ocp-audio-plugin`: a monolith that crammed NLP, search orchestration, player
state machine, MPRIS, and GUI into a single mycroft audio backend.

The NLP portion was later extracted into `ovos-ocp-pipeline-plugin` (now `ocp-pipeline`), and the
player is now being migrated to `ovos-media`. Both the old plugin and the new daemon currently
exist in parallel:

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

**Package:** `ocp-pipeline` (`ovos_ocp_pipeline_plugin`)
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

The OCP matcher contributes several confidence-ranked pipeline stages — `ocp_high`, `ocp_medium`, `ocp_low`, plus `ocp_legacy` for old-style CommonPlay skills. Place them at the appropriate confidence tier in your pipeline:

```json
{
  "intents": {
    "pipeline": [
      "...",
      "ocp_high",
      "ocp_medium",
      "ocp_low",
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


- `ovos_media/gui.py` — `OCPGUIInterface`, `OCPGUIState` — pushes GUI state to mycroft-gui


- `ovos_media/mpris.py` — MPRIS integration

### Available Media Backend Plugins

Media backends are typed: audio players register on the `opm.media.audio` entry-point group,
video players on `opm.media.video`, and web players on `opm.media.web`. They are configured under
`media.audio_players` / `media.video_players` / `media.web_players` (see the config example below).

| Package | Type | Description |
|---|---|---|
| `ovos-media-audio-plugin-vlc` / `ovos-media-video-plugin-vlc` | audio / video | VLC instance |
| `ovos-media-audio-plugin-mplayer` | audio | mplayer |
| `ovos-media-audio-plugin-mpv` | audio | mpv |
| `ovos-media-audio-plugin-cli` | audio | Command-line player (simple fallback) |
| `ovos-media-audio-plugin-spotify` | audio | Spotify Connect |
| `ovos-media-audio-plugin-mass` | audio | Music Assistant |
| `ovos-media-web-plugin-browser` | web | Open in local browser |
| `ovos-media-audio-plugin-gui` / `ovos-media-video-plugin-gui` / `ovos-media-web-plugin-gui` | audio / video / web | Hand off to the GUI player |

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

### GUI still Qt5/mycroft-gui bound

`ovos_media/gui.py` still ships Qt5 [QML](qt5-gui.md) files (`ovos_media/qt5/`) and drives the GUI in the
mycroft-gui style. No alternative renderers (web UI, kiosk, headless) are supported without
replacing `gui.py`. The GUI adapter plugin system (`opm.gui_adapter`) is the planned fix but
has not yet been applied to `ovos-media`.

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

# OCP Pipeline

!!! abstract "In a nutshell"
    When you say "play some jazz" or "next song", the assistant first has to realise you are talking about *media* and not, say, the weather. This is the part that does that: it spots that an utterance is a playback request, figures out what kind of media you want, asks the installed music/podcast/video skills to search for it, and hands the best result off to be played. Think of it as the dispatcher that turns "play X" into actual playback. See the [Intent Pipeline](pipelines-overview.md) overview or the [Glossary](glossary.md) for related terms.

The **OCP (OVOS Common Play)** Pipeline Plugin handles media playback commands —
"play some jazz", "pause", "next song". It recognises that an utterance is about
media, works out what kind of media is wanted, asks OCP-enabled skills to search
for it, filters the results, and hands the best one to `ovos-audio` to play.

Skills act purely as catalogs: they return search results, they do not play
anything themselves. OCP centralises selection and playback.

---

## Quick start

```bash
pip install ovos-ocp-pipeline-plugin
```

It exposes confidence-tiered matchers (`ovos-ocp-pipeline-plugin-high`,
`ovos-ocp-pipeline-plugin-medium`, `ovos-ocp-pipeline-plugin-low`) plus a legacy
matcher (`ovos-ocp-pipeline-plugin-legacy`). A typical pipeline puts the high tier
early and the low tier last:

```json
{
  "intents": {
    "pipeline": [
      "ovos-ocp-pipeline-plugin-high",
      "ovos-padatious-pipeline-plugin-high",
      "ovos-adapt-pipeline-plugin-high",
      "ovos-ocp-pipeline-plugin-medium",
      "ovos-fallback-pipeline-plugin-medium",
      "ovos-ocp-pipeline-plugin-low"
    ]
  }
}
```

The older short names `ocp_high` / `ocp_medium` / `ocp_low` / `ocp_legacy` still work
as **deprecated aliases** (ovos-core rewrites them to the canonical IDs above), but new
configs should use the canonical names.

Then install OCP-enabled media skills and ask to play something.

---

## Pipeline matchers

The matcher class is `OCPPipelineMatcher`, registered under the single OPM entry point
`ovos-ocp-pipeline-plugin`. Because it is a `ConfidenceMatcherPipeline`, OVOS derives three
tier matchers from it at runtime via `match_high` / `match_medium` / `match_low` — you reference
them in the pipeline by the IDs below (the short `ocp_*` aliases are deprecated):

| Pipeline ID  | Legacy alias | Tier   | When to use |
|--------------|--------------|--------|-------------|
| `ovos-ocp-pipeline-plugin-high`   | `ocp_high`   | high   | Explicit OCP intents ("play.intent", "pause", "next") — primary media commands. |
| `ovos-ocp-pipeline-plugin-medium` | `ocp_medium` | medium | Utterance classified as a media query by keyword matching. |
| `ovos-ocp-pipeline-plugin-low`    | `ocp_low`    | low    | Broad keyword hits — only on devices used mainly for media playback. |

A separate class, `MycroftCPSLegacyPipeline`, is registered as its own entry point
`ovos-ocp-pipeline-plugin-legacy` (alias `ocp_legacy`). It
bridges to deprecated Mycroft CommonPlaySkill (CPS) skills and is off by default —
only useful if you still run legacy CPS skills.

> `ocp_low` keys off skill-registered media keywords, so it can fire on phrases
> that merely contain a known artist or show name even when no playback was
> intended. Place it last and only enable it on media-focused devices.

---

## How a media intent is recognised

OCP combines several signals:

* **Explicit intents** (`ocp_high`) — localized `.intent` files for play, pause,
  resume, stop, next, previous, shuffle, etc.
* **Keyword matching** (`ocp_medium` / `ocp_low`) — `voc_match_media()` maps
  vocabulary (MusicKeyword, PodcastKeyword, MovieKeyword, NewsKeyword, …) to a
  `MediaType` with a heuristic confidence. `is_ocp_query()` treats any non-GENERIC
  media type as a playback query.
* **Skill-registered keywords** — skills announce entities (artist names, show
  titles) over `ovos.common_play.register_keyword`; these feed the
  `AhocorasickNER` entity matcher and bias media-type classification.

Media-type classification on `dev` is keyword/vocab based (localizable, but
heuristic). If a query maps to exactly one media type that a skill can serve, that
type is used with full confidence.

Supported media types include `music`, `podcast`, `movie`, `radio`, `audiobook`,
`news`, and many more from `ovos_utils.ocp.MediaType`.

---

## Search and result filtering

After classifying, OCP emits `ovos.common_play.query` and gathers
`ovos.common_play.query.response` results from skills, then filters them in
`filter_results()`:

* **Confidence** — drops results whose `match_confidence` is below `min_score`.
* **Media-type consistency** — when a non-GENERIC type was classified, results of
  other types are removed (`filter_media`).
* **Stream-extractor availability** — results needing a Stream Extractor plugin
  (SEI) that is not installed are removed (`filter_SEI`). Available extractors come
  from the `opm.ocp.extractor` plugin group, queried via
  `ovos.common_play.SEI.get`.
* **Playback mode** — audio-only / video-only preferences drop incompatible
  results (`playback_mode`).

OCP tracks player state per `Session` over the bus (`ovos.common_play.status`,
`ovos.common_play.track.state`), so context-dependent commands behave correctly —
e.g. "next song" does nothing when no player is active.

---

## Configuration

```json
{
  "intents": {
    "ovos-ocp-pipeline-plugin": {
      "legacy": false,
      "min_score": 50,
      "filter_media": true,
      "filter_SEI": true,
      "playback_mode": 0,
      "search_fallback": true,
      "entity_csvs": []
    }
  }
}
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `legacy` | bool | `false` | Use the classic (Mycroft) audio service API instead of OCP. Not recommended. |
| `min_score` | int | `50` | Minimum `match_confidence` to keep a skill result (0–100). |
| `filter_media` | bool | `true` | Drop results whose media type differs from the classified one. |
| `filter_SEI` | bool | `true` | Drop results needing an unavailable Stream Extractor plugin. |
| `playback_mode` | int | `0` | `0` = auto, `10` = audio-only, `20` = video-only (`PlaybackMode`). |
| `search_fallback` | bool | `true` | Run a generic search when no type-specific results are found. |
| `entity_csvs` | list | `[]` | User-supplied keyword CSVs feeding the entity matcher. |

The config block is read from `intents.ovos-ocp-pipeline-plugin` (the plugin's
entry-point ID), the section ovos-core passes to the plugin when loading it.

---

## Gotcha: legacy vs. OCP playback

`ocp_legacy` and `legacy: true` are two different things. `ocp_legacy` is a
pipeline matcher that routes to deprecated Mycroft CPS skills; `legacy: true` forces
OCP to drive playback through the classic audio service API instead of OCP itself.
Leave both off unless you specifically need to support pre-OCP skills.

---

*Source code: [OpenVoiceOS/ovos-ocp-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-ocp-pipeline-plugin).*

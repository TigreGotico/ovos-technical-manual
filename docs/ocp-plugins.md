# OCP Plugins Reference

!!! abstract "In a nutshell"
    OCP (the OpenVoiceOS Common Play system) is the part of OVOS that plays media — music, podcasts, news, radio and the like. Each plugin on this page teaches it to handle one kind of source, such as YouTube links, Bandcamp pages, RSS feeds, or local files. So if you ask to play something, the right plugin knows how to find the actual audio stream and start it. See the [Glossary](glossary.md) for unfamiliar terms.

| Plugin | Description |
|--------|-------------|
| [ovos-ocp-files-plugin](#ovos-ocp-files-plugin) | Lets OCP play local files (`file://` URIs) and reads their audio tags/metadata so the player can show a title and artist |
| [ovos-ocp-news-plugin](#ovos-ocp-news-plugin) | Extracts the real stream for a known set of spoken-news provider URLs at playback time |
| [ovos-ocp-bandcamp-plugin](#ovos-ocp-bandcamp-plugin) | Scrapes Bandcamp pages via `py-bandcamp` to extract the real audio stream |
| [ovos-ocp-rss-plugin](#ovos-ocp-rss-plugin) | Parses an RSS/podcast feed and extracts the newest audio enclosure as the playable stream |
| [ovos-ocp-youtube-plugin](#ovos-ocp-youtube-plugin) | Resolves YouTube/YouTube Music URLs via a selectable `yt-dlp`/pytube/Invidious/webview backend |
| [ovos-ocp-m3u-plugin](#ovos-ocp-m3u-plugin) | Downloads a `.pls`/`.m3u` playlist and extracts the first playable stream URL inside it |
| [ovos-media-classifier](#ovos-media-classifier) | ⚠️ experimental — pluggable media-intent classifier that routes a request to the right `MediaProvider`s |

## ovos-ocp-files-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ocp-files-plugin](https://github.com/OpenVoiceOS/ovos-ocp-files-plugin)


- **Description**: A stream extractor that lets OCP play local files (`file://` URIs, or plain
  paths on disk) and reads their embedded audio tags (title, artist, album) so the player can
  display them. It bundles a fork of the `audio-metadata` tag-reading library.

---

## ovos-ocp-news-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ocp-news-plugin](https://github.com/OpenVoiceOS/ovos-ocp-news-plugin)


- **Description**: A stream extractor for spoken-news providers. It registers the stream
  extractor id (SEI) `news`, so any result URI of the form `news//<url>` is routed to it; it
  also recognizes a hardcoded table of known news-provider URLs directly (`URL_MAPPINGS`) so
  skills can hand it a raw provider URL without the `news//` prefix. At playback time it looks
  the URL up in that table and calls the matching extractor function to resolve the real,
  playable stream.

---

## ovos-ocp-bandcamp-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ocp-bandcamp-plugin](https://github.com/OpenVoiceOS/ovos-ocp-bandcamp-plugin)


- **Description**: A stream extractor for [Bandcamp](https://bandcamp.com) pages, registering
  the SEI `bandcamp`. It recognizes both `bandcamp//<url>` results and any bare URL containing
  `bandcamp.`, then delegates the actual page scraping to the `py-bandcamp` library
  (`get_stream_data`) to pull out the real audio stream URL and track metadata.

---

## ovos-ocp-rss-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ocp-rss-plugin](https://github.com/OpenVoiceOS/ovos-ocp-rss-plugin)


- **Description**: A stream extractor for RSS/podcast feeds, registering the SEI `rss`. Given a
  `rss//<feed-url>` (or bare feed URL), it parses the feed with `feedparser`, takes the most
  recent entry, and returns the first enclosure link whose MIME type contains `audio` — along
  with that entry's title, publish timestamp, and duration when the feed provides them. It only
  ever surfaces the newest playable item in the feed, not the whole episode list.

---

## ovos-ocp-youtube-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ocp-youtube-plugin](https://github.com/OpenVoiceOS/ovos-ocp-youtube-plugin)


- **Description**: A stream extractor for YouTube and YouTube Music links. Unlike the other
  extractors on this page, it is a small router over multiple interchangeable backends —
  `youtube-dl`/`yt-dlp`, `pytube`, an Invidious mirror, or a webview fallback — selectable via
  the `youtube_backend` / `ydl_backend` / `invidious_host` settings, since any single scraping
  approach tends to break whenever YouTube changes its page format. It also has a dedicated path
  for resolving a channel's current live stream.

---

## ovos-ocp-m3u-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ocp-m3u-plugin](https://github.com/OpenVoiceOS/ovos-ocp-m3u-plugin)


- **Description**: A stream extractor for `.m3u` and `.pls` playlist URLs, registering the SEIs
  `m3u` and `pls`. These playlist formats aren't understood by the GUI player directly, so the
  plugin downloads the playlist file itself and returns the first line that looks like an
  `http` stream URL as the actual playable URI.

---

## ovos-media-classifier

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-media-classifier](https://github.com/OpenVoiceOS/ovos-media-classifier)


- **Description**: ⚠️ **Experimental — work in progress, not yet deployed in OpenVoiceOS.**
  A self-describing, pluggable media-intent classifier: given a spoken request, it decides
  whether it is a media request at all and, if so, classifies it along several axes at once
  (media type, playback modality, structure, explicitness, tags, qualifiers) so OCP can route
  it to the right `MediaProvider`s and apply content policy. It is a router, not a
  resolver — it does not turn a title into a playable stream, the OCP stream-extractor
  plugins on this page do that.

---


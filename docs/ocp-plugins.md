# OCP Plugins Reference

!!! abstract "In a nutshell"
    OCP (the OpenVoiceOS Common Play system) is the part of OVOS that plays media — music, podcasts, news, radio and the like. Each plugin on this page teaches it to handle one kind of source, such as YouTube links, Bandcamp pages, RSS feeds, or local files. So if you ask to play something, the right plugin knows how to find the actual audio stream and start it. See the [Glossary](glossary.md) for unfamiliar terms.

| Plugin | Description |
|--------|-------------|
| [ovos-ocp-files-plugin](#ovos-ocp-files-plugin) | Lets OCP play local files (`file://` URIs) and reads their audio tags/metadata so the player can show a title and artist |
| [ovos-ocp-news-plugin](#ovos-ocp-news-plugin) | allows OCP to play urls for some news providers, this plugin will extract the real stream at playback time |
| [ovos-ocp-bandcamp-plugin](#ovos-ocp-bandcamp-plugin) | allows OCP to play bandcamp urls, streams will be extracted at playback time |
| [ovos-ocp-rss-plugin](#ovos-ocp-rss-plugin) | allows OCP to play rss feeds, the plugin will extract the first playable stream |
| [ovos-ocp-youtube-plugin](#ovos-ocp-youtube-plugin) | allows OCP to play youtube urls |
| [ovos-ocp-m3u-plugin](#ovos-ocp-m3u-plugin) | allows OCP to play .pls and .m3u urls as playlists |
| [ovos-media-classifier](#ovos-media-classifier) | ⚠️ experimental — pluggable media-intent classifier that routes a request to the right `MediaProvider`s |

## ovos-ocp-files-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ocp-files-plugin](https://github.com/OpenVoiceOS/ovos-ocp-files-plugin)


- **Description**: A stream extractor that lets OCP play local files (`file://` URIs, or plain
  paths on disk) and reads their embedded audio tags (title, artist, album) so the player can
  display them. It bundles a fork of the `audio-metadata` tag-reading library.

---

## ovos-ocp-news-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ocp-news-plugin](https://github.com/OpenVoiceOS/ovos-ocp-news-plugin)


- **Description**: allows OCP to play urls for some news providers, this plugin will extract the real stream at playback time

---

## ovos-ocp-bandcamp-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ocp-bandcamp-plugin](https://github.com/OpenVoiceOS/ovos-ocp-bandcamp-plugin)


- **Description**: allows OCP to play bandcamp urls, streams will be extracted at playback time

---

## ovos-ocp-rss-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ocp-rss-plugin](https://github.com/OpenVoiceOS/ovos-ocp-rss-plugin)


- **Description**: allows OCP to play rss feeds, the plugin will extract the first playable stream

---

## ovos-ocp-youtube-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ocp-youtube-plugin](https://github.com/OpenVoiceOS/ovos-ocp-youtube-plugin)


- **Description**: allows OCP to play youtube urls

---

## ovos-ocp-m3u-plugin

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-ocp-m3u-plugin](https://github.com/OpenVoiceOS/ovos-ocp-m3u-plugin)


- **Description**: allows OCP to play .pls and .m3u urls as playlists

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


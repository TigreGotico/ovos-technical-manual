# OCP Skills

!!! warning "Getting deprecated — OCP skills are being phased out"
    OCP **skills** (media-provider skills built on `OVOSCommonPlaybackSkill` /
    [`@ocp_search`](#search-results)) are how media search works **today** and still work,
    but they are **slated for deprecation**. The replacement is a dedicated **MediaProvider**
    plugin type (`opm.media.provider`) that the OCP pipeline will load **in-process** and call
    `search()` on directly — instead of broadcasting `ovos.common_play.query` over the bus to
    skills — moving media catalogs out of skills and into plugins. This is **upcoming, not
    released**: it is in flight in
    [ovos-plugin-manager#405](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/405)
    (Phase 1 of the `ovos-media` migration). Keep using OCP skills for now; this page will track
    the migration as it lands.

!!! abstract "In a nutshell"
    OCP (OVOS Common Playback) is the part of OVOS that handles playing media, like music, podcasts, or radio. An OCP skill doesn't listen for "play X" itself; instead it acts as a source of media. When someone asks to play something, OVOS asks every OCP skill "can you find this?", each one answers with whatever it can offer and how good a match it thinks it is, and OVOS plays the best result. It's like asking several record shops for an album and going with whoever has the closest match. New terms are explained in the [Glossary](glossary.md).

OCP (OVOS Common Playback) skills are built from the `OVOSCommonPlaybackSkill` class.

**What / why (beginners):** an OCP skill is a *media provider*. You do **not** write intents like "play X" — OCP owns the "play music / play a podcast / play the radio" voice interaction. Your skill only answers the question *"given this search phrase, what can you play?"*. You decorate one or more search methods with `@ocp_search`, return a list (or yield a stream) of result dicts with a confidence score, and OCP picks the best match across every installed OCP skill and handles the actual playback, queueing and GUI.

```python
from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill
```

> `MediaType` and `PlaybackType` are imported from `ovos_utils.ocp`. The OCP decorators (`ocp_search`, `ocp_featured_media`, `ocp_play`, `ocp_pause`, `ocp_resume`, `ocp_next`, `ocp_previous`) live in `ovos_workshop.decorators.ocp`.

## Search Results

Search results are returned as a list of dicts, skills can also use iterators to yield results 1 at a time as they become available

Mandatory fields are

```python
uri: str  # URL/URI of media, OCP will handle formatting and file handling
title: str
media_type: MediaType
playback: PlaybackType
match_confidence: int  # 0-100

```

Other optional metadata includes artists, album, length and images for the GUI

```python
artist: str
album: str
image: str # uri/file path
bg_image: str # uri/file path
skill_icon: str # uri/file path
length: int # seconds, -1 for live streams

```

![imagem](https://github.com/OpenVoiceOS/ovos-technical-manual/assets/33701864/08e31d2d-90e8-45ea-ab2f-dbd235892cb3)

### OCP [Skill](skill-design-guidelines.md)

General Steps to create a skill

- subclass your skill from `OVOSCommonPlaybackSkill`


- Pass `supported_media` to `super().__init__()` to indicate [the media types you want to handle](https://github.com/OpenVoiceOS/ovos-utils/blob/dev/ovos_utils/ocp.py) (`MediaType` / `PlaybackType` live in `ovos_utils.ocp`)


- `self.voc_match(phrase, "skill_name")` to handle specific requests for your skill


- `self.remove_voc(phrase, "skill_name")` to remove matched phrases from the search request


- Implement the `ocp_search` decorator, as many as you want (they run in parallel)


  - The decorated method can return a list or be an iterator of `result_dict` (track or playlist)


  - The search function can be entirely inline or call another Python library, like [pandorinha](https://github.com/OpenJarbas/pandorinha) or [plexapi](https://github.com/pkkid/python-plexapi)


- `self.extend_timeout()` to delay OCP from selecting a result, requesting more time to perform the search


- Implement a confidence score formula


  - Values are between 0 and 100


  - High confidence scores cancel other OCP skill searches


- `ocp_featured_media`, return a playlist for the OCP menu if selected from GUI (optional)


- Create a `requirements.txt` file with third-party package requirements


```python
from os.path import join, dirname

import radiosoma

from ovos_utils import classproperty
from ovos_utils.ocp import MediaType, PlaybackType
from ovos_utils.parse import fuzzy_match
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill


class SomaFMSkill(OVOSCommonPlaybackSkill):

    def __init__(self, *args, **kwargs):
        super().__init__(
            supported_media=[MediaType.MUSIC, MediaType.RADIO],
            skill_icon=join(dirname(__file__), "ui", "somafm.png"),
            *args, **kwargs)

    @ocp_featured_media()
    def featured_media(self):
        # playlist when selected from OCP skills menu
        return [{
            "match_confidence": 90,
            "media_type": MediaType.RADIO,
            "uri": ch.direct_stream,
            "playback": PlaybackType.AUDIO,
            "image": ch.image,
            "bg_image": ch.image,
            "skill_icon": self.skill_icon,
            "title": ch.title,
            "artist": "SomaFM",
            "length": 0
        } for ch in radiosoma.get_stations()]

    @ocp_search()
    def search_somafm(self, phrase, media_type):
        # check if user asked for a known radio station
        base_score = 0

        if media_type == MediaType.RADIO:
            base_score += 20
        else:
            base_score -= 30

        if self.voc_match(phrase, "radio"):
            base_score += 10
            phrase = self.remove_voc(phrase, "radio")

        if self.voc_match(phrase, "somafm"):
            base_score += 30  # explicit request
            phrase = self.remove_voc(phrase, "somafm")

        for ch in radiosoma.get_stations():
            score = round(base_score + fuzzy_match(ch.title.lower(),
                                                   phrase.lower()) * 100)
            if score < 50:
                continue
            yield {
                "match_confidence": min(100, score),
                "media_type": MediaType.RADIO,
                "uri": ch.direct_stream,
                "playback": PlaybackType.AUDIO,
                "image": ch.image,
                "bg_image": ch.image,
                "skill_icon": self.skill_icon,
                "title": ch.title,
                "artist": "SomaFM",
                "length": 0
            }

```


## OCP Keywords

OCP skills often need to match hundreds or thousands of strings against the query string, `self.voc_match` can quickly become impractical to use in this scenario

To help with this the OCP skill class provides efficient keyword matching

```python
def register_ocp_keyword(self, media_type: MediaType, label: str,
                         samples: List, langs: List[str] = None):
    """ register strings as native OCP keywords (eg, movie_name, artist_name ...)
    for a given media_type. ocp keywords can be efficiently matched with the
    self.ocp_voc_match helper method that uses the Aho–Corasick algorithm
    """

def load_ocp_keyword_from_csv(self, csv_path: str, lang: str = None):
    """ load entities from a .csv file for usage with self.ocp_voc_match
    see the ocp_entities.csv datatsets for example files built from wikidata SPARQL queries

    examples contents of csv file

        label,entity
        film_genre,swashbuckler film
        film_genre,neo-noir
        film_genre,actual play film
        film_genre,alternate history film
        film_genre,spy film
        ...
    """

```

### OCP Voc match

uses [Aho–Corasick algorithm](https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm) to match OCP keywords

this efficiently matches many keywords against an utterance

OCP keywords are registered via `self.register_ocp_keyword`

wordlists can also be loaded from a .csv file, see [the OCP dataset](https://github.com/OpenVoiceOS/ovos-classifiers/tree/dev/scripts/training/ocp/datasets) for a list of keywords gathered from wikidata with SPARQL queries


### OCP Database Skill

```python
import json

from ovos_utils.fakebus import FakeBus
from ovos_utils.ocp import MediaType
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill


class HorrorBabbleSkill(OVOSCommonPlaybackSkill):

    def initialize(self):
        # get file from
        # https://github.com/JarbasSkills/skill-horrorbabble/blob/dev/bootstrap.json
        with open("hb.json") as f:
            db = json.load(f)
        book_names = []
        book_authors = []
        for url, data in db.items():
            t = data["title"].split("/")[0].strip()
            if " by " in t:
                title, author = t.split(" by ")
                title = title.replace('"', "").strip()
                author = author.split("(")[0].strip()
                book_names.append(title)
                book_authors.append(author)
                if " " in author:
                    book_authors += author.split(" ")
            elif t.startswith('"') and t.endswith('"'):
                book_names.append(t[1:-1])
            else:
                book_names.append(t)
        self.register_ocp_keyword(MediaType.AUDIOBOOK,
                                  "book_author",
                                  list(set(book_authors)))
        self.register_ocp_keyword(MediaType.AUDIOBOOK,
                                  "book_name",
                                  list(set(book_names)))
        self.register_ocp_keyword(MediaType.AUDIOBOOK,
                                  "audiobook_streaming_provider",
                                  ["HorrorBabble", "Horror Babble"])

```

```python
s = HorrorBabbleSkill(bus=FakeBus(), skill_id="demo.fake")

entities = s.ocp_voc_match("read The Call of Cthulhu by Lovecraft")

# {'book_author': 'Lovecraft', 'book_name': 'The Call of Cthulhu'}
print(entities)

entities = s.ocp_voc_match("play HorrorBabble")

# {'audiobook_streaming_provider': 'HorrorBabble'}
print(entities)

```


## Playlist Results

Results can also be playlists, not only single tracks, for instance full albums or a full season for a series

When a playlist is selected from Search Results, it will replace the Now Playing list

Playlist results look exactly the same as regular results, but instead of a `uri` they provide a `playlist`

```python
playlist: list  # list of dicts, each dict is a regular search result
title: str
media_type: MediaType
playback: PlaybackType
match_confidence: int  # 0-100

```

> NOTE: nested playlists are a work in progress and not guaranteed to be functional, ie, the `"playlist"` dict key should not include other playlists

### Playlist Skill

```python
class MyJamsSkill(OVOSCommonPlaybackSkill):

    def __init__(self, *args, **kwargs):
        super().__init__(
            supported_media=[MediaType.MUSIC],
            skill_icon=join(dirname(__file__), "ui", "myjams.png"),
            *args, **kwargs)

    @ocp_search()
    def search_my_jams(self, phrase, media_type):
        if self.voc_match(...):
            results = [...]  # regular result dicts, as in examples above
            score = 70  # Match confidence

            yield {
                "match_confidence": min(100, score),
                "media_type": MediaType.MUSIC,
                "playlist": results, # replaces "uri"
                "playback": PlaybackType.AUDIO,
                "image": self.image,
                "bg_image": self.image,
                "skill_icon": self.skill_icon,
                "title": "MyJams",
                "length": sum([r["length"] for r in results])  # total playlist duration
            }

```

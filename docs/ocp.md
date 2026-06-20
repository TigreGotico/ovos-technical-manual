# OCP / Common Play Testing

`ovoscope.ocp` provides `OCPTest` and `assert_ocp_query_response` for testing
OCP (OpenVoiceOS Common Play) skills that handle media queries.  For testing
the OCP player state machine, see `OCPPlayerHarness` in `ovoscope.media`.

## OCP Message Flow

```
recognizer_loop:utterance
  → ovos.common_play.query              (broadcast to all OCP skills)
  → ovos.common_play.query.response     (skill replies with MediaEntry list)
  → ovos.common_play.start              (selected track)

```

## Quick Start

`OCPTest` is the one-liner path: give it skill IDs and an utterance, stub any HTTP
the skill makes, and state what media you expect back. It spins up a `MiniCroft`,
fires `recognizer_loop:utterance`, waits for the asynchronous OCP responses, and
asserts on them — no bus wiring by hand.

## `OCPTest` — Declarative Style

`OCPTest` — `ocp.py:OCPTest`

```python
from ovoscope.ocp import OCPTest

result = OCPTest(
    skill_ids=["ovos-skill-youtube.openvoiceos"],
    utterance="play lofi hip hop",
    mock_responses={
        "youtube.com": {"items": [{"title": "Lofi Radio", "url": "..."}]},
    },
    expected_media=[{"title": "Lofi Radio"}],
    lang="en-US",
    timeout=20.0,
).execute()

```

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `skill_ids` | `List[str]` | **required** | OCP skill IDs to load. |
| `utterance` | `str` | **required** | User utterance. |
| `mock_responses` | `Dict[str, Any]` | `{}` | URL-substring → JSON response body. |
| `expected_media` | `List[Dict]` | `[]` | Partial dicts; each must match one `media_list` item. |
| `expected_stream_url` | `Optional[str]` | `None` | Substring expected in `ovos.common_play.start` URI. |
| `lang` | `str` | `"en-US"` | Language tag. |
| `timeout` | `float` | `20.0` | Max wait in seconds. |
| `patch_targets` | `List[str]` | `[]` | Additional `requests`-like module paths to patch (dotted Python path to the callable to replace). |

### `execute()`

Returns `List[Message]` — all bus messages captured during the interaction
(same format as `CaptureSession.responses`). Before returning, `execute()` calls
`assert_ocp_query_response(captured, expected_media=..., expected_stream_url=...)`,
so the `expected_media` and `expected_stream_url` fields are enforced automatically.
The other checks (`min_results`, `media_type`, `stream_url_contains`) are **not**
applied by `execute()`; run `assert_ocp_query_response` yourself on the returned list
when you need them:

```python
from ovoscope.ocp import OCPTest, assert_ocp_query_response

messages = OCPTest(
    skill_ids=["ovos-skill-somafm.openvoiceos"],
    utterance="play groove salad",
).execute()

assert_ocp_query_response(messages, min_results=1, media_type="audio")
```

## HTTP Mocking

When `mock_responses` is non-empty, HTTP calls are intercepted via
`unittest.mock.patch` on `requests.Session.get` **and** `requests.get` by default
(both are patched automatically — `requests.Session.get` is the primary target).

The `mock_responses` dict maps **URL substrings** to JSON response bodies.
The patched `get()` returns a `MagicMock` Response whose `.json()` checks each key
against the request URL and returns the first body whose key is a substring of the
URL (falling back to `{}`). The mock also sets `status_code = 200` and `ok = True`.

For skills using non-standard HTTP clients (e.g. `aiohttp`, `httpx`), pass
additional dotted Python module paths in `patch_targets`. The path must point
to the exact callable that the skill imports and calls:

```python

# Default: patches requests.Session.get and requests.get automatically.

# Use patch_targets for any other HTTP client the skill uses.

OCPTest(
    skill_ids=["ovos-skill-example-aiohttp.openvoiceos"],
    utterance="play jazz",
    mock_responses={
        "api.example.com": {"results": [{"title": "Jazz Radio", "url": "http://stream.example.com/jazz"}]},
    },
    # Dotted path: <module-where-the-symbol-is-used>.<callable>
    patch_targets=["ovos_skill_example.api_client.aiohttp.ClientSession.get"],
).execute()

```

The format is the same as `unittest.mock.patch` target strings — the dotted
path to where the symbol is **used** (not where it is defined). See
[unittest.mock patch docs](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.patch)
for details.

## `assert_ocp_query_response`

The standalone assertion. All arguments after `messages` are **keyword-only**:

```python
from ovoscope.ocp import assert_ocp_query_response

assert_ocp_query_response(
    messages,
    min_results=1,
    media_type="audio",
    expected_media=[{"title": "My Song"}],
    stream_url_contains="cdn.example.com",
)

```

```python
def assert_ocp_query_response(
    messages,
    *,
    min_results=0,
    media_type=None,
    expected_media=None,
    stream_url_contains=None,
    expected_stream_url=None,
) -> None: ...
```

| Argument | Default | Description |
|----------|---------|-------------|
| `messages` | **required** | Captured message list. |
| `min_results` | `0` | Minimum number of items across all `ovos.common_play.query.response` `media_list` (falls back to `results`). `0` skips the check. |
| `media_type` | `None` | If set, every result item must have this `media_type`. |
| `expected_media` | `None` | List of partial dicts; each must subset-match at least one result item (only the keys you provide are compared). |
| `stream_url_contains` | `None` | Substring required in the `ovos.common_play.start` `uri` (falls back to `url`). |
| `expected_stream_url` | `None` | Alias for `stream_url_contains`; pass either. |

The `min_results`/`expected_media`/`media_type` block only runs when `min_results > 0`
or `expected_media` is given, so calling with no media arguments is a no-op for those
checks.

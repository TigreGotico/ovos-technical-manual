
# ovos-color-parser

OpenVoiceOS's multilingual color parsing and color-space conversion library. It turns natural-language color descriptions ("bright, slightly warm muted blue") into concrete RGB/HLS/HSV values, and provides color-space utilities needed for smart-light control and similar voice-driven color applications.

## Why it exists

Voice assistants frequently need to interpret color commands: "change the lamp to moss green", "make it darker", "a bit more saturated". Standard CSS/X11 color name lookups only cover exact matches. `ovos-color-parser` layers on top of a multilingual color-name database (nearly 6 000 English name-to-hex mappings) and a language-keyed adjective/modifier system so that fuzzy descriptions and modifier words ("bright", "warm", "muted") are resolved to a real sRGB value.

A secondary use-case is scientific: the library supports the full electromagnetic spectrum (including UV, IR, microwaves and radio waves) mapped through spectral color palettes, so physicists who say "set the lamp to 520 nanometres" are handled without special-casing in skills.

---

## Package layout

| Module | Responsibility |
|--------|---------------|
| `ovos_color_parser/__init__.py` | Public re-exports of every model class and every matching function |
| `ovos_color_parser/models.py` | Dataclasses for all color spaces plus pre-built spectral palettes and language vocabulary objects |
| `ovos_color_parser/matching.py` | Aho-Corasick automaton-based color name lookup, adjective adjustment, `ColorMatcher` class, utility functions |
| `ovos_color_parser/res/<lang>/` | Per-language JSON word-lists (`*.json`) and object-color mappings (`object_colors.json`) and adjective descriptors (`color_descriptors.json`) |

Dependencies: `ahocorasick`, `colorspacious` (for CIEDE2000 color distance), `ovos-utils` (fuzzy matching via `MatchStrategy`).

---

## Architecture

### Color space model (`models.py`)

All color representations are Python `@dataclass` objects. Internal operations are performed in HLS space; conversions between spaces are implemented as properties.

```
sRGBAColor  ──as_hls──►  HLSColor  ──as_hsv──►  HSVColor
     │                      │                       │
     │◄──────as_rgb─────────│◄──────as_rgb──────────│
     │                                               │
     └──as_spectral_color──► SpectralColor ◄─────────┘

```

The `HueRange` dataclass bridges the hue angle (0–360°) to the physical wavelength domain using `ISCCNBSSpectralColorTerms` as the default mapping table.

### Matching pipeline (`matching.py`)

`color_from_description()` runs four steps:

1. **Exact / Aho-Corasick lookup** — loads a language-specific Aho-Corasick automaton from the per-language JSON word lists. The automaton is built once per language and cached thread-safely in `ColorMatcher._color_automatons`.


2. **Fuzzy fallback** — when `fuzzy=True`, iterates all color names with `fuzzy_match()` using `TOKEN_SET_RATIO` pre-screening and the requested `MatchStrategy`.


3. **Object-color lookup** — checks `object_colors.json` for object-to-color mappings (e.g. "sky" → #87CEEB).


4. **Adjective adjustment** — reads `color_descriptors.json` for the language and applies saturation, brightness, opacity, and temperature modifiers to the averaged candidate color.

Weighted circular-mean hue averaging (`average_colors()`) prevents wrap-around errors for hues near 0°/360°.

---

## API reference

### Color model classes (`ovos_color_parser/models.py`)

| Class | Key fields | Notable properties / methods |
|-------|-----------|------------------------------|
| `sRGBAColor` | `r`, `g`, `b` (0–255 int), `a` (0–255, default 255), `name`, `description` | `.as_hls`, `.as_hsv`, `.as_spectral_color`, `.hex_str`, `from_hex_str(hex_str)` |
| `HLSColor` | `h` (0–360 int), `l` (0–1 float), `s` (0–1 float), `name`, `description` | `.as_rgb`, `.as_hsv`, `.as_spectral_color`, `.hex_str`, `from_hex_str(hex_str)` |
| `HSVColor` | `h` (0–360 int), `s` (0–1 float), `v` (0–1 float), `name`, `description` | `.as_rgb`, `.as_hls`, `.as_spectral_color`, `.hex_str`, `from_hex_str(hex_str)` |
| `SpectralColor` | `wavelen_nm_min`, `wavelen_nm_max`, `hex_approximation`, `hue_approximation`, `name` | `.wavelen` (midpoint), `.as_rgb`, `.as_hls`, `.as_hsv`, `from_rgb()`, `from_hsv()`, `from_hls()`, `from_hex_str()` |
| `HueRange` | `min_hue_approximation`, `max_hue_approximation`, `name`, `hex_approximation` | `.hue` (midpoint), `.as_spectral_color` |
| `ColorTerm` | `name`, `hue: HueRange`, `hex_approximation` | `.as_rgb` |
| `LanguageColorVocabulary` | `terms: List[ColorTerm]` | — |
| `sRGBAColorPalette` | `colors: List[sRGBAColor]` | `.as_hsv`, `.as_hls` |
| `HSVColorPalette` | `colors: List[HSVColor]` | `.as_rgb`, `.as_hls` |
| `HLSColorPalette` | `colors: List[HLSColor]` | `.as_rgb`, `.as_hsv` |
| `SpectralColorPalette` | `colors: List[SpectralColor]` | `.as_rgb`, `.as_hsv`, `.as_hls` |

Type aliases exported from `models.py`:

- `Color = Union[sRGBAColor, HSVColor, HLSColor, SpectralColor, ColorTerm]`


- `ColorPalette = Union[sRGBAColorPalette, HSVColorPalette, HLSColorPalette, SpectralColorPalette]`

### Pre-built palettes and vocabularies (`ovos_color_parser/models.py`)

| Name | Type | Description |
|------|------|-------------|
| `NewtonSpectralColorTerms` | `SpectralColorPalette` | Newton's 7-color spectrum (380–690 nm) |
| `ISCCNBSSpectralColorTerms` | `SpectralColorPalette` | ISCC-NBS 8-term spectrum (380–730 nm); default for hue↔wavelength conversion |
| `MalacaraSpectralColorTerms` | `SpectralColorPalette` | Malacara 7-term spectrum |
| `CRCHandbookSpectralColorTerms` | `SpectralColorPalette` | CRC Handbook 6-term spectrum |
| `IRSpectralColors` | `SpectralColorPalette` | Infrared / Microwave / Radio spectrum |
| `UVSpectralColors` | `SpectralColorPalette` | UV / X-Ray / Gamma ray spectrum |
| `ElectroMagneticSpectrum` | `SpectralColorPalette` | Full spectrum: IR + ISCC-NBS visible + UV |
| `EnglishColorTerms` | `LanguageColorVocabulary` | 10-entry basic English color → hue range map |
| `OtjihereroColorTerms` | `LanguageColorVocabulary` | Otjiherero language color vocabulary (11 terms) |

### Matching and utility functions (`ovos_color_parser/matching.py`)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `color_from_description` | `(description: str, lang: str = "en", strategy: MatchStrategy = DAMERAU_LEVENSHTEIN_SIMILARITY, cast_to_palette: bool = False, fuzzy: bool = True) -> Optional[sRGBAColor]` | `sRGBAColor` or `None` | Main entry point. Resolves a natural-language description to an RGB color. Returns `None` if no color candidates are found. When `cast_to_palette=True`, snaps the result to the nearest matched candidate instead of returning an averaged value. |
| `color_distance` | `(color_a: Color, color_b: Color) -> float` | `float` | CIEDE2000 perceptual distance between two colors in sRGB-255 space. Lower is more similar. Uses `colorspacious.deltaE`. |
| `closest_color` | `(color: Color, color_opts: List[Color]) -> Color` | `Color` | Returns the element of `color_opts` with the smallest `color_distance` to `color`. |
| `average_colors` | `(colors: List[Color], weights: Optional[List[float]] = None) -> HLSColor` | `HLSColor` | Weighted average of a list of colors. Hue is averaged using circular mean (atan2) to avoid wrap-around errors. Returns an `HLSColor`. |
| `convert_K_to_RGB` | `(colour_temperature: int) -> sRGBAColor` | `sRGBAColor` | Converts a color temperature in Kelvin (1 000–40 000 K) to an sRGB color. Algorithm by Tanner Helland. |
| `get_contrasting_black_or_white` | `(hex_code: str) -> sRGBAColor` | `sRGBAColor` | Returns black or white, whichever provides the best contrast against the input hex color, using the YIQ luma formula. |
| `palette_from_description` | `(description: str, lang: str = "en", strategy: MatchStrategy = ...) -> sRGBAColorPalette` | `sRGBAColorPalette` | Returns all candidate colors matched from a description (fuzzy, no adjective adjustment). Useful for UI palette suggestions. |
| `lookup_name` | `(color: Color, lang: str = "en") -> str` | `str` | Reverse-lookup: given a color object, find its name in the language word list. Raises `ValueError` if the hex code has no named entry. |
| `rgb_to_cmyk` | `(r, g, b, cmyk_scale=100, rgb_scale=255) -> Tuple[float, float, float, float]` | `(c, m, y, k)` | Convert sRGB to CMYK. |
| `cmyk_to_rgb` | `(c, m, y, k, cmyk_scale=100, rgb_scale=255) -> Tuple[int, int, int]` | `(r, g, b)` | Convert CMYK to sRGB. |
| `is_hex_code_valid` | `(hex_code: str) -> bool` | `bool` | Validate a hex color string (must be 6 hex digits, with or without leading `#`). |

### `ColorMatcher` class (`ovos_color_parser/matching.py:58`)

Thread-safe class that owns the Aho-Corasick automata. Automata are class-level dicts (`_color_automatons`, `_object_automatons`) keyed by language code and built lazily.

| Method | Signature | Description |
|--------|-----------|-------------|
| `load_color_automaton` | `(cls, lang: str) -> ahocorasick.Automaton` | Build (or return cached) Aho-Corasick automaton from all non-descriptor JSON word lists for `lang`. |
| `load_object_automaton` | `(cls, lang: str) -> ahocorasick.Automaton` | Build (or return cached) automaton from `object_colors.json` for `lang`. |
| `match_color_automaton` | `(cls, description: str, lang: str, strategy: MatchStrategy, fuzzy: bool) -> zip(candidates, weights)` | Match description against color name database. Returns zip of `(HLSColor, float)` tuples. |
| `match_object_automaton` | `(cls, description: str, lang: str, strategy: MatchStrategy) -> zip(candidates, weights)` | Match description against object-color database. |
| `match_automaton` | `(automaton, description) -> List[str]` | Low-level: iterate the automaton over a normalized description and return hex strings. |

---

## Usage examples

### Resolve a description to RGB

```python
from ovos_color_parser import color_from_description

color = color_from_description("bright vibrant green")
print(color.hex_str)        # e.g. "#4CBF31"
print(color.r, color.g, color.b)

```

### Average vs. snapped result

```python
from ovos_color_parser import color_from_description

# Averaged across all "red" entries in the database
averaged = color_from_description("Red")
print(averaged.hex_str)   # "#D21B1B"

# Snapped to the nearest exact palette entry
snapped = color_from_description("Red", cast_to_palette=True)
print(snapped.hex_str)    # "#CE202B"  (Fire engine red)

```

### Perceptual distance

```python
from ovos_color_parser import color_distance, color_from_description

a = color_from_description("green")
b = color_from_description("purple")
print(color_distance(a, b))   # ~64.97

```

### Closest color from a custom palette

```python
from ovos_color_parser import sRGBAColor, sRGBAColorPalette, closest_color

palette = sRGBAColorPalette(colors=[
    sRGBAColor(r=0,   g=128, b=128, name="Teal"),
    sRGBAColor(r=0,   g=255, b=255, name="Cyan"),
    sRGBAColor(r=64,  g=224, b=208, name="Turquoise"),
])

result = closest_color(sRGBAColor(r=0, g=200, b=200), palette.colors)
print(result.name)   # "Cyan"

```

### Color temperature to RGB

```python
from ovos_color_parser import convert_K_to_RGB

warm_white = convert_K_to_RGB(2700)
print(warm_white.hex_str)   # "#FF9329" (approximate warm incandescent)

daylight = convert_K_to_RGB(6500)
print(daylight.hex_str)     # "#FFE8D5" (approximate daylight)

```

### Contrasting text color

```python
from ovos_color_parser import get_contrasting_black_or_white

# For a dark background, returns white for readable text
contrast = get_contrasting_black_or_white("#1A1A2E")
print(contrast.hex_str)   # "#FFFFFF"

```

### Color space conversions

```python
from ovos_color_parser import sRGBAColor

rgb = sRGBAColor(r=255, g=165, b=0, name="Orange")
hls = rgb.as_hls
hsv = rgb.as_hsv
spectral = rgb.as_spectral_color

print(hls.h, hls.l, hls.s)
print(hsv.h, hsv.s, hsv.v)
print(spectral.wavelen)        # approximate wavelength in nm

```

---

## Language support

Language-keyed resources live in `ovos_color_parser/res/<lang>/`. The language code is derived from the BCP-47 code by taking the primary subtag (e.g. `"en-US"` → `"en"`).

Each language directory may contain:

| File | Purpose |
|------|---------|
| `*.json` (except the two below) | Map of `"#RRGGBB"` → `"color name"` — one or more files per language |
| `object_colors.json` | Map of `"#RRGGBB"` → `"object name"` (e.g. sky, grass, ocean) |
| `color_descriptors.json` | Adjective lists keyed by `very_high_saturation`, `high_saturation`, `low_saturation`, `very_low_saturation`, `very_high_brightness`, `high_brightness`, `low_brightness`, `very_low_brightness`, `very_high_opacity`, `high_opacity`, `low_opacity`, `very_low_opacity`, `very_high_temperature`, `high_temperature`, `low_temperature`, `very_low_temperature` |

English (`en`) ships approximately 6 000 hex-to-name entries aggregated from X11, web colors, Crayola, XKCD, and other named color standards.

---

## Configuration

No runtime configuration object is used. Language selection is passed explicitly to every function via the `lang` parameter. `MatchStrategy` (imported from `ovos_utils.parse`) controls the fuzzy matching algorithm:

| Strategy | Description |
|----------|-------------|
| `MatchStrategy.DAMERAU_LEVENSHTEIN_SIMILARITY` | Default. Edit-distance similarity. |
| `MatchStrategy.TOKEN_SET_RATIO` | Pre-screening pass for fuzzy matching. |

---

## Cross-references

| Package | How it uses ovos-color-parser |
|---------|-------------------------------|
| `ovos-core` | Indirectly via skills that handle lighting commands |
| `ovos-workshop` | [Skill](skill-design-guidelines.md) base classes delegate color parsing to this library |
| `ovos-number-parser` | Peer library in the OVOS NLP stack; not a dependency of this package |
| `ovos-date-parser` | Peer library in the OVOS NLP stack; not a dependency of this package |
| `ovos-lang-parser` | Peer library in the OVOS NLP stack; not a dependency of this package |

See also:

- [`ovos-number-parser/docs/index.md`](index.md)


- [`ovos-date-parser/docs/index.md`](index.md)


- [`ovos-lang-parser/docs/index.md`](index.md)


- `QUICK_FACTS.md`


- `FAQ.md`


- `AUDIT.md`

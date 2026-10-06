# Lyric / caption map

When GPT authors the lyrics, preserve structure **at authoring time** instead of
reconstructing it later from audio.

The lyric map is a lightweight source-of-truth that sits between song writing and
video direction.

## Why this exists

If the assistant already wrote:

- section labels;
- line order;
- repeated choruses;
- pauses;
- instrumental breaks;
- spoken lines;
- emphasis and motif phrases;

then that information should survive into the music-video pipeline.

Later audio alignment should refine timing, not rediscover structure.

## Three timing states

A lyric map can move through three increasingly precise states:

1. **authored** — ordered sections/lines, no real audio timing yet;
2. **estimated** — rough phrase timings derived from expected section lengths or
   a first-pass song map;
3. **aligned** — phrase/word timings corrected against the rendered audio.

Do not discard earlier semantic structure when alignment occurs.

## Recommended shape

Each entry should keep both **meaning** and **time**:

- section id;
- line id;
- text;
- lyric role such as verse, pre-chorus, chorus, bridge, spoken, outro;
- repeated-from id when a chorus repeats;
- motif tags such as `home`, `1:11`, `sugar-bear`;
- vocal mode hint such as intimate, sung, falsetto, spoken, hold-note;
- start/end timing when known;
- timing confidence/state;
- optional word-level timing once aligned.

This is richer than a plain subtitle file, but can export to LRC/SRT/ASS when
needed.

## Caption-map principle

Treat the structured lyric map as the master. Caption formats are projections.

For example:

- LRC → simple timed lyric display;
- SRT/VTT → conventional captions;
- ASS → styled karaoke/caption work;
- Manim overlay manifest → kinetic typography;
- Manim world manifest → spatial lyric landmarks;
- actor-state planner → choose `mouth=singing_open` or `hold_note`;
- scene planner → map sections to archetypes.

## Authoring-time advantage

When GPT writes Suno lyrics, it already knows the exact text and section
boundaries. Immediately serialize that information before the text is handed to
Suno.

Example lifecycle:

```
lyrics authored
  ↓
lyric-map.authored.json
  ↓
Suno render
  ↓
rough song-section map
  ↓
lyric-map.estimated.json
  ↓
forced alignment / manual correction
  ↓
lyric-map.aligned.json
  ↓
captions + actor state + scene archetypes + Manim world
```

## Spatial lyric use

A spatial Manim sequence should consume semantic events from the lyric map rather
than raw text.

Examples:

- repeated `home` lines can resolve to the same persistent landmark;
- `1:11` can recur at one fixed semantic location;
- chorus phrases can be promoted to large horizon-scale words;
- verses can become smaller roadside or tunnel landmarks;
- instrumental sections explicitly contain no lyric event, allowing procedural
  graphics or sprite landmarks to take over.

This makes it possible for sprites and stills to be **walked down the lyrics**:
the camera follows a deterministic path, lyric events occupy stations along that
path, and persistent actor/still objects can be attached to selected stations.

## Low-cognitive-load rule

Future GPT should decide semantic roles, not subtitle bookkeeping.

Prefer decisions like:

- this is the chorus;
- this line is a recurring motif;
- this phrase should become a spatial landmark;
- this line is sung softly;
- this section has no lyric text.

Then let deterministic tooling produce caption files, Manim events, and timing
manifests.

## Alignment hierarchy

Prefer:

1. exact user/provided timings;
2. timings preserved from the generation system, if available;
3. alignment against the known authored lyrics;
4. transcription only when the original lyrics are unavailable.

If GPT authored the lyrics, transcription should be the last resort, not the
first step.

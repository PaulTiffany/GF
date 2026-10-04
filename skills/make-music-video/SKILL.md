---
name: make-music-video
description: Make and deliver a playable music video from a supplied or generated song using reusable templates, style packs, StickerBook-style asset packs, scene archetypes, local motion/compositing, stock or existing clips, typography/procedural animation, and optional generative video. Use for Claude Pop, narrative, performance, lyric, ambient/sonification, or hybrid work. Success is a playable artifact, not a storyboard or prompt pack.
---

# Make a music video

The target is **a playable music video**. Do not confuse asset generation, prompts,
a storyboard, or a valid MP4 container with completion.

The core portability lesson is that a music video does **not** require a paid
text-to-video model. A supplied song plus image generation and a local media
runtime can already produce an authored moving video through persistent sprite
assets, scene archetypes, reframing, compositing, typography, procedural
animation, cuts, and encoding. Generated video is an optional shot source, not
the definition of Conjure mode.

## Capability gate

Choose the strongest route the current host actually supports.

### Conjure from primitives

Use when the host can access a finished song (supplied or generated), create or
obtain enough visual assets, and render moving media locally. Useful primitives
include:

- still-image generation or existing photographs/artwork,
- StickerBook-style sprite/pose atlases and reusable asset packs,
- local FFmpeg or equivalent compositing,
- generated typography/Manim/procedural fields when available,
- rights-compatible stock clips or user-owned footage,
- optional generated motion clips.

A successful run starts from a creative brief and ends with a playable video,
plus a poster/thumbnail when the local renderer is used.

### Provider-assisted motion

If connected tools can generate video, use them selectively where continuous
action or difficult camera motion adds real value. Do not make a paid video
provider a prerequisite when cheaper primitives can express the idea.

### Assembly mode

Use when song and visual assets already exist. The bundled helper validates a
bounded project manifest, adds deterministic still motion when requested,
assembles accepted image/video shots, verifies the MP4, and extracts a poster.

### Not equipped

Name the actual missing capability. A supplied song + image generation + local
FFmpeg is enough for many videos; lack of text-to-video alone is not a blocker.
Do not silently downgrade a request for a video into a storyboard or prompt pack.

## Observable success

Keep these claims separate:

1. creative direction exists;
2. song/audio exists;
3. visual assets exist;
4. moving visual composition exists;
5. complete playable video exists;
6. poster/thumbnail exists when applicable;
7. the current host actually exposes an inline player, if inline playback is
   claimed;
8. target platform accepts/plays it, if publication was requested.

For “make me a music video,” success is normally #5. “Plays inline here” is a
separate delivery claim and must be observed rather than assumed.

## Start with the visual grammar

Do not invent every shot independently. Read `references/visual-grammar.md`,
`references/asset-packs.md`, `templates/catalog.json`, and
`archetypes/catalog.json`, then choose:

1. **one video template** for song-level attention and section roles;
2. **one style pack** for world/continuity;
3. **one or more reusable asset packs** for persistent characters/props/effects;
4. **one to three motifs** tied to lyrics or musical events;
5. **two to four scene archetypes** for reusable situations;
6. **a small module palette** for the final renderable shots.

Bundled starting templates are:

- `templates/ballad-narrative.json`
- `templates/pop-hook.json`
- `templates/ambient-sonification.json`

Bundled archetypes include:

- `archetypes/driving-loop.json`
- `archetypes/slow-dance-loop.json`
- `archetypes/window-rain.json`
- `archetypes/lyric-cloud.json`

`styles/noir-romance.json` is an example style pack, not a default aesthetic.
Create another small style pack when the project needs a different world.

This separation is how the skill gets variety without high cognitive load.

## Use asset packs, not one-shot images

When continuity matters, a visual-generation call should often produce a reusable
atlas rather than one finished frame.

One generated output can intentionally contain:

- several named character poses,
- expression variants,
- recurring props,
- foreground/effect mattes,
- transparent-friendly cutouts,
- background plates.

Treat these as persistent objects. Give poses semantic names/tags so later
reasoning can ask for `driving + romantic` or `bridge + intimate` rather than
remembering frame coordinates. See `references/asset-packs.md` and
`examples/asset-pack.json`.

This is especially valuable when stronger generation models are throttled:
spend inference once on a coherent pack, then reuse it mechanically.

## Instantiate scene archetypes

An archetype is a reusable mini-directing recipe, not a finished shot.

For example, `driving-loop` combines a persistent vehicle/character sprite pack
with a repeatable moving road plate. Background motion, foreground blur, tiny
vehicle oscillation, passing light, rain, crop changes, and pose swaps can create
many distinct driving shots from the same generated assets.

Likewise, `slow-dance-loop`, `window-rain`, and `lyric-cloud` capture common
visual situations whose variation can be parameterized instead of re-invented.

Prefer instantiating and varying archetypes before asking inference to regenerate
an entire scene.

## Map the song

Prefer real timestamps from audio analysis or supplied section boundaries. Keep
lyrics, sections, tempo feel, and edit tempo distinct: a 70-BPM-feeling ballad
may be detected at double time, and mechanical beat cutting can ruin the song.

For each section decide:

- section role from the chosen template;
- average shot length/density;
- recurring versus new motif;
- visual energy change;
- lyric or musical events worth synchronization;
- whether the edit should deliberately hold across a downbeat.

## Build visual interest cheaply first

Use the visual-interest ladder before spending expensive motion inference:

1. strong still composition or persistent sprite assets;
2. deterministic reframe or a scene archetype;
3. typography or lyric fields;
4. procedural animation: particles, rain, grain, waveform, vector fields,
   Lissajous forms, data/sonification mappings;
5. masks, parallax, compositing, overlays, reflections, split-screen;
6. rights-compatible stock or user footage for connective texture;
7. generated motion footage where continuous action matters.

A still can be a source layer rather than the entire frame. A hero image or
sprite over moving rain, animated light, lyric geometry, a scrolling background,
or a procedural field is a moving composition even though the character art is
static.

## Generate assets with continuity

Establish one anchor image/world before generating a large batch. Reuse the
anchor as a reference for recurring characters, palette, wardrobe, props, and
locations. Prefer one high-value atlas/pack over many isolated generations when
the same subject will recur.

Generate in small batches and stop spending inference when the style is already
coherent enough for the edit.

If generation is throttled or a stronger model is unavailable, degrade the asset
route rather than abandoning the production: fewer hero images, reusable packs,
stock texture, procedural animation, archetypes, and deterministic motion are
valid tools.

## Deterministic local renderer

Schema 1 remains supported for old hard-cut manifests. Prefer schema 2 for new
projects.

```json
{
  "schema": 2,
  "title": "My music video",
  "audio": "media/song.wav",
  "width": 1920,
  "height": 1080,
  "fps": 30,
  "poster_time": 1.0,
  "shots": [
    {"asset": "media/hero.png", "kind": "image", "duration": 5.0,
     "motion": "push_in", "transition": "fade_black"},
    {"asset": "media/road.png", "kind": "image", "duration": 4.0,
     "motion": "pan_right"},
    {"asset": "media/stock.mp4", "kind": "video", "duration": 3.0,
     "source_start": 2.0}
  ]
}
```

Image `motion` may be `static`, `push_in`, `pull_out`, `pan_left`, or
`pan_right`. `transition` may be `cut` or `fade_black`. Video shots preserve
native motion and may use `source_start`.

Inspect the plan:

```bash
python scripts/music_video.py plan /project/music-video.json \
  --output /project/out/music-video.mp4
```

Render, verify, and extract the poster:

```bash
python scripts/music_video.py render /project/music-video.json \
  --output /project/out/music-video.mp4
```

The poster is written beside the MP4 as `music-video.poster.jpg`. Render mode
checks FFmpeg/FFprobe, song duration, trimmed video-source duration, overwrite
intent, output streams, dimensions, final duration, and poster creation; it
returns byte lengths and SHA-256 values for both outputs.

## Typography, Manim, archetypes, procedural fields, and stock

These are upstream shot generators. Keep the final renderer provider-neutral:
render a sprite/archetype composition, Manim lyric cloud, procedural field, or
authorized stock treatment to a normal clip, then list that clip as an ordinary
`video` shot in the project manifest.

This keeps the compositor simple while letting future hosts add new visual tools
without changing the project contract.

## Review

Watch the artifact, not just the logs. Check the first 10 seconds, every section
transition, strongest hook, instrumental/solo treatment, text legibility,
continuity, final image, and audio integrity. Sampled frame inspection is useful
but does not replace watching the full video when the host can do so.

If the result feels like a slideshow, do not solve that only by generating more
stills. Change the visual grammar: instantiate archetypes, use persistent sprite
packs, add fields/text/overlays/stock motion/masking, or move into abstraction.

## Present or publish

For chat delivery, attach/present the MP4 through the host-native media surface
when available and surface the poster/thumbnail as well. A sandbox/download link
is useful fallback delivery but is not evidence that the host rendered an inline
player. If inline playback fails, record that as a delivery-layer failure rather
than a render failure.

If publication was requested, use only accounts/platforms already authorized in
the task and distinguish local render success from platform playback success.

## Bounds and stopping conditions

The local helper enforces at most 300 shots, 20 minutes, 120 seconds per shot,
60 fps, 4K-class pixel count, 2 GiB per input, 10 GiB total input, and project-
directory confinement. Existing output/poster files are not replaced unless
`--force` is explicit.

Stop when the requested playable artifact is produced and the available review
is complete, when a genuinely required capability is absent, or when another
attempt would repeat a failed route without a concrete change.

See `references/evidence.md`, `references/visual-grammar.md`,
`references/asset-packs.md`, and `references/field-notes.md`. Retain the
bundled MIT `LICENSE` when copying the skill independently.

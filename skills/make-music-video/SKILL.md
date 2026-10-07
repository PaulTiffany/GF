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

## Operating model: select → object → refine

Optimize for the next assistant's cognitive load.

Do **not** begin by inventing shots, coordinates, prompts, or animation code. Use
bounded selectors to materialize typed objects first, then descend into one
object only when refinement is useful.

Common path:

1. **Select** a video template, style, scene/archetype family, actor family, and
   lyric treatment from the bundled catalogs/defaults.
2. **Materialize** those choices as typed objects/manifests.
3. **Inspect** the concrete object that needs attention; preserve all unaffected
   objects.
4. **Refine one mechanic** using that object's semantic handles.
5. **Route the mechanic** to the helper/toolset that performs it reliably.
6. **Verify** the refined object or rendered artifact, then return it to the
   composition.

Examples:

- diner feels stiff → refine actor gaze/mouth state, not the whole video;
- chorus text feels dull → refine the lyric/Manim object, not the actors;
- timing is wrong → refine the lyric map/alignment, not image generation;
- sprite sheet is malformed → reject/regenerate that actor object, do not make
  Manim or FFmpeg compensate for it.

Read `references/refinement-router.md` after selection when deeper work is
needed. It maps each object class to its useful refinement surface and preferred
toolset.

Selectors are defaults, not a prison. A custom mechanic remains available when
the selected object cannot express the requested result, but custom generation
should not be the common path.

## Capability gate

Choose the strongest route the current host actually supports.

### Prefer what the host already has

Before adding a model, package, provider, or service, inspect the current host
and prefer an adequate capability that is already available. Existing package
helpers and local tools reduce setup, provider state, authentication, fallback
logic, and future-model cognitive load.

Host-native-first is a preference, not permission to use the wrong observation
channel. For musical structure, local audio tools may be enough. For **timed
lyrics**, lexical acoustic evidence is required: auto-caption/ASR the rendered
performance, then reconcile that timestamped transcript against the canonical
lyric map. If no suitable ASR/aligner is already present, acquiring one is a
justified escalation when line/word timing is requested.

Do not substitute energy minima, pauses, or proportional timing for hearing which
words were sung. See `references/lyric-sync.md`.

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
`references/refinement-router.md`, `references/visual-grammar.md`, `references/asset-packs.md`, `references/scene-graph.md`, `references/pose-types.md`, `references/pose-families.md`, `references/lyric-map.md`, `references/lyric-sync.md`, `references/manim-lyrics.md`, `references/visual-out-contract.md`, `templates/catalog.json`, `scenes/catalog.json`, and `archetypes/catalog.json`, then choose:

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

## Script every visual-out call

Before invoking image generation for a production asset, write a compact visual-out brief. Declare the artifact role, downstream use, subject/continuity lock, layout, camera/scale, background requirement, allowed variation, forbidden artifacts, and acceptance checks.

This prevents a common failure: asking for an evocative concept and receiving a beautiful but unusable artifact class. A storyboard poster with baked timestamps, captions, borders, or a play icon is not a sprite atlas. A thumbnail prompt is not an environment-plate prompt. See `references/visual-out-contract.md` and `examples/visual-out-brief.json`.

Inspect each generated visual against its brief before using it. Reject/regenerate when the output violates the asset contract; do not rationalize the wrong artifact merely because it looks good.

## Use asset packs, not one-shot images

When continuity matters, a visual-generation call should often produce a reusable asset pack rather than one finished frame. For recurring actors, default to the proven **one-subject, four-pose, 2×2 sheet** pattern.

Keep scene roles separate. Prefer separate calls/packs for:

- one actor's four named poses;
- another actor's four named poses;
- props/sets such as a car or diner booth;
- occluders such as dashboard/glass/table edges;
- foreground/effect mattes;
- environment plates.

Treat these as persistent objects. Give poses semantic names/tags so later
reasoning can ask for `driving + romantic` or `bridge + intimate` rather than
remembering frame coordinates. See `references/asset-packs.md` and
`examples/asset-pack.json`.

This is especially valuable when stronger generation models are throttled:
spend inference once on a coherent pack, then reuse it mechanically.

## Mechanically split pose sheets

The 2×2 actor-sheet layout is a file format, not a visual suggestion. Never use
vision to find the four poses.

```bash
python scripts/pose_sheet.py examples/pose-sheet.json \
  --output-dir /project/media/paul-bear-driving
```

The helper probes only dimensions, divides the source into four equal quadrants
in row-major order, writes the four named PNGs, and returns exact crop
coordinates, pose types, byte lengths, and SHA-256 values.

If the image cannot be divided cleanly by those fixed quadrants, the generated
sheet failed the visual-out contract and should be regenerated.

## Match actors to character-free scenes

Scenes are separate from actors. Choose a character-free scene template, then
mechanically match actor poses to its typed slots.

```bash
python scripts/scene_contract.py validate scenes/car-front-seat.json
python scripts/scene_contract.py match \
  scenes/car-front-seat.json examples/pose-sheet.json --slot driver
```

The matcher returns only compatible poses plus the slot's normalized anchor,
scale, z-order, facing hint, and occluder list. Do not visually improvise
placement when a scene template already provides it.

Bundled scene templates include `car-front-seat`, `diner-booth`,
`standing-room`, and `bedside`.

## Refine actors inside compatible scenes

Body pose compatibility and performance state are separate.

For schema-2 actor sheets, each of the four cells also declares:

- `gaze` — e.g. forward, partner, phone, audience, eyes-closed;
- `mouth` — closed, smile, soft-open, singing-open, hold-note;
- `interaction` — none, partner, phone, steering-wheel, table, guitar, microphone.

This lets a diner actor remain `seated_table` while choosing whether to listen,
look at the partner, sing softly, or sing openly. It lets a driver remain
`seated_driver` while looking forward, looking at the partner, singing, or
glancing at a phone.

Filter those states mechanically:

```bash
python scripts/scene_contract.py match \
  scenes/diner-booth.json examples/pose-sheet-diner-v2.json \
  --slot right_seat --gaze partner --mouth singing_open
```

Prefer reusable four-state families from `references/pose-families.md` rather
than inventing four arbitrary variants per scene.

For tightly held objects such as guitars, use a four-pose **interaction pack**
with the actor and held object already aligned. Keep the surrounding stage/set,
lighting, haze, occluders, lyrics and camera separate.

## Instantiate scene archetypes

An archetype is a reusable mini-directing recipe, not a finished shot.

For example, `driving-loop` combines a moving road/environment plate, a separate car set/prop, one four-pose driver sheet, one four-pose passenger sheet, front-of-actor dashboard/glass occluders, plus optional foreground blur, rain and passing light. The bears are actors **inside** the car scene; they are not part of the car asset.

Scene templates specify where actors fit; archetypes specify what moves over time. Likewise, `slow-dance-loop`, `window-rain`, and `lyric-cloud` capture common
visual situations whose variation can be parameterized instead of re-invented.

Prefer instantiating and varying archetypes before asking inference to regenerate
an entire scene.

## Compile Manim lyric overlays

Treat lyric animation as a separate graphics layer above a compiled scene.

```bash
python scripts/lyric_overlay.py examples/lyric-overlay.json \
  --output /project/generated/sugar-bear-overlay.py
```

The compiler validates timing, canvas, normalized anchors, text length, scale,
rotation, and a bounded behavior vocabulary: `fade_hold`, `drift_up`,
`pulse`, `orbit`, `rain`, and `scatter`.

It then emits deterministic Manim source. In a host with Manim installed, render
that source on a transparent background to an alpha-capable intermediate, then
composite it above any compiled scene. The lyrics remain independently timed and
editable; they are never baked into actor sheets or scene/set generation.

Use this sparingly. The goal is moving typography as part of the visual world,
not default karaoke subtitles.

## Preserve lyric structure when GPT authors the song

If GPT authored the lyrics, immediately preserve a structured lyric map before
sending the text to Suno or another music generator. Do not wait for audio and
then transcribe the words GPT already knows.

The lyric map should retain section/line ids, repeated-section relationships,
motif tags, vocal-mode hints, pauses/instrumentals, and timing state. It may begin
with no timestamps at all.

Timing progresses from `authored` → `estimated` → `performed` → `aligned` when needed. The performed layer records what the rendered singer actually did; later reconciliation corrects timing/wording while preserving the authored semantic structure.

Treat caption formats as exports from this richer map:

- LRC/SRT/VTT/ASS for captions;
- Manim overlay/world events for kinetic/spatial lyrics;
- actor mouth/gaze state planning;
- section-to-archetype mapping.

See `references/lyric-map.md`.

## Synchronize performed lyrics

When captions, kinetic lyrics, or lyric-triggered actor states are requested,
use the actual performance as the timing source.

Default path:

1. auto-caption/ASR the rendered audio and preserve its raw timestamped output;
2. sequence-align that noisy performed transcript with the canonical lyric map;
3. repair names, wording, punctuation, token splits/merges, and obvious ASR
   errors while retaining acoustic spans;
4. preserve singer repeats, omissions, and inserted phrases as performed events;
5. export the reconciled map to SRT/ASS/Manim/actor-state timing.

Use `section_aligned`, `line_aligned`, and `word_aligned` as explicit
fidelity claims. Ordinary beat/onset/energy analysis may support
`section_aligned`; it cannot certify lyric lines.

See `references/lyric-sync.md`.

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
render a layered scene-graph/archetype composition, Manim lyric cloud, procedural field, or
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

See `references/evidence.md`, `references/refinement-router.md`, `references/visual-grammar.md`,
`references/asset-packs.md`, `references/scene-graph.md`, `references/pose-types.md`, `references/pose-families.md`, `references/lyric-map.md`, `references/lyric-sync.md`, `references/manim-lyrics.md`, `references/visual-out-contract.md`, and `references/field-notes.md`. Retain the
bundled MIT `LICENSE` when copying the skill independently.

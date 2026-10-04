# Visual grammar

The skill separates **editorial judgement** from **render mechanics** so a future
agent can make varied videos without rebuilding a filmmaking workflow from
scratch.

## Six layers

1. **Video template** — how a class of song spends visual attention over time.
   Examples: narrative ballad, hook-driven pop, ambient/sonification.
2. **Style pack** — the visual world: palette, characters, locations, recurring
   objects, prompt anchors, continuity rules, and forbidden drift.
3. **Asset packs** — persistent reusable visual objects such as sprite atlases,
   expressions, props, cutouts, effects, and repeatable environments. See
   `asset-packs.md`.
4. **Motif pack** — a small set of recurring ideas tied to lyrics or musical
   events: a clock, road, sticker, constellation, waveform, color change, etc.
5. **Scene archetypes** — reusable mini-directing recipes that combine layers and
   motion into recognizable situations: driving loop, slow dance, window rain,
   lyric cloud. See `../archetypes/catalog.json`.
6. **Shot modules** — final renderable primitives: hero still, native footage,
   push/pull, pan, typography, procedural field, stock insert, abstraction, or a
   clip rendered from an archetype.

The layers are deliberately composable. `ballad-narrative` +
`noir-romance` + `driving-loop` should feel different from the same ballad
template with a bright storybook style pack, while retaining useful song-level
structure.

## Why archetypes matter

An archetype captures a reusable *situation*, not a finished shot.

For example, a driving scene can be built from:

- one vehicle/character sprite pack,
- one repeatable or sufficiently long road background,
- optional foreground blur,
- optional rain,
- periodic light sweeps,
- small pose swaps and camera changes.

That one composition can yield many shots without re-generating the whole scene.
The background can loop or scroll continuously while the persistent foreground
sprites remain stable. Variation comes from speed, crop, pose, lighting, weather,
parallax, and overlays.

This is the same general lesson as persistent StickerBook objects: reuse stable
visual entities and change bounded state rather than asking inference to recreate
the world every time.

## Selection rule

Do not ask the model to invent every shot independently. Pick one video template
first, one style pack second, then choose reusable asset packs and a limited set
of archetypes/modules. Introduce novelty by changing one layer at a time.

A useful default budget is:

- 1–3 reusable asset packs,
- 3–6 recurring hero images or locations,
- 1–3 motif treatments,
- 2–4 scene archetypes,
- 2–4 low-level motion/compositing modules,
- optional stock or generated motion only where it adds something the still/
  sprite language cannot.

This keeps continuity strong and generation cost bounded.

## Supported deterministic still motion

The schema-2 local renderer supports these image motions:

- `static`
- `push_in`
- `pull_out`
- `pan_left`
- `pan_right`

It also supports `cut` and `fade_black` boundaries and automatically extracts a
JPEG poster after rendering. These are primitives, not an artistic ceiling.
A capable host may additionally create Manim scenes, animated typography,
procedural fields, stock-footage inserts, masks, overlays, sprite compositions,
or generated video and pass the resulting clips to the same final renderer as
ordinary video shots.

## Visual-interest ladder

Before paying for text-to-video inference, prefer the cheapest layer that adds
real value:

1. reuse/animate strong stills or persistent sprites;
2. instantiate a scene archetype such as driving, rain-window, or slow-dance;
3. add typography or procedural fields;
4. composite overlays, masks, particles, rain, grain, light, or waveform/data
   animation;
5. use rights-compatible stock footage for connective texture;
6. generate motion footage when continuity or action truly requires it.

A good music video is organized visual attention over time. It is not defined by
whether every source asset began life as video.

## Delivery is part of the build

A successful render produces both an MP4 and a poster image. When the host has a
native media surface, attach/present the MP4 there and use the poster when the
surface supports it. Treat "a file exists" and "the user can play it inline" as
separate observations. Do not claim inline playback until it is actually visible
or otherwise verified in the current host.

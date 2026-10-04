# Visual grammar

The skill separates **editorial judgement** from **render mechanics** so a future
agent can make varied videos without rebuilding a filmmaking workflow from
scratch.

## Four layers

1. **Video template** — how a class of song spends visual attention over time.
   Examples: narrative ballad, hook-driven pop, ambient/sonification.
2. **Style pack** — the visual world: palette, characters, locations, recurring
   objects, prompt anchors, continuity rules, and forbidden drift.
3. **Motif pack** — a small set of recurring ideas tied to lyrics or musical
   events: a clock, road, sticker, constellation, waveform, color change, etc.
4. **Shot modules** — concrete renderable moves: hero still, native footage,
   push/pull, pan, typography, procedural field, stock insert, or abstraction.

The layers are deliberately composable. `ballad-narrative` plus `noir-romance`
should feel different from the same ballad template with a bright storybook
style pack, while retaining useful song-level structure.

## Selection rule

Do not ask the model to invent every shot independently. Pick one video template
first, one style pack second, then instantiate sections using a limited palette
of modules. Introduce novelty by changing one layer at a time.

A useful default budget is:

- 3–6 recurring hero images or locations,
- 1–3 motif treatments,
- 2–4 motion/compositing modules,
- optional stock or generated motion only where it adds something the still
  language cannot.

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
procedural fields, stock-footage inserts, masks, overlays, or generated video
and pass the resulting clips to the same final renderer as ordinary video shots.

## Visual-interest ladder

Before paying for text-to-video inference, prefer the cheapest layer that adds
real value:

1. reframe or animate strong stills;
2. add typography or procedural fields;
3. composite overlays, masks, particles, rain, grain, light, or waveform/data
   animation;
4. use rights-compatible stock footage for connective texture;
5. generate motion footage when continuity or action truly requires it.

A good music video is organized visual attention over time. It is not defined by
whether every source asset began life as video.

## Delivery is part of the build

A successful render produces both an MP4 and a poster image. When the host has a
native media surface, attach/present the MP4 there and use the poster when the
surface supports it. Treat "a file exists" and "the user can play it inline" as
separate observations. Do not claim inline playback until it is actually visible
or otherwise verified in the current host.

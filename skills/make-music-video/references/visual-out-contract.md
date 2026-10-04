# Visual-out contract

Do not call image generation from a vague aesthetic paragraph when the output is
intended to become a production asset.

Before every visual-generation call, write a small **visual-out brief** that says
what the image is *for*, not merely what it should look like.

The motivating failure was instructive: a request meant to demonstrate reusable
music-video assets instead produced a beautiful storyboard poster with baked-in
timestamps, captions, panel borders, and a fake play button. It looked good but
was the wrong artifact class. The image generator optimized the visible concept
rather than the downstream compositing need because the production contract was
underspecified.

## Required fields

A visual-out brief should contain:

- **role** — hero still, sprite atlas, expression atlas, prop atlas, environment
  plate, effect matte, stock-reference target, thumbnail/poster, etc.;
- **downstream use** — which archetype/module will consume it;
- **subject lock** — exact recurring character/object identity to preserve;
- **layout** — single frame, N×M atlas, isolated objects, panoramic plate, etc.;
- **camera/scale** — fixed or intentionally varied;
- **background requirement** — transparent, flat keyable, seamless, scenic;
- **allowed variation** — pose, expression, angle, lighting, prop state;
- **forbidden artifacts** — text, labels, borders, UI, timestamps, play icons,
  watermarks, overlapping cells, duplicate poses, perspective drift;
- **acceptance checks** — observable facts that make the output usable.

## Asset-role examples

### Sprite / pose atlas

Use a fixed grid and named pose plan. Require:

- same subject design and wardrobe in every cell;
- one pose per cell;
- non-overlapping silhouettes;
- consistent scale and camera angle unless the pose requires otherwise;
- flat or transparent-friendly background;
- no labels or decorative typography;
- enough empty margin around every subject to crop cleanly.

### Character-free scene / set plate

A reusable scene is generated **without recurring characters**. It should be
designed around typed actor slots rather than baked performers.

Require:

- no recurring actors in the pixels;
- enough negative/clear space for each declared slot;
- composition appropriate to the slot pose family, e.g. seated actors for a
  diner booth or car, standing actors for a room/stage;
- set/prop geometry consistent with the normalized anchors in the scene
  template;
- if actors must appear behind foreground geometry, provide that geometry as a
  separate occluder asset rather than baking actors into the scene;
- no decorative UI/text unless the scene itself genuinely contains signage.

The scene template, not the generated image, declares which pose types fit each
slot.

### Repeatable background plate

Require:

- no characters unless explicitly part of the environment;
- composition safe for horizontal or vertical scrolling;
- edge structure compatible with looping, mirroring, or masked repetition;
- no baked text/signage unless it is intentionally part of the world;
- sufficient motion cues (road lines, lights, rain, clouds, texture) for the
  target archetype.

### Effect matte

Require:

- isolated effect only: rain, haze, light sweep, particles, smoke, etc.;
- simple black/white, alpha-friendly, or chroma-key-friendly background;
- no scenic illustration or subjects;
- no text.

### Poster / thumbnail

This is the opposite case: baked title treatment, typography, layout, and a
single strong read may be desirable. Do not accidentally reuse poster prompting
for production atlases.

## Pre-call self-check

Before invoking image generation, answer:

1. What exact artifact class am I requesting?
2. Can the downstream compositor crop/use it without manual repair or visual placement discovery?
3. What must remain identical across cells/variants?
4. What must **not** appear in the pixels?
5. How will I reject the result if the generator gets creative in the wrong way?

If those answers are not explicit, write them before making the call.

## Post-call acceptance gate

Inspect the image against the brief before using it.

For an atlas, reject/regenerate when any of these are present unless explicitly
requested:

- baked text, timestamps, titles, captions, UI, or play buttons;
- panel frames that consume useful crop area;
- overlapping subjects across cells;
- inconsistent identity, wardrobe, scale, or camera;
- missing required poses;
- duplicates where distinct poses were requested;
- backgrounds too complex to segment;
- insufficient margins for cropping.

Do not rescue the wrong artifact class merely because the image is attractive.
A beautiful poster is still a failed sprite atlas.

## Cost rule

The brief is cheap; generation is expensive. Spend reasoning before inference.

One well-scripted visual call should ideally produce several downstream assets, but do not compound unrelated scene roles merely to reduce call count. Actor sheets, scene/set plates, occluders, and effects should remain mechanically separable.

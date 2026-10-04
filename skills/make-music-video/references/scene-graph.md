# Scene graph

Music-video archetypes are layered scene graphs, not flattened collages.

Keep reusable objects separate until an archetype has been composed into a normal
video clip.

## Canonical z-order

Back to front:

1. **environment** — sky, road, city, room, landscape, wall, floor;
2. **set / large prop** — car, diner booth, bed, stage, desk;
3. **actors** — each recurring character is an independent object;
4. **midground occluders** — steering wheel, dashboard, windshield frame, table,
   door frame, curtains, furniture that must appear in front of actors;
5. **foreground** — poles, branches, bokeh, blurred passing objects;
6. **weather / atmosphere** — rain, haze, dust, smoke;
7. **lighting / reflections** — passing light, neon wash, lens flare, glass
   reflection;
8. **graphics / typography** — lyric objects, clocks, titles, motif graphics.

Do not fuse roles merely because they appear together in the final shot.

## Driving example

A correct driving scene is:

```
environment: moving road / night landscape
set:         car body or car-interior shell
actor A:     driver bear
actor B:     passenger bear
occluders:   dashboard / steering wheel / windshield frame / glass
foreground:  fast blurred roadside elements
weather:     rain
lighting:    passing lamps / headlights / neon
graphics:    optional lyric or 1:11 motif
```

The bears are **in** the car scene. They are not part of the car asset.

Consequences:

- driver and passenger poses can change independently;
- the car can bob/scale/shift without deforming the bears;
- the road can scroll without moving the car;
- dashboard/glass can occlude the actors correctly;
- lighting can affect multiple layers without flattening them;
- the same actors can be placed in a diner, motel room, stage, or other
  archetype without regeneration.

## Four-pose actor sheets

Prefer the proven small-sheet pattern for recurring actors:

- one subject per sheet;
- four poses;
- 2×2 layout;
- consistent identity, wardrobe, scale, and camera;
- simple/keyable or real-alpha background;
- no labels, borders, UI, timestamps, or decorative text;
- generous crop margin around each pose.

A second recurring actor gets a second independent four-pose sheet. Do not put
both actors into one pose cell unless the **pair itself** is intentionally the
persistent object for a specific archetype.

## Acceptance rule

Reject an upstream asset when it collapses scene roles needed by the intended
archetype.

Examples:

- a bear fused into a car image is not acceptable when the bear must later
  change pose;
- a diner booth with the characters baked in is not a reusable set;
- rain baked into a character cutout is not a reusable effect layer;
- checkerboard pixels that merely *look* transparent are not alpha.

Flattening is allowed only after the archetype has been composed and the clip is
ready for the final timeline renderer.

## StickerBook principle

Treat every reusable actor/prop as a persistent object with its own identity and
bounded state. Scene assembly changes placement, pose, visibility, scale, and
z-order; it does not ask inference to recreate the whole world for every shot.

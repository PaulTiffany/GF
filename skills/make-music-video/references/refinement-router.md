# Refinement router

Use this table after the common-path selectors have produced a concrete object.
Do not reopen the entire music-video problem merely because one object needs work.

| Selected object | Refine semantically | Preferred mechanics / toolset | Return to workflow as |
| --- | --- | --- | --- |
| video template | section emphasis, attention curve, novelty budget | template JSON + editorial reasoning | selected template |
| style pack | world, palette, continuity, forbidden drift | style JSON + image-generation references | style pack |
| lyric map | section roles, repeated motifs, vocal intent, landmark importance | authored map first; alignment tool only to add/correct timing | authored/estimated/aligned lyric map |
| actor pack | body family, gaze, mouth/vocal state, interaction | image generation for fixed 2×2 source; `pose_sheet.py` for mechanical slicing | typed four-pose pack |
| scene template | narrative situation, desired actor relationship | character-free image/set generation; `scene_contract.py` for slots/compatibility | typed scene |
| archetype | what changes through time | archetype JSON + deterministic scene compositor | rendered archetype clip |
| held-object interaction | how actor physically contacts guitar/phone/mic | dedicated actor+held-object 2×2 interaction pack; do not loose-layer the prop | interaction pack |
| lyric overlay | phrase choice, semantic emphasis, screen role | `lyric_overlay.py` → deterministic Manim source; render with Manim when available | transparent graphics clip |
| spatial lyric world | path metaphor, landmark hierarchy, section transitions | Manim 3D/text/camera grammar from lyric-map events; deterministic geometry preferred | rendered world clip |
| final timeline | editorial order, holds, transitions | `music_video.py` + FFmpeg/FFprobe | verified MP4 + poster + receipts |

## Routing rule

Selectors should answer **what kind of object should exist**. Once selected, work
inside that object's refinement surface until it is acceptable, then return it to
the parent composition.

Examples:

- Do not rethink the whole video because a diner actor looks stiff; refine the
  actor pack's gaze/mouth state.
- Do not regenerate the actors because the chorus typography is dull; refine the
  lyric overlay/world object.
- Do not ask image generation to solve a timing problem; refine the lyric map.
- Do not ask Manim to fix a malformed sprite sheet; reject/regenerate the actor
  source against its visual-out contract.
- Do not ask GPT to remember crop coordinates or z-order that a helper already
  certifies mechanically.

## Escalation rule

Prefer the cheapest certified mechanic first. Escalate only when the current
object cannot express the requested refinement.

Typical order:

1. selector/default;
2. parameter change on the existing object;
3. deterministic helper/compiler;
4. regenerate only that object;
5. custom mechanic;
6. expensive generated motion only when the cheaper grammar cannot express the
   required continuous action.

The parent workflow should retain all unaffected objects while one object is
being refined.

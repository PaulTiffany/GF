# Manim lyric overlays

Manim is an **upstream graphics renderer** for lyrics and motif animation. It
does not own character placement, scene composition, or the final edit.

Render the actors/set first, render Manim graphics separately on a transparent
background, then composite the graphics above the compiled scene.

## Why a manifest instead of bespoke code

Future GPT should select from a small motion vocabulary rather than write a new
Manim program for every song.

A lyric overlay manifest declares:

- output duration;
- timed text events;
- normalized anchor positions;
- a small behavior vocabulary;
- typography scale and optional rotation;
- optional motif/group ids for recurring treatments.

The bundled compiler validates that contract and emits deterministic Manim source.
The compiler itself does not require Manim to be installed.

## Behavior vocabulary

Start small:

- `fade_hold` — fade in, hold, fade out;
- `drift_up` — enter softly and rise while visible;
- `pulse` — scale pulse around a fixed anchor;
- `orbit` — phrase follows a small circular path;
- `rain` — phrase drops vertically through the frame;
- `scatter` — individual words enter from small radial offsets and settle.

Use these as graphic roles, not as karaoke defaults.

## Overlay philosophy

Lyrics should usually be **objects in the visual world**, not subtitles.

Examples:

- “1:11” can pulse near a phone or clock motif;
- “home” can gather other words toward it;
- “Sugar Bear” can recur in a consistent signature treatment;
- a guitar solo can replace literal lyrics with waveform or phrase fragments;
- bridge text can become sparse while the scene underneath simplifies.

## Transparent delivery

The emitted Manim scene sets a transparent background and should be rendered to
an alpha-capable intermediate supported by the host. The final compositor then
places that clip above the scene and below any intentionally frontmost UI/title
layer.

Do not flatten lyrics into generated scene art when they need independent timing,
revisions, masks, or reuse.

## Acceptance checks

Before compositing a lyric overlay:

- exact overlay duration matches the declared manifest;
- no text event exceeds the overlay duration;
- normalized anchors stay in frame;
- behavior name is from the supported vocabulary;
- text remains legible at target resolution;
- no event contains huge blocks of lyrics by default;
- the transparent render really contains alpha or a deterministic keyable
  background.

The same overlay manifest can be reused over different scene archetypes.

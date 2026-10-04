# Asset packs

A visual-generation call should not default to producing one finished shot.
When continuity matters, prefer generating a **reusable asset pack** that can
feed many shots and archetypes.

This pattern is informed by StickerBook's persistent-object approach: visual
subjects remain identifiable objects with bounded poses, states and reusable
motion semantics rather than being re-invented frame by frame.

## Pack types

- **sprite pack** — several full-body poses or animation frames on one atlas;
- **expression pack** — stable framing with several emotional states;
- **cutout pack** — transparent character, prop, foreground or effect elements;
- **prop pack** — recurring car, phone, sign, instrument, furniture, etc.;
- **effect pack** — rain, haze, glow, shadow, flare or light mattes;
- **environment pack** — repeatable/extendable background plates.

One generation can deliberately request a contact-sheet or atlas containing many
usable elements. The host may then crop/segment those elements into separate
files or treat the atlas as the source of truth.

## Semantic pose metadata

Prefer semantic names over frame numbers:

```json
{
  "id": "sugar-bears-v1",
  "type": "sprite-pack",
  "poses": [
    {"id": "driving_forward", "tags": ["driving", "verse", "neutral"]},
    {"id": "leaning_close", "tags": ["driving", "romantic", "chorus"]},
    {"id": "slow_dance_left", "tags": ["dance", "romantic"]},
    {"id": "slow_dance_right", "tags": ["dance", "romantic"]},
    {"id": "forehead_touch", "tags": ["intimate", "bridge", "closeup"]}
  ]
}
```

Future GPT can then choose poses by intent instead of remembering coordinates or
filenames.

## Why packs beat shot-by-shot generation

- identity and wardrobe continuity improve;
- a single visual-generation call has higher downstream value;
- archetypes can reuse the same subject in different environments;
- local animation becomes deterministic and cheap;
- model throttling or unavailable high-tier inference hurts less;
- the agent reasons in terms of characters and actions rather than raw pixels.

## Sprite-atlas prompt rule

When requesting a sprite/pose atlas, explicitly ask for:

- the same subject design in every cell;
- a simple or transparent-friendly background;
- separated non-overlapping poses;
- consistent scale and camera angle unless variation is intentional;
- a finite named pose list;
- no text labels inside the image unless labels are genuinely useful.

A generated atlas is an upstream source artifact. The final compositor should
consume extracted/cropped sprites or rendered archetype clips rather than become
dependent on one image-generation provider.

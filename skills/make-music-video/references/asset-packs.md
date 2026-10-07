# Asset packs

A visual-generation call should not default to producing one finished shot.
When continuity matters, prefer generating a **reusable asset pack** that can
feed many shots and archetypes.

This pattern is informed by StickerBook's persistent-object approach: visual
subjects remain identifiable objects with bounded poses, states and reusable
motion semantics rather than being re-invented frame by frame.

## Pack types

- **actor pack** — one recurring subject, usually as a small four-pose 2×2 sheet;
- **expression pack** — one actor with several emotional states;
- **prop/set pack** — car, phone, sign, instrument, booth, bed, furniture, etc.;
- **occluder pack** — dashboard, windshield frame, table edge, curtains, foliage, etc.;
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
- archetypes can place the same actor independently into different sets and environments;
- local scene composition becomes deterministic and cheap;
- model throttling or unavailable high-tier inference hurts less;
- the agent reasons in terms of characters and actions rather than raw pixels.

## Script the visual-out call first

Before requesting any atlas, read `visual-out-contract.md` and write a visual-out brief. The brief must declare the artifact role, downstream archetype, layout, continuity locks, forbidden pixels, and acceptance checks. Do not spend image inference until the production need is explicit.

## Sprite-atlas prompt rule

When requesting a sprite/pose atlas, explicitly ask for:

- the same subject design in every cell;
- a simple or transparent-friendly background;
- separated non-overlapping poses;
- consistent scale and camera angle unless variation is intentional;
- a finite named pose list;
- no text labels inside the image unless labels are genuinely useful.

After generation, inspect the output against the visual-out brief. Reject attractive but wrong artifact classes such as storyboard posters, contact sheets with baked captions/UI, or atlases whose cells cannot be cleanly cropped.

A generated atlas is an upstream source artifact. The final compositor should
consume extracted/cropped sprites or rendered archetype clips rather than become
dependent on one image-generation provider.


## Default actor-pack size: four poses

For recurring characters, default to **one subject per 2×2 four-pose sheet**.
This is intentionally small. It is easier for image generation to preserve
identity, easier to crop cleanly, and easier for the agent to reason about.

Typical four-pose sets should be archetype-specific, for example:

- driving: `forward`, `look_partner`, `lean_close`, `phone_glance`;
- romance: `idle`, `embrace`, `forehead_touch`, `resting`;
- performance: `sing_neutral`, `sing_open`, `gesture`, `hold_note`.

Generate a second four-pose sheet for a second recurring actor. Keep the actors
separate from each other and from props/sets unless a fused pair is explicitly
the reusable object required by the archetype.

## Respect scene roles

A character that appears in a car should remain an **actor asset**, while the car
remains a **prop/set asset**. The road is an **environment**, windshield/dashboard
can be **occluders**, and rain/light remain **effects**.

This separation is what makes the same actor pack reusable across driving, diner,
motel, stage, and other scenes. See `scene-graph.md`.

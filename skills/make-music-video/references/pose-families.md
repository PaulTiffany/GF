# Four-state pose families

Future GPT should not invent four arbitrary poses for every scene. Prefer a
small library of **scene-aware four-state families**.

Each family keeps body compatibility fixed while varying gaze, mouth/vocal state,
and interaction state. This gives the editor useful expressive choices without
breaking slot compatibility.

## Driving — driver

Body type: `seated_driver`

1. `driving_forward` — gaze forward, mouth closed, steering-wheel interaction;
2. `look_at_partner` — gaze partner, smile, steering-wheel interaction;
3. `sing_while_driving` — gaze forward, singing-open, steering-wheel interaction;
4. `phone_glance` — gaze phone, soft-open, phone interaction.

## Driving — passenger

Body type: `seated_passenger` or generic `seated`

1. `ride_forward` — gaze forward, mouth closed;
2. `look_at_partner` — gaze partner, smile;
3. `sing_soft` — gaze partner or forward, soft-open;
4. `rest_close` — gaze partner or eyes-closed, closed/smile.

## Diner booth

Body type: `seated_table`

1. `listen` — gaze partner, closed;
2. `smile_partner` — gaze partner, smile;
3. `sing_soft` — gaze partner, soft-open;
4. `sing_open` — gaze forward/partner, singing-open.

The table remains a separate occluder.

## Standing romance

Body type: `standing`, `standing_close`, or `embrace`

1. `face_partner`;
2. `lean_close`;
3. `embrace`;
4. `sing_to_partner`.

Do not fake continuous dance choreography from these four states. Use long holds,
camera/light movement, and occasional state changes.

## Vocal performance

Body type: `performance`

1. `sing_closed` — preparatory/rest mouth state;
2. `sing_open` — standard singing-open state;
3. `hold_note` — hold-note mouth state;
4. `gesture` — singing-open or smile with a distinct arm gesture.

## Instrument performance

When a held prop must align tightly with the body, prefer an **interaction pack**
instead of layering the prop afterward.

For a guitar pack, each of the four cells should already contain the same actor
holding the same guitar correctly:

1. `guitar_rest`;
2. `guitar_play`;
3. `guitar_look_down`;
4. `guitar_hold_note`.

The actor+guitar pair is the reusable interaction object. The stage, mic stand,
lighting, haze, audience and lyric overlays remain separate scene layers.

## Selection rule

Choose in this order:

1. scene template;
2. actor slot;
3. compatible body-type family;
4. desired gaze;
5. desired mouth/vocal state;
6. desired interaction state.

Use `scene_contract.py match` to perform the filtering mechanically whenever
possible.

# Pose types

Pose types are a small compatibility vocabulary between **actor packs** and
**character-free scene templates**.

They are not exhaustive animation labels. They answer a simpler production
question: *can this cutout plausibly occupy this scene slot?*

## Core types

- `standing` — full-body or three-quarter standing pose;
- `standing_close` — standing/intimate pose intended for close placement with
  another actor;
- `seated` — generic seated pose;
- `seated_driver` — seated pose oriented for a steering wheel / driver slot;
- `seated_passenger` — seated pose compatible with a passenger seat;
- `seated_table` — seated pose whose lower body can be hidden by a table/booth
  occluder;
- `reclined` — bed/couch/rest pose;
- `embrace` — pose intended to overlap or pair with another actor;
- `performance` — singer/player/gesture pose with open presentation space;
- `custom` — allowed only when the consuming scene explicitly names a custom
  contract.

A pose may have a specific semantic id such as `look_at_partner` while still
having a compatibility type such as `seated_driver`.

## Scene slots

A scene template declares actor slots with:

- slot id;
- accepted pose types;
- normalized anchor `x,y` in 0..1 scene coordinates;
- nominal scale;
- optional facing/orientation hint;
- z index;
- occluders that are expected to sit in front of the actor.

Example:

```json
{
  "id": "driver",
  "accepts": ["seated_driver"],
  "anchor": {"x": 0.43, "y": 0.58},
  "scale": 0.34,
  "facing": "front_three_quarter",
  "z": 30,
  "occluded_by": ["dashboard_front", "steering_wheel"]
}
```

Future GPT should select a scene first, then choose actor poses whose **type**
matches each slot. The semantic pose id chooses the emotional/action variant
inside that compatible family.

## Why this reduces cognitive load

The agent no longer has to visually reason from scratch about whether a standing
bear belongs in a diner booth or whether a reclined pose fits a car seat. The
scene advertises the contract; the actor pack advertises its compatible pose
types; selection can be validated before any compositing.


## Performance state is orthogonal to body type

Body compatibility answers **where can this actor fit?** Performance state answers
**what is the actor doing emotionally/vocally inside that compatible body pose?**

Schema-2 pose sheets add three bounded state dimensions:

- **gaze** — `forward`, `partner`, `down`, `phone`, `audience`,
  `offscreen_left`, `offscreen_right`, `eyes_closed`;
- **mouth** — `closed`, `smile`, `soft_open`, `singing_open`,
  `hold_note`;
- **interaction** — `none`, `partner`, `phone`, `steering_wheel`,
  `table`, `guitar`, `microphone`.

A diner actor can therefore remain `seated_table` across all four cells while
changing from listening → smiling at partner → soft singing → open singing.

A driver can remain `seated_driver` while changing gaze or singing state.

Use `scene_contract.py match --gaze ... --mouth ... --interaction ...` to filter
compatible poses mechanically after the body-type match.

See `pose-families.md` for reusable four-state families.

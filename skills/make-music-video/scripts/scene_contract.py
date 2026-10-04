#!/usr/bin/env python3
"""Validate a character-free scene template and mechanically match typed actor poses to slots."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
POSE_TYPES = {
    "standing", "standing_close", "seated", "seated_driver",
    "seated_passenger", "seated_table", "reclined", "embrace",
    "performance", "custom"
}
ROLES = {"environment", "set", "occluder", "foreground", "weather", "lighting", "graphics"}
MAX_METADATA = 64 * 1024


class ValidationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def read_json(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    require(len(data) <= MAX_METADATA, f"{path.name} exceeds 64 KiB")
    value = json.loads(data)
    require(isinstance(value, dict), f"{path.name} must contain a JSON object")
    return value


def valid_name(value: Any, label: str) -> str:
    require(isinstance(value, str) and NAME_RE.fullmatch(value) is not None,
            f"{label} must match {NAME_RE.pattern}")
    return value


def load_scene(path: Path) -> dict[str, Any]:
    value = read_json(path)
    required = {"schema", "id", "character_free", "required_assets", "optional_assets", "actor_slots", "motion_defaults"}
    require(set(value) == required, f"scene fields must be exactly: {', '.join(sorted(required))}")
    require(value["schema"] == 1 and type(value["schema"]) is int, "unsupported scene schema")
    valid_name(value["id"], "scene.id")
    require(value["character_free"] is True, "scene templates must be character_free=true")

    asset_ids: set[str] = set()
    for group in ("required_assets", "optional_assets"):
        assets = value[group]
        require(isinstance(assets, list), f"{group} must be a list")
        for index, asset in enumerate(assets):
            require(isinstance(asset, dict) and set(asset) == {"id", "role", "z"},
                    f"{group}[{index}] must contain exactly id, role, z")
            asset_id = valid_name(asset["id"], f"{group}[{index}].id")
            require(asset_id not in asset_ids, f"duplicate scene asset id: {asset_id}")
            require(asset["role"] in ROLES, f"{group}[{index}].role is invalid")
            require(type(asset["z"]) is int, f"{group}[{index}].z must be an integer")
            asset_ids.add(asset_id)

    slots = value["actor_slots"]
    require(isinstance(slots, list) and slots, "actor_slots must be a nonempty list")
    slot_ids: set[str] = set()
    for index, slot in enumerate(slots):
        required_slot = {"id", "accepts", "anchor", "scale", "facing", "z", "occluded_by"}
        require(isinstance(slot, dict) and set(slot) == required_slot,
                f"actor_slots[{index}] has invalid fields")
        slot_id = valid_name(slot["id"], f"actor_slots[{index}].id")
        require(slot_id not in slot_ids, f"duplicate actor slot id: {slot_id}")
        slot_ids.add(slot_id)
        accepts = slot["accepts"]
        require(isinstance(accepts, list) and accepts, f"actor_slots[{index}].accepts must be nonempty")
        for pose_type in accepts:
            require(pose_type in POSE_TYPES, f"unknown pose type in slot {slot_id}: {pose_type}")
        anchor = slot["anchor"]
        require(isinstance(anchor, dict) and set(anchor) == {"x", "y"}, f"slot {slot_id} anchor must contain x,y")
        for axis in ("x", "y"):
            require(type(anchor[axis]) in (int, float) and 0 <= float(anchor[axis]) <= 1,
                    f"slot {slot_id} anchor.{axis} must be in 0..1")
        require(type(slot["scale"]) in (int, float) and 0 < float(slot["scale"]) <= 4,
                f"slot {slot_id} scale must be in (0,4]")
        require(isinstance(slot["facing"], str) and slot["facing"], f"slot {slot_id} facing must be nonempty")
        require(type(slot["z"]) is int, f"slot {slot_id} z must be an integer")
        require(isinstance(slot["occluded_by"], list), f"slot {slot_id} occluded_by must be a list")
        for asset_id in slot["occluded_by"]:
            require(asset_id in asset_ids, f"slot {slot_id} references unknown occluder: {asset_id}")

    require(isinstance(value["motion_defaults"], dict), "motion_defaults must be an object")
    return value


def load_actor_sheet(path: Path) -> dict[str, Any]:
    value = read_json(path)
    require(set(value) == {"schema", "actor_id", "source", "poses"},
            "actor pose sheet must contain exactly actor_id, poses, schema, source")
    require(value["schema"] == 1 and type(value["schema"]) is int, "unsupported actor sheet schema")
    valid_name(value["actor_id"], "actor_id")
    require(isinstance(value["source"], str) and value["source"], "actor source must be nonempty")
    poses = value["poses"]
    require(isinstance(poses, list) and len(poses) == 4, "actor sheet must contain exactly four poses")
    seen: set[str] = set()
    for index, pose in enumerate(poses):
        require(isinstance(pose, dict) and set(pose) == {"id", "type"},
                f"poses[{index}] must contain exactly id and type")
        pose_id = valid_name(pose["id"], f"poses[{index}].id")
        require(pose_id not in seen, f"duplicate pose id: {pose_id}")
        seen.add(pose_id)
        require(pose["type"] in POSE_TYPES, f"unknown pose type: {pose['type']}")
    return value


def compatible(scene: dict[str, Any], actor: dict[str, Any], slot_id: str) -> dict[str, Any]:
    slot = next((s for s in scene["actor_slots"] if s["id"] == slot_id), None)
    require(slot is not None, f"unknown scene slot: {slot_id}")
    accepted = set(slot["accepts"])
    matches = [p for p in actor["poses"] if p["type"] in accepted]
    return {
        "scene": scene["id"],
        "slot": slot_id,
        "accepts": slot["accepts"],
        "actor_id": actor["actor_id"],
        "compatible_poses": matches,
        "compatible": bool(matches),
        "placement": {
            "anchor": slot["anchor"],
            "scale": slot["scale"],
            "facing": slot["facing"],
            "z": slot["z"],
            "occluded_by": slot["occluded_by"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("scene", type=Path)
    match = sub.add_parser("match")
    match.add_argument("scene", type=Path)
    match.add_argument("actor_sheet", type=Path)
    match.add_argument("--slot", required=True)
    args = parser.parse_args()

    try:
        scene = load_scene(args.scene)
        if args.command == "validate":
            print(json.dumps({"valid": True, "scene": scene["id"], "slots": [s["id"] for s in scene["actor_slots"]]}, indent=2))
        else:
            actor = load_actor_sheet(args.actor_sheet)
            print(json.dumps(compatible(scene, actor, args.slot), indent=2))
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        parser.exit(2, f"scene-contract: {error}\n")


if __name__ == "__main__":
    main()

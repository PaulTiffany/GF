#!/usr/bin/env python3
"""List, inspect, and validate GF build metadata without executing build code."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EFFECTS = {"local-read", "local-write", "network-read", "network-write", "account-write", "spend"}
FIELDS = {"schema", "id", "summary", "skill", "entrypoint", "license", "requires",
          "inputs", "outputs", "effects", "bounds", "stop_when", "evidence"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique_object(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    with path.open("rb") as source:
        data = source.read(65_537)
    require(len(data) <= 65_536, f"Metadata exceeds 64 KiB: {path.name}")
    value = json.loads(data, object_pairs_hook=unique_object)
    require(isinstance(value, dict), f"Expected a JSON object: {path.name}")
    return value


def fields(value: object, expected: set, label: str) -> None:
    require(isinstance(value, dict) and set(value) == expected,
            f"{label}: expected fields {', '.join(sorted(expected))}")


def strings(value: object, label: str, *, empty: bool = False) -> list:
    require(isinstance(value, list) and (empty or bool(value)), f"{label}: expected a list")
    require(all(isinstance(item, str) and item.strip() for item in value),
            f"{label}: expected nonempty strings")
    return value


def reference(root: Path, name: str, *, directory: bool = False) -> Path:
    require(isinstance(name, str) and bool(name), "Reference must be a nonempty path")
    path = Path(name)
    require(not path.is_absolute() and ".." not in path.parts,
            f"Reference must stay within its package: {name}")
    target = (root / path).resolve()
    require(target.is_relative_to(root.resolve()), f"Reference escapes its package: {name}")
    require(target.is_dir() if directory else target.is_file(), f"Missing reference: {name}")
    return target


def load_catalog(root: Path = ROOT) -> list[dict]:
    catalog = read_json(reference(root, "catalog.json"))
    fields(catalog, {"schema", "builds"}, "catalog")
    require(type(catalog["schema"]) is int and catalog["schema"] == 1, "Unsupported catalog schema")
    require(isinstance(catalog["builds"], list), "builds: expected a list")
    builds, seen = [], set()
    for entry in catalog["builds"]:
        fields(entry, {"package", "checks"}, "catalog entry")
        package = reference(root, entry["package"], directory=True)
        build = read_json(reference(package, "build.json"))
        fields(build, FIELDS, entry["package"])
        require(type(build["schema"]) is int and build["schema"] == 1, "Unsupported build schema")
        name = build["id"]
        require(isinstance(name, str) and len(name) < 64 and
                re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) is not None, "Invalid build id")
        require(name not in seen, f"Duplicate build id: {name}")
        seen.add(name)
        require(isinstance(build["summary"], str) and bool(build["summary"].strip()), "Missing summary")
        for key in ("skill", "entrypoint", "license"):
            reference(package, build[key])
        for key in ("requires", "inputs", "outputs", "stop_when", "evidence"):
            strings(build[key], f"{name}.{key}")
        effects = strings(build["effects"], f"{name}.effects", empty=True)
        require(set(effects) <= EFFECTS, f"{name}: unknown effect")
        fields(build["bounds"], {"enforced", "operator"}, f"{name}.bounds")
        strings(build["bounds"]["enforced"], f"{name}.bounds.enforced", empty=True)
        strings(build["bounds"]["operator"], f"{name}.bounds.operator")
        for record in build["evidence"]:
            reference(package, record)
        for check in strings(entry["checks"], f"{name}.checks"):
            reference(root, check)
        builds.append({"package": entry["package"], "checks": entry["checks"], **build})
    return builds


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List available builds")
    show = commands.add_parser("show", help="Print a build's declared contract as JSON")
    show.add_argument("id")
    commands.add_parser("check", help="Validate metadata and referenced files")
    args = parser.parse_args()
    try:
        builds = load_catalog()
        if args.command == "list":
            for build in builds:
                print(f"{build['id']} — {build['summary']}")
        elif args.command == "show":
            match = next((build for build in builds if build["id"] == args.id), None)
            require(match is not None, f"Unknown build: {args.id}")
            print(json.dumps(match, indent=2))
        else:
            print(f"Validated {len(builds)} build(s): metadata and references only; no code executed.")
    except (OSError, ValueError) as error:
        parser.exit(1, f"catalog: {error}\n")


if __name__ == "__main__":
    main()

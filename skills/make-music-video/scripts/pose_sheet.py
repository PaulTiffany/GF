#!/usr/bin/env python3
"""Mechanically split a fixed 2x2 single-actor pose sheet into four named cells."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
MAX_METADATA = 32 * 1024
MAX_INPUT_BYTES = 128 * 1024 * 1024
MIN_CELL = 128


class ValidationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def read_json(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    require(len(data) <= MAX_METADATA, "pose-sheet manifest exceeds 32 KiB")
    value = json.loads(data)
    require(isinstance(value, dict), "pose-sheet manifest must be an object")
    return value


def safe_source(root: Path, name: Any) -> Path:
    require(isinstance(name, str) and name.strip(), "source must be a nonempty relative path")
    raw = Path(name)
    require(not raw.is_absolute() and ".." not in raw.parts, "source must stay inside the manifest directory")
    path = (root / raw).resolve()
    require(path.is_relative_to(root.resolve()), "source escapes the manifest directory")
    require(path.is_file(), f"missing source image: {name}")
    require(path.stat().st_size <= MAX_INPUT_BYTES, "source image exceeds 128 MiB")
    return path


def load_manifest(path: Path) -> tuple[Path, tuple[str, ...]]:
    path = path.resolve()
    value = read_json(path)
    require(set(value) == {"schema", "source", "poses"},
            "pose-sheet fields must be exactly: poses, schema, source")
    require(value["schema"] == 1 and type(value["schema"]) is int, "unsupported pose-sheet schema")
    poses = value["poses"]
    require(isinstance(poses, list) and len(poses) == 4, "poses must contain exactly four names")
    names: list[str] = []
    for index, pose in enumerate(poses):
        require(isinstance(pose, str) and NAME_RE.fullmatch(pose) is not None,
                f"poses[{index}] must match {NAME_RE.pattern}")
        require(pose not in names, f"duplicate pose name: {pose}")
        names.append(pose)
    return safe_source(path.parent, value["source"]), tuple(names)


def crop_boxes(width: int, height: int) -> tuple[tuple[int, int, int, int], ...]:
    require(type(width) is int and type(height) is int, "dimensions must be integers")
    require(width % 2 == 0 and height % 2 == 0, "pose sheet dimensions must be even")
    cell_w, cell_h = width // 2, height // 2
    require(cell_w >= MIN_CELL and cell_h >= MIN_CELL,
            f"each pose cell must be at least {MIN_CELL}x{MIN_CELL}")
    return (
        (0, 0, cell_w, cell_h),
        (cell_w, 0, cell_w, cell_h),
        (0, cell_h, cell_w, cell_h),
        (cell_w, cell_h, cell_w, cell_h),
    )


def run_json(args: list[str], label: str) -> dict[str, Any]:
    result = subprocess.run(args, check=False, text=True, capture_output=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()[-2000:]
        raise ValidationError(f"{label} failed: {detail}")
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ValidationError(f"{label} returned invalid JSON") from error
    require(isinstance(value, dict), f"{label} returned an unexpected result")
    return value


def probe_dimensions(path: Path) -> tuple[int, int]:
    require(shutil.which("ffprobe") is not None, "ffprobe is not available on PATH")
    value = run_json([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "json", str(path)
    ], "ffprobe")
    streams = value.get("streams", [])
    require(isinstance(streams, list) and streams, "source image has no video/image stream")
    width, height = streams[0].get("width"), streams[0].get("height")
    require(type(width) is int and type(height) is int, "could not determine source dimensions")
    return width, height


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def slice_sheet(manifest: Path, output_dir: Path, *, force: bool = False) -> dict[str, Any]:
    require(shutil.which("ffmpeg") is not None, "ffmpeg is not available on PATH")
    source, names = load_manifest(manifest)
    width, height = probe_dimensions(source)
    boxes = crop_boxes(width, height)
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    planned = [output_dir / f"{name}.png" for name in names]
    if not force:
        existing = [p.name for p in planned if p.exists()]
        require(not existing, f"output files already exist: {', '.join(existing)}")

    results = []
    for name, (x, y, w, h), out in zip(names, boxes, planned):
        command = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-y" if force else "-n", "-i", str(source),
            "-vf", f"crop={w}:{h}:{x}:{y}", "-frames:v", "1", str(out)
        ]
        process = subprocess.run(command, check=False, text=True, capture_output=True)
        if process.returncode != 0:
            detail = (process.stderr or process.stdout).strip()[-2000:]
            raise ValidationError(f"ffmpeg crop failed for {name}: {detail}")
        require(out.is_file() and out.stat().st_size > 0, f"missing crop output for {name}")
        results.append({
            "pose": name,
            "row": 0 if y == 0 else 1,
            "column": 0 if x == 0 else 1,
            "crop": {"x": x, "y": y, "width": w, "height": h},
            "path": str(out),
            "bytes": out.stat().st_size,
            "sha256": sha256(out),
        })

    return {
        "schema": 1,
        "source": str(source),
        "source_width": width,
        "source_height": height,
        "layout": {"rows": 2, "columns": 2, "order": "row-major"},
        "poses": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        result = slice_sheet(args.manifest, args.output_dir, force=args.force)
        print(json.dumps(result, indent=2))
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        parser.exit(2, f"pose-sheet: {error}\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Render a small, deterministic GIF from a GF animation specification."""

from __future__ import annotations

import argparse
import base64
import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw


def connected(cells: list[dict]) -> bool:
    points = {(int(cell["x"]), int(cell["y"])) for cell in cells}
    if len(points) != len(cells) or len(points) < 2:
        return False

    seen = {next(iter(points))}
    queue = deque(seen)
    while queue:
        x, y = queue.popleft()
        for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if neighbor in points and neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return seen == points


def render_frame(spec: dict, frame: dict) -> Image.Image:
    width, height = map(int, spec.get("canvas", [320, 320]))
    size = int(spec.get("cell_size", 48))
    background = spec.get("background", "#fffaf0")
    cells = frame.get("cells", [])

    if not connected(cells):
        raise ValueError("Every frame must contain one edge-connected animal of at least two cells")

    image = Image.new("RGBA", (width, height), background)
    draw = ImageDraw.Draw(image)
    ox, oy = map(int, frame.get("offset", [0, 0]))

    for cell in cells:
        x = ox + int(cell["x"]) * size
        y = oy + int(cell["y"]) * size
        box = (x, y, x + size - 1, y + size - 1)
        outline_width = max(2, size // 16)
        draw.rectangle(box, fill=cell.get("color", "#ffcc33"), outline="#181818", width=outline_width)

        if cell.get("face", True):
            eye = max(2, size // 14)
            eye_y = y + size * 2 // 5
            for eye_x in (x + size // 3, x + size * 2 // 3):
                draw.rectangle((eye_x - eye, eye_y - eye, eye_x + eye, eye_y + eye), fill="#181818")
            mouth_y = y + size * 2 // 3
            draw.arc(
                (x + size // 3, mouth_y - size // 8, x + size * 2 // 3, mouth_y + size // 8),
                0,
                180,
                fill="#181818",
                width=max(2, size // 18),
            )
    return image


def render(source: Path, destination: Path) -> None:
    spec = json.loads(source.read_text(encoding="utf-8"))
    frames = [render_frame(spec, frame) for frame in spec["frames"]]
    if not frames:
        raise ValueError("The animal needs at least one frame")

    destination.parent.mkdir(parents=True, exist_ok=True)
    preview = destination.with_suffix(".png")
    frames[0].save(preview, format="PNG", optimize=True)
    frames[0].save(
        destination,
        save_all=True,
        append_images=frames[1:],
        duration=int(spec.get("duration_ms", 220)),
        loop=int(spec.get("loop", 0)),
        disposal=2,
        optimize=True,
    )

    for artifact in (destination, preview):
        sidecar = artifact.with_suffix(f"{artifact.suffix}.b64")
        payload = base64.b64encode(artifact.read_bytes()).decode("ascii")
        sidecar.write_text(f"{payload}\n", encoding="ascii")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    render(args.source, args.destination)


if __name__ == "__main__":
    main()

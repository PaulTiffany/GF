#!/usr/bin/env python3
"""Render and validate a ChatGPT Pets v1 sprite sheet from a GF specification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

SHEET_SIZE = (1536, 1872)
CELL_SIZE = (192, 208)
FRAMES_PER_ROW = (6, 8, 8, 4, 5, 8, 6, 6, 6)
BLOCK_SIZE = 32


def draw_animal(spec_frame: dict) -> Image.Image:
    cells = spec_frame["cells"]
    points = [(int(cell["x"]), int(cell["y"])) for cell in cells]
    min_x = min(x for x, _ in points)
    max_x = max(x for x, _ in points)
    min_y = min(y for _, y in points)
    max_y = max(y for _, y in points)
    animal_width = (max_x - min_x + 1) * BLOCK_SIZE
    animal_height = (max_y - min_y + 1) * BLOCK_SIZE
    origin_x = (CELL_SIZE[0] - animal_width) // 2
    origin_y = (CELL_SIZE[1] - animal_height) // 2

    image = Image.new("RGBA", CELL_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    for cell in cells:
        x = origin_x + (int(cell["x"]) - min_x) * BLOCK_SIZE
        y = origin_y + (int(cell["y"]) - min_y) * BLOCK_SIZE
        box = (x, y, x + BLOCK_SIZE - 1, y + BLOCK_SIZE - 1)
        draw.rectangle(box, fill=cell.get("color", "#ffcc33"), outline="#181818", width=2)
        if cell.get("face", True):
            eye_y = y + 13
            draw.rectangle((x + 9, eye_y, x + 11, eye_y + 2), fill="#181818")
            draw.rectangle((x + 21, eye_y, x + 23, eye_y + 2), fill="#181818")
            draw.arc((x + 11, y + 16, x + 21, y + 24), 0, 180, fill="#181818", width=2)
    return image


def validate_sheet(sheet: Image.Image) -> None:
    if sheet.size != SHEET_SIZE:
        raise ValueError(f"Expected {SHEET_SIZE}, got {sheet.size}")
    if sheet.mode != "RGBA":
        raise ValueError("Pet sheet must be RGBA")

    alpha = sheet.getchannel("A")
    for row, used_count in enumerate(FRAMES_PER_ROW):
        for column in range(8):
            box = (
                column * CELL_SIZE[0],
                row * CELL_SIZE[1],
                (column + 1) * CELL_SIZE[0],
                (row + 1) * CELL_SIZE[1],
            )
            occupied = alpha.crop(box).getbbox() is not None
            if column < used_count and not occupied:
                raise ValueError(f"Missing artwork at row {row}, frame {column}")
            if column >= used_count and occupied:
                raise ValueError(f"Unexpected artwork at row {row}, frame {column}")


def render_pet(source: Path, destination: Path) -> None:
    spec = json.loads(source.read_text(encoding="utf-8"))
    frames = spec.get("frames", [])
    if not frames:
        raise ValueError("The animal needs at least one frame")

    sheet = Image.new("RGBA", SHEET_SIZE, (0, 0, 0, 0))
    for row, count in enumerate(FRAMES_PER_ROW):
        for column in range(count):
            source_frame = frames[(row + column) % len(frames)]
            sprite = draw_animal(source_frame)
            sheet.alpha_composite(sprite, (column * CELL_SIZE[0], row * CELL_SIZE[1]))

    validate_sheet(sheet)
    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination, format="PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    render_pet(args.source, args.destination)


if __name__ == "__main__":
    main()

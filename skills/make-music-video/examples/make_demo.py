#!/usr/bin/env python3
"""Create a zero-cost four-second fixture for the make-music-video skill."""

from __future__ import annotations

import argparse
import json
import math
import struct
import wave
from pathlib import Path


def write_wav(path: Path, seconds: int = 4, rate: int = 44_100) -> None:
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        for index in range(rate * seconds):
            sample = int(6000 * math.sin(2 * math.pi * 220 * index / rate))
            handle.writeframesraw(struct.pack("<h", sample))


def write_ppm(path: Path, rgb: tuple[int, int, int], width: int = 640, height: int = 360) -> None:
    path.write_bytes(f"P6\n{width} {height}\n255\n".encode("ascii") + bytes(rgb) * width * height)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    root = args.directory.resolve()
    media = root / "media"
    media.mkdir(parents=True, exist_ok=True)
    write_wav(media / "song.wav")
    write_ppm(media / "opening.ppm", (30, 80, 180))
    write_ppm(media / "closing.ppm", (180, 60, 80))
    project = {
        "schema": 1,
        "title": "GF music-video demo",
        "audio": "media/song.wav",
        "width": 640,
        "height": 360,
        "fps": 30,
        "shots": [
            {"asset": "media/opening.ppm", "kind": "image", "duration": 2.0},
            {"asset": "media/closing.ppm", "kind": "image", "duration": 2.0}
        ]
    }
    manifest = root / "music-video.json"
    manifest.write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")
    print(manifest)


if __name__ == "__main__":
    main()

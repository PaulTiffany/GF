#!/usr/bin/env python3
"""Verify and stage an existing GIF for chat attachment; optionally build a player."""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import io
import json
import re
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from PIL import Image

MAX_BYTES = 20 * 1024 * 1024
MAX_PIXELS = 16_000_000  # Sum of decoded frame areas; a small-animation helper.
MAX_PLAYER_BYTES = 1024 * 1024


def read_gif(source: Path, member: str | None) -> bytes:
    if member is None:
        if source.stat().st_size > MAX_BYTES:
            raise ValueError("GIF exceeds the helper's 20 MiB limit")
        return source.read_bytes()
    with ZipFile(source) as archive:
        matches = [entry for entry in archive.infolist() if entry.filename == member]
        if len(matches) != 1 or matches[0].is_dir():
            raise ValueError("Name exactly one GIF member in the ZIP")
        if matches[0].file_size > MAX_BYTES:
            raise ValueError("GIF exceeds the helper's 20 MiB limit")
        # Read the member without extracting its path into the filesystem.
        return archive.read(matches[0])


def output_path(path: Path, suffix: str) -> Path:
    path = path.resolve()
    if path.suffix.lower() != suffix or not re.fullmatch(r"[A-Za-z0-9_./:-]+", str(path)):
        raise ValueError(f"Use an ASCII {suffix} output path without spaces or Markdown punctuation")
    return path


def inspect_gif(data: bytes, player: bool) -> tuple[dict, list[dict]]:
    frames = []
    durations = []
    with Image.open(io.BytesIO(data)) as image:
        if image.format != "GIF":
            raise ValueError("Input must be a GIF")
        count = image.n_frames
        if count < 2:
            raise ValueError("Input must contain at least two GIF frames")
        if image.width * image.height * count > MAX_PIXELS:
            raise ValueError("GIF exceeds the helper's 16 million decoded-pixel limit")
        facts = {"width": image.width, "height": image.height, "frames": count,
                 "loop": image.info.get("loop")}
        for index in range(count):
            image.seek(index)
            image.load()
            delay = int(image.info.get("duration", 0))
            durations.append(delay)
            if player:
                buffer = io.BytesIO()
                image.convert("RGBA").save(buffer, format="PNG", optimize=True)
                frames.append({"src": "data:image/png;base64," +
                               base64.b64encode(buffer.getvalue()).decode("ascii"),
                               "ms": max(20, delay) if delay > 0 else 100})
    return {**facts, "durations_ms": durations}, frames


def prepare(source: Path, output: Path, *, member: str | None = None,
            sha256: str | None = None, alt: str = "Animated GIF",
            player: Path | None = None) -> dict:
    data = read_gif(source, member)
    digest = hashlib.sha256(data).hexdigest()
    if sha256 is not None and digest != sha256.lower().removeprefix("sha256:"):
        raise ValueError("GIF SHA-256 does not match the expected digest")
    facts, frames = inspect_gif(data, player is not None)
    output = output_path(output, ".gif")
    pending = {output: data}
    alt = " ".join(alt.split())
    if player is not None:
        player = output_path(player, ".html")
        template = Path(__file__).resolve().parents[1] / "assets" / "player.html"
        root_id = "gf-" + hashlib.sha256(str(player).encode()).hexdigest()[:12]
        fragment = template.read_text(encoding="utf-8")
        values = {"__ROOT__": root_id, "__ALT__": html.escape(alt, quote=True),
                  "__FIRST_FRAME__": frames[0]["src"],
                  "__PAYLOAD__": json.dumps({"frames": frames, "loop": facts["loop"]})}
        fragment = re.sub(r"__(?:ROOT|ALT|FIRST_FRAME|PAYLOAD)__",
                          lambda match: values[match.group()], fragment)
        encoded = fragment.encode("utf-8")
        if len(encoded) > MAX_PLAYER_BYTES:
            raise ValueError("Player exceeds 1 MiB; use the GIF attachment without --player")
        pending[player] = encoded
    # Check every destination before writing either file; never replace different content.
    for path, content in pending.items():
        if path.exists() and path.read_bytes() != content:
            raise ValueError(f"Output already contains different content: {path}")
    for path, content in pending.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            with path.open("xb") as target:
                target.write(content)
    safe_alt = alt.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
    result = {"path": str(output), "mime": "image/gif", "bytes": len(data),
              "sha256": digest, **facts,
              "markdown_image": f"![{safe_alt}](sandbox:{output.as_posix()})"}
    if player is not None:
        result["player_path"] = str(player)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Local GIF or ZIP")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--member", help="Exact GIF member name when source is a ZIP")
    parser.add_argument("--sha256", help="Expected digest of GIF bytes, not the ZIP")
    parser.add_argument("--alt", default="Animated GIF")
    parser.add_argument("--player", type=Path, help="Optional HTML visualization fragment")
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(**vars(args)), indent=2))
    except (OSError, ValueError, BadZipFile, EOFError, Image.DecompressionBombError) as error:
        parser.exit(1, f"prepare_gif: {error}\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validate a lyric-overlay manifest and emit deterministic Manim source."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
BEHAVIORS = {"fade_hold", "drift_up", "pulse", "orbit", "rain", "scatter"}
MAX_METADATA = 128 * 1024
MAX_EVENTS = 120
MAX_TEXT = 160
MAX_DURATION = 20 * 60


class ValidationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def number(value: Any, label: str, minimum: float, maximum: float) -> float:
    require(type(value) in (int, float), f"{label} must be numeric")
    result = float(value)
    require(minimum <= result <= maximum, f"{label} must be between {minimum} and {maximum}")
    return result


def load_manifest(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    require(len(data) <= MAX_METADATA, "lyric overlay manifest exceeds 128 KiB")
    value = json.loads(data)
    require(isinstance(value, dict), "lyric overlay manifest must be an object")
    required = {"schema", "id", "duration", "canvas", "events"}
    require(set(value) == required, f"fields must be exactly: {', '.join(sorted(required))}")
    require(value["schema"] == 1 and type(value["schema"]) is int, "unsupported lyric overlay schema")
    require(isinstance(value["id"], str) and ID_RE.fullmatch(value["id"]) is not None,
            f"id must match {ID_RE.pattern}")
    duration = number(value["duration"], "duration", 0.1, MAX_DURATION)
    canvas = value["canvas"]
    require(isinstance(canvas, dict) and set(canvas) == {"width", "height", "fps"},
            "canvas must contain exactly width, height, fps")
    width = int(number(canvas["width"], "canvas.width", 256, 3840))
    height = int(number(canvas["height"], "canvas.height", 256, 3840))
    fps = int(number(canvas["fps"], "canvas.fps", 1, 60))
    require(width % 2 == 0 and height % 2 == 0, "canvas dimensions must be even")

    events = value["events"]
    require(isinstance(events, list) and events, "events must be a nonempty list")
    require(len(events) <= MAX_EVENTS, f"events exceeds {MAX_EVENTS}")
    parsed = []
    for index, event in enumerate(events):
        label = f"events[{index}]"
        required_event = {"start", "end", "text", "behavior", "anchor", "scale", "rotation_degrees"}
        require(isinstance(event, dict) and set(event) == required_event,
                f"{label} has invalid fields")
        start = number(event["start"], f"{label}.start", 0, duration)
        end = number(event["end"], f"{label}.end", 0, duration)
        require(end > start, f"{label}.end must be after start")
        text = event["text"]
        require(isinstance(text, str) and text.strip(), f"{label}.text must be nonempty")
        require(len(text) <= MAX_TEXT, f"{label}.text exceeds {MAX_TEXT} characters")
        behavior = event["behavior"]
        require(behavior in BEHAVIORS, f"{label}.behavior must be one of: {', '.join(sorted(BEHAVIORS))}")
        anchor = event["anchor"]
        require(isinstance(anchor, dict) and set(anchor) == {"x", "y"}, f"{label}.anchor must contain x,y")
        x = number(anchor["x"], f"{label}.anchor.x", 0, 1)
        y = number(anchor["y"], f"{label}.anchor.y", 0, 1)
        scale = number(event["scale"], f"{label}.scale", 0.1, 4.0)
        rotation = number(event["rotation_degrees"], f"{label}.rotation_degrees", -180, 180)
        parsed.append({
            "start": start, "end": end, "text": text, "behavior": behavior,
            "anchor": {"x": x, "y": y}, "scale": scale,
            "rotation_degrees": rotation,
        })
    return {
        "schema": 1,
        "id": value["id"],
        "duration": duration,
        "canvas": {"width": width, "height": height, "fps": fps},
        "events": parsed,
    }


def py_string(value: str) -> str:
    return repr(value)


def compile_source(manifest: dict[str, Any]) -> str:
    payload = json.dumps(manifest, separators=(",", ":"))
    return f'''from manim import *
import json
import math

MANIFEST = json.loads({payload!r})

class LyricOverlay(Scene):
    def construct(self):
        self.camera.background_color = None
        frame_w = config.frame_width
        frame_h = config.frame_height

        def point(anchor):
            x = (anchor["x"] - 0.5) * frame_w
            y = (0.5 - anchor["y"]) * frame_h
            return np.array([x, y, 0.0])

        tracks = []
        total = MANIFEST["duration"]

        for event in MANIFEST["events"]:
            text = Text(event["text"])
            text.scale(event["scale"])
            text.rotate(math.radians(event["rotation_degrees"]))
            target = point(event["anchor"])
            text.move_to(target)
            start = event["start"]
            end = event["end"]
            visible = max(0.05, end - start)
            fade = min(0.35, visible / 4)
            behavior = event["behavior"]

            if behavior == "fade_hold":
                action = Succession(
                    Wait(start),
                    FadeIn(text, run_time=fade),
                    Wait(max(0, visible - 2 * fade)),
                    FadeOut(text, run_time=fade),
                )
            elif behavior == "drift_up":
                text.shift(DOWN * 0.25)
                action = Succession(
                    Wait(start),
                    FadeIn(text, shift=UP * 0.10, run_time=fade),
                    text.animate.shift(UP * 0.5).set_run_time(max(0.05, visible - fade)),
                    FadeOut(text, run_time=fade),
                )
            elif behavior == "pulse":
                action = Succession(
                    Wait(start),
                    FadeIn(text, run_time=fade),
                    text.animate.scale(1.12).set_run_time(max(0.05, visible * 0.35)),
                    text.animate.scale(1/1.12).set_run_time(max(0.05, visible * 0.35)),
                    FadeOut(text, run_time=fade),
                )
            elif behavior == "orbit":
                path = Circle(radius=0.35).move_to(target)
                action = Succession(
                    Wait(start),
                    FadeIn(text, run_time=fade),
                    MoveAlongPath(text, path, run_time=max(0.05, visible - 2 * fade)),
                    FadeOut(text, run_time=fade),
                )
            elif behavior == "rain":
                text.shift(UP * 1.6)
                action = Succession(
                    Wait(start),
                    FadeIn(text, run_time=fade),
                    text.animate.shift(DOWN * 3.2).set_run_time(max(0.05, visible - 2 * fade)),
                    FadeOut(text, run_time=fade),
                )
            else:  # scatter
                words = VGroup(*[Text(word) for word in event["text"].split()])
                words.arrange(RIGHT, buff=0.15).move_to(target)
                words.scale(event["scale"])
                for i, word in enumerate(words):
                    angle = (i / max(1, len(words))) * TAU
                    word.shift(np.array([math.cos(angle), math.sin(angle), 0]) * 0.45)
                action = Succession(
                    Wait(start),
                    AnimationGroup(*[word.animate.move_to(target + RIGHT * ((i-(len(words)-1)/2)*0.55))
                                     for i, word in enumerate(words)], lag_ratio=0.05,
                                   run_time=max(0.05, visible - fade)),
                    FadeOut(words, run_time=fade),
                )
                text = words

            tracks.append(action)

        self.play(AnimationGroup(*tracks, lag_ratio=0), run_time=total)
'''

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        manifest = load_manifest(args.manifest)
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(compile_source(manifest), encoding="utf-8")
        print(json.dumps({
            "id": manifest["id"],
            "duration": manifest["duration"],
            "event_count": len(manifest["events"]),
            "output": str(output),
            "requires_runtime": "manim"
        }, indent=2))
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        parser.exit(2, f"lyric-overlay: {error}\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validate and render a bounded music-video timeline with FFmpeg."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MAX_METADATA = 96 * 1024
MAX_SHOTS = 300
MAX_TIMELINE_SECONDS = 20 * 60
MAX_SHOT_SECONDS = 120.0
MAX_INPUT_BYTES = 2 * 1024 * 1024 * 1024
MAX_TOTAL_INPUT_BYTES = 10 * 1024 * 1024 * 1024
MAX_DIMENSION = 3840
MAX_PIXELS = 3840 * 2160
MOTIONS = {"static", "push_in", "pull_out", "pan_left", "pan_right"}
TRANSITIONS = {"cut", "fade_black"}


class ValidationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        require(key not in value, f"duplicate JSON key: {key}")
        value[key] = item
    return value


def read_json(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    require(len(data) <= MAX_METADATA, "project manifest exceeds 96 KiB")
    value = json.loads(data, object_pairs_hook=unique_object)
    require(isinstance(value, dict), "project manifest must be a JSON object")
    return value


def number(value: Any, label: str, *, minimum: float, maximum: float) -> float:
    require(type(value) in (int, float), f"{label} must be a number")
    result = float(value)
    require(minimum <= result <= maximum, f"{label} must be between {minimum} and {maximum}")
    return result


def integer(value: Any, label: str, *, minimum: int, maximum: int) -> int:
    require(type(value) is int, f"{label} must be an integer")
    require(minimum <= value <= maximum, f"{label} must be between {minimum} and {maximum}")
    return value


def safe_input(root: Path, name: Any, label: str) -> Path:
    require(isinstance(name, str) and name.strip(), f"{label} must be a nonempty relative path")
    raw = Path(name)
    require(not raw.is_absolute() and ".." not in raw.parts, f"{label} must stay inside the project directory")
    target = (root / raw).resolve()
    require(target.is_relative_to(root.resolve()), f"{label} escapes the project directory")
    require(target.is_file(), f"missing input file: {name}")
    size = target.stat().st_size
    require(size <= MAX_INPUT_BYTES, f"input exceeds 2 GiB: {name}")
    return target


@dataclass(frozen=True)
class Shot:
    asset: Path
    kind: str
    duration: float
    source_start: float
    motion: str
    transition: str


@dataclass(frozen=True)
class Project:
    manifest: Path
    schema: int
    title: str
    audio: Path
    width: int
    height: int
    fps: int
    poster_time: float
    shots: tuple[Shot, ...]

    @property
    def duration(self) -> float:
        return sum(shot.duration for shot in self.shots)


def load_project(manifest: Path) -> Project:
    manifest = manifest.resolve()
    require(manifest.is_file(), f"missing project manifest: {manifest}")
    value = read_json(manifest)
    schema = value.get("schema")
    require(type(schema) is int and schema in {1, 2}, "unsupported project schema")
    required = {"schema", "title", "audio", "width", "height", "fps", "shots"}
    optional = {"poster_time"} if schema == 2 else set()
    require(required <= set(value) and set(value) <= required | optional,
            f"project fields must be: {', '.join(sorted(required | optional))}")
    require(isinstance(value["title"], str) and value["title"].strip(), "title must be a nonempty string")

    width = integer(value["width"], "width", minimum=256, maximum=MAX_DIMENSION)
    height = integer(value["height"], "height", minimum=256, maximum=MAX_DIMENSION)
    require(width % 2 == 0 and height % 2 == 0, "width and height must be even for yuv420p output")
    require(width * height <= MAX_PIXELS, "frame size exceeds 4K-class pixel bound")
    fps = integer(value["fps"], "fps", minimum=1, maximum=60)

    root = manifest.parent
    audio = safe_input(root, value["audio"], "audio")
    shots_value = value["shots"]
    require(isinstance(shots_value, list) and shots_value, "shots must be a nonempty list")
    require(len(shots_value) <= MAX_SHOTS, f"shots exceeds {MAX_SHOTS}")

    shots: list[Shot] = []
    total_bytes = audio.stat().st_size
    for index, item in enumerate(shots_value):
        label = f"shots[{index}]"
        require(isinstance(item, dict), f"{label} must be an object")
        require(item.get("kind") in {"image", "video"}, f"{label}.kind must be image or video")
        kind = item["kind"]
        base_allowed = {"asset", "kind", "duration"} | ({"source_start"} if kind == "video" else set())
        v2_allowed = {"motion", "transition"} if schema == 2 else set()
        allowed = base_allowed | v2_allowed
        require(set(item) <= allowed and {"asset", "kind", "duration"} <= set(item),
                f"{label} has invalid or missing fields")
        if kind == "image":
            require("source_start" not in item, f"{label}.source_start is only valid for video")
        duration = number(item["duration"], f"{label}.duration", minimum=0.10, maximum=MAX_SHOT_SECONDS)
        source_start = number(item.get("source_start", 0.0), f"{label}.source_start", minimum=0.0, maximum=MAX_TIMELINE_SECONDS)
        motion = item.get("motion", "static" if kind == "image" else "native")
        if kind == "image":
            require(motion in MOTIONS, f"{label}.motion must be one of: {', '.join(sorted(MOTIONS))}")
        else:
            require(motion == "native", f"{label}.motion is only available for images")
        transition = item.get("transition", "cut")
        require(transition in TRANSITIONS, f"{label}.transition must be one of: {', '.join(sorted(TRANSITIONS))}")
        asset = safe_input(root, item["asset"], f"{label}.asset")
        total_bytes += asset.stat().st_size
        shots.append(Shot(asset=asset, kind=kind, duration=duration, source_start=source_start,
                          motion=motion, transition=transition))

    require(total_bytes <= MAX_TOTAL_INPUT_BYTES, "total local input size exceeds 10 GiB")
    duration = sum(shot.duration for shot in shots)
    require(duration <= MAX_TIMELINE_SECONDS, "timeline exceeds 20 minutes")
    poster_time = number(value.get("poster_time", min(1.0, duration / 2)), "poster_time",
                         minimum=0.0, maximum=duration)
    return Project(manifest, schema, value["title"].strip(), audio, width, height, fps, poster_time, tuple(shots))


def q(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def still_motion_filter(shot: Shot, project: Project) -> str:
    base = (f"scale={project.width}:{project.height}:force_original_aspect_ratio=increase,"
            f"crop={project.width}:{project.height}")
    if shot.motion == "static":
        return f"{base},fps={project.fps}"
    frames = max(1, round(shot.duration * project.fps))
    last = max(1, frames - 1)
    if shot.motion == "push_in":
        z = "min(zoom+0.0012,1.12)"
        x = "iw/2-(iw/zoom/2)"
    elif shot.motion == "pull_out":
        z = "if(eq(on,0),1.12,max(zoom-0.0012,1.0))"
        x = "iw/2-(iw/zoom/2)"
    elif shot.motion == "pan_left":
        z = "1.08"
        x = f"(iw-iw/zoom)*(1-on/{last})"
    else:  # pan_right
        z = "1.08"
        x = f"(iw-iw/zoom)*on/{last}"
    y = "ih/2-(ih/zoom/2)"
    return f"{base},zoompan=z='{z}':x='{x}':y='{y}':d=1:s={project.width}x{project.height}:fps={project.fps}"


def visual_filter(index: int, shot: Shot, project: Project) -> str:
    if shot.kind == "image":
        chain = still_motion_filter(shot, project)
    else:
        chain = (f"scale={project.width}:{project.height}:force_original_aspect_ratio=increase,"
                 f"crop={project.width}:{project.height},fps={project.fps}")
    fade = min(0.45, shot.duration / 4)
    if index > 0 and project.shots[index - 1].transition == "fade_black":
        chain += f",fade=t=in:st=0:d={q(fade)}"
    if shot.transition == "fade_black":
        chain += f",fade=t=out:st={q(max(0.0, shot.duration - fade))}:d={q(fade)}"
    chain += f",setsar=1,format=yuv420p,trim=duration={q(shot.duration)},setpts=PTS-STARTPTS"
    return chain


def poster_path_for(output: Path) -> Path:
    return output.with_name(f"{output.stem}.poster.jpg")


def ffmpeg_argv(project: Project, output: Path, *, force: bool = False) -> list[str]:
    args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y" if force else "-n", "-i", str(project.audio)]
    for shot in project.shots:
        if shot.kind == "image":
            args.extend(["-framerate", str(project.fps), "-loop", "1", "-t", q(shot.duration), "-i", str(shot.asset)])
        else:
            if shot.source_start:
                args.extend(["-ss", q(shot.source_start)])
            args.extend(["-t", q(shot.duration), "-i", str(shot.asset)])

    filters: list[str] = []
    labels: list[str] = []
    for zero_index, shot in enumerate(project.shots):
        input_index = zero_index + 1
        label = f"v{zero_index}"
        filters.append(f"[{input_index}:v:0]{visual_filter(zero_index, shot, project)}[{label}]")
        labels.append(f"[{label}]")
    filters.append(f"{''.join(labels)}concat=n={len(labels)}:v=1:a=0[vout]")

    args.extend([
        "-filter_complex", ";".join(filters),
        "-map", "[vout]",
        "-map", "0:a:0",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", q(project.duration),
        "-movflags", "+faststart",
        str(output),
    ])
    return args


def poster_argv(project: Project, output: Path, poster: Path, *, force: bool = False) -> list[str]:
    return [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y" if force else "-n",
        "-ss", q(project.poster_time), "-i", str(output), "-frames:v", "1", "-q:v", "2", str(poster)
    ]


def run_json_command(args: list[str], label: str) -> dict[str, Any]:
    try:
        result = subprocess.run(args, check=False, text=True, capture_output=True)
    except OSError as error:
        raise ValidationError(f"cannot run {label}: {error}") from error
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()[-4000:]
        raise ValidationError(f"{label} failed: {detail}")
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ValidationError(f"{label} returned invalid JSON") from error
    require(isinstance(value, dict), f"{label} returned an unexpected result")
    return value


def ffprobe(path: Path) -> dict[str, Any]:
    return run_json_command([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=index,codec_type,width,height,duration",
        "-of", "json", str(path)
    ], "ffprobe")


def duration_from_probe(value: dict[str, Any], label: str) -> float:
    raw = value.get("format", {}).get("duration")
    try:
        duration = float(raw)
    except (TypeError, ValueError) as error:
        raise ValidationError(f"could not determine duration for {label}") from error
    require(duration >= 0, f"invalid duration for {label}")
    return duration


def preflight_media(project: Project) -> None:
    require(shutil.which("ffmpeg") is not None, "ffmpeg is not available on PATH")
    require(shutil.which("ffprobe") is not None, "ffprobe is not available on PATH")
    tolerance = max(0.25, 2 / project.fps)
    audio_duration = duration_from_probe(ffprobe(project.audio), "audio")
    require(abs(audio_duration - project.duration) <= tolerance,
            f"audio is {audio_duration:.3f}s but timeline is {project.duration:.3f}s; align them before rendering")
    for index, shot in enumerate(project.shots):
        if shot.kind != "video":
            continue
        clip_duration = duration_from_probe(ffprobe(shot.asset), f"shots[{index}]")
        needed = shot.source_start + shot.duration
        require(clip_duration + tolerance >= needed,
                f"shots[{index}] needs {needed:.3f}s of source but clip is {clip_duration:.3f}s")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_output(project: Project, output: Path) -> dict[str, Any]:
    require(output.is_file() and output.stat().st_size > 0, "render did not create a nonempty output file")
    probe = ffprobe(output)
    streams = probe.get("streams", [])
    require(isinstance(streams, list), "ffprobe output has no streams list")
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    require(video is not None, "rendered file has no video stream")
    require(audio is not None, "rendered file has no audio stream")
    require(video.get("width") == project.width and video.get("height") == project.height,
            "rendered dimensions do not match the project")
    duration = duration_from_probe(probe, "rendered output")
    tolerance = max(0.25, 2 / project.fps)
    require(abs(duration - project.duration) <= tolerance,
            f"rendered duration {duration:.3f}s does not match timeline {project.duration:.3f}s")
    return {"duration_seconds": duration, "width": video.get("width"), "height": video.get("height")}


def result_for(project: Project, output: Path, *, include_command: bool, force: bool = False) -> dict[str, Any]:
    poster = poster_path_for(output.resolve())
    result: dict[str, Any] = {
        "title": project.title,
        "manifest": str(project.manifest),
        "schema": project.schema,
        "audio": str(project.audio),
        "shot_count": len(project.shots),
        "duration_seconds": project.duration,
        "width": project.width,
        "height": project.height,
        "fps": project.fps,
        "output": str(output.resolve()),
        "poster": str(poster),
        "poster_time": project.poster_time,
    }
    if include_command:
        result["ffmpeg_argv"] = ffmpeg_argv(project, output.resolve(), force=force)
        result["poster_argv"] = poster_argv(project, output.resolve(), poster, force=force)
    return result


def run_process(command: list[str], label: str) -> None:
    try:
        process = subprocess.run(command, check=False, text=True, capture_output=True)
    except OSError as error:
        raise ValidationError(f"cannot run {label}: {error}") from error
    if process.returncode != 0:
        detail = (process.stderr or process.stdout).strip()[-4000:]
        raise ValidationError(f"{label} failed: {detail}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "render"):
        cmd = commands.add_parser(name)
        cmd.add_argument("project", type=Path)
        cmd.add_argument("--output", type=Path, required=True)
        if name == "render":
            cmd.add_argument("--force", action="store_true", help="Allow replacing existing video/poster outputs")
    args = parser.parse_args()

    try:
        project = load_project(args.project)
        output = args.output.resolve()
        poster = poster_path_for(output)
        if args.command == "plan":
            print(json.dumps(result_for(project, output, include_command=True), indent=2))
            return

        if (output.exists() or poster.exists()) and not args.force:
            raise ValidationError("output or poster already exists; pass --force only when replacement is intended")
        output.parent.mkdir(parents=True, exist_ok=True)
        preflight_media(project)
        run_process(ffmpeg_argv(project, output, force=args.force), "ffmpeg render")
        verified = verify_output(project, output)
        run_process(poster_argv(project, output, poster, force=args.force), "poster extraction")
        require(poster.is_file() and poster.stat().st_size > 0, "poster extraction did not create a nonempty image")
        result = result_for(project, output, include_command=False)
        result.update({
            "bytes": output.stat().st_size,
            "sha256": sha256(output),
            "poster_bytes": poster.stat().st_size,
            "poster_sha256": sha256(poster),
            "verified": verified,
        })
        print(json.dumps(result, indent=2))
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        parser.exit(2, f"music-video: {error}\n")


if __name__ == "__main__":
    main()

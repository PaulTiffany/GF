---
name: make-music-video
description: Turn a finished song and a set of local visual assets into a reproducible music video. Use when directing an AI-assisted music video, Claude Pop-style clip sequence, lyric/performance/ambient video, or when an existing creative workflow needs a deterministic shot timeline and verified MP4 export. The creative generation stage is provider-neutral; the bundled helper validates and renders local assets with FFmpeg.
---

# Make a music video

Make the video as a **creative production with a mechanical finish**, not as one giant prompt.
The assistant can direct, generate, select, revise, and organize shots using whatever media tools the host actually provides. The bundled helper only owns the final bounded move: validate a local shot manifest, assemble the accepted shots over one finished audio track, and verify the MP4.

This separation is what makes the skill portable. ChatGPT Work can use its files, browser, connectors, and media tools when available. A normal tool-equipped chat, Codex/CLI session, or another skill host can use equivalent tools. Loading this skill does not grant access to Suno, Claude, a video generator, publishing accounts, or paid inference.

## Target

Land one music video whose creative choices can be inspected and whose final timeline can be reproduced from local source assets.

Keep these outcomes separate:

1. **Song ready:** the intended finished audio file exists locally.
2. **Creative plan ready:** aspect ratio, visual grammar, section map, and recurring motifs are explicit.
3. **Shots accepted:** each timeline asset has been generated, found, or filmed and reviewed.
4. **Timeline valid:** `music-video.json` passes the helper's bounded checks.
5. **Render verified:** the output contains audio + video at the requested dimensions and duration.
6. **Audience result observed:** a person actually watched the intended video in the target client/platform.

A successful encode does not prove the video is artistically good, and a good preview does not prove a published upload is correct.

## Equip

- One finished local audio file. If music generation is part of the user's request, finish or obtain the song before final assembly.
- Local still images and/or video clips that the user is authorized to use.
- Python 3.10+.
- FFmpeg and FFprobe on `PATH` for rendering.
- A writable workspace.
- Optional host tools for image generation, video generation, web/connector retrieval, audio analysis, transcription, or publishing.

Treat paid model calls, remote uploads, account changes, and publication as separate effects. Do not acquire credentials, buy generation credits, or publish merely because the render skill is loaded.

## Direct before generating

Choose a visual grammar before producing dozens of clips. If the user has already chosen one, use it instead of reopening the decision.

Common lanes include:

- **Claude Pop / internet-native AI pop:** short high-concept generated shots, recurring characters or visual jokes, aggressive hook recognition, deliberate artificiality when it serves the song.
- **Narrative:** recurring subjects, locations, props, and causal progression across sections.
- **Performance:** singer/band/performance footage with cutaways and section-aware pacing.
- **Lyric:** typography or lyric imagery is the foreground; exact words and timing need a separate text/subtitle workflow.
- **Ambient / sonification:** motion, environment, data, texture, or mapped visual parameters carry the structure rather than literal narrative.
- **Hybrid:** combine lanes, but state what changes at verse/chorus/bridge so the result does not become random B-roll.

Write down at least: target aspect ratio, visual premise in one sentence, 2–5 recurring motifs, subject continuity rules, and what the chorus/hook should look like. Reuse existing project art when it is already the right visual identity instead of regenerating it gratuitously.

## Map the song

Use measured timestamps when an audio-analysis or transcription tool is available. Otherwise work from known section times supplied by the user or from a deliberately approximate editorial map; do not invent exact beat times and present them as measured.

For each section, decide:

- shot density and average shot length,
- what visual motif enters or returns,
- whether energy rises through camera motion, subject motion, edit rate, scale, or contrast,
- which lyric or musical events deserve literal synchronization,
- which shots must persist long enough to be understood.

Do not force every cut onto a beat. Pop craft often benefits from anticipation, holds across the downbeat, and section-level contrast.

## Generate or collect shots

Work shot by shot or in small batches. Keep a prompt/asset ledger outside the mechanical manifest if generated media is involved. For recurring subjects, reuse a stable description/reference and change only the action, framing, or environment needed for that shot.

Prefer one legible action per generated shot. Review candidates before spending more inference on downstream animation. If the same defect survives two materially different correction strategies, change the shot design instead of repeatedly drawing another lottery ticket.

The final renderer is intentionally provider-neutral: it accepts already-selected stills and video clips. Provider-specific generation scripts belong in adapters or project repositories, not in this build unless a future GF build explicitly adds them.

## Write the mechanical manifest

Keep the manifest beside the media it references. All input paths are relative to that directory and may not escape it.

```json
{
  "schema": 1,
  "title": "My music video",
  "audio": "media/song.wav",
  "width": 1920,
  "height": 1080,
  "fps": 30,
  "shots": [
    {"asset": "media/shot-001.png", "kind": "image", "duration": 3.5},
    {"asset": "media/shot-002.mp4", "kind": "video", "duration": 4.0, "source_start": 0.5}
  ]
}
```

This v1 timeline uses **hard cuts**. Still images are held for their declared duration. Video clips may start at `source_start` and are trimmed to `duration`. Every source is scaled to cover the frame and center-cropped to the requested dimensions.

Before rendering, inspect the deterministic plan:

```bash
python scripts/music_video.py plan /project/music-video.json \
  --output /project/out/music-video.mp4
```

The helper reports total duration, shot count, output geometry, and the exact FFmpeg argv. Planning reads local files but does not decode media or write the video.

## Render and verify

```bash
python scripts/music_video.py render /project/music-video.json \
  --output /project/out/music-video.mp4
```

Render mode:

- checks that FFmpeg/FFprobe are installed,
- probes the actual song duration and requires it to align with the declared visual timeline,
- probes video-source duration before trimming,
- refuses to replace an existing output unless `--force` is explicit,
- renders H.264 video + AAC audio with `faststart`,
- re-probes the result for audio/video streams, dimensions, and duration,
- returns byte length and SHA-256.

Watch the complete export after mechanical verification. Check the opening, every section transition, the strongest chorus/hook, any text, subject continuity, and the final frame. Mechanical QA cannot judge whether a joke lands, an edit feels late, or a generated face drifts.

## Zero-cost proof first

Before connecting a model API or using paid generation, verify the local assembly path:

```bash
python examples/make_demo.py /tmp/gf-music-video-demo
python scripts/music_video.py render \
  /tmp/gf-music-video-demo/music-video.json \
  --output /tmp/gf-music-video-demo/music-video.mp4
```

The demo generates a four-second WAV and two PPM stills using only Python's standard library. FFmpeg is the only external runtime dependency for the encode.

## Present or publish

If the host can attach the finished MP4, present the verified local file. If the user asks to publish it, use the requested platform/account only under the authority already present in the task, then distinguish local render verification from successful platform upload/playback.

Do not silently upload source stems, private footage, likenesses, model prompts, or project files just because the final MP4 is publishable.

## Bounds and stopping conditions

The helper enforces at most 300 shots, 20 minutes of timeline, 120 seconds per shot, 60 fps, 4K-class pixel count, 2 GiB per local input, and 10 GiB total local inputs. Inputs must stay inside the manifest directory.

Stop when the requested MP4 is rendered and verified, when a required local asset/runtime is missing, when the song and visual timeline do not align, or when another attempt would merely repeat a failed generation/render route without a concrete change.

See `references/evidence.md` for what this package has actually been tested to do and `references/field-notes.md` for related public workflow patterns. Retain the bundled MIT `LICENSE` when copying the skill independently.

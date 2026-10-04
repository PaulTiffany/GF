---
name: make-music-video
description: Conjure a finished music video from a creative brief when the host has connected music/video generation capability; otherwise assemble accepted local media into a verified MP4. Use for Claude Pop-style videos, narrative/performance/lyric/ambient work, or any request whose actual success condition is a playable music video artifact rather than a storyboard or prompt pack.
---

# Make a music video

The target is not "write prompts about a music video." The target is **a playable music video**.

Use the strongest media capabilities the current host actually exposes. A connected generation app may be able to create music, images, motion clips, or an entire multi-shot video inside the conversation. The bundled FFmpeg helper is the deterministic last mile when local source media is available. It is not, by itself, the capability this skill is trying to teach.

## Capability gate

Choose one mode before doing creative work.

### Conjure mode

Use this mode when the host exposes connected tools that can create the needed media.

A successful run starts from a brief such as "make me a strange three-minute Claude Pop video about X" and ends with an actual playable video artifact. Depending on the host, the path may be:

creative brief -> song/audio generation or supplied song -> visual direction -> generated moving shots or multi-shot video -> review/revision -> final playable video

For ChatGPT specifically, a connected generative-media app can satisfy this gate. At the time this skill was written, the ChatGPT plugin directory exposed Runway with image, video, music/audio, and multi-shot video generation capabilities. Treat that as one adapter, not a dependency or endorsement. Other hosts and future plugins may provide equivalent capabilities.

Do **not** claim Conjure mode merely because image generation, FFmpeg, or prompt writing is available. The host must be able to create enough moving visual media and audio (or receive supplied audio) to land the requested result without making the user manually ferry assets between unrelated tools.

### Assembly mode

Use this mode when the song and visual assets already exist locally, or after Conjure mode has produced/exported them into the workspace.

The bundled helper validates a shot manifest, renders the accepted assets over one finished audio track, and verifies the MP4.

### Not equipped

If the user asked you to conjure a music video and the current host cannot generate video (or cannot access the requested song/audio), say exactly which capability is missing. Do not substitute a storyboard, manifest, PR, generated still image, or synthetic test clip and call the task complete.

That distinction is the core portability rule of this skill.

## Observable success

Keep these outcomes separate:

1. **Creative direction exists.**
2. **Song/audio exists.**
3. **Moving visual media exists.**
4. **A complete playable video exists.**
5. **The final artifact was watched/reviewed.**
6. **A target platform accepted and plays it**, if publication was requested.

For a request to "make a music video," success is normally #4, not #1–#3.

## Direct before generating

Choose a visual grammar before spending generation budget. Reuse a user's established visual identity when appropriate.

Useful lanes include:

- **Claude Pop / internet-native AI pop:** compact high-concept shots, recurring visual jokes or characters, hook recognition, deliberate synthetic aesthetics.
- **Narrative:** recurring subjects, places, props, and causal progression.
- **Performance:** singer/band/performance imagery with section-aware cutaways.
- **Lyric:** typography or lyric imagery as the foreground.
- **Ambient / sonification:** environment, motion, texture, mapped data, or visual parameters carry musical structure.
- **Hybrid:** explicitly define what changes at verse, chorus, bridge, and outro.

Write down at least: aspect ratio, one-sentence premise, recurring motifs, continuity rules, and what the chorus/hook should look like.

## Map the song

Use measured timestamps when the host can analyze or transcribe audio. Otherwise use supplied section times or clearly approximate editorial timing.

For each section decide:

- average shot length / density,
- recurring or new motif,
- how visual energy changes,
- which lyric or musical events deserve synchronization,
- where the edit should deliberately hold rather than cut on every beat.

Pop editing can anticipate a downbeat or hold across it. Mechanical beat matching is not the same as musical phrasing.

## Generate moving media

In Conjure mode, **generate motion, not just key art**.

Prefer shot-sized prompts with one legible action and a stable subject description. Reuse references for recurring characters or art direction. Review small batches before spending more inference.

If the host can generate a whole multi-shot video directly, it may be better to make a coherent first pass there and repair weak sections rather than individually generating every shot.

If the same defect survives two materially different correction strategies, redesign the shot instead of repeatedly sampling the same idea.

Keep a lightweight ledger of prompts, source references, selected outputs, durations, and revisions whenever the host exposes those artifacts.

## Song generation

If the user supplied a finished song, use it.

If the user asked for the song to be created too and the host exposes music/audio generation, make the song as part of Conjure mode before final video assembly. Preserve the user's stylistic and lyrical intent; do not silently replace their song with generic stock audio.

If the host cannot generate music but can generate video, the task can still proceed when the user supplies audio. Otherwise name the missing capability.

## Deterministic assembly

When local source media exists, keep the manifest beside the media it references. Inputs are relative to that directory and may not escape it.

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

The v1 local renderer uses hard cuts. Stills are held for their declared duration. Video clips may start at `source_start` and are trimmed to `duration`. Sources are scaled to cover and center-cropped.

Inspect the plan:

```bash
python scripts/music_video.py plan /project/music-video.json \
  --output /project/out/music-video.mp4
```

Render and verify:

```bash
python scripts/music_video.py render /project/music-video.json \
  --output /project/out/music-video.mp4
```

Render mode checks FFmpeg/FFprobe, song duration, trimmed video-source duration, overwrite intent, output audio/video streams, dimensions, and final duration; it returns byte length and SHA-256.

## Zero-cost mechanical proof

A zero-cost test exists only to prove the local assembly half:

```bash
python examples/make_demo.py /tmp/gf-music-video-demo
python scripts/music_video.py render \
  /tmp/gf-music-video-demo/music-video.json \
  --output /tmp/gf-music-video-demo/music-video.mp4
```

That synthetic clip is **not evidence that Conjure mode is equipped**. It proves only that local assets can be assembled and verified.

## Review

Watch the complete artifact after generation/assembly. Check the opening, section transitions, strongest hook, text, continuity, lip/action artifacts when relevant, and the final frame.

A codec-valid file can still be a bad video.

## Present or publish

For an in-chat request, present the playable result using the host's media surface when available. The user should not have to visit the repository to infer that a video exists.

If publication was requested, use the chosen platform/account under the authority already present in the task and distinguish local generation from successful platform playback.

## Bounds and stopping conditions

The local helper enforces at most 300 shots, 20 minutes, 120 seconds per shot, 60 fps, 4K-class pixel count, 2 GiB per input, 10 GiB total input, and project-directory confinement.

Generation providers have their own costs, limits, and policies; inspect those before invoking them.

Stop when the requested playable video is produced and reviewed, when a required generation/audio/runtime capability is absent, or when another attempt would repeat a failed route without a concrete change.

See `references/evidence.md` for tested claims and `references/field-notes.md` for related public workflow patterns. Retain the bundled MIT `LICENSE` when copying the skill independently.

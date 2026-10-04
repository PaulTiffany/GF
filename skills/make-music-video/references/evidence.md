# Evidence

## What is proven

### 2026-10-04 local assembly probe

The bundled helper was exercised in a local Debian tool environment with Python
and `ffmpeg version 7.1.5-0+deb13u1`.

Input:

- one generated 4.000-second mono WAV,
- two generated PPM stills,
- a two-shot 640x360, 30 fps manifest with two 2.0-second hard-cut shots.

Observed result:

- render exited successfully,
- output size: 75,517 bytes,
- output SHA-256: `5235b4f78dca9cc7a7521cb401358036f914777cae73e367b849ee5b6c4896e4`,
- FFprobe reported one 640x360 video stream and one audio stream,
- FFprobe format duration was exactly 4.000 seconds,
- the helper's post-render verification accepted the file.

The same development pass added unit coverage for bounded project loading,
mixed image/video command construction, project-directory path confinement,
invalid image trimming fields, and the 4K-class pixel bound.

## Conjure-mode capability observation

On 2026-10-04, ChatGPT's plugin directory returned a Runway integration whose
declared capabilities include generating and editing images, videos, and audio,
generating music and sound effects, and building multi-shot story videos
directly from ChatGPT.

That observation establishes that a ChatGPT host can in principle expose the
kind of generative adapter required by this skill. It does **not** establish
that Runway is installed or connected for any particular user/session, that the
account has sufficient credits, or that this GF skill has already produced a
music video through it.

## What is not proven

The synthetic FFmpeg probe does not prove Conjure mode. It establishes only the
mechanical assembly/verification path.

As of the first draft of this build, the motivating phone conversation had not
yet produced a newly generated music video through a connected media-generation
provider. Therefore the build must not describe a storyboard, manifest, pull
request, generated still, or synthetic fixture as the user's requested music
video.

The completed `P(HOP)` music video that motivated the build is prior production
experience for the workflow idea, not execution evidence for this new skill.
A future end-to-end probe should begin with a creative brief in a host with a
connected generation adapter and end with a playable music video shown to the
user in that same workflow.

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

### 2026-10-04 phone-chat Conjure-mode probe

The motivating phone conversation then exercised a stronger path without paid
video-generation inference.

Input:

- one user-supplied finished WAV, `My Sugar Bear.wav`, duration 349.360 seconds,
- an exact lyric/section structure supplied by the user,
- ChatGPT-native image generation for a recurring pair of romantic "sugar bear"
  characters and a coherent noir roadside/motel visual world,
- local FFmpeg motion/compositing to turn the generated stills into moving shots
  and synchronize them to the supplied song.

Observed result:

- a complete 5:49 music-video artifact was rendered,
- 1280x720 H.264 video plus AAC audio were verified with FFprobe,
- the master duration was 349.375 seconds,
- a phone-oriented 960x540 H.264/AAC derivative was produced at 13,768,826 bytes,
- the phone derivative SHA-256 was
  `ba567b4fa9405fa531ecadbcf6c809165e2983bcc09e0d989f1f59ceb9f47568`,
- sampled frames across intro, chorus, bridge, and outro showed the intended
  progression from moonlit roadside/car imagery through motel-room imagery to
  dawn.

This is evidence that Conjure mode does **not** inherently require a paid
text-to-video model. In a host with native still-image generation plus a local
media runtime, a supplied song can be turned into an actual moving music-video
artifact through deterministic motion, cuts, compositing, and encoding.

The visual motion in this probe is generated from still images rather than a
video diffusion model. That distinction should remain explicit.

## Runway capability observation

On 2026-10-04, ChatGPT's plugin directory returned a Runway integration whose
declared capabilities include generating and editing images, videos, and audio,
generating music and sound effects, and building multi-shot story videos
directly from ChatGPT.

The user connected Runway during the probe. The connected workspace was on the
Free plan and exposed image models but no video-generation models, so Runway
video generation was not used. That failure helped establish the fallback rule:
paid generative-video access is optional acceleration, not the success gate.

## What is not proven

This probe does not establish arbitrary text-to-song generation, lip sync,
performance-video generation, photorealistic continuous motion, or universal
mobile playback across every ChatGPT client.

The completed `P(HOP)` music video that originally motivated the build remains
prior production experience rather than execution evidence for this package.
The `My Sugar Bear` probe is the first end-to-end evidence attached directly
to this build's intended Conjure-mode boundary.

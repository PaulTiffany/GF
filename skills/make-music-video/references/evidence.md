# Evidence

## 2026-10-04 synthetic render probe

The new helper was exercised in a local Debian tool environment with Python and
`ffmpeg version 7.1.5-0+deb13u1`.

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

The same session ran four unit tests covering bounded project loading, mixed
image/video command construction, project-directory path confinement, invalid
image trimming fields, and the 4K-class pixel bound.

## What this does not establish

The synthetic probe does not establish creative quality, correctness of any
particular image/video generation provider, lip sync, subtitle rendering,
transition effects, publishing, or playback in a specific ChatGPT/mobile client.
It also does not prove that an arbitrary codec accepted by one FFmpeg build will
be accepted by every other FFmpeg build.

The completed `P(HOP)` music video that motivated this build is production
experience for the broader workflow idea, not test evidence for this newly
written helper. A future reproduction using retained `P(HOP)` source media may
be added as a separate evidence record if those inputs are deliberately made
available to the build.

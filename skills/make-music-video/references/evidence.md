# Evidence

## What is proven

### 2026-10-04 local assembly probe

The original helper was exercised in a local Debian tool environment with
Python and FFmpeg. A generated 4.000-second mono WAV plus two generated PPM
stills rendered successfully to a 640x360 H.264/AAC MP4. FFprobe reported one
video stream, one audio stream, and exactly 4.000 seconds duration.

That pass established bounded loading, path confinement, source-duration checks,
render verification, and SHA-256 reporting.

### 2026-10-04 phone-chat music-video probe

The motivating phone conversation exercised the actual user-facing boundary
without paid text-to-video inference.

Input:

- one user-supplied finished WAV, duration 349.360 seconds;
- exact lyrics and song structure supplied in the conversation;
- native still-image generation for a recurring pair of romantic “sugar bear”
  characters and a coherent noir roadside/motel visual world;
- local FFmpeg motion/editing to turn those stills into a full-length composition.

Observed result:

- a complete 1280x720 H.264/AAC MP4 was created;
- FFprobe reported 349.000 seconds duration;
- output size was 23,419,040 bytes;
- the artifact was delivered back into the phone conversation as a file/link.

The first generation route encountered a safety/model throttle and the user
switched to a lower model. A subsequent visual-generation attempt completed
quickly. The operational lesson is to establish a coherent anchor style, then
reuse references and deterministic media primitives rather than assuming a
particular high-tier generation model will remain available.

The user then identified two shortcomings in the first full-length cut:

1. delivery should include a thumbnail/poster and should verify whether the host
   actually renders an in-chat player rather than merely returning a file link;
2. the stills were attractive but the visual grammar needed more variety than
   repeated photographic reframing.

Those observations directly motivated schema 2 and the visual-grammar layer.

### 2026-10-04 schema-2 renderer probe

The revised local renderer was exercised with a zero-cost 4.000-second fixture.
It used two PPM stills, `push_in` and `pan_right` motion, and a fade-through-black
boundary.

Observed result:

- 5 unit tests passed;
- output: 640x360 H.264/AAC, exactly 4.000 seconds;
- output size: 75,250 bytes;
- output SHA-256: `7fc293b1a03ede81b4cd2dfbd4a26f20c1cdb12e5911cfe4be91c6d18565d227`;
- JPEG poster size: 1,603 bytes;
- poster SHA-256: `4dd29a6db15c8ee07b85c42496d080dd127e7f2a977ab5277403741e5f1fb893`;
- FFprobe confirmed one video stream, one audio stream, and the requested frame
  geometry.

Schema 1 remains backward-compatible. Schema 2 adds deterministic still motion,
fade-through-black transitions, `poster_time`, and automatic poster extraction.

## What the probe establishes

A useful music-video skill does **not** inherently require a paid generative-
video provider. In a host with a supplied song, still-image generation, and a
local media runtime, the agent can create an actual moving music-video artifact
through authored reframing, compositing, typography/procedural clips, stock or
existing footage, and deterministic assembly.

Generated video remains useful for continuous action and difficult camera work,
but it is an optional source type rather than the capability gate.

## Runway capability observation

On 2026-10-04 the user connected Runway. The connected workspace exposed image
models but no video-generation models because video generation required a paid
plan. No Runway video generation was used. This established a concrete reason
not to make paid provider access part of the portable GF contract.

## What is not proven

This evidence does not establish arbitrary text-to-song generation, lip sync,
photorealistic continuous action, or universal inline playback across every
ChatGPT client. The first phone delivery created and attached the MP4 but did
not establish that the client rendered the desired thumbnail/player UI.

The completed `P(HOP)` music video that motivated the build remains prior
production experience rather than execution evidence for this package.

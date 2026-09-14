# AGENTS.md

## Scope

These instructions apply to the entire repository.

GF is a utility-level capability runner. Its present use is deliberately narrow:
turn a text animation specification into deterministic image artifacts through
GitHub Actions.

## Present capability

- Edit `examples/lattice-animal.json` to describe frames as grid cells.
- Run `gf.py` to validate edge connectivity and render the animation.
- Produce `out/lattice-animal.gif` as the animated artifact.
- Produce `out/lattice-animal.png` as its static first-frame poster.
- Produce numbered `out/lattice-animal-frame-XX.png` files and base64
  sidecars for deterministic, ordered native presentation in chat threads.
- Upload both files as workflow artifacts and commit them to the repository.
- Publish a stable player, media URLs, and `manifest.json` through GitHub Pages.
- Probe deployed status, MIME types, and SHA-256 hashes before calling the
  presentation endpoint certified.
- Run `pet.py` to produce `out/lattice-animal-pet.png`, a deterministic
  ChatGPT Pets v1 sprite sheet with transparent, fixed-size frame cells.

Prefer text specifications and deterministic rendering. Keep the build small,
auditable, and purpose-built. Do not add a general agent runtime when a narrow
script or Action will land the artifact.

## Confirmed interface boundary

As observed in the ChatGPT Android interface on 2026-09-14:

- GF can create a valid GIF.
- GitHub can store and directly serve the GIF.
- ChatGPT can return an ordinary clickable link to that file.
- ChatGPT did not reliably animate a remote GitHub GIF inline.
- ChatGPT also did not reliably display the remote GitHub PNG poster inline.
- The same PNG and GIF published at certified GitHub Pages endpoints still
  produced no inline image on the ChatGPT Android client.
- A second direct-GIF attempt from GitHub Pages also produced no inline image.
- Native ChatGPT-generated images and remote GitHub-hosted images travel through
  different presentation paths.

Therefore, do not claim that a Markdown image or clickable poster will render in
the ChatGPT phone client merely because the underlying URL is valid. Serve a
plain link to the GitHub Pages browser player as the reliable phone fallback.

Treat this as a client presentation boundary, not a GIF-generation failure.
A confirmed alternative is to fetch pre-rendered PNG sidecars through the
authorized GitHub connector and emit them through the native generated-image
presentation wrapper. This displays without regeneration or manual transfer.
Ordered frames are a thread-native sequence, not timed GIF playback.

## Native chat transport

For small media, GF also writes an ASCII base64 sidecar beside each artifact:
`name.gif.b64` and `name.png.b64`. An authorized GitHub connector can read
these UTF-8 files and pass their contents to a chat client's native image
channel as `data:<mime>;base64,<payload>`. This avoids relying on remote
Markdown image loading while keeping GitHub as the audited capability boundary.

Treat sidecars as a narrow transport, not a general blob tunnel:

- Generate them only from repository-built artifacts.
- Keep them small enough for connector and conversation limits.
- Never encode secrets, credentials, private data, or untrusted payloads.
- Verify provenance from the repository ref and use the binary artifact's
  manifest digest where the client can decode and hash it.
- Fall back to the certified URL for media too large for native transport.

GitHub Pages is the repository-owned serving experiment authorized for this
boundary. A successful serving probe certifies the URL, not the client. Record
whether the client displays it as a separate observation.

Do not introduce Azure, another CDN, cloud credentials, or further infrastructure
without an explicit human request and a defined test.

## ChatGPT Pet boundary

A Pets sheet is a native animation input, not an ordinary inline image. GF may
render and validate the sheet in GitHub Actions, but creating or selecting a pet
requires an explicit user-scoped ChatGPT Pets upload. Do not create, replace,
select, share, or delete a pet without the user's request. Preserve the source
specification and generated sheet in Git as provenance.

## Contribution protocol

Use pull requests for capability changes.

- Agents open draft pull requests.
- Select exactly one attribution box.
- Agents leave the human readback box untouched.
- A human reads the full diff, ticks the readback box, and marks the pull request
  ready.
- `Tiffany-Studios/pr-readback@v1` checks the attestation shape.

Actions are capability grants. Keep permissions minimal, preserve provenance,
and never let recursive capability silently acquire recursive authority.

Good fight.

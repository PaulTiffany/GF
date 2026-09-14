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
- Upload both files as workflow artifacts and commit them to the repository.
- Publish a stable player, media URLs, and `manifest.json` through GitHub Pages.
- Probe deployed status, MIME types, and SHA-256 hashes before calling the
  presentation endpoint certified.

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
GitHub Pages is the repository-owned serving experiment authorized for this
boundary. A successful serving probe certifies the URL, not the client. Record
whether the client displays it as a separate observation.

Do not introduce Azure, another CDN, cloud credentials, or further infrastructure
without an explicit human request and a defined test.

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

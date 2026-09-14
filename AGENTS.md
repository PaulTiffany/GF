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
- Native ChatGPT-generated images and remote GitHub-hosted images travel through
  different presentation paths.

Therefore, do not claim that a Markdown image or clickable poster will render in
the ChatGPT phone client merely because the underlying URL is valid. Serve a
plain link as the reliable fallback.

Treat this as a client presentation boundary, not a GIF-generation failure.

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

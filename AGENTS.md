# AGENTS.md

## Scope and present use

These instructions apply to the entire repository. GF is a utility-level
capability runner: keep each build narrow, auditable, and reproducible.

- `catalog.json` indexes builds; `catalog.py` lists, inspects, and validates
  metadata without executing build code. See `ARCHITECTURE.md` for the contract.
- `gf.py` validates a grid-cell specification and renders a GIF plus PNG poster.
- `skills/check-model/` searches finite models for safety failures and replays
  witnesses. Preserve modeling assumptions and label capped searches inconclusive;
  a finite-model result does not verify an external implementation.
- `skills/serve-gif/` packages the portable delivery instructions, local
  preparation helper, optional player, and evidence. Keep this folder usable
  outside GF; it must not depend on this repository's name or account.
- GitHub Actions is an optional renderer and artifact source. The default
  render uploads and records only the GIF and poster.
- `serve.py` builds and probes the optional GitHub Pages endpoint.
- `pet.py` retains the historical Pets v1 sheet experiment outside the default
  workflow. Check current format requirements before any requested Pet work.

Prefer existing media and deterministic helpers. Do not add a general agent
runtime, service, or duplicate transport encoding when a narrow move suffices.
Keep the bundled skill license when copying it independently.

## Build contract and bounded experiments

Register new builds with a package-local `build.json`: requirements, inputs,
outputs, effects, enforced and operator-applied bounds, stopping conditions,
and evidence. Keep referenced skill, helper, license, and evidence files inside
the package. Declare repository checks in `catalog.json` and connect them to CI.

Use small local fixtures for experiments. Include effects on other people's
data, accounts, attention, or money in the task's authorized scope. Apply
existing authorization without inventing new approval steps. A build's metadata
does not grant authority or enforce isolation; check the helper and host.

Keep catalogue inspection read-only. Do not add automatic installs, workflow
dispatch, self-scheduling, or recursive execution to the catalogue. End failed
attempts and retry only to address a concrete cause. Keep CI properties, client
observations, and portability claims distinct, with their supporting evidence.

## Presentation contract

The successful phone experiment on 2026-09-14 used actual downloaded files in a
file-capable workspace. The assistant emitted a GIF attachment with an absolute
`sandbox:` Markdown image target and an embedded player using existing frames.
The user confirmed “Both work”. No manual download/re-upload was required.

Remote GitHub/Pages embeds and base64 image-wrapper attempts had failed in that
conversation. Earlier claims that the wrappers were confirmed successful were
incorrect. See [the probe record](skills/serve-gif/references/phone-evidence.md)
for the fixture and evidence limits.

Keep three outcomes separate:

1. **Artifact verified:** bytes, format, frames, timing, and any expected digest.
2. **Attachment emitted:** an existing file sent through a supported chat surface.
3. **Client playback observed:** evidence that the recipient actually saw motion.

CI, valid URLs, tool previews, or base64 text cannot attest to the third outcome.
Do not claim a universal new ChatGPT capability or assume every mobile session
has the same tools. Check available runtime and presentation facilities. Use
the host's file persistence rules, then emit the actual attachment. If a
capability is absent, identify it rather than repeat the same failed route.

A Pages browser link is an optional external player. A successful serving probe
certifies the endpoint, not the client. Do not introduce Azure, another CDN,
cloud credentials, or further infrastructure without an explicit human request
and a defined test.

## ChatGPT Pet boundary

A Pets sheet is an animation input, not an installed pet. Do not create, replace,
select, share, or delete a pet without the user's request. Preserve the source
specification and any deliberately retained sheet in Git as provenance.

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

---
name: serve-gif
description: Deliver an existing animated GIF inside a chat that supports workspace file attachments. Use when a GIF link or tool preview does not appear for the user, or when preparing a GIF for inline delivery. Supports an optional embedded frame player when the host provides an HTML visualization surface.
---

# Serve GIF

Land the existing animation in the conversation without asking the user to
download and re-upload it. This recipe needs a runtime that can write files
and a host that can present those files; loading instructions grants neither.

## Equip

- Use an existing GIF, or finish the requested generation before this skill.
- Locate a writable workspace and its supported attachment mechanism.
- Use Python 3.10+ and Pillow for the bundled preparation helper.
- If the source is remote, use an available authorized download/connector.
  GitHub is optional. Read [references/github.md](references/github.md) only
  for a GitHub source.

## Execute

1. Materialize the actual bytes in the workspace. A remote URL, base64 text,
   tool-side image preview, or invented local path is not a file attachment.
2. Run the helper with absolute output paths. Resolve `scripts/` relative to
   this skill, not the caller's working directory:

   ```bash
   python scripts/prepare_gif.py /path/to/source.gif \
     --output /workspace/gif/dance.gif \
     --alt "A lattice animal dancing"
   ```

   For a ZIP, add `--member path/inside/archive.gif`; this names one exact
   member. Add `--sha256 <expected-GIF-digest>` when a trusted source supplies
   the GIF's digest. That flag hashes the GIF bytes, not the ZIP container.

3. Inspect the JSON result: dimensions, frame count, durations, loop count,
   byte length, and SHA-256. The helper preserves the original GIF bytes.
4. Follow the host's file persistence rules, then present the attachment in
   the final response. In hosts supporting sandbox images, emit the returned
   `markdown_image` as actual Markdown, outside a code fence. It looks like:

   ```markdown
   ![A lattice animal dancing](sandbox:/workspace/gif/dance.gif)
   ```

5. Distinguish preparation, attachment emission, and user-visible playback.
   Report playback as confirmed only with evidence from the receiving client.
   A new client can be checked with one short question about whether it moves.

## Optional frame player

When the user wants an inline player and the host exposes an HTML visualization
surface, first read that host's visualization instructions. Add
`--player /workspace/dance-player.html` to produce a self-contained fragment
from the GIF's composited frames. Present it through the host's visualization
renderer. A downloadable HTML link alone is not an inline player.

The player has pause/resume controls, respects reduced motion, and makes no
network requests. It preserves positive frame durations (minimum 20 ms) and
finite/infinite loop behavior. Missing/zero delays use 100 ms. Player output
is capped at 1 MiB; the attachment route remains available for larger media.

## When the build cannot equip

Name the specific missing runtime or presentation capability. A browser link
may still be useful, but do not call it successful in-thread delivery. Do not
repeat an unchanged failed embed, re-render the art to solve transport, or
require manual file transfer as the normal last step. Change the delivery
mechanism only when the available tools support that change.

See [references/phone-evidence.md](references/phone-evidence.md) for the observed
successful routes and the limits of that evidence. This skill is MIT licensed;
retain its bundled `LICENSE` when copying the folder.

---
name: serve-gif
description: Deliver an existing animated GIF inside a chat that supports workspace file attachments. Use when a GIF link or tool preview does not appear for the user, when preparing a GIF for inline delivery, or when the user needs a mobile-shareable copy. Supports an optional embedded frame player when the host provides an HTML visualization surface.
---

# Serve GIF

Land the existing animation in the conversation without asking the user to
download and re-upload it. This recipe needs a runtime that can write files
and a host that can present those files; loading instructions grants neither.

Treat these as separate delivery properties:

1. the GIF bytes were prepared correctly,
2. the chat emitted an attachment,
3. the receiving client plays it inline,
4. the receiving client can retrieve/share/export it.

Success at one layer does not prove the next. In particular, inline playback
does not prove that a phone's download or share action reaches a usable file.

## Equip

- Use an existing GIF, or finish the requested generation before this skill.
- Locate a writable workspace and its supported attachment mechanism.
- Use Python 3.10+ and Pillow for the bundled preparation helper.
- Identify whether the user only needs inline playback or also needs a
  retrievable/shareable copy.
- If sharing/export is required, identify an available transport that yields
  either a host-native file attachment or a durable user-reachable URL.
  A sandbox image path alone is not evidence of mobile shareability.
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

5. If the user asked to save, share, forward, or export the GIF from a phone,
   do not stop at inline playback. Provide a distinct retrieval/share route
   when the available host or an authorized external store supports one.
   Publishing the GIF to a repository, release, Pages site, cloud drive, or
   other external destination is a separate side effect and requires the
   user's authorization when it is not already part of the task.

6. Distinguish preparation, attachment emission, user-visible playback, and
   retrieval/shareability in status claims. Report each as confirmed only with
   evidence from the receiving client. A new client can be checked with one
   short question tailored to the requested goal: whether it moves, whether
   the file opens, or whether the share sheet can send it.

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
may still be useful, but do not call it successful in-thread delivery.

If inline playback works but a phone's download/share action resolves to a
missing Library item, dead attachment, or otherwise unusable destination,
treat that as a transport failure. Do not re-render the art to solve transport,
and do not merely rename or re-emit the same sandbox attachment as the normal
retry. Change the delivery mechanism when available: prefer a host-native file
attachment, or an authorized durable external URL/storage route. If no such
route is available, say that inline playback is confirmed but mobile
retrieval/share is not equipped.

Do not repeat an unchanged failed embed or require manual file transfer as the
normal last step.

See [references/phone-evidence.md](references/phone-evidence.md) for the observed
successful and failed routes and the limits of that evidence. This skill is MIT
licensed; retain its bundled `LICENSE` when copying the folder.

# GF

> Good fight. Small build. Clean execution. Show the result.

GF is an executable build wiki for tool-equipped assistants.
The first build delivers an existing animated GIF inside a compatible chat.
The teaching style borrows from OSRS rusher build guides: name the requirements,
teach the sequence, identify the matchup, and show what actually landed.

## Find a build

```bash
python catalog.py list
python catalog.py show serve-gif
```

The catalogue shows each build's requirements, inputs, outputs, effects, bounds,
and evidence. It uses only Python's standard library and does not execute the
listed helpers. Read the build, then run its helper within the requested task.

The [architecture](ARCHITECTURE.md) explains how builds travel between hosts
and how to contribute one using the [build template](templates/build.json).
Small fixtures, explicit stopping conditions, and reviewed contributions keep
experiments bounded. GitHub stores and checks the builds; the host supplies the
runtime and permissions.

## Build 01: serve a GIF

**Result:** an animation the user can see in the conversation, without manually
downloading and re-uploading it.

| Equip | Why it matters |
| --- | --- |
| Existing GIF | Reuse the finished animation. |
| File-capable runtime | Materialize and verify the actual bytes. |
| Python 3.10+ and Pillow | Run the small preparation helper. |
| Chat attachment surface | Present the resulting file to the user. |
| Optional HTML visualization surface | Play existing frames with pause/resume controls. |

**Sequence:** obtain bytes → verify and stage → attach → check visible playback.

```bash
python -m pip install --requirement requirements.txt
python skills/serve-gif/scripts/prepare_gif.py out/lattice-animal.gif \
  --output /workspace/gif/lattice-animal.gif \
  --alt "Seven connected grid cells dancing"
```

The helper returns the media facts and `markdown_image`. In a compatible chat,
the assistant emits that value as Markdown, outside a code fence:

```markdown
![Seven connected grid cells dancing](sandbox:/workspace/gif/lattice-animal.gif)
```

Use the host's actual writable workspace and file persistence rules. The helper
does not upload files or modify the host. It accepts a local GIF or an exact
member of a downloaded ZIP, preserves the GIF bytes, and refuses to overwrite
different content. For an optional embedded player, add
`--player /workspace/lattice-player.html` and present the fragment through the
host's visualization renderer.

**Matchup:** this needs runtime and presentation tools. Instructions alone do
not add them to an ordinary phone chat. GitHub is an optional source/build
adapter; it is not required when the file is already available locally.

**Proof:** in the GF phone conversation on 2026-09-14, the user confirmed both
the real file attachment and an embedded frame player worked. That is a useful
reproduction result, not a guarantee for all ChatGPT phone sessions. See the
[probe record](skills/serve-gif/references/phone-evidence.md), including failed
remote embeds and the correction to our earlier base64 claims.

## Transfer the build

The self-contained [serve-gif skill](skills/serve-gif/SKILL.md) includes the
instructions, helper, player template, source adapter, evidence, and MIT license.
Copy the `skills/serve-gif` folder into a skill-capable environment using that
host's installation procedure. Keeping it in this repository does not install
it into every ChatGPT session. A tool-equipped assistant can also read the
instructions and run the helper directly.

For the next micro-tool, teach the same compact build card:

1. **Target:** one observable user outcome.
2. **Equip:** tools, inputs, permissions, and client requirements.
3. **Execute:** the shortest reproducible sequence and reusable helper.
4. **Matchup:** where the sequence works and what blocks it.
5. **Proof:** artifact checks and the user's observed result, kept distinct.

Each registered build includes a `build.json` declaration alongside its skill.
The GIF package is the first complete example. Add builds through the process
in [ARCHITECTURE.md](ARCHITECTURE.md#add-a-build).

## Optional renderer and GitHub adapter

To make the included lattice animal from its text specification:

```bash
python gf.py examples/lattice-animal.json out/lattice-animal.gif
```

Every frame requires at least two distinct, edge-connected cells. The renderer
writes a GIF and first-frame PNG. The **GF — render GIF** Action does the same
on relevant pushes to `main` or manual dispatch, uploads those two artifacts,
and records them in Git when running on `main`.

The separate **GF — certified serving** Action publishes the
[browser player](https://paultiffany.github.io/GF/) and
[manifest](https://paultiffany.github.io/GF/manifest.json). Its HTTP/MIME/hash
probe certifies the endpoint only. It cannot certify inline phone playback.
See the [GitHub adapter](skills/serve-gif/references/github.md) for retrieval.

`pet.py` remains an optional historical Pets v1 sheet exporter. It is outside
the default GIF workflow; producing a sheet does not install or select a pet.
Current Pets compatibility must be checked separately if requested.

## Checks and contributions

```bash
python catalog.py check
python -m unittest discover -s tests -v
node --test tests/player.test.cjs
```

The checks exercise preparation, byte preservation, archive handling, and player
controls. Phone rendering still needs client evidence. Follow [AGENTS.md](AGENTS.md):
agents open draft PRs; a human reads the diff and completes the readback.

## License

Code, original documentation, example specifications, and repository-authored
outputs are [MIT licensed](LICENSE), unless a file says otherwise. GF uses no
game assets and is not affiliated with Jagex. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

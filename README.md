# GF

> Good fight.

**GF** is Old School RuneScape rusher architecture for GPT artifact generation: keep the build small, expose one decisive capability, and let GitHub Actions land the hit.

The first rush is GIF generation. A GPT edits a tiny JSON animation spec. GitHub renders it deterministically and commits the finished GIF. No binary-generation interface is required.

## The build

```text
animation.json
      ↓
   gf.py
      ↓
 output.gif
```

- **Text in:** auditable, patchable animation instructions.
- **Artifact out:** an actual looping GIF plus a PNG poster frame for interfaces that cannot display animation.
- **GitHub as boundary:** the workflow defines the granted capability.
- **Git as ledger:** the specification and result remain attributable.

## Quick start

Edit `examples/lattice-animal.json`, commit it, and run **GF — render GIF** from the Actions tab. A push that changes an example also runs automatically.

Locally:

```bash
python -m pip install Pillow
python gf.py examples/lattice-animal.json out/lattice-animal.gif
```

The JSON format is intentionally tiny:

```json
{
  "canvas": [320, 320],
  "cell_size": 48,
  "duration_ms": 220,
  "frames": [
    {
      "cells": [
        {"x": 1, "y": 1, "color": "#ffcc33", "face": true}
      ]
    }
  ]
}
```

Coordinates are grid coordinates. Every frame must contain at least two edge-connected cells: single cells do not count; only animals do.

## Display contract

Each render creates both `name.gif` and `name.png`. The PNG is the first-frame poster for interfaces that can display remote images but cannot animate remote GIFs. Make the poster clickable:

```markdown
[![Tap to play](https://raw.githubusercontent.com/OWNER/REPO/main/out/name.png)](https://github.com/OWNER/REPO/raw/refs/heads/main/out/name.gif)
```

Creation and presentation are separate capabilities. GF ships both sides of that boundary.

## Rusher philosophy

A rusher is not a maxed account. It is a purpose-built configuration that keeps irrelevant levels low and concentrates power where it matters. GF applies that culture to machine capabilities:

1. Grant one narrow move.
2. Make the move reproducible.
3. Test the boundary.
4. Land the artifact.
5. Say “gf.”

This project is inspired by player-created Old School RuneScape rusher culture. It is unofficial, uses no game assets, and is not affiliated with or endorsed by Jagex. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

Code and original project documentation are released under the [MIT License](LICENSE). Example specifications and generated outputs authored in this repository are covered by the same license unless a file states otherwise.

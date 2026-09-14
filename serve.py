#!/usr/bin/env python3
"""Build and verify GF's stable presentation endpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

MEDIA = {
    "lattice-animal.png": "image/png",
    "lattice-animal.gif": "image/gif",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build(source: Path, site: Path, base_url: str, commit: str) -> None:
    site.mkdir(parents=True, exist_ok=True)
    assets = {}

    for name, mime in MEDIA.items():
        source_file = source / name
        target = site / name
        shutil.copyfile(source_file, target)
        data = target.read_bytes()
        with Image.open(target) as image:
            facts = {
                "url": f"{base_url.rstrip('/')}/{name}",
                "sha256": digest(data),
                "bytes": len(data),
                "mime": mime,
                "width": image.width,
                "height": image.height,
            }
            if name.endswith(".gif"):
                facts["frames"] = getattr(image, "n_frames", 1)
        assets[name] = facts

    manifest = {
        "schema": 1,
        "build_commit": commit,
        "player_url": f"{base_url.rstrip('/')}/",
        "assets": assets,
    }
    (site / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (site / ".nojekyll").touch()
    (site / "index.html").write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>GF — lattice animal</title>
  <meta name="description" content="A brief agreement among strangers found the beat.">
  <meta property="og:image" content="{assets['lattice-animal.png']['url']}">
  <style>
    :root {{ color-scheme: light; font-family: system-ui, sans-serif; }}
    body {{ margin: 0; min-height: 100vh; display: grid; place-items: center;
            background: #fffaf0; color: #181818; }}
    main {{ width: min(92vw, 32rem); text-align: center; }}
    img {{ display: block; width: 100%; height: auto; image-rendering: pixelated; }}
    a {{ color: inherit; }}
  </style>
</head>
<body>
  <main>
    <a href="lattice-animal.gif" aria-label="Open the animated GIF">
      <img src="lattice-animal.gif"
           alt="Seven colorful connected grid cells dancing as a lattice animal">
    </a>
    <p><a href="lattice-animal.gif">Open or download the GIF</a> · <a href="manifest.json">manifest</a></p>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


def fetch_without_redirect(url: str) -> tuple[bytes, str]:
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, request, fp, code, msg, headers, newurl):
            return None

    opener = urllib.request.build_opener(NoRedirect)
    with opener.open(url, timeout=20) as response:
        if response.status != 200:
            raise RuntimeError(f"{url}: expected 200, got {response.status}")
        return response.read(), response.headers.get_content_type()


def probe(base_url: str, attempts: int) -> None:
    base_url = base_url.rstrip("/")
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            manifest_bytes, manifest_type = fetch_without_redirect(f"{base_url}/manifest.json")
            if manifest_type != "application/json":
                raise RuntimeError(f"manifest: expected application/json, got {manifest_type}")
            manifest = json.loads(manifest_bytes)

            for name, expected in manifest["assets"].items():
                data, content_type = fetch_without_redirect(expected["url"])
                if content_type != expected["mime"]:
                    raise RuntimeError(
                        f"{name}: expected {expected['mime']}, got {content_type}"
                    )
                if digest(data) != expected["sha256"]:
                    raise RuntimeError(f"{name}: deployed bytes do not match manifest")
            print(json.dumps(manifest, indent=2, sort_keys=True))
            return
        except (OSError, KeyError, ValueError, RuntimeError, urllib.error.HTTPError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(5)

    raise RuntimeError(f"serving contract failed after {attempts} attempts: {last_error}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--source", type=Path, default=Path("out"))
    build_parser.add_argument("--site", type=Path, default=Path("_site"))
    build_parser.add_argument("--base-url", required=True)
    build_parser.add_argument("--commit", required=True)

    probe_parser = subparsers.add_parser("probe")
    probe_parser.add_argument("--base-url", required=True)
    probe_parser.add_argument("--attempts", type=int, default=12)

    args = parser.parse_args()
    if args.command == "build":
        build(args.source, args.site, args.base_url, args.commit)
    else:
        probe(args.base_url, args.attempts)


if __name__ == "__main__":
    main()

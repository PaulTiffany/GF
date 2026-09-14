# GitHub source adapter

Use this only when the requested GIF lives in GitHub. The core helper has no
GitHub API, network, token, repository-name, or Pages dependency.

1. Identify the repository and the intended ref/run. Prefer an existing
   completed render; dispatch a new workflow only if the requested artifact
   needs rebuilding and that operation is authorized.
2. Use the authorized connector to list that run's artifacts and download the
   selected artifact. If the connector returns a signed download URL, use it
   to fetch the ZIP into the workspace. Treat the URL as temporary transport,
   not a durable user-facing link; do not log its query string.
3. Compare the ZIP's SHA-256 with the artifact digest when supplied. Then pass
   the local ZIP and exact GIF member name to `scripts/prepare_gif.py`.
   `--sha256` on that helper checks the GIF, so do not pass it the ZIP digest.
4. Return to the skill's attachment step. A successful workflow or download
   has not yet tested phone playback.

For a directly accessible GIF, an authorized download of its bytes is enough.
For a text-only connector, base64 is usable only if an available runtime can
decode it into a real file. Base64 sidecars are not themselves a presentation
channel. Read binary contents through the connector when it supports them;
avoid committing duplicate encodings solely for chat transport.

GF also has a Pages player and a manifest with media hashes. Endpoint probes
validate HTTP responses and bytes; client display is a separate observation.

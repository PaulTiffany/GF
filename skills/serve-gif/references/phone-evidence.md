# Phone probes

Evidence comes from Paul Tiffany's GF conversations in ChatGPT on his phone.
These observations establish behavior in specific sessions, not universal
mobile support or the date on which the product first gained GIF capability.

## 2026-09-14

| Route | Observation |
| --- | --- |
| Remote GitHub / Pages GIF and PNG Markdown embeds | User repeatedly reported no image. |
| Base64 sidecars emitted through image / generated-image wrappers | User reported no image. Earlier repository claims of success were incorrect. |
| Native image generation | Static images appeared; this did not demonstrate delivery of an existing GIF. |
| Download workflow ZIP into workspace, extract GIF, attach actual file using sandbox Markdown | User confirmed it worked. |
| Present an embedded HTML player cycling the existing four PNG frames | User confirmed it worked. |

The successful turn had filesystem/runtime tools available. The assistant
downloaded the artifact through the GitHub connector, checked the archive hash,
extracted the media, persisted the GIF as required by that host, and emitted
the actual attachment. The user did not manually transfer files. The player
reused existing frames. After both were presented, the user replied “Both work”.

The experiment changed several delivery conditions together. It does not prove
which individual condition was necessary, isolate client-version differences,
or show that an ordinary phone chat without these tools can use the same route.

### Reproduction fixture

- Repository: `PaulTiffany/GF`
- Render run: `34884496597`
- Artifact: `10364062067` (`lattice-animal`)
- Commit: `2517f197311399a2385d7a8173d53d8748046c9c`
- ZIP SHA-256: `3afec10d2fa9eca516fa7ef2e40a9a9cdf5fb2b6e19f09769546be8c1c0d6d83`
- GIF SHA-256: `24ff6722ea460ccca7e94c3a513a15ae23349eca9cedbfe6ff2e49f9aee2458d`
- GIF: 9,868 bytes; 384 × 384; four frames; 220 ms per frame; infinite loop.

Workflow artifacts may expire. The commit retains the original GIF. The helper
and template in this skill generalize the successful manual sequence; their
automated checks are not an additional phone-client observation.

## 2026-09-23

A newly generated 512 × 512, 24-frame GIF was prepared with this skill's
`prepare_gif.py` helper and emitted in chat using sandbox Markdown.

| Property | Observation |
| --- | --- |
| Inline animation | User confirmed: “It works”. |
| Phone retrieval/share | User reported that attempting to download/share led to “library not found”. |

This is evidence that inline playback and mobile retrieval/shareability are
different delivery properties. A successful sandbox embed must not be treated
as proof that the receiving phone can obtain a shareable file.

The appropriate retry target is transport, not rendering. Re-rendering,
renaming, or re-emitting identical GIF bytes through the same sandbox route
does not address the observed failure unless the client supplies new evidence
that the alternate emission path is materially different. Prefer a host-native
file attachment or, when authorized, a durable user-reachable external URL.

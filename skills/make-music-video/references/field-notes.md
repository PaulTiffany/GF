# Field notes: music-video workflows as inspectable skills

GF's `make-music-video` build is intentionally provider-neutral and small, but
it sits inside a visible public pattern: creators are publishing the production
method alongside the finished generative-media artifact.

Two useful public examples observed while designing this build:

- `chenqianshinian/music-mv-studio` describes itself as an Agent Skill for
  turning a song and lyrics into a music video. Its public workflow separates
  shot design, keyframe review, per-shot generation, composition, QA, and
  targeted repair. Repository: https://github.com/chenqianshinian/music-mv-studio
- `toki-plus/ai-video-workflow` demonstrates a multi-provider pipeline with
  explicit human review between prompt generation, image generation, image-to-
  video, music, and FFmpeg composition. Repository:
  https://github.com/toki-plus/ai-video-workflow

These are references, not runtime dependencies. No code or documentation from
those projects is bundled here. GF keeps the reusable mechanical core local and
leaves provider adapters, credentials, inference spend, and publication outside
this build's authority.

The motivating in-house case is Paul Tiffany's completed `P(HOP)` song/video
work around StickerBook. The practical lesson retained here is the separation
between creative iteration (song, visual identity, generated or existing
assets, editorial judgment) and deterministic assembly/verification. The skill
is broader than that case and does not require Suno, Claude, StickerBook, or a
particular visual genre.

# Lyric synchronization: auto-caption, then canonical surgery

Use this procedure whenever the deliverable needs lyric captions, kinetic lyrics,
or line/word-level lyric timing.

## Certification boundary

Audio-only structure tools can establish duration, beats, onsets, pauses, vocal
activity, and likely section boundaries. They **cannot establish which lyric was
sung at a particular time**.

Therefore:

- `section_aligned` may use ordinary audio analysis;
- `line_aligned` requires a lexical observation of the performance, normally
  ASR/auto-caption output;
- `word_aligned` requires timestamped ASR, CTC/forced alignment, or equivalent
  word/phoneme evidence.

Do not promote section/energy boundaries into lyric timestamps.

## Default selector

When canonical lyrics are available and captions are requested:

```
rendered audio
  ↓
auto-caption / ASR of the actual performance
  ↓
timestamped noisy performed transcript
  ↓
sequence-align against canonical lyrics
  ↓
surgery: repair wording while preserving acoustic timestamps
  ↓
performed + canonical aligned lyric map
  ↓
SRT / ASS / Manim / actor-state timing
```

The ASR transcript is an **observation channel**, not the lexical authority.
Canonical lyrics are the **intended lexical/semantic source**, not the timing
authority. The rendered audio is authoritative for what happened when.

## Canonical surgery

Reconcile the timestamped ASR stream against canonical lyrics with sequence
alignment rather than simple string replacement.

Expected edits include:

- homophone/name repair, e.g. `Grayson` → `Gracyn`;
- punctuation/casing restoration;
- joining or splitting ASR tokens;
- restoring canonical wording where the acoustic match is credible;
- preserving repeats that the singer actually performed;
- recording omitted canonical lines as omissions rather than forcing them into
  unused time;
- retaining extra/interpolated performed phrases as performed-only events;
- marking uncertain substitutions instead of silently inventing certainty.

Timestamp surgery should preserve the acoustic span whenever possible. If several
ASR words map to one canonical phrase, use the enclosing ASR start/end span. If
one ASR token maps to several canonical words, distribute subword timing only
when the aligner provides evidence; otherwise keep a phrase-level span.

## Required retained objects

Keep both views after reconciliation:

- `canonical_text`: what the authored lyric map says;
- `performed_text`: what the singer appears to have performed;
- `observed_asr`: raw/noisy auto-caption text when useful for provenance;
- `start` / `end`: acoustic timing;
- `alignment_confidence`;
- `operation`: match, substitute, repeat, omission, insertion, split, merge;
- `source`: exact timing / ASR / forced alignment / manual correction.

Do not destroy the raw ASR observation when producing cleaned captions.

## Tool routing

1. If the host already exposes auto-caption/ASR with timestamps, use it.
2. If an ASR package/model is already installed/cached, use it locally.
3. If neither exists and line/word lyric timing is required, acquiring or calling
   an ASR/alignment capability is a **justified escalation**. Host-native-first
   does not mean pretending non-lexical audio tools can hear words.
4. Use librosa/FFmpeg/Demucs/beat tools in parallel for musical structure and
   video editing, not as substitutes for lexical observation.

Prefer the smallest ASR capable of useful timestamps. The canonical lyric map
already reduces the semantic search space, so perfect transcription is not
required.

## Stopping rule

Do not claim `line_aligned` or `word_aligned` until every displayed lyric span
is grounded in lexical acoustic evidence (ASR/CTC/forced alignment/manual timing)
plus reconciliation. If that evidence is unavailable, stop at
`section_aligned` and omit timed lyric captions.

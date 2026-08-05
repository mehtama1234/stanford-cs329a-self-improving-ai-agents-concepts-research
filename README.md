# Stanford CS329A Self-Improving AI Agents Concept Research

Transcript-backed first-principles notes for Stanford CS329A Self-Improving AI Agents.

## Current Source

- Playlist: CS329A Self-Improving AI Agents
- URL: https://www.youtube.com/playlist?list=PLangBM27OtEA
- Videos: 9
- Transcript status: 9/9 available locally
- Note: the earlier URL contained `list=PLangBM27OtEAin`, which YouTube did not expose as a playlist. The corrected playlist id is `PLangBM27OtEA`.

## Workflow

```bash
python3 scripts/download_youtube_transcripts.py
python3 scripts/build_site.py
python3 scripts/validate_all.py
```

## Current Analysis Coverage

- Concepts: 27
- Evidence anchors: 34
- Generated HTML pages: overview, lectures, concepts, evidence, and transcript index
- Coverage gate: every lecture has at least one selected evidence anchor

The project keeps raw captions separate from interpretation:

- `raw-material/youtube/transcripts/.../raw-vtt/`: downloaded caption files
- `raw-material/youtube/transcripts/.../clean/`: cleaned transcript text
- `raw-material/youtube/transcripts/.../cues/`: timestamped cue JSON
- `raw-material/youtube/transcript-index.json`: machine-readable source index
- `analysis/concepts/concept-atlas.json`: first-principles concept writeups
- `analysis/evidence/evidence-ledger.json`: transcript-backed evidence anchors
- `site/`: generated static HTML

## Standard

This is not a transcript summary. Each concept page should explain:

- the ordinary problem the concept solves
- why the naive approach fails
- the first-principles move
- what the transcript directly supports
- what is synthesis beyond the transcript
- what breaks when the idea is misused

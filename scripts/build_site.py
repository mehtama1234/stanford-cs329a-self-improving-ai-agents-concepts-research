#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
ASSETS = SITE / "assets"


def load_json(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def page(title: str, body: str, prefix: str = "") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <link rel="stylesheet" href="{prefix}assets/styles.css">
</head>
<body>
  <header class="topbar">
    <a class="brand" href="{prefix}index.html">CS329A Concept Lab</a>
    <nav>
      <a href="{prefix}index.html">Overview</a>
      <a href="{prefix}primers.html">Primers</a>
      <a href="{prefix}concepts.html">Concepts</a>
      <a href="{prefix}lectures.html">Lectures</a>
      <a href="{prefix}evidence.html">Evidence</a>
      <a href="{prefix}transcripts.html">Transcripts</a>
    </nav>
  </header>
  <main>{body}</main>
</body>
</html>
"""


def concept_page(title: str, body: str) -> str:
    return page(title, body.replace('href="', 'href="../') if False else f'<p><a href="../concepts.html">Back to concepts</a></p>{body}')


def render_index(summary: dict[str, Any], concepts: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> None:
    body = f"""
<section class="hero">
  <p class="eyebrow">Transcript-backed first-principles notes</p>
  <h1>Stanford CS329A Self-Improving AI Agents</h1>
  <p class="lede">This package turns the 9-lecture playlist into a concept map: scaling, reasoning traces, test-time compute, verifiers, tool feedback, planning, train-time RL, search, deep research, agent evaluation, memory, and future self-improvement directions.</p>
</section>
<section class="stats">
  <article><strong>{summary['video_count']}</strong><span>source video</span></article>
  <article><strong>{summary['transcript_count']}</strong><span>available transcript</span></article>
  <article><strong>{summary['word_count']:,}</strong><span>transcript words</span></article>
  <article><strong>{len(concepts)}</strong><span>concepts</span></article>
  <article><strong>{len(evidence)}</strong><span>evidence anchors</span></article>
</section>
<section>
  <h2>First-Principles Thesis</h2>
  <p>An AI agent is not just a larger chatbot. Across the playlist, the move from LLMs to agents is a systems move: give the model a goal, let it act through tools, observe feedback, preserve memory, verify intermediate work, and revise until it either completes the task or knows it cannot.</p>
  <p>The core pressure is feedback. Scaling gives base capability. Reasoning traces expose intermediate process. Test-time compute samples or searches more paths. Verifiers select, reject, or reward paths. Train-time RL can then use those signals to change future behavior.</p>
</section>
<section>
  <h2>New Primer Track</h2>
  <p>The primer track collects the concepts we discussed after the lectures: pretraining, base-model latent capability, sampling, SFT, distillation, RLHF, RLVR, GRPO, DAPO, pass@k, diversity collapse, data progress, MoE, MLA, Muon, power sampling, and RL information inefficiency.</p>
  <p><a class="button" href="primers.html">Open the primer track</a></p>
</section>
<section>
  <h2>Concept Route</h2>
  <div class="grid">
    {''.join(f'<article class="card"><h3><a href="concepts/{slugify(c["id"])}.html">{esc(c["name"])}</a></h3><p>{esc(c["plain_language_definition"])}</p></article>' for c in concepts)}
  </div>
</section>
"""
    (SITE / "index.html").write_text(page("CS329A Concept Lab", body), encoding="utf-8")


def render_primers(primers: list[dict[str, Any]]) -> None:
    primer_by_id = {primer["id"]: primer for primer in primers}
    cards = []
    for number, primer in enumerate(primers, start=1):
        href = f"primers/{slugify(primer['id'])}.html"
        cards.append(
            f"""<article class="card">
  <p class="quiet">#{number:02d} · {esc(primer['theme'])}</p>
  <h3><a href="{href}">{esc(primer['title'])}</a></h3>
  <p>{esc(primer['plain_meaning'])}</p>
</article>"""
        )

        links = []
        for connected_id in primer.get("connections", []):
            connected = primer_by_id.get(connected_id)
            if connected:
                links.append(f'<a class="chip" href="{slugify(connected_id)}.html">{esc(connected["title"])}</a>')

        body = f"""
<p><a href="../primers.html">Back to primers</a></p>
<section class="page-head">
  <p class="eyebrow">{esc(primer['theme'])}</p>
  <h1>{esc(primer['title'])}</h1>
  <p class="lede">{esc(primer['plain_meaning'])}</p>
</section>
<div class="two-col">
  <section class="detail"><h2>First Principles</h2><p>{esc(primer['first_principles'])}</p></section>
  <section class="detail"><h2>Concrete Example</h2><p>{esc(primer['example'])}</p></section>
  <section class="detail"><h2>Why It Matters</h2><p>{esc(primer['why_it_matters'])}</p></section>
  <section class="detail"><h2>Common Misunderstanding</h2><p>{esc(primer['misunderstanding'])}</p></section>
</div>
<section class="detail">
  <h2>Connects To</h2>
  <p>{''.join(links) if links else 'No linked primers yet.'}</p>
</section>
"""
        (SITE / "primers" / f"{slugify(primer['id'])}.html").write_text(page(primer["title"], body, prefix="../"), encoding="utf-8")

    body = f"""
<section class="page-head">
  <p class="eyebrow">Concept primer track</p>
  <h1>AI Reasoning Concepts, One By One</h1>
  <p class="lede">A standalone sequence for the ideas we discussed around base models, sampling, RLVR, data progress, architecture, and agent evaluation.</p>
</section>
<div class="grid">{''.join(cards)}</div>
"""
    (SITE / "primers.html").write_text(page("Concept Primers", body), encoding="utf-8")


def render_concepts(concepts: list[dict[str, Any]], evidence_by_id: dict[str, dict[str, Any]]) -> None:
    cards = []
    for concept in concepts:
        href = f"concepts/{slugify(concept['id'])}.html"
        cards.append(f'<article class="card"><h3><a href="{href}">{esc(concept["name"])}</a></h3><p>{esc(concept["ordinary_problem"])}</p><p class="quiet">{esc(concept["theme"])}</p></article>')
        ev_html = []
        for ev_id in concept.get("evidence_ids", []):
            ev = evidence_by_id[ev_id]
            ev_html.append(
                f"""<article class="evidence-item">
  <h3>{esc(ev['title'])}</h3>
  <p><a href="{esc(ev['url'])}">{esc(ev['url'])}</a></p>
  <blockquote>{esc(ev['quote'])}</blockquote>
  <p><strong>Evidence type:</strong> {esc(ev['evidence_type'])}</p>
  <p>{esc(ev['why_span_matters'])}</p>
</article>"""
            )
        body = f"""
<section class="page-head">
  <p class="eyebrow">{esc(concept['theme'])}</p>
  <h1>{esc(concept['name'])}</h1>
  <p class="lede">{esc(concept['plain_language_definition'])}</p>
</section>
<div class="two-col">
  <section class="detail"><h2>Ordinary Problem</h2><p>{esc(concept['ordinary_problem'])}</p></section>
  <section class="detail"><h2>Naive Picture</h2><p>{esc(concept['naive_picture'])}</p></section>
  <section class="detail"><h2>Why It Fails</h2><p>{esc(concept['why_naive_fails'])}</p></section>
  <section class="detail"><h2>First-Principles Move</h2><p>{esc(concept['first_principles'])}</p></section>
  <section class="detail"><h2>What Breaks Without It</h2><p>{esc(concept['what_breaks_without_it'])}</p></section>
  <section class="detail"><h2>Course Role</h2><p>{esc(concept['course_role'])}</p></section>
</div>
<section>
  <h2>Transcript Evidence</h2>
  {''.join(ev_html)}
</section>
"""
        html_text = page(concept["name"], f'<p><a href="../concepts.html">Back to concepts</a></p>{body}', prefix="../")
        (SITE / "concepts" / f"{slugify(concept['id'])}.html").write_text(html_text, encoding="utf-8")
    body = f"""
<section class="page-head">
  <p class="eyebrow">Concept atlas</p>
  <h1>First-Principles Concepts</h1>
  <p class="lede">Each page starts from an ordinary problem, then explains the mathematical or systems move the lecture is building toward.</p>
</section>
<div class="grid">{''.join(cards)}</div>
"""
    (SITE / "concepts.html").write_text(page("Concepts", body), encoding="utf-8")


def render_evidence(evidence: list[dict[str, Any]], concepts_by_id: dict[str, dict[str, Any]]) -> None:
    items = []
    for ev in evidence:
        concept_links = " ".join(
            f'<a class="chip" href="concepts/{slugify(cid)}.html">{esc(concepts_by_id[cid]["name"])}</a>'
            for cid in ev.get("supports_concepts", [])
            if cid in concepts_by_id
        )
        items.append(
            f"""<article class="evidence-item" id="{esc(ev['id'])}">
  <h2>{esc(ev['title'])}</h2>
  <p><a href="{esc(ev['url'])}">{esc(ev['url'])}</a></p>
  <blockquote>{esc(ev['quote'])}</blockquote>
  <p><strong>Source tier:</strong> {esc(ev['source_tier'])} · <strong>Type:</strong> {esc(ev['evidence_type'])}</p>
  <p>{esc(ev['why_span_matters'])}</p>
  <p>{concept_links}</p>
</article>"""
        )
    body = f"""
<section class="page-head">
  <p class="eyebrow">Evidence ledger</p>
  <h1>Transcript Anchors</h1>
  <p class="lede">Short timestamped transcript spans supporting the concept atlas. Quotes are kept brief; the explanation is synthesis.</p>
</section>
{''.join(items)}
"""
    (SITE / "evidence.html").write_text(page("Evidence", body), encoding="utf-8")


def render_lectures(index: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> None:
    evidence_by_lecture: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for ev in evidence:
        evidence_by_lecture[int(ev["lecture_index"])].append(ev)

    cards = []
    for row in index:
        lecture_index = int(row["index"])
        href = f"lectures/{lecture_index:02d}.html"
        cards.append(
            f"""<article class="card">
  <h3><a href="{href}">Part {lecture_index}: {esc(row['title'].split('|')[-1].strip())}</a></h3>
  <p>{row['word_count']:,} transcript words · {len(evidence_by_lecture.get(lecture_index, []))} evidence anchors</p>
  <p class="quiet">{esc(row['transcript_status'])} · {esc(row['source_tier'])}</p>
</article>"""
        )
        items = []
        for ev in sorted(evidence_by_lecture.get(lecture_index, []), key=lambda item: item["timestamp_seconds"]):
            items.append(
                f"""<article class="evidence-item">
  <h3>{esc(ev['title'])}</h3>
  <p><a href="{esc(ev['url'])}">{esc(ev['url'])}</a></p>
  <blockquote>{esc(ev['quote'])}</blockquote>
  <p>{esc(ev['why_span_matters'])}</p>
</article>"""
            )
        body = f"""
<p><a href="../lectures.html">Back to lectures</a></p>
<section class="page-head">
  <p class="eyebrow">Lecture {lecture_index}</p>
  <h1>{esc(row['title'])}</h1>
  <p class="lede">{row['word_count']:,} words · {row['cue_count']:,} timestamped cues · <a href="{esc(row['url'])}">YouTube source</a></p>
</section>
<section>
  <h2>Transcript-Backed Anchors</h2>
  {''.join(items) if items else '<p>No evidence anchors have been selected for this lecture yet.</p>'}
</section>
<section>
  <h2>Local Source Files</h2>
  <p><code>{esc(row.get('clean_txt'))}</code></p>
  <p><code>{esc(row.get('cues_json'))}</code></p>
</section>
"""
        html_text = page(row["title"], body, prefix="../")
        (SITE / "lectures" / f"{lecture_index:02d}.html").write_text(html_text, encoding="utf-8")

    body = f"""
<section class="page-head">
  <p class="eyebrow">Lecture index</p>
  <h1>Course Videos</h1>
  <p class="lede">Each lecture page shows the local transcript status and selected evidence anchors used by the concept atlas.</p>
</section>
<div class="grid">{''.join(cards)}</div>
"""
    (SITE / "lectures.html").write_text(page("Lectures", body), encoding="utf-8")


def render_transcripts(index: list[dict[str, Any]]) -> None:
    rows = []
    for row in index:
        rows.append(
            f"""<tr>
  <td>{esc(row['index'])}</td>
  <td><a href="{esc(row['url'])}">{esc(row['title'])}</a></td>
  <td>{esc(row['transcript_status'])}</td>
  <td>{esc(row['source_tier'])}</td>
  <td>{row['word_count']:,}</td>
  <td><code>{esc(row.get('clean_txt'))}</code></td>
</tr>"""
        )
    body = f"""
<section class="page-head">
  <p class="eyebrow">Source index</p>
  <h1>Transcripts</h1>
  <p class="lede">Raw captions and clean transcripts are archived locally for review.</p>
</section>
<table>
  <thead><tr><th>#</th><th>Video</th><th>Status</th><th>Source Tier</th><th>Words</th><th>Clean Text</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
"""
    (SITE / "transcripts.html").write_text(page("Transcripts", body), encoding="utf-8")


def render_styles() -> None:
    css = """
:root { color-scheme: light; --ink: #202124; --muted: #5f6368; --line: #d8dee4; --bg: #f7f8fa; --panel: #ffffff; --accent: #b42318; }
* { box-sizing: border-box; }
body { margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); background: var(--bg); line-height: 1.55; }
a { color: #0b57d0; text-decoration: none; }
a:hover { text-decoration: underline; }
.topbar { display: flex; align-items: center; justify-content: space-between; gap: 24px; padding: 14px 28px; border-bottom: 1px solid var(--line); background: #fff; position: sticky; top: 0; z-index: 2; }
.brand { font-weight: 750; color: var(--ink); }
nav { display: flex; gap: 14px; flex-wrap: wrap; font-size: 14px; }
main { max-width: 1180px; margin: 0 auto; padding: 32px 24px 64px; }
.hero, .page-head { border-bottom: 1px solid var(--line); padding-bottom: 24px; margin-bottom: 24px; }
.eyebrow { text-transform: uppercase; letter-spacing: .08em; color: var(--accent); font-weight: 800; font-size: 12px; margin: 0 0 8px; }
h1 { font-size: clamp(32px, 5vw, 58px); line-height: 1.02; margin: 0 0 14px; letter-spacing: 0; }
h2 { margin: 0 0 10px; font-size: 22px; }
h3 { margin: 0 0 8px; }
.lede { font-size: 19px; max-width: 860px; color: #34373b; }
.stats { display: grid; grid-template-columns: repeat(5, minmax(120px, 1fr)); gap: 12px; margin: 20px 0 30px; }
.stats article, .card, .detail, .evidence-item { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 18px; }
.button { display: inline-block; background: var(--ink); color: #fff; border-radius: 8px; padding: 9px 13px; font-weight: 700; }
.button:hover { text-decoration: none; background: #3c4043; }
.stats strong { display: block; font-size: 28px; }
.stats span, .quiet { color: var(--muted); font-size: 14px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }
.two-col { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 14px; margin-bottom: 28px; }
.evidence-item { margin: 14px 0; }
blockquote { border-left: 4px solid var(--accent); margin: 12px 0; padding: 8px 14px; background: #fff7f5; color: #3b1c18; }
.chip { display: inline-block; border: 1px solid var(--line); border-radius: 999px; padding: 4px 10px; margin: 2px; background: #fff; font-size: 13px; }
table { width: 100%; border-collapse: collapse; background: #fff; border: 1px solid var(--line); }
th, td { text-align: left; border-bottom: 1px solid var(--line); padding: 10px; vertical-align: top; }
code { font-size: 12px; overflow-wrap: anywhere; }
@media (max-width: 760px) { .topbar { align-items: flex-start; flex-direction: column; } .stats { grid-template-columns: repeat(2, 1fr); } main { padding: 24px 16px 48px; } }
"""
    (ASSETS / "styles.css").write_text(css.strip() + "\n", encoding="utf-8")


def main() -> int:
    SITE.mkdir(exist_ok=True)
    ASSETS.mkdir(exist_ok=True)
    (SITE / "concepts").mkdir(exist_ok=True)
    (SITE / "lectures").mkdir(exist_ok=True)
    (SITE / "primers").mkdir(exist_ok=True)
    for folder in [SITE / "concepts", SITE / "lectures", SITE / "primers"]:
        for stale in folder.glob("*.html"):
            stale.unlink()
    summary = load_json("raw-material/youtube/summary.json")
    index = load_json("raw-material/youtube/transcript-index.json")
    concepts = load_json("analysis/concepts/concept-atlas.json")
    evidence = load_json("analysis/evidence/evidence-ledger.json")
    primers = load_json("analysis/primers/concept-primers.json")
    evidence_by_id = {ev["id"]: ev for ev in evidence}
    concepts_by_id = {concept["id"]: concept for concept in concepts}
    render_styles()
    render_index(summary, concepts, evidence)
    render_primers(primers)
    render_concepts(concepts, evidence_by_id)
    render_lectures(index, evidence)
    render_evidence(evidence, concepts_by_id)
    render_transcripts(index)
    manifest = sorted(str(path.relative_to(SITE)) for path in SITE.rglob("*.html"))
    (SITE / "page-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(manifest)} html pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

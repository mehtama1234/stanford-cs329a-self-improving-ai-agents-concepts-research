#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def main() -> int:
    errors: list[str] = []
    index = load("raw-material/youtube/transcript-index.json")
    concepts = load("analysis/concepts/concept-atlas.json")
    evidence = load("analysis/evidence/evidence-ledger.json")
    concept_ids = {concept["id"] for concept in concepts}
    evidence_ids = {ev["id"] for ev in evidence}
    evidence_lecture_indices = {int(ev["lecture_index"]) for ev in evidence}

    if not index:
        errors.append("transcript index is empty")
    for row in index:
        if int(row["index"]) not in evidence_lecture_indices:
            errors.append(f"lecture {row.get('index')} has no selected evidence anchors")
        if row.get("transcript_status") == "available":
            for field in ["raw_vtt", "clean_txt", "cues_json"]:
                if not row.get(field) or not (ROOT / row[field]).exists():
                    errors.append(f"missing {field} for {row.get('id')}")
            if row.get("word_count", 0) < 1000:
                errors.append(f"weak transcript word count for {row.get('id')}")

    required_concept_fields = [
        "plain_language_definition",
        "ordinary_problem",
        "naive_picture",
        "why_naive_fails",
        "first_principles",
        "what_breaks_without_it",
        "course_role",
    ]
    for concept in concepts:
        for field in required_concept_fields:
            if words(str(concept.get(field, ""))) < 8:
                errors.append(f"concept {concept['id']} has shallow {field}")
        if not concept.get("evidence_ids"):
            errors.append(f"concept {concept['id']} has no evidence")
        for ev_id in concept.get("evidence_ids", []):
            if ev_id not in evidence_ids:
                errors.append(f"concept {concept['id']} references missing evidence {ev_id}")

    for ev in evidence:
        if ev.get("source_tier") != "youtube-caption":
            errors.append(f"evidence {ev['id']} has unexpected source tier")
        if words(ev.get("quote", "")) > 20:
            errors.append(f"evidence {ev['id']} quote too long")
        if words(ev.get("why_span_matters", "")) < 12:
            errors.append(f"evidence {ev['id']} has shallow why_span_matters")
        for concept_id in ev.get("supports_concepts", []):
            if concept_id not in concept_ids:
                errors.append(f"evidence {ev['id']} references missing concept {concept_id}")

    html_files = list((ROOT / "site").rglob("*.html"))
    if len(html_files) < len(concepts) + 3:
        errors.append("not enough generated html files")
    lecture_pages = list((ROOT / "site" / "lectures").glob("*.html"))
    if len(lecture_pages) != len(index):
        errors.append(f"expected {len(index)} lecture pages, found {len(lecture_pages)}")
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        if "<title>" not in text or "<h1>" not in text:
            errors.append(f"html page missing title or h1: {path.relative_to(ROOT)}")

    manifest = ROOT / "site" / "page-manifest.json"
    if not manifest.exists():
        errors.append("missing site/page-manifest.json")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"validated {len(index)} transcript records, {len(concepts)} concepts, {len(evidence)} evidence anchors, {len(html_files)} html pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

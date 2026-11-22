from __future__ import annotations

from typing import Any

from extraction.candidates import ExtractionCandidate


SOURCE_PRIORITY = {
    "dataset_file": 100,
    "readme": 90,
    "pdf": 80,
    "pdf_table": 78,
    "pdf_figure": 75,
    "zenodo_description": 60,
    "zenodo_abstract": 55,
    "zenodo_title": 50,
    "llm_inference": 10,
}


def choose_best_candidate(
    candidates: list[ExtractionCandidate],
) -> ExtractionCandidate | None:
    if not candidates:
        return None

    def key(c: ExtractionCandidate):
        return (
            SOURCE_PRIORITY.get(c.source_type, 0),
            c.confidence,
        )

    return max(candidates, key=key)


def resolve_candidates(
    candidates: list[ExtractionCandidate],
) -> dict[str, ExtractionCandidate]:
    """Choose a provisional value per field without hiding conflicts."""
    grouped: dict[str, list[ExtractionCandidate]] = {}

    for c in candidates:
        grouped.setdefault(c.field_name, []).append(c)

    return {
        field: choose_best_candidate(items)
        for field, items in grouped.items()
    }


def detect_conflicts(
    candidates: list[ExtractionCandidate],
) -> list[dict[str, Any]]:
    """Return fields with multiple distinct extracted values."""

    grouped: dict[str, list[ExtractionCandidate]] = {}
    for c in candidates:
        grouped.setdefault(c.field_name, []).append(c)

    conflicts = []
    for field, items in grouped.items():
        values = {str(i.value) for i in items}
        if len(values) > 1:
            conflicts.append({
                "field_name": field,
                "values": sorted(values),
                "candidates": [i.as_dict() for i in items],
            })

    return conflicts

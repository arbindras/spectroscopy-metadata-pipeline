from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def load_zenodo_records(path: str | Path) -> dict[str, dict[str, Any]]:
    """Load a Zenodo CSV/JSON metadata file keyed by record_id."""

    path = Path(path)

    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            rows = data.get("records", data.get("data", []))
        else:
            rows = data
    elif path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
    else:
        raise ValueError(f"Unsupported Zenodo metadata format: {path.suffix}")

    result = {}
    for row in rows:
        if "record_id" not in row:
            continue
        result[str(row["record_id"])] = dict(row)

    return result


def build_zenodo_text(record: dict[str, Any]) -> str:
    """Create a clearly labelled text block for later semantic extraction."""
    fields = [
        ("TITLE", record.get("title")),
        ("ABSTRACT", record.get("abstract")),
        ("DESCRIPTION", record.get("description")),
        ("KEYWORDS", record.get("keywords")),
    ]
    chunks = []
    for label, value in fields:
        if value not in (None, "", []):
            chunks.append(f"{label}:\n{value}")
    return "\n\n".join(chunks)

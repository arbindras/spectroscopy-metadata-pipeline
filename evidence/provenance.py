from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALID_VALUE_ORIGINS = {
    "author_provided",
    "file_derived",
    "calculated",
    "inferred",
    "unknown",
}


def serialize_value(value: Any) -> str | None:
    if value is None:
        return None

    if hasattr(value, "item"):
        value = value.item()

    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, default=str)

    return str(value)


def make_evidence(
    *,
    record_id: str,
    field_name: str,
    field_value: Any,
    source_file: str | Path | None,
    source_type: str,
    evidence_text: str,
    dataset_path: str | Path | None,
    extraction_method: str,
    confidence: float,
    value_origin: str,
    page_number: int | None = None,
    section: str | None = None,
) -> dict[str, Any]:
    if field_value is None:
        raise ValueError("Evidence must not be created for a NULL value.")

    if value_origin not in VALID_VALUE_ORIGINS:
        raise ValueError(f"Invalid value_origin: {value_origin}")

    return {
        "record_id": str(record_id),
        "field_name": field_name,
        "field_value": serialize_value(field_value),
        "source_file": str(source_file) if source_file else None,
        "source_type": source_type,
        "evidence_text": evidence_text,
        "page_number": page_number,
        "section": section,
        "dataset_path": str(dataset_path) if dataset_path else None,
        "extraction_method": extraction_method,
        "confidence": float(confidence),
        "value_origin": value_origin,
        "timestamp": datetime.now(timezone.utc),
    }


def add_field_with_evidence(
    row: dict[str, Any],
    evidence: list[dict[str, Any]],
    *,
    field_name: str,
    value: Any,
    record_id: str,
    source_file: str | Path,
    source_type: str,
    evidence_text: str,
    dataset_path: str | Path,
    extraction_method: str,
    confidence: float,
    value_origin: str,
) -> None:
    if value is None:
        return

    row[field_name] = value
    evidence.append(
        make_evidence(
            record_id=record_id,
            field_name=field_name,
            field_value=value,
            source_file=source_file,
            source_type=source_type,
            evidence_text=evidence_text,
            dataset_path=dataset_path,
            extraction_method=extraction_method,
            confidence=confidence,
            value_origin=value_origin,
        )
    )

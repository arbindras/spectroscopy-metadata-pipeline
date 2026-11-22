from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExtractionCandidate:
    field_name: str
    value: Any
    source_type: str
    source_file: str
    page_number: int | None
    evidence_text: str
    extraction_method: str
    confidence: float

    def as_dict(self) -> dict:
        return {
            "field_name": self.field_name,
            "value": self.value,
            "source_type": self.source_type,
            "source_file": self.source_file,
            "page_number": self.page_number,
            "evidence_text": self.evidence_text,
            "extraction_method": self.extraction_method,
            "confidence": self.confidence,
        }

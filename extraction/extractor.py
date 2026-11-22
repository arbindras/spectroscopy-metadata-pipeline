from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .candidates import ExtractionCandidate
from .spectral_patterns import extract_spectral_candidates
from pdf.pdf_reader import PDFReader


class PDFSpectralExtractor:
    """Run page-level deterministic extraction and retain all evidence."""

    def __init__(self, reader: PDFReader | None = None):
        self.reader = reader or PDFReader()

    def extract(self, pdf_path: str | Path) -> list[ExtractionCandidate]:
        if Path(pdf_path).suffix.lower() in {".xml", ".nxml"}:
            from pdf.jats_reader import JATSReader

            document = JATSReader().read(pdf_path)
        else:
            document = self.reader.read(pdf_path)
        candidates: list[ExtractionCandidate] = []

        for page in document.iter_pages():
            candidates.extend(
                extract_spectral_candidates(
                    page.text,
                    page_number=page.page_number,
                    source_file=document.source_file,
                )
            )

        return candidates

    @staticmethod
    def group_by_field(
        candidates: list[ExtractionCandidate],
    ) -> dict[str, list[ExtractionCandidate]]:
        grouped = defaultdict(list)
        for candidate in candidates:
            grouped[candidate.field_name].append(candidate)
        return dict(grouped)

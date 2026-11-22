from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

try:
    import fitz  # PyMuPDF
except ImportError as exc:
    raise ImportError(
        "PyMuPDF is required. Install with: pip install pymupdf"
    ) from exc


@dataclass(frozen=True)
class PDFPage:
    page_number: int
    text: str


@dataclass
class PDFDocument:
    source_file: str
    pages: list[PDFPage]

    @property
    def text(self) -> str:
        return "\n\n".join(p.text for p in self.pages)

    def iter_pages(self) -> Iterator[PDFPage]:
        yield from self.pages


class PDFReader:
    """Page-preserving PDF text reader.

    This intentionally extracts text only. Tables/images are separate concerns
    and can be added later without changing the page API.
    """

    def __init__(self, min_text_length: int = 1):
        self.min_text_length = min_text_length

    def read(self, path: str | Path) -> PDFDocument:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(path)

        pages: list[PDFPage] = []
        with fitz.open(path) as doc:
            for i, page in enumerate(doc):
                text = page.get_text("text") or ""
                text = self._clean_text(text)
                if len(text) >= self.min_text_length:
                    pages.append(PDFPage(page_number=i + 1, text=text))

        return PDFDocument(source_file=str(path), pages=pages)

    @staticmethod
    def _clean_text(text: str) -> str:
        text = text.replace("\u00a0", " ")
        text = text.replace("\u00ad", "")
        # Preserve line breaks; normalize only excessive horizontal whitespace.
        lines = [" ".join(line.split()) for line in text.splitlines()]
        return "\n".join(line for line in lines if line)

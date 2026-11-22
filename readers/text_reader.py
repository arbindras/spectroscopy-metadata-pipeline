"""Reader for plain-text spectra (.txt, .dat, .asc, .xy ...).

Handles the common layouts seen in Zenodo spectroscopy datasets:

* Comment-prefixed headers (``#``, ``COMMENT``, ``%``, ``!``, ``;``) followed
  by whitespace/tab/comma separated numeric columns, e.g. the Montreal
  Spectral Library files::

      COMMENT Column 1 is the wavelength (microns),
      COMMENT Column 2 is the flux (F_lambda),
      COMMENT Column 3 is the error on the flux.
      0.80312  1.2e-15  3.4e-17

* A header row naming the axis column followed by many spectra columns::

      # Wavenumber  0  1  4  7 ...
      3999.13  0.00069  0.00139 ...

The first column is used as the spectral axis only when it is monotonic AND
there is explicit textual evidence of what it is (a column name or a comment
mentioning wavelength / wavenumber / a unit). Files without such evidence
(README files, logs, tables of results) are skipped silently.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from models import ReaderResult
from readers.base_reader import BaseReader
from readers.spectral_helpers import (
    is_monotonic,
    make_axis_spectral_record,
    modality_from_text,
    unit_from_text,
)


COMMENT_PREFIXES = ("#", "comment", "%", "!", ";", "//", "history")
AXIS_WORDS = (
    "wavelength",
    "wavenumber",
    "wave number",
    "wave_number",
    "lambda",
    "raman shift",
    "spectral axis",
)
ERROR_WORDS = ("error", "uncertainty", "sigma", "std", "noise", "snr", "err")
# Ocean Optics SpectraSuite/OceanView exports: wavelength (nm) + counts.
OCEAN_MARKERS = ("spectrasuite data file", "oceanview", "begin processed spectral data", "begin spectral data")
# Bruker OPUS "data point table" exports are always wavenumber (cm-1), value.
DPT_EXTENSIONS = {".dpt"}
COLUMN_LABEL_RE = re.compile(
    r"column\s*(\d+)\s*(?:is|=|:)\s*(?:the\s+)?(.+)", re.IGNORECASE
)
SPLIT_RE = re.compile(r"[,\t;]+|\s+")


def _parse_floats(tokens: list[str]) -> list[float] | None:
    values = []
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        try:
            values.append(float(token.replace("D", "E").replace("d", "e")))
        except ValueError:
            return None
    return values or None


def _split(line: str) -> list[str]:
    return [t for t in SPLIT_RE.split(line.strip()) if t]


def detect_encoding(path: Path) -> str:
    """UTF-16 exports (e.g. Agilent ChemStation) carry a BOM; default UTF-8."""
    with path.open("rb") as stream:
        head = stream.read(4)
    if head[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return "utf-16"
    if head[:3] == b"\xef\xbb\xbf":
        return "utf-8-sig"
    return "utf-8"


def numeric_header_line(comments: list[str], n_columns: int, min_count: int) -> tuple[str, np.ndarray] | None:
    """Find a text line ``<label> v1 v2 ... v(n-1)`` whose values form a
    monotonic spectral axis for a wide table (rows = time/sample, columns =
    wavelengths), e.g. Agilent ``Time-WL  190  191 ... 1100``."""
    for text in comments:
        tokens = _split(text)
        if len(tokens) != n_columns or len(tokens) - 1 < max(min_count, 2):
            continue
        values = _parse_floats(tokens[1:])
        if values is None or len(values) != n_columns - 1:
            continue
        axis = np.asarray(values, dtype=float)
        if is_monotonic(axis) and float(np.max(np.abs(axis))) >= 50:
            return tokens[0], axis
    return None


class TextReader(BaseReader):
    extensions = {".txt", ".dat", ".asc", ".xy", ".prn", ".sp", ".tab", ".dpt"}

    def read(
        self,
        *,
        record_id: str,
        dataset_path: Path,
        file_path: Path,
    ) -> ReaderResult:
        result = ReaderResult()
        max_mb = float(self.reader_config.get("text_max_mb", 500))
        min_points = int(self.reader_config.get("text_min_points", 10))

        try:
            if file_path.stat().st_size > max_mb * 1024 * 1024:
                return result

            comments: list[str] = []
            header_tokens: list[str] | None = None
            last_text_line: str | None = None
            rows: list[list[float]] = []

            encoding = detect_encoding(file_path)
            with file_path.open("r", encoding=encoding, errors="replace") as stream:
                for raw in stream:
                    line = raw.strip()
                    if not line:
                        continue

                    lowered = line.lower()
                    is_comment = lowered.startswith(COMMENT_PREFIXES)
                    body = line
                    if is_comment:
                        body = re.sub(
                            r"^(#+|comment|%+|!+|;+|//|history)\s*",
                            "",
                            line,
                            flags=re.IGNORECASE,
                        )

                    numbers = None if is_comment else _parse_floats(_split(line))
                    if numbers is None:
                        if body:
                            comments.append(body)
                            if not rows:
                                last_text_line = body
                        continue

                    if not rows and last_text_line is not None:
                        header_tokens = re.split(r"[,\t;]+", last_text_line.strip())
                        if len(header_tokens) == 1:
                            header_tokens = _split(last_text_line)
                    rows.append(numbers)

            # Row count is checked per layout below: in a wide table the
            # spectral points are columns, so few rows is fine.
            if not rows:
                return result

            # Keep the dominant column count; drop ragged lines.
            widths = np.bincount([len(r) for r in rows])
            n_columns = int(np.argmax(widths))
            if n_columns < 2:
                return result
            data = np.asarray(
                [r for r in rows if len(r) == n_columns], dtype=float
            )

            wide = numeric_header_line(
                comments, n_columns, int(self.reader_config.get("numeric_header_min_count", 5))
            )
            if wide is not None:
                return self._wide_record(
                    result, record_id, dataset_path, file_path, wide, data.shape[0]
                )

            axis_values = data[:, 0]
            if axis_values.size < min_points or not is_monotonic(axis_values):
                return result

            # Column labels from "Column N is the ..." comments, else header row.
            labels: dict[int, str] = {}
            for text in comments:
                match = COLUMN_LABEL_RE.search(text)
                if match:
                    labels[int(match.group(1)) - 1] = match.group(2).strip()
            if not labels and header_tokens and len(header_tokens) >= 1:
                for index, token in enumerate(header_tokens[:n_columns]):
                    labels[index] = token.strip()

            axis_label = labels.get(0, "")
            comment_text = "\n".join(comments[:200])
            axis_text = axis_label.lower()

            has_axis_word = any(word in axis_text for word in AXIS_WORDS)
            unit = unit_from_text(axis_label) if axis_label else None
            if unit is None:
                # e.g. "wavenumbers (cm-1)" mentioned elsewhere in the header.
                for text in comments[:200]:
                    lowered = text.lower()
                    if any(word in lowered for word in AXIS_WORDS):
                        unit = unit_from_text(text)
                        if unit:
                            has_axis_word = True
                            break

            lowered_comments = comment_text.lower()
            if unit is None and any(marker in lowered_comments for marker in OCEAN_MARKERS):
                unit, has_axis_word = "nm", True
                axis_label = axis_label or "wavelength (Ocean Optics export)"
            if unit is None and file_path.suffix.lower() in DPT_EXTENSIONS:
                unit, has_axis_word = "cm^-1", True
                axis_label = axis_label or "wavenumber (OPUS data point table)"

            unlabelled = not has_axis_word and unit is None
            if unlabelled and not self.reader_config.get("text_accept_unlabelled_axis", False):
                return result

            spectra_columns = [
                index
                for index in range(1, n_columns)
                if not any(
                    re.search(rf"\b{word}\b", labels.get(index, "").lower())
                    for word in ERROR_WORDS
                )
            ]

            prefix = (
                f"Text file column 1 ({axis_label or 'unnamed'}), "
                f"{data.shape[0]} rows x {n_columns} columns"
            )
            row, evidence = make_axis_spectral_record(
                record_id=record_id,
                dataset_path=dataset_path,
                file_path=file_path,
                axis_values=axis_values,
                unit=unit,
                source_type="spectral_file",
                evidence_prefix=prefix,
                extraction_method=(
                    "text_unlabelled_first_column_axis" if unlabelled
                    else "text_first_column_axis"
                ),
                confidence=0.5 if unlabelled else (0.95 if unit else 0.8),
                modality=modality_from_text(comment_text),
                num_spectra=len(spectra_columns) or None,
                num_spectra_evidence=(
                    f"{len(spectra_columns)} data column(s) after the axis "
                    f"column, excluding error columns; labels={labels}"
                )[:2000],
            )
            result.spectral_records.append(row)
            result.evidence_records.extend(evidence)

        except Exception as exc:
            result.errors.append({
                "record_id": record_id,
                "source_file": str(file_path),
                "reader": type(self).__name__,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            })

        return result

    def _wide_record(self, result, record_id, dataset_path, file_path, wide, n_rows):
        label, axis = wide
        lowered = label.lower()
        unit = unit_from_text(label)
        if unit is None and ("wl" in lowered or "wavelength" in lowered) and 100 <= axis.min() and axis.max() <= 3500:
            unit = "nm"  # ChemStation "Time-WL" header: wavelengths in nm
        row, evidence = make_axis_spectral_record(
            record_id=record_id,
            dataset_path=dataset_path,
            file_path=file_path,
            axis_values=axis,
            unit=unit,
            source_type="spectral_file",
            evidence_prefix=f"Text header row {label!r} with {axis.size} numeric columns",
            extraction_method="text_numeric_header_axis",
            confidence=0.85 if unit else 0.6,
            num_spectra=n_rows,
            num_spectra_evidence=f"{n_rows} data rows under the numeric header (one spectrum per row)",
        )
        result.spectral_records.append(row)
        result.evidence_records.extend(evidence)
        return result

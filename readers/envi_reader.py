"""Reader for ENVI hyperspectral image headers (``*.hdr``).

Push-broom cameras (e.g. Specim Lumo exports) store a binary cube next to a
text header::

    ENVI
    samples = 384
    lines   = 5904
    bands   = 144
    wavelength units = Nanometers
    wavelength = { 968.669983, 979.869995, ... }

Only the header is parsed; the cube itself is never loaded. Dark/white
reference captures (``DARKREF_*``, ``WHITEREF_*``) are calibration frames and
are skipped.
"""

from __future__ import annotations

import re
from pathlib import Path

from evidence.provenance import add_field_with_evidence
from models import ReaderResult
from readers.base_reader import BaseReader
from readers.spectral_helpers import make_axis_spectral_record, unit_from_text

REFERENCE_PREFIXES = ("darkref", "whiteref", "dark_ref", "white_ref")


def parse_envi_header(text: str) -> dict[str, str]:
    """Return ``key -> raw value`` (braced lists joined onto one line)."""
    values: dict[str, str] = {}
    for match in re.finditer(r"^\s*([^=\n{}]+?)\s*=\s*(\{[^}]*\}|[^\n]*)", text, re.MULTILINE):
        values[match.group(1).strip().lower()] = match.group(2).strip()
    return values


def parse_list(raw: str | None) -> list[float]:
    if not raw:
        return []
    numbers = []
    for token in raw.strip("{} \n").split(","):
        token = token.strip()
        if token:
            try:
                numbers.append(float(token))
            except ValueError:
                return []
    return numbers


class ENVIReader(BaseReader):
    extensions = {".hdr"}

    def read(self, *, record_id: str, dataset_path: Path, file_path: Path) -> ReaderResult:
        result = ReaderResult()
        try:
            if file_path.name.lower().startswith(REFERENCE_PREFIXES):
                return result
            text = file_path.read_text(encoding="utf-8", errors="replace")
            if not text.lstrip().upper().startswith("ENVI"):
                return result
            header = parse_envi_header(text)
            wavelengths = parse_list(header.get("wavelength"))
            if not wavelengths:
                return result

            samples = int(float(header.get("samples", 0) or 0))
            lines = int(float(header.get("lines", 0) or 0))
            units = header.get("wavelength units", "")
            unit = unit_from_text(units) or ("nm" if "nanomet" in units.lower() else None)
            if unit is None and "micromet" in units.lower():
                unit = "um"
            reflectance = "refl" in file_path.name.lower() or "reflectance" in text.lower()
            pixels = samples * lines if samples and lines else None

            row, evidence = make_axis_spectral_record(
                record_id=record_id,
                dataset_path=dataset_path,
                file_path=file_path,
                axis_values=wavelengths,
                unit=unit,
                source_type="spectral_file",
                evidence_prefix=(
                    f"ENVI header: samples={samples}, lines={lines}, "
                    f"bands={header.get('bands')}, wavelength units={units or 'n/a'}"
                ),
                extraction_method="envi_header",
                confidence=0.95 if unit else 0.7,
                modality="hyperspectral imaging" + (" (reflectance)" if reflectance else ""),
                num_spectra=pixels,
                num_spectra_evidence=f"one spectrum per pixel: {samples} x {lines}",
            )
            for field, value in (
                ("num_images", 1),
                ("num_pixels", pixels),
                ("image_height", lines or None),
                ("image_width", samples or None),
            ):
                add_field_with_evidence(
                    row, evidence, field_name=field, value=value, record_id=record_id,
                    source_file=file_path, source_type="spectral_file",
                    evidence_text=f"ENVI header samples={samples}, lines={lines}",
                    dataset_path=dataset_path, extraction_method="envi_header",
                    confidence=1.0, value_origin="file_derived",
                )
            fwhm = parse_list(header.get("fwhm"))
            if fwhm and unit:
                add_field_with_evidence(
                    row, evidence, field_name="spectral_resolution",
                    value=sum(fwhm) / len(fwhm), record_id=record_id,
                    source_file=file_path, source_type="spectral_file",
                    evidence_text="mean of ENVI 'fwhm' list", dataset_path=dataset_path,
                    extraction_method="envi_header", confidence=0.9, value_origin="calculated",
                )
                add_field_with_evidence(
                    row, evidence, field_name="spectral_resolution_unit",
                    value=row.get("spectral_range_original_unit"), record_id=record_id,
                    source_file=file_path, source_type="spectral_file",
                    evidence_text="ENVI fwhm uses the wavelength unit", dataset_path=dataset_path,
                    extraction_method="envi_header", confidence=0.9, value_origin="calculated",
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

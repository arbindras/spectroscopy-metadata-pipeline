from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from evidence.provenance import add_field_with_evidence
from models import empty_spectral_record
from normalization.spectral_units import (
    normalize_spectral_bounds,
    normalize_spectral_unit,
)


def decode_scalar(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, np.ndarray) and value.size == 1:
        return decode_scalar(value.reshape(-1)[0])
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value


def unit_from_text(text: str | None) -> str | None:
    if not text:
        return None

    lowered = text.lower()
    if (
        "wavenumber" in lowered
        or re.search(r"cm\s*[\^-]?\s*1", lowered)
        or re.search(r"1\s*/\s*cm", lowered)
        or "cm⁻¹" in lowered
    ):
        return "cm^-1"
    if (
        "µm" in lowered
        or "μm" in lowered
        or "micron" in lowered
        or "micrometer" in lowered
        or "micrometre" in lowered
        or re.search(r"\bum\b", lowered)
    ):
        return "um"
    if "angstrom" in lowered or "ångström" in lowered or re.search(r"\(\s*å\s*\)|\[\s*å\s*\]", lowered):
        return "angstrom"
    if "wavelength" in lowered and "nm" in lowered:
        return "nm"
    if re.search(r"\bnm\b", lowered):
        return "nm"
    return None


def modality_from_text(value: Any) -> str | None:
    if value is None:
        return None

    text = str(decode_scalar(value)).lower()

    if "near infrared" in text or "near-infrared" in text or re.search(r"\bnir\b", text):
        return "NIR"
    if "mid infrared" in text or "mid-infrared" in text or re.search(r"\bmir\b", text):
        return "MIR"
    if "ftir" in text or "fourier transform infrared" in text:
        return "FTIR"
    if "raman" in text:
        return "Raman"
    if "uv-vis" in text or "uv/vis" in text or "ultraviolet-visible" in text:
        return "UV-Vis"
    if "fluorescence" in text:
        return "fluorescence"
    if "terahertz" in text or re.search(r"\bthz\b", text):
        return "THz"
    if "infrared" in text:
        return "IR"

    return None


def is_evenly_spaced(values: np.ndarray) -> tuple[bool, float | None]:
    if values.size < 2:
        return False, None

    differences = np.diff(values.astype(float))
    if not np.all(np.isfinite(differences)):
        return False, None

    interval = float(np.median(np.abs(differences)))
    tolerance = max(abs(interval) * 1e-6, 1e-12)
    return bool(np.allclose(np.abs(differences), interval, atol=tolerance)), interval


def make_axis_spectral_record(
    *,
    record_id: str,
    dataset_path: Path,
    file_path: Path,
    axis_values: Iterable[float],
    unit: str | None,
    source_type: str,
    evidence_prefix: str,
    extraction_method: str,
    confidence: float,
    modality: str | None = None,
    num_spectra: int | None = None,
    num_spectra_evidence: str | None = None,
) -> tuple[dict, list[dict]]:
    values = np.asarray(list(axis_values), dtype=float)
    values = values[np.isfinite(values)]

    row = empty_spectral_record(record_id)
    row["source_file"] = str(file_path)
    evidence: list[dict] = []

    if values.size == 0:
        return row, evidence

    # Angstrom is common in astronomy (FITS) but is not one of the pipeline's
    # canonical units. Convert to nm up front and say so in the evidence.
    if unit == "angstrom":
        values = values / 10.0
        unit = "nm"
        evidence_prefix = f"{evidence_prefix}; converted from Angstrom to nm"

    # Project convention (see JCAMP FIRSTX/LASTX and tests): the "original"
    # columns keep the first/last coordinate as stored in the file; the
    # normalized wavelength_*/wavenumber_* columns are sorted ascending.
    start = float(values[0])
    end = float(values[-1])

    add_field_with_evidence(
        row,
        evidence,
        field_name="spectral_range_original_min",
        value=start,
        record_id=record_id,
        source_file=file_path,
        source_type=source_type,
        evidence_text=f"{evidence_prefix}; first coordinate={start}",
        dataset_path=dataset_path,
        extraction_method=extraction_method,
        confidence=confidence,
        value_origin="file_derived",
    )
    add_field_with_evidence(
        row,
        evidence,
        field_name="spectral_range_original_max",
        value=end,
        record_id=record_id,
        source_file=file_path,
        source_type=source_type,
        evidence_text=f"{evidence_prefix}; last coordinate={end}",
        dataset_path=dataset_path,
        extraction_method=extraction_method,
        confidence=confidence,
        value_origin="file_derived",
    )

    normalized_unit = normalize_spectral_unit(unit)
    if normalized_unit:
        add_field_with_evidence(
            row,
            evidence,
            field_name="spectral_range_original_unit",
            value=normalized_unit,
            record_id=record_id,
            source_file=file_path,
            source_type=source_type,
            evidence_text=f"{evidence_prefix}; unit={unit}",
            dataset_path=dataset_path,
            extraction_method=extraction_method,
            confidence=confidence,
            value_origin="author_provided",
        )

    add_field_with_evidence(
        row,
        evidence,
        field_name="num_spectral_channels",
        value=int(values.size),
        record_id=record_id,
        source_file=file_path,
        source_type=source_type,
        evidence_text=f"{evidence_prefix}; coordinate length={values.size}",
        dataset_path=dataset_path,
        extraction_method=extraction_method,
        confidence=1.0,
        value_origin="file_derived",
    )

    even, interval = is_evenly_spaced(values)
    if even and interval is not None:
        add_field_with_evidence(
            row,
            evidence,
            field_name="sampling_interval",
            value=interval,
            record_id=record_id,
            source_file=file_path,
            source_type=source_type,
            evidence_text=f"{evidence_prefix}; constant coordinate difference",
            dataset_path=dataset_path,
            extraction_method=extraction_method,
            confidence=1.0,
            value_origin="calculated",
        )
        if normalized_unit:
            add_field_with_evidence(
                row,
                evidence,
                field_name="sampling_interval_unit",
                value=normalized_unit,
                record_id=record_id,
                source_file=file_path,
                source_type=source_type,
                evidence_text=f"Sampling interval uses coordinate unit {normalized_unit}",
                dataset_path=dataset_path,
                extraction_method=extraction_method,
                confidence=1.0,
                value_origin="calculated",
            )

    for field, value in normalize_spectral_bounds(start, end, normalized_unit).items():
        if value is None:
            continue
        add_field_with_evidence(
            row,
            evidence,
            field_name=field,
            value=value,
            record_id=record_id,
            source_file=file_path,
            source_type="derived_from_data",
            evidence_text=(
                f"Calculated from ordered endpoints {start}, {end} "
                f"with unit {normalized_unit}"
            ),
            dataset_path=dataset_path,
            extraction_method="spectral_unit_conversion",
            confidence=1.0,
            value_origin="calculated",
        )

    if modality:
        add_field_with_evidence(
            row,
            evidence,
            field_name="modality",
            value=modality,
            record_id=record_id,
            source_file=file_path,
            source_type=source_type,
            evidence_text=f"{evidence_prefix}; modality metadata={modality}",
            dataset_path=dataset_path,
            extraction_method=extraction_method,
            confidence=0.99,
            value_origin="author_provided",
        )
    elif row.get("wavelength_min_nm") is not None and normalized_unit in {"nm", "um"}:
        inferred = modality_from_wavelength_range(
            row["wavelength_min_nm"], row["wavelength_max_nm"]
        )
        if inferred:
            add_field_with_evidence(
                row,
                evidence,
                field_name="modality",
                value=inferred,
                record_id=record_id,
                source_file=file_path,
                source_type="derived_from_data",
                evidence_text=(
                    "Inferred from wavelength range "
                    f"{row['wavelength_min_nm']:.6g}-{row['wavelength_max_nm']:.6g} nm"
                ),
                dataset_path=dataset_path,
                extraction_method="wavelength_range_rule",
                confidence=0.6,
                value_origin="inferred",
            )

    if num_spectra is not None and num_spectra > 0:
        add_field_with_evidence(
            row,
            evidence,
            field_name="num_spectra",
            value=int(num_spectra),
            record_id=record_id,
            source_file=file_path,
            source_type=source_type,
            evidence_text=num_spectra_evidence or f"{evidence_prefix}; spectra={num_spectra}",
            dataset_path=dataset_path,
            extraction_method=extraction_method,
            confidence=0.95,
            value_origin="file_derived",
        )
        add_field_with_evidence(
            row,
            evidence,
            field_name="num_spectral_values",
            value=int(num_spectra) * int(values.size),
            record_id=record_id,
            source_file=file_path,
            source_type="derived_from_data",
            evidence_text=f"{num_spectra} spectra x {values.size} channels",
            dataset_path=dataset_path,
            extraction_method="spectra_channel_multiplication",
            confidence=0.95,
            value_origin="calculated",
        )

    row["confidence"] = confidence
    return row, evidence


# Conservative wavelength bands (nm). A file is only labelled when its whole
# range falls inside one band; anything straddling bands is left NULL.
_WAVELENGTH_BANDS = (
    ("UV-Vis", 180.0, 800.0),
    ("NIR", 700.0, 2600.0),
    ("MIR", 2500.0, 25000.0),
    ("FIR", 25000.0, 1000000.0),
)


def modality_from_wavelength_range(low_nm: float, high_nm: float) -> str | None:
    if low_nm is None or high_nm is None:
        return None
    for name, low, high in _WAVELENGTH_BANDS:
        if low <= low_nm and high_nm <= high:
            return name
    if 350.0 <= low_nm and high_nm <= 2600.0:
        return "VIS-NIR"
    return None


def is_monotonic(values: np.ndarray) -> bool:
    finite = values[np.isfinite(values)]
    if finite.size < 2:
        return False
    diff = np.diff(finite)
    return bool(np.all(diff > 0) or np.all(diff < 0))


def numeric_header_axis(
    columns: list[str],
    min_count: int = 5,
) -> tuple[list[int], np.ndarray] | None:
    """Detect "wide" tables whose column headers are the spectral axis.

    Example header: ``sample_id, 400, 401, 402, ... 2500``.
    Returns the indexes of the numeric header columns and their values.
    """

    indexes: list[int] = []
    numbers: list[float] = []
    for index, column in enumerate(columns):
        text = str(column).strip()
        # Strip common decorations such as "X400", "nm_400", "400nm".
        match = re.fullmatch(r"(?:[Xx]|[Ww][Ll]_?|nm_?)?\s*([-+]?\d+(?:\.\d+)?)\s*(?:nm|cm-1|um)?", text)
        if not match:
            continue
        try:
            value = float(match.group(1))
        except ValueError:
            continue
        indexes.append(index)
        numbers.append(value)

    if len(numbers) < max(min_count, 2):
        return None

    values = np.asarray(numbers, dtype=float)
    # Reject index-like headers (1, 2, 3 ...) and PCA/component numbering.
    if not is_monotonic(values) or float(np.max(np.abs(values))) < 50:
        return None
    return indexes, values


def identify_explicit_axis_column(columns: list[str]) -> tuple[str, str | None] | None:
    patterns = (
        "wavelength",
        "wavenumber",
        "wave_number",
        "spectral_axis",
        "frequency_cm",
    )

    matches = [
        column for column in columns
        if any(pattern in str(column).lower() for pattern in patterns)
    ]

    if len(matches) != 1:
        return None

    column = matches[0]
    return column, unit_from_text(column)

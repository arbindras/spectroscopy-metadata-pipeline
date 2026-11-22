from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SPECTRAL_COLUMNS = [
    "record_id",
    "modality",
    "spectral_range_original_min",
    "spectral_range_original_max",
    "spectral_range_original_unit",
    "wavelength_min_nm",
    "wavelength_max_nm",
    "wavenumber_min_cm1",
    "wavenumber_max_cm1",
    "num_spectral_channels",
    "spectral_resolution",
    "spectral_resolution_unit",
    "sampling_interval",
    "sampling_interval_unit",
    "num_samples",
    "num_spectra",
    "num_images",
    "num_pixels",
    "num_spectral_values",
    "image_height",
    "image_width",
    "spatial_resolution",
    "spatial_resolution_unit",
    "spectral_target_relationship",
    "source_file",
    "confidence",
]


@dataclass
class ReaderResult:
    spectral_records: list[dict[str, Any]] = field(default_factory=list)
    evidence_records: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


def empty_spectral_record(record_id: str) -> dict[str, Any]:
    row = {column: None for column in SPECTRAL_COLUMNS}
    row["record_id"] = str(record_id)
    row["confidence"] = 0.0
    return row

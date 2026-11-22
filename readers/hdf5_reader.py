from __future__ import annotations

from pathlib import Path
from typing import Any

import h5py
import numpy as np

from evidence.provenance import add_field_with_evidence
from models import ReaderResult
from readers.base_reader import BaseReader
from readers.spectral_helpers import (
    decode_scalar,
    make_axis_spectral_record,
    modality_from_text,
    unit_from_text,
)


AXIS_NAMES = {
    "wavelength",
    "wavelengths",
    "wavenumber",
    "wavenumbers",
    "spectral_axis",
    "spectralaxis",
    "bands",
    "band_centers",
}


AXIS_NAME_FRAGMENTS = (
    "wavelength",
    "wavenumber",
    "wave_number",
    "spectral_axis",
    "spectral_grid",
    "spectralgrid",
    "raman_shift",
)


def is_axis_name(basename: str) -> bool:
    """Exact coordinate names, or names that clearly denote a spectral grid
    (e.g. ``spectrum_wavenumber``, ``wavelength_nm``). Names that only
    describe a resolution/step (``wavelength_step``) are excluded."""
    name = basename.lower()
    if name in AXIS_NAMES:
        return True
    if any(word in name for word in ("step", "resolution", "delta", "error", "width")):
        return False
    return any(fragment in name for fragment in AXIS_NAME_FRAGMENTS)


def find_attribute(attributes: Any, names: set[str]) -> Any:
    for key in attributes.keys():
        if str(key).lower() in names:
            return decode_scalar(attributes[key])
    return None


class HDF5Reader(BaseReader):
    # NetCDF-4 (.nc/.nc4/.cdf) files are HDF5 containers; see NetCDFReader
    # for the NetCDF-3 "classic" fallback.
    extensions = {".h5", ".hdf5", ".he5"}

    def read(
        self,
        *,
        record_id: str,
        dataset_path: Path,
        file_path: Path,
    ) -> ReaderResult:
        result = ReaderResult()
        max_coordinates = int(
            self.reader_config.get("max_coordinate_values", 1000000)
        )

        try:
            with h5py.File(file_path, "r") as handle:
                datasets: dict[str, h5py.Dataset] = {}

                def collect(name: str, obj: Any) -> None:
                    if isinstance(obj, h5py.Dataset):
                        datasets[name] = obj

                handle.visititems(collect)

                root_modality = find_attribute(
                    handle.attrs,
                    {"modality", "technique", "spectroscopy_type"},
                )

                for name, dataset in datasets.items():
                    basename = name.rsplit("/", 1)[-1].lower()
                    if not is_axis_name(basename):
                        continue
                    if dataset.ndim != 1:
                        continue
                    if dataset.size == 0 or dataset.size > max_coordinates:
                        continue
                    if not np.issubdtype(dataset.dtype, np.number):
                        continue

                    values = np.asarray(dataset[...], dtype=float)
                    unit_value = find_attribute(
                        dataset.attrs,
                        {"unit", "units", "xunits", "x_units"},
                    )
                    unit = unit_from_text(
                        f"{name} {decode_scalar(unit_value)}"
                    )

                    modality_value = find_attribute(
                        dataset.attrs,
                        {"modality", "technique", "spectroscopy_type"},
                    )
                    modality = modality_from_text(
                        modality_value or root_modality
                    )

                    row, evidence = make_axis_spectral_record(
                        record_id=record_id,
                        dataset_path=dataset_path,
                        file_path=file_path,
                        axis_values=values,
                        unit=unit,
                        source_type="spectral_file",
                        evidence_prefix=(
                            f"HDF5 dataset /{name}, "
                            f"shape={dataset.shape}, dtype={dataset.dtype}"
                        ),
                        extraction_method="hdf5_coordinate_dataset",
                        confidence=1.0,
                        modality=modality,
                    )

                    self._add_matching_array_structure(
                        row=row,
                        evidence=evidence,
                        record_id=record_id,
                        dataset_path=dataset_path,
                        file_path=file_path,
                        coordinate_name=name,
                        channel_count=int(values.size),
                        datasets=datasets,
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

    def _add_matching_array_structure(
        self,
        *,
        row: dict,
        evidence: list[dict],
        record_id: str,
        dataset_path: Path,
        file_path: Path,
        coordinate_name: str,
        channel_count: int,
        datasets: dict[str, h5py.Dataset],
    ) -> None:
        candidates = []

        for name, dataset in datasets.items():
            if name == coordinate_name or dataset.ndim < 1:
                continue

            matching_axes = [
                index for index, size in enumerate(dataset.shape)
                if int(size) == channel_count
            ]
            if len(matching_axes) == 1:
                candidates.append((name, dataset, matching_axes[0]))

        if len(candidates) != 1:
            return

        name, dataset, spectral_axis = candidates[0]
        shape = tuple(int(value) for value in dataset.shape)
        prefix = f"HDF5 dataset /{name}, shape={shape}, spectral_axis={spectral_axis}"

        add_field_with_evidence(
            row,
            evidence,
            field_name="num_spectral_values",
            value=int(np.prod(shape)),
            record_id=record_id,
            source_file=file_path,
            source_type="spectral_file",
            evidence_text=prefix,
            dataset_path=dataset_path,
            extraction_method="hdf5_shape_inspection",
            confidence=1.0,
            value_origin="file_derived",
        )

        non_spectral = [
            size for index, size in enumerate(shape)
            if index != spectral_axis
        ]

        if dataset.ndim == 1:
            spectra_count = 1
        else:
            spectra_count = int(np.prod(non_spectral))

        add_field_with_evidence(
            row,
            evidence,
            field_name="num_spectra",
            value=spectra_count,
            record_id=record_id,
            source_file=file_path,
            source_type="spectral_file",
            evidence_text=prefix,
            dataset_path=dataset_path,
            extraction_method="hdf5_shape_inspection",
            confidence=1.0,
            value_origin="file_derived",
        )

        if dataset.ndim == 3 and len(non_spectral) == 2:
            height, width = non_spectral

            for field, value in (
                ("image_height", height),
                ("image_width", width),
            ):
                add_field_with_evidence(
                    row,
                    evidence,
                    field_name=field,
                    value=value,
                    record_id=record_id,
                    source_file=file_path,
                    source_type="spectral_file",
                    evidence_text=prefix,
                    dataset_path=dataset_path,
                    extraction_method="hdf5_shape_inspection",
                    confidence=1.0,
                    value_origin="file_derived",
                )

            add_field_with_evidence(
                row,
                evidence,
                field_name="num_pixels",
                value=height * width,
                record_id=record_id,
                source_file=file_path,
                source_type="derived_from_data",
                evidence_text=f"{height} × {width}",
                dataset_path=dataset_path,
                extraction_method="image_dimension_multiplication",
                confidence=1.0,
                value_origin="calculated",
            )

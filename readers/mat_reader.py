from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy.io import loadmat, whosmat

from models import ReaderResult
from readers.base_reader import BaseReader
from readers.hdf5_reader import HDF5Reader
from readers.spectral_helpers import make_axis_spectral_record, unit_from_text


AXIS_VARIABLE_NAMES = {
    "wavelength",
    "wavelengths",
    "wavenumber",
    "wavenumbers",
    "spectral_axis",
    "bands",
}


class MATReader(BaseReader):
    extensions = {".mat"}

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
            variables = whosmat(file_path)
        except (NotImplementedError, ValueError):
            # MATLAB v7.3 files are HDF5 containers.
            return HDF5Reader(self.config).read(
                record_id=record_id,
                dataset_path=dataset_path,
                file_path=file_path,
            )
        except Exception as exc:
            result.errors.append({
                "record_id": record_id,
                "source_file": str(file_path),
                "reader": type(self).__name__,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            })
            return result

        for variable_name, shape, _mat_type in variables:
            normalized_name = variable_name.lower()
            if normalized_name not in AXIS_VARIABLE_NAMES:
                continue

            size = int(np.prod(shape))
            if size == 0 or size > max_coordinates:
                continue
            if len(shape) > 2 or (len(shape) == 2 and min(shape) != 1):
                continue

            try:
                loaded = loadmat(
                    file_path,
                    variable_names=[variable_name],
                    squeeze_me=True,
                )
                values = np.asarray(loaded[variable_name], dtype=float).reshape(-1)
            except Exception as exc:
                result.errors.append({
                    "record_id": record_id,
                    "source_file": str(file_path),
                    "reader": type(self).__name__,
                    "error_type": type(exc).__name__,
                    "error_message": f"{variable_name}: {exc}",
                })
                continue

            row, evidence = make_axis_spectral_record(
                record_id=record_id,
                dataset_path=dataset_path,
                file_path=file_path,
                axis_values=values,
                unit=unit_from_text(variable_name),
                source_type="spectral_file",
                evidence_prefix=(
                    f"MAT variable {variable_name!r}, shape={shape}"
                ),
                extraction_method="mat_coordinate_variable",
                confidence=1.0,
            )
            result.spectral_records.append(row)
            result.evidence_records.extend(evidence)

        return result

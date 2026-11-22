"""NetCDF reader.

* NetCDF-4 files (magic ``\\x89HDF``) are HDF5 containers and are delegated
  to :class:`HDF5Reader` (h5py), which already knows how to find coordinate
  datasets such as ``wavenumber`` or ``wavelength``.
* NetCDF-3 "classic" files (magic ``CDF\\x01`` / ``CDF\\x02``) are read with
  ``scipy.io.netcdf_file`` (scipy is already a dependency).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from models import ReaderResult
from readers.base_reader import BaseReader
from readers.hdf5_reader import HDF5Reader, is_axis_name
from readers.spectral_helpers import (
    decode_scalar,
    make_axis_spectral_record,
    modality_from_text,
    unit_from_text,
)


class NetCDFReader(BaseReader):
    extensions = {".nc", ".nc4", ".cdf", ".netcdf"}

    def read(
        self,
        *,
        record_id: str,
        dataset_path: Path,
        file_path: Path,
    ) -> ReaderResult:
        with file_path.open("rb") as stream:
            magic = stream.read(4)

        if magic.startswith(b"\x89HDF"):
            return HDF5Reader(self.config).read(
                record_id=record_id,
                dataset_path=dataset_path,
                file_path=file_path,
            )

        result = ReaderResult()
        if not magic.startswith(b"CDF"):
            return result

        max_coordinates = int(
            self.reader_config.get("max_coordinate_values", 1000000)
        )
        try:
            from scipy.io import netcdf_file

            with netcdf_file(file_path, "r", mmap=False) as handle:
                global_text = " ".join(
                    str(decode_scalar(v)) for v in handle._attributes.values()
                )
                for name, variable in handle.variables.items():
                    if not is_axis_name(name):
                        continue
                    if variable.data.ndim != 1:
                        continue
                    if variable.data.size == 0 or variable.data.size > max_coordinates:
                        continue
                    if not np.issubdtype(variable.data.dtype, np.number):
                        continue

                    values = np.asarray(variable.data, dtype=float).copy()
                    unit_attr = getattr(variable, "units", b"")
                    unit = unit_from_text(f"{name} {decode_scalar(unit_attr)}")

                    row, evidence = make_axis_spectral_record(
                        record_id=record_id,
                        dataset_path=dataset_path,
                        file_path=file_path,
                        axis_values=values,
                        unit=unit,
                        source_type="spectral_file",
                        evidence_prefix=(
                            f"NetCDF-3 variable {name!r}, shape={variable.data.shape}, "
                            f"units={decode_scalar(unit_attr)!r}"
                        ),
                        extraction_method="netcdf3_coordinate_variable",
                        confidence=1.0,
                        modality=modality_from_text(global_text),
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

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from models import ReaderResult
from readers.base_reader import BaseReader
from readers.spectral_helpers import (
    identify_explicit_axis_column,
    is_monotonic,
    make_axis_spectral_record,
    numeric_header_axis,
    unit_from_text,
)


def _is_number(text: str) -> bool:
    try:
        float(text)
    except ValueError:
        return False
    return True


def csv_read_options(path: Path, probe_bytes: int = 65536) -> dict:
    """Encoding (UTF-8, else Latin-1 - e.g. IODP reports with 'µ') and the
    number of leading ``#`` comment lines (e.g. a description preamble)."""
    with path.open("rb") as stream:
        head = stream.read(probe_bytes)
    encoding = "utf-8-sig"
    try:
        head.decode("utf-8")
    except UnicodeDecodeError as exc:
        if exc.start < len(head) - 4:  # not just a multibyte char cut at the probe end
            encoding = "latin-1"
    skip = 0
    for line in head.decode(encoding, errors="replace").splitlines():
        if line.lstrip().startswith("#"):
            skip += 1
        else:
            break
    return {"encoding": encoding, "skiprows": skip}


class CSVReader(BaseReader):
    extensions = {".csv", ".tsv"}

    def read(
        self,
        *,
        record_id: str,
        dataset_path: Path,
        file_path: Path,
    ) -> ReaderResult:
        result = ReaderResult()
        separator = "\t" if file_path.suffix.lower() == ".tsv" else ","
        chunk_size = int(self.reader_config.get("csv_chunk_size", 50000))

        try:
            self._opts = csv_read_options(file_path)
            header =pd.read_csv(file_path, sep=separator, nrows=0, **self._opts)
            columns = [str(column) for column in header.columns]
            if columns and all(_is_number(column) for column in columns):
                return self._read_headerless(
                    result=result,
                    record_id=record_id,
                    dataset_path=dataset_path,
                    file_path=file_path,
                    separator=separator,
                )
            axis = identify_explicit_axis_column(columns)

            if axis is None:
                return self._read_wide_table(
                    result=result,
                    record_id=record_id,
                    dataset_path=dataset_path,
                    file_path=file_path,
                    separator=separator,
                    columns=columns,
                    chunk_size=chunk_size,
                )

            axis_column, unit = axis
            values: list[np.ndarray] = []

            for chunk in pd.read_csv(
                file_path,
                sep=separator,
                **self._opts,
                usecols=[axis_column],
                chunksize=chunk_size,
            ):
                numeric = pd.to_numeric(chunk[axis_column], errors="coerce")
                valid = numeric.dropna().to_numpy(dtype=float)
                if valid.size:
                    values.append(valid)

            if not values:
                return result

            axis_values = np.concatenate(values)
            row, evidence = make_axis_spectral_record(
                record_id=record_id,
                dataset_path=dataset_path,
                file_path=file_path,
                axis_values=axis_values,
                unit=unit,
                source_type="spectral_file",
                evidence_prefix=f"CSV column {axis_column!r}",
                extraction_method="csv_explicit_axis_column",
                confidence=0.99,
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

    def _read_headerless(
        self,
        *,
        result: ReaderResult,
        record_id: str,
        dataset_path: Path,
        file_path: Path,
        separator: str,
    ) -> ReaderResult:
        """Purely numeric CSV without a header row (instrument exports such
        as ``wavenumber,absorbance``). The first column is accepted as the
        spectral axis only when monotonic; the unit is unknown, so only the
        original range and channel count are recorded, at low confidence."""
        min_points = int(self.reader_config.get("text_min_points", 10))
        frame = pd.read_csv(file_path, sep=separator, header=None, **self._opts)
        frame = frame.apply(pd.to_numeric, errors="coerce").dropna(axis=1, how="all")
        if frame.shape[1] < 2:
            return result
        axis_values = frame.iloc[:, 0].dropna().to_numpy(dtype=float)
        if axis_values.size < min_points or not is_monotonic(axis_values):
            return result

        row, evidence = make_axis_spectral_record(
            record_id=record_id,
            dataset_path=dataset_path,
            file_path=file_path,
            axis_values=axis_values,
            unit=None,
            source_type="spectral_file",
            evidence_prefix=f"Headerless numeric CSV, {frame.shape[0]} rows x {frame.shape[1]} columns",
            extraction_method="csv_headerless_first_column_axis",
            confidence=0.5,
            num_spectra=frame.shape[1] - 1,
            num_spectra_evidence=f"{frame.shape[1] - 1} value column(s) after the axis column",
        )
        result.spectral_records.append(row)
        result.evidence_records.extend(evidence)
        return result

    def _read_wide_table(
        self,
        *,
        result: ReaderResult,
        record_id: str,
        dataset_path: Path,
        file_path: Path,
        separator: str,
        columns: list[str],
        chunk_size: int,
    ) -> ReaderResult:
        """Wide layout: one spectrum per row, spectral axis in the header
        (e.g. ``id, 400, 402, 404, ...``)."""
        min_count = int(self.reader_config.get("numeric_header_min_count", 5))
        detected = numeric_header_axis(columns, min_count=min_count)
        if detected is None:
            return result

        indexes, axis_values = detected
        rows = 0
        for chunk in pd.read_csv(
            file_path,
            sep=separator,
            **self._opts,
            usecols=[indexes[0]],
            chunksize=chunk_size,
        ):
            rows += len(chunk)

        # Units are only recorded when the header text states one.
        unit = unit_from_text(" ".join(columns[i] for i in indexes[:3]))
        row, evidence = make_axis_spectral_record(
            record_id=record_id,
            dataset_path=dataset_path,
            file_path=file_path,
            axis_values=axis_values,
            unit=unit,
            source_type="spectral_file",
            evidence_prefix=(
                f"CSV numeric header columns {columns[indexes[0]]!r}..."
                f"{columns[indexes[-1]]!r} ({len(indexes)} columns)"
            ),
            extraction_method="csv_numeric_header_axis",
            confidence=0.85,
            num_spectra=rows or None,
            num_spectra_evidence=f"{rows} data rows in wide table",
        )
        result.spectral_records.append(row)
        result.evidence_records.extend(evidence)
        return result

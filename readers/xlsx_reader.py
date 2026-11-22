from __future__ import annotations

from pathlib import Path

import numpy as np
from openpyxl import load_workbook

from models import ReaderResult
from readers.base_reader import BaseReader
from readers.spectral_helpers import (
    identify_explicit_axis_column,
    make_axis_spectral_record,
)


class XLSXReader(BaseReader):
    extensions = {".xlsx"}

    def read(
        self,
        *,
        record_id: str,
        dataset_path: Path,
        file_path: Path,
    ) -> ReaderResult:
        result = ReaderResult()
        max_rows = int(self.reader_config.get("xlsx_max_rows", 1000000))

        try:
            workbook = load_workbook(
                file_path,
                read_only=True,
                data_only=True,
            )

            for worksheet in workbook.worksheets:
                rows = worksheet.iter_rows(values_only=True)
                header = next(rows, None)
                if not header:
                    continue

                columns = [
                    str(value) if value is not None else ""
                    for value in header
                ]
                axis = identify_explicit_axis_column(columns)
                if axis is None:
                    continue

                axis_column, unit = axis
                column_index = columns.index(axis_column)
                values: list[float] = []

                for row_index, row in enumerate(rows):
                    if row_index >= max_rows:
                        break
                    if column_index >= len(row):
                        continue
                    try:
                        value = float(row[column_index])
                    except (TypeError, ValueError):
                        continue
                    if np.isfinite(value):
                        values.append(value)

                if not values:
                    continue

                spectral_row, evidence = make_axis_spectral_record(
                    record_id=record_id,
                    dataset_path=dataset_path,
                    file_path=file_path,
                    axis_values=values,
                    unit=unit,
                    source_type="metadata_file",
                    evidence_prefix=(
                        f"XLSX sheet {worksheet.title!r}, "
                        f"column {axis_column!r}"
                    ),
                    extraction_method="xlsx_explicit_axis_column",
                    confidence=0.99,
                )
                result.spectral_records.append(spectral_row)
                result.evidence_records.extend(evidence)

            workbook.close()

        except Exception as exc:
            result.errors.append({
                "record_id": record_id,
                "source_file": str(file_path),
                "reader": type(self).__name__,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            })

        return result

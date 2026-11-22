from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq


FILE_SCHEMA = pa.schema([
    ("record_id", pa.string()),
    ("file_path", pa.string()),
    ("relative_path", pa.string()),
    ("file_name", pa.string()),
    ("extension", pa.string()),
    ("file_size_bytes", pa.int64()),
    ("parent_directory", pa.string()),
    ("is_archive", pa.bool_()),
    ("is_document", pa.bool_()),
    ("is_spectral", pa.bool_()),
    ("is_tabular", pa.bool_()),
    ("is_image", pa.bool_()),
    ("scan_status", pa.string()),
])

SPECTRAL_SCHEMA = pa.schema([
    ("record_id", pa.string()),
    ("modality", pa.string()),
    ("spectral_range_original_min", pa.float64()),
    ("spectral_range_original_max", pa.float64()),
    ("spectral_range_original_unit", pa.string()),
    ("wavelength_min_nm", pa.float64()),
    ("wavelength_max_nm", pa.float64()),
    ("wavenumber_min_cm1", pa.float64()),
    ("wavenumber_max_cm1", pa.float64()),
    ("num_spectral_channels", pa.int64()),
    ("spectral_resolution", pa.float64()),
    ("spectral_resolution_unit", pa.string()),
    ("sampling_interval", pa.float64()),
    ("sampling_interval_unit", pa.string()),
    ("num_samples", pa.int64()),
    ("num_spectra", pa.int64()),
    ("num_images", pa.int64()),
    ("num_pixels", pa.int64()),
    ("num_spectral_values", pa.int64()),
    ("image_height", pa.int64()),
    ("image_width", pa.int64()),
    ("spatial_resolution", pa.float64()),
    ("spatial_resolution_unit", pa.string()),
    ("spectral_target_relationship", pa.string()),
    ("source_file", pa.string()),
    ("confidence", pa.float64()),
])

EVIDENCE_SCHEMA = pa.schema([
    ("record_id", pa.string()),
    ("field_name", pa.string()),
    ("field_value", pa.string()),
    ("source_file", pa.string()),
    ("source_type", pa.string()),
    ("evidence_text", pa.string()),
    ("page_number", pa.int64()),
    ("section", pa.string()),
    ("dataset_path", pa.string()),
    ("extraction_method", pa.string()),
    ("confidence", pa.float64()),
    ("value_origin", pa.string()),
    ("timestamp", pa.timestamp("us", tz="UTC")),
])

ERROR_SCHEMA = pa.schema([
    ("record_id", pa.string()),
    ("source_file", pa.string()),
    ("reader", pa.string()),
    ("error_type", pa.string()),
    ("error_message", pa.string()),
])

SCHEMAS = {
    "dataset_file_index": FILE_SCHEMA,
    "spectroscopy_metadata": SPECTRAL_SCHEMA,
    "evidence": EVIDENCE_SCHEMA,
    "extraction_errors": ERROR_SCHEMA,
}


def safe_record_key(record_id: str) -> str:
    return hashlib.sha256(str(record_id).encode("utf-8")).hexdigest()[:24]


class ParquetStore:
    def __init__(self, output_directory: str | Path):
        self.output_directory = Path(output_directory).resolve()
        self.fragment_directory = self.output_directory / "_fragments"
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.fragment_directory.mkdir(parents=True, exist_ok=True)

    def write_fragment(
        self,
        table_name: str,
        record_id: str,
        rows: list[dict[str, Any]],
    ) -> None:
        schema = SCHEMAS[table_name]
        directory = self.fragment_directory / table_name
        directory.mkdir(parents=True, exist_ok=True)

        destination = directory / f"{safe_record_key(record_id)}.parquet"
        temporary = destination.with_suffix(".parquet.tmp")

        table = pa.Table.from_pylist(rows, schema=schema)
        pq.write_table(table, temporary, compression="zstd")
        os.replace(temporary, destination)

    def consolidate(self, table_name: str) -> Path:
        schema = SCHEMAS[table_name]
        directory = self.fragment_directory / table_name
        destination = self.output_directory / f"{table_name}.parquet"
        temporary = destination.with_suffix(".parquet.tmp")

        fragments = sorted(directory.glob("*.parquet")) if directory.exists() else []

        if fragments:
            tables = [pq.read_table(path, schema=schema) for path in fragments]
            table = pa.concat_tables(tables)
        else:
            table = pa.Table.from_pylist([], schema=schema)

        pq.write_table(table, temporary, compression="zstd")
        os.replace(temporary, destination)
        return destination

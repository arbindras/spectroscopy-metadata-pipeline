from __future__ import annotations

import pytest


@pytest.fixture
def base_config(tmp_path):
    return {
        "paths": {
            "metadata_file": str(tmp_path / "metadata.parquet"),
            "dataset_roots": [str(tmp_path / "datasets")],
            "output_directory": str(tmp_path / "output"),
        },
        "mapping": {
            "mapping_file": None,
            "allow_exact_doi_directory_match": True,
            "allow_exact_title_directory_match": True,
            "search_depth": 2,
        },
        "scanner": {
            "inspect_archives": True,
            "max_archive_members": 1000,
        },
        "readers": {
            "max_coordinate_values": 100000,
            "csv_chunk_size": 100,
            "xlsx_max_rows": 10000,
            "jcamp_max_header_bytes": 100000,
        },
        "pipeline": {
            "write_empty_spectral_row": True,
        },
    }

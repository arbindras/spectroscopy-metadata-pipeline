from __future__ import annotations

import pandas as pd

from pipeline import load_metadata


def test_load_metadata_reads_csv_and_normalizes_record_id(tmp_path):
    metadata_path = tmp_path / "metadata.csv"
    pd.DataFrame({"record_id": [123], "title": ["Example"]}).to_csv(
        metadata_path,
        index=False,
    )

    result = load_metadata({"paths": {"metadata_file": metadata_path}})

    assert result.loc[0, "record_id"] == "123"


def test_load_metadata_reads_parquet(tmp_path):
    metadata_path = tmp_path / "metadata.parquet"
    pd.DataFrame({"record_id": ["abc"]}).to_parquet(metadata_path, index=False)

    result = load_metadata({"paths": {"metadata_file": metadata_path}})

    assert result.loc[0, "record_id"] == "abc"

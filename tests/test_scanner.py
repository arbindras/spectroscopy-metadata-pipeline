import zipfile

from scanner.file_indexer import FileIndexer


def test_archive_is_indexed_without_extraction(base_config, tmp_path):
    dataset = tmp_path / "dataset"
    dataset.mkdir()

    archive_path = dataset / "spectra.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("inside/example.jdx", "##TITLE=test")

    rows = FileIndexer(base_config).scan("123", dataset)

    archive_rows = [row for row in rows if row["file_name"] == "spectra.zip"]
    member_rows = [row for row in rows if row["file_name"] == "example.jdx"]

    assert len(archive_rows) == 1
    assert archive_rows[0]["is_archive"]
    assert len(member_rows) == 1
    assert member_rows[0]["is_spectral"]
    assert "::" in member_rows[0]["file_path"]


def test_direct_record_id_mapping(base_config, tmp_path):
    import pandas as pd

    from scanner.dataset_scanner import DatasetMapper

    root = tmp_path / "datasets"
    dataset = root / "123456"
    dataset.mkdir(parents=True)

    mapper = DatasetMapper(base_config)
    result = mapper.map_dataset({
        "record_id": "123456",
        "doi": None,
        "title": "Example",
    })

    assert result["mapping_status"] == "resolved_record_id"
    assert result["dataset_local_path"] == str(dataset.resolve())


def test_relative_explicit_mapping_is_resolved_from_dataset_root(
    base_config, tmp_path
):
    import pandas as pd

    from scanner.dataset_scanner import DatasetMapper

    root = tmp_path / "datasets"
    dataset = root / "19060_Spectra_from_BANYAN_VII"
    dataset.mkdir(parents=True)

    mapping_file = tmp_path / "mapping.csv"
    pd.DataFrame({
        "record_id": ["19060"],
        "dataset_local_path": [dataset.name],
    }).to_csv(mapping_file, index=False)
    base_config["mapping"]["mapping_file"] = str(mapping_file)

    result = DatasetMapper(base_config).map_dataset({
        "record_id": "19060",
        "doi": None,
        "title": "Spectra from BANYAN VII",
    })

    assert result["mapping_status"] == "resolved_explicit"
    assert result["dataset_local_path"] == str(dataset.resolve())

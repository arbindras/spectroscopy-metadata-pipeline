"""Batch1 layouts: archive-file datasets, nested/damaged archives, new readers."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import numpy as np

from readers.csv_reader import CSVReader
from readers.exomol_reader import ExoMolReader
from readers.text_reader import TextReader
from scanner import archive_access
from scanner.dataset_scanner import DatasetMapper
from scanner.file_indexer import FileIndexer


def _nested_zip(path: Path) -> None:
    inner = io.BytesIO()
    with zipfile.ZipFile(inner, "w") as archive:
        rows = "\n".join(f"{w:.3f},{0.1:.3f}" for w in np.linspace(4000, 400, 50))
        archive.writestr("FTIR/sample1.dpt", rows)
        archive.writestr("README.txt", "FTIR spectra of samples")
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("data.zip", inner.getvalue())
        archive.writestr("__MACOSX/._data.zip", "junk")
        archive.writestr("folder/.DS_Store", "junk")


def test_prefix_mapping_resolves_archive_file(base_config, tmp_path):
    root = tmp_path / "datasets"
    root.mkdir()
    dataset = root / "5218787_Surface_characterization.zip"
    _nested_zip(dataset)

    mapper = DatasetMapper(base_config)
    result = mapper.map_dataset({"record_id": "5218787", "doi": None, "title": "x"})

    assert result["mapping_status"] == "resolved_record_id_prefix"
    assert result["dataset_local_path"] == str(dataset.resolve())
    assert "5218787" in mapper.local_record_ids()


def test_indexer_walks_nested_archives_and_skips_junk(base_config, tmp_path):
    dataset = tmp_path / "123_x.zip"
    _nested_zip(dataset)

    rows = FileIndexer(base_config).scan("123", dataset)
    paths = [row["file_path"] for row in rows]

    assert paths[0] == str(dataset.resolve())
    assert any(p.endswith("data.zip::FTIR/sample1.dpt") for p in paths)
    assert not any("__MACOSX" in p or "DS_Store" in p for p in paths)


def test_nested_member_extraction_and_dpt_reader(base_config, tmp_path):
    dataset = tmp_path / "123_x.zip"
    _nested_zip(dataset)
    virtual = f"{dataset}::data.zip::FTIR/sample1.dpt"

    target = archive_access.extract_member(virtual, tmp_path / "sample1.dpt")
    row = TextReader(base_config).read(
        record_id="123", dataset_path=dataset, file_path=target
    ).spectral_records[0]

    assert row["spectral_range_original_unit"] == "cm^-1"
    assert row["num_spectral_channels"] == 50
    assert abs(row["wavenumber_max_cm1"] - 4000) < 1e-9


def test_keep_open_reuses_zip_chain_until_closed(tmp_path):
    dataset = tmp_path / "123_x.zip"
    _nested_zip(dataset)
    first = f"{dataset}::data.zip::FTIR/sample1.dpt"
    second = f"{dataset}::data.zip::README.txt"

    try:
        archive_access.extract_member(first, tmp_path / "a.dpt", keep_open=True)
        cached = archive_access._cached_chain
        archive_access.extract_member(second, tmp_path / "b.txt", keep_open=True)
        assert archive_access._cached_chain is cached
    finally:
        archive_access.close_cached()

    assert archive_access._cached_chain is None
    assert (tmp_path / "b.txt").read_text() == "FTIR spectra of samples"
    dataset.unlink()  # no handle left open (Windows would refuse)


def test_damaged_zip_members_are_recovered(base_config, tmp_path):
    good = tmp_path / "good.zip"
    with zipfile.ZipFile(good, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("a.txt", "first member")
        archive.writestr("b.txt", "second member " * 100)
    data = good.read_bytes()
    damaged = tmp_path / "999_damaged.zip"
    cut = data.find(b"PK\x01\x02")  # drop the central directory
    damaged.write_bytes(data[:cut] + b"\0" * 4096)

    rows = FileIndexer(base_config).scan("999", damaged)
    members = [row for row in rows if "::" in row["file_path"]]

    assert rows[0]["scan_status"] == "archive_partially_recovered"
    assert {row["file_name"] for row in members} == {"a.txt", "b.txt"}
    assert all(row["scan_status"] == "archive_member_recovered" for row in members)
    assert archive_access.read_member_bytes(f"{damaged}::b.txt").startswith(b"second")


def test_exomol_def_reader(base_config, tmp_path):
    path = tmp_path / "39K-35Cl__Barton.def"
    path.write_text(
        "EXOMOL.def      # ID\n"
        "(39K)(35Cl)     # IsoFormula\n"
        "Barton          # Isotopologue dataset name\n"
        "3000.00         # Maximum temperature of linelist\n"
        "60741           # No. of states in .states file\n"
        "1326765         # Total number of transitions\n"
        "2927.25         # Maximum wavenumber (in cm-1)\n"
    )
    row = ExoMolReader(base_config).read(
        record_id="5716977", dataset_path=tmp_path, file_path=path
    ).spectral_records[0]

    assert row["wavenumber_max_cm1"] == 2927.25
    assert row["num_spectral_values"] == 1326765
    assert "39K" in row["modality"]


def test_text_reader_utf16_time_wavelength_matrix(base_config, tmp_path):
    path = tmp_path / "kinetics.TXT"
    wavelengths = list(range(190, 260))
    lines = ["Name: | Date: 6/24/21", "X/Z\tNm\tNw", "2\t15\t70",
             "Time-WL\t" + "\t".join(str(w) for w in wavelengths)]
    for t in (1.5, 61.5, 121.5):
        lines.append(f"{t}\t" + "\t".join("0.1" for _ in wavelengths))
    path.write_bytes("\r\n".join(lines).encode("utf-16"))

    row = TextReader(base_config).read(
        record_id="1", dataset_path=tmp_path, file_path=path
    ).spectral_records[0]

    assert row["spectral_range_original_unit"] == "nm"
    assert row["num_spectral_channels"] == len(wavelengths)
    assert row["num_spectra"] == 3


def test_text_reader_ocean_optics_export(base_config, tmp_path):
    path = tmp_path / "shot_NIRQuest.txt"
    lines = ["SpectraSuite Data File", "Integration Time (usec): 100000",
             ">>>>>Begin Processed Spectral Data<<<<<"]
    lines += [f"{w:.2f}\t{100.0:.1f}" for w in np.linspace(899.34, 1720.27, 64)]
    lines.append(">>>>>End Processed Spectral Data<<<<<")
    path.write_text("\n".join(lines))

    row = TextReader(base_config).read(
        record_id="1", dataset_path=tmp_path, file_path=path
    ).spectral_records[0]

    assert row["spectral_range_original_unit"] == "nm"
    assert abs(row["wavelength_max_nm"] - 1720.27) < 1e-6


def test_csv_headerless_numeric(base_config, tmp_path):
    path = tmp_path / "1b_acacia_1.CSV"
    path.write_text("\n".join(f"{w:.4e},{0.5:.4e}" for w in np.linspace(399.7, 4000.1, 40)))

    row = CSVReader(base_config).read(
        record_id="1", dataset_path=tmp_path, file_path=path
    ).spectral_records[0]

    assert row["num_spectral_channels"] == 40
    assert row["spectral_range_original_unit"] is None
    assert row["confidence"] == 0.5


def test_pipeline_archive_dataset_with_readme_unit(base_config, tmp_path):
    import pandas as pd

    from pipeline import Pipeline

    root = tmp_path / "datasets"
    root.mkdir()
    dataset = root / "5564539_Infrared_spectra.zip"
    with zipfile.ZipFile(dataset, "w") as archive:
        archive.writestr(
            "README.txt",
            "column 1 (x) is in increasing wavenumber (cm^-1)\ncolumn 2 is optical depth",
        )
        archive.writestr(
            "En99tau.dat",
            "\n".join(f"{w:.3f}  {0.01:.4f}" for w in np.linspace(80, 1200, 100)),
        )
    pd.DataFrame({"record_id": ["5564539"], "title": ["Pyroxenes"]}).to_parquet(
        base_config["paths"]["metadata_file"]
    )
    base_config["readers"]["text_accept_unlabelled_axis"] = True

    pipeline = Pipeline(base_config)
    assert pipeline.selected_record_ids() == ["5564539"]
    pipeline.process_record("5564539")
    pipeline.consolidate()

    output = Path(base_config["paths"]["output_directory"])
    rows = pd.read_parquet(output / "spectroscopy_metadata.parquet")
    row = rows.iloc[0]
    assert row["spectral_range_original_unit"] == "cm^-1"
    assert abs(row["wavenumber_max_cm1"] - 1200) < 1e-9
    assert pipeline.state.status("5564539") == "completed"


def test_tgz_inside_zip_members_read_in_one_pass(base_config, tmp_path):
    import tarfile

    from pipeline import Pipeline
    import pandas as pd

    tgz = io.BytesIO()
    with tarfile.open(fileobj=tgz, mode="w:gz") as tar:
        for i in range(3):
            text = "# wavenumber (cm-1) absorbance\n" + "\n".join(
                f"{w:.2f} 0.1" for w in np.linspace(600, 4000 + 100 * i, 20)
            )
            data = text.encode()
            info = tarfile.TarInfo(f"fig_{i}/spectrum.dat")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    root = tmp_path / "datasets"
    root.mkdir()
    dataset = root / "7064870_x.zip"
    with zipfile.ZipFile(dataset, "w") as archive:
        archive.writestr("fig.tgz", tgz.getvalue())
    pd.DataFrame({"record_id": ["7064870"], "title": ["x"]}).to_parquet(
        base_config["paths"]["metadata_file"]
    )

    pipeline = Pipeline(base_config)
    rows = pipeline.indexer.scan("7064870", dataset)
    prefetched = pipeline._prefetch_tar_members(rows, tmp_path, [])
    assert len(prefetched) == 3

    pipeline.process_record("7064870")
    pipeline.consolidate()
    out = pd.read_parquet(Path(base_config["paths"]["output_directory"]) / "spectroscopy_metadata.parquet")
    assert len(out) == 3
    assert all("fig.tgz::fig_" in source for source in out["source_file"])


def test_envi_header_reader(base_config, tmp_path):
    from readers.envi_reader import ENVIReader

    path = tmp_path / "swir_core_refl.hdr"
    waves = ", ".join(f"{w:.3f}" for w in np.linspace(968.67, 2574.07, 144))
    path.write_text(
        "ENVI\ndescription = {\n reflectance cube}\nsamples = 384\nlines   = 5904\n"
        f"bands   = 144\ninterleave = bil\nwavelength units = Nanometers\nwavelength = {{\n{waves}\n}}\n"
    )
    row = ENVIReader(base_config).read(
        record_id="5801251", dataset_path=tmp_path, file_path=path
    ).spectral_records[0]

    assert row["num_spectral_channels"] == 144
    assert row["image_width"] == 384 and row["image_height"] == 5904
    assert row["num_spectra"] == 384 * 5904
    assert abs(row["wavelength_max_nm"] - 2574.07) < 1e-6
    assert (tmp_path / "DARKREF_x.hdr").write_text("ENVI\nwavelength = {1,2}") and not ENVIReader(
        base_config).read(record_id="1", dataset_path=tmp_path, file_path=tmp_path / "DARKREF_x.hdr").spectral_records


def test_csv_latin1_and_comment_preamble(base_config, tmp_path):
    path = tmp_path / "absorbance_table.csv"
    lines = ["# Absorbance spectra (a.u.)", "# Effective thickness (cm): 1e-6 µ"]
    lines += ["wavenumber,Sample1"] + [f"{w:.3f},0.001" for w in np.linspace(4000, 700, 30)]
    path.write_bytes("\n".join(lines).encode("latin-1"))

    row = CSVReader(base_config).read(
        record_id="7005320", dataset_path=tmp_path, file_path=path
    ).spectral_records[0]

    assert row["num_spectral_channels"] == 30
    assert row["spectral_range_original_unit"] == "cm^-1"


def test_xray_raman_is_not_optical_raman():
    from extraction.spectral_patterns import extract_spectral_candidates

    def modalities(text):
        return {c.value for c in extract_spectral_candidates(text) if c.field_name == "modality"}

    assert "Raman" not in modalities("We use high-resolution X-ray\nRaman spectroscopy (XRS)")
    assert "Raman" not in modalities("refs 15, 16). X-\nray Raman spectra")
    assert "Raman" in modalities("Raman spectra were recorded at 785 nm")


def test_curated_batch1_tables():
    from curation.build import build_details_table, build_spectroscopy_table, load_batch
    from storage.parquet_writer import SPECTRAL_SCHEMA

    spectral, details = load_batch("batch1")
    table, problems = build_spectroscopy_table(spectral)

    assert table.num_rows == 52 and set(spectral) == set(details)
    assert table.schema.equals(SPECTRAL_SCHEMA)
    assert problems == []
    assert build_details_table(details).num_columns == 22
    row = table.to_pandas().set_index("record_id").loc["6641623"]
    assert abs(row["wavelength_min_nm"] - 1067.27) < 1e-6  # Angstrom input

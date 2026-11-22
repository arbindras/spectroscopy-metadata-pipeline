"""Deduplication of spectral rows: two formats of one spectrum, and copies of
one file (byte-identical files, extracted or nested archives, loose copies),
count once; same-named files with different contents in different folders
or archives are different spectra."""

from __future__ import annotations

import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from pipeline import Pipeline


def _row(source: str, low: float = 2500.0) -> dict:
    return {
        "source_file": source,
        "num_spectral_channels": 3601,
        "wavelength_min_nm": low,
        "wavelength_max_nm": 25000.0,
    }


def _sources(rows: list[dict]) -> list[str]:
    return [row["source_file"] for row in rows]


def _spectrum(absorbance: float) -> bytes:
    lines = ["# wavenumber (cm-1) absorbance"]
    lines += [f"{w:.2f} {absorbance}" for w in np.linspace(600, 4000, 50)]
    return "\n".join(lines).encode()


def _run_record(base_config, record_id: str) -> pd.DataFrame:
    pd.DataFrame({"record_id": [record_id], "title": ["test"]}).to_parquet(
        base_config["paths"]["metadata_file"]
    )
    pipeline = Pipeline(base_config)
    pipeline.process_record(record_id)
    pipeline.consolidate()
    output = Path(base_config["paths"]["output_directory"])
    return pd.read_parquet(output / "spectroscopy_metadata.parquet")


def test_same_name_in_different_folders_is_kept(tmp_path):
    first = str(tmp_path / "run1" / "spectrum.txt")
    second = str(tmp_path / "run2" / "spectrum.txt")
    evidence = [{"source_file": first}, {"source_file": second}]

    kept, kept_evidence = Pipeline._deduplicate([_row(first), _row(second)], evidence, tmp_path)

    assert _sources(kept) == [first, second]
    assert kept_evidence == evidence


def test_same_data_in_two_formats_is_dropped_with_its_evidence(tmp_path):
    fits = str(tmp_path / "fits" / "J0001.fits")
    text = str(tmp_path / "ascii" / "J0001.txt")
    evidence = [{"source_file": fits}, {"source_file": text}]

    # float32 FITS axis vs text precision still match at 5 significant digits
    kept, kept_evidence = Pipeline._deduplicate(
        [_row(fits, low=2500.0001), _row(text)], evidence, tmp_path
    )

    assert _sources(kept) == [fits]
    assert kept_evidence == [{"source_file": fits}]


def test_byte_identical_copy_in_another_folder_is_dropped(tmp_path):
    body = str(tmp_path / "Body" / "spectrum.csv")
    combined = str(tmp_path / "Combined" / "spectrum.csv")
    fingerprints = {body: "1000:abc", combined: "1000:abc"}

    kept, _ = Pipeline._deduplicate([_row(body), _row(combined)], [], tmp_path, fingerprints)

    assert _sources(kept) == [body]


def test_loose_copy_of_an_archive_member_is_dropped(tmp_path):
    member = f"{tmp_path / 'data.zip'}::run1/spectrum.txt"
    loose = str(tmp_path / "run1" / "spectrum.txt")

    kept, _ = Pipeline._deduplicate([_row(member), _row(loose)], [], tmp_path)

    assert _sources(kept) == [member]


def test_nested_and_extracted_copies_count_once(tmp_path):
    # Record 16268857 layout: Data.zip, its extracted folder, and a nested
    # zip that appears both inside Data.zip and in the extracted folder.
    nested = f"{tmp_path / 'Data.zip'}::SECM/scans.zip::s1/a.dat"
    loose_zip = f"{tmp_path / 'Data' / 'SECM' / 'scans.zip'}::s1/a.dat"
    extracted = str(tmp_path / "Data" / "SECM" / "scans" / "s1" / "a.dat")

    kept, _ = Pipeline._deduplicate([_row(nested), _row(loose_zip), _row(extracted)], [], tmp_path)

    assert _sources(kept) == [nested]


def test_same_member_path_in_two_archives_is_kept(tmp_path):
    first = f"{tmp_path / 'sample_a.zip'}::spectrum.txt"
    second = f"{tmp_path / 'sample_b.zip'}::spectrum.txt"

    kept, _ = Pipeline._deduplicate([_row(first), _row(second)], [], tmp_path)

    assert _sources(kept) == [first, second]


def test_pipeline_counts_same_named_spectra_in_separate_folders(base_config, tmp_path):
    dataset = tmp_path / "datasets" / "777_runs"
    for run, absorbance in (("run1", 0.1), ("run2", 0.2)):
        (dataset / run).mkdir(parents=True)
        (dataset / run / "spectrum.dat").write_bytes(_spectrum(absorbance))

    rows = _run_record(base_config, "777")

    assert sorted(Path(source).parent.name for source in rows["source_file"]) == ["run1", "run2"]


def test_pipeline_counts_a_byte_identical_copy_once(base_config, tmp_path):
    # Record 7809074 layout: a "Combined" folder repeats per-tissue files.
    dataset = tmp_path / "datasets" / "778_tissues"
    (dataset / "Body").mkdir(parents=True)
    (dataset / "Body" / "spectrum.dat").write_bytes(_spectrum(0.1))
    with zipfile.ZipFile(dataset / "extra.zip", "w") as archive:
        archive.writestr("Combined/spectrum.dat", _spectrum(0.1))

    rows = _run_record(base_config, "778")

    assert len(rows) == 1
    assert Path(rows.loc[0, "source_file"]).parent.name == "Body"

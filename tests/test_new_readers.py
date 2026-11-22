from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.io import netcdf_file

from readers.csv_reader import CSVReader
from readers.fits_reader import FITSReader
from readers.netcdf_reader import NetCDFReader
from readers.text_reader import TextReader


def _write_fits(path, data, cards):
    header = [
        "SIMPLE  =                    T",
        "BITPIX  =                  -32",
        f"NAXIS   = {data.ndim:>20}",
    ]
    for i, size in enumerate(data.shape[::-1], start=1):
        header.append(f"NAXIS{i}  = {size:>20}")
    header += cards + ["END"]
    text = "".join(card.ljust(80) for card in header)
    text = text.ljust(((len(text) + 2879) // 2880) * 2880)
    payload = data.astype(">f4").tobytes()
    payload += b"\0" * ((2880 - len(payload) % 2880) % 2880)
    path.write_bytes(text.encode("ascii") + payload)


def test_text_reader_comment_header(base_config, tmp_path):
    path = tmp_path / "star.txt"
    lines = [
        "COMMENT Column 1 is the wavelength (microns),",
        "COMMENT Column 2 is the flux (F_lambda),",
        "COMMENT Column 3 is the error on the flux.",
    ]
    lines += [f"{w:.4f} 1e-15 1e-17" for w in np.linspace(0.8, 2.4, 50)]
    path.write_text("\n".join(lines))

    row = TextReader(base_config).read(
        record_id="1", dataset_path=tmp_path, file_path=path
    ).spectral_records[0]

    assert row["spectral_range_original_unit"] == "um"
    assert row["num_spectral_channels"] == 50
    assert abs(row["wavelength_min_nm"] - 800) < 1e-6
    assert row["num_spectra"] == 1  # error column excluded


def test_text_reader_wavenumber_header(base_config, tmp_path):
    path = tmp_path / "IR_01.txt"
    axis = np.linspace(4000, 600, 100)
    body = "\n".join("\t".join(f"{v}" for v in [w, 0.1, 0.2, 0.3]) for w in axis)
    path.write_text("# Wavenumber\t0\t1\t4\n# \n" + body)

    row = TextReader(base_config).read(
        record_id="1", dataset_path=tmp_path, file_path=path
    ).spectral_records[0]

    assert row["spectral_range_original_unit"] == "cm^-1"
    assert row["wavenumber_min_cm1"] == 600
    assert row["wavenumber_max_cm1"] == 4000
    assert row["num_spectra"] == 3


def test_text_reader_ignores_readme(base_config, tmp_path):
    path = tmp_path / "README.txt"
    path.write_text("This data set contains spectra from 600-4000 wavenumbers.")
    result = TextReader(base_config).read(
        record_id="1", dataset_path=tmp_path, file_path=path
    )
    assert not result.spectral_records
    assert not result.errors


def test_fits_wavelength_row(base_config, tmp_path):
    path = tmp_path / "star.fits"
    data = np.vstack([np.linspace(0.8, 2.4, 64), np.ones(64), np.ones(64)])
    _write_fits(path, data, [
        "COMMENT Dimension 1 is the wavelength (microns),",
        "COMMENT Dimension 2 is the flux (F_lambda),",
    ])

    row = FITSReader(base_config).read(
        record_id="1", dataset_path=tmp_path, file_path=path
    ).spectral_records[0]

    assert row["num_spectral_channels"] == 64
    assert abs(row["wavelength_max_nm"] - 2400) < 1e-3
    assert row["modality"] == "NIR"


def test_fits_linear_wcs(base_config, tmp_path):
    path = tmp_path / "wcs.fits"
    _write_fits(path, np.ones(100), [
        "CRVAL1  =               4000.0",
        "CDELT1  =                  2.0",
        "CRPIX1  =                  1.0",
        "CTYPE1  = 'WAVE    '",
        "CUNIT1  = 'Angstrom'",
    ])

    row = FITSReader(base_config).read(
        record_id="1", dataset_path=tmp_path, file_path=path
    ).spectral_records[0]

    assert row["spectral_range_original_unit"] == "nm"
    assert row["wavelength_min_nm"] == 400
    assert abs(row["wavelength_max_nm"] - 419.8) < 1e-9


def test_netcdf3_reader(base_config, tmp_path):
    path = tmp_path / "x.nc"
    with netcdf_file(path, "w") as handle:
        handle.createDimension("w", 50)
        variable = handle.createVariable("wavenumber", "f8", ("w",))
        variable[:] = np.linspace(700, 1200, 50)
        variable.units = "cm-1"

    row = NetCDFReader(base_config).read(
        record_id="1", dataset_path=tmp_path, file_path=path
    ).spectral_records[0]

    assert row["num_spectral_channels"] == 50
    assert row["wavenumber_max_cm1"] == 1200


def test_csv_wide_table(base_config, tmp_path):
    path = tmp_path / "wide.csv"
    columns = ["sample"] + [str(w) for w in range(400, 1000, 10)]
    pd.DataFrame(np.random.rand(4, len(columns)), columns=columns).to_csv(
        path, index=False
    )

    row = CSVReader(base_config).read(
        record_id="1", dataset_path=tmp_path, file_path=path
    ).spectral_records[0]

    assert row["num_spectral_channels"] == 60
    assert row["num_spectra"] == 4

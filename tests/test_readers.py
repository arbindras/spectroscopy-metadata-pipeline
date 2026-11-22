from pathlib import Path

import h5py
import numpy as np
import pandas as pd
from openpyxl import Workbook
from scipy.io import savemat

from readers.csv_reader import CSVReader
from readers.hdf5_reader import HDF5Reader
from readers.jcamp_reader import JCAMPReader
from readers.mat_reader import MATReader
from readers.xlsx_reader import XLSXReader


def test_csv_reader(base_config, tmp_path):
    path = tmp_path / "spectra.csv"
    pd.DataFrame({
        "wavelength_nm": [900, 901, 902, 903],
        "absorbance": [0.1, 0.2, 0.3, 0.4],
    }).to_csv(path, index=False)

    result = CSVReader(base_config).read(
        record_id="1",
        dataset_path=tmp_path,
        file_path=path,
    )

    row = result.spectral_records[0]
    assert row["num_spectral_channels"] == 4
    assert row["wavelength_min_nm"] == 900
    assert row["wavelength_max_nm"] == 903
    assert result.evidence_records


def test_xlsx_reader(base_config, tmp_path):
    path = tmp_path / "spectra.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["wavenumber_cm-1", "absorbance"])
    for value in [3800, 3798, 3796, 3794]:
        sheet.append([value, 0.1])
    workbook.save(path)

    result = XLSXReader(base_config).read(
        record_id="1",
        dataset_path=tmp_path,
        file_path=path,
    )

    row = result.spectral_records[0]
    assert row["num_spectral_channels"] == 4
    assert row["spectral_range_original_min"] == 3800
    assert row["spectral_range_original_max"] == 3794


def test_hdf5_cube_shape(base_config, tmp_path):
    path = tmp_path / "cube.h5"

    with h5py.File(path, "w") as handle:
        axis = handle.create_dataset(
            "wavenumbers",
            data=np.linspace(3800, 950, 1479),
        )
        axis.attrs["units"] = "cm^-1"
        handle.create_dataset(
            "cube",
            shape=(16, 12, 1479),
            dtype="float32",
            chunks=(1, 12, 1479),
        )

    result = HDF5Reader(base_config).read(
        record_id="1",
        dataset_path=tmp_path,
        file_path=path,
    )

    row = result.spectral_records[0]
    assert row["num_spectral_channels"] == 1479
    assert row["image_height"] == 16
    assert row["image_width"] == 12
    assert row["num_pixels"] == 192
    assert row["num_spectra"] == 192


def test_mat_reader(base_config, tmp_path):
    path = tmp_path / "spectra.mat"
    savemat(path, {
        "wavelengths": np.arange(900, 905, dtype=float),
        "spectra": np.zeros((3, 5)),
    })

    result = MATReader(base_config).read(
        record_id="1",
        dataset_path=tmp_path,
        file_path=path,
    )

    assert result.spectral_records[0]["num_spectral_channels"] == 5


def test_jcamp_reader(base_config, tmp_path):
    path = tmp_path / "spectrum.jdx"
    path.write_text(
        "\n".join([
            "##TITLE=Example",
            "##DATA TYPE=INFRARED SPECTRUM",
            "##XUNITS=1/CM",
            "##FIRSTX=3800",
            "##LASTX=950",
            "##NPOINTS=1479",
            "##DELTAX=-1.927",
            "##XYDATA=(X++(Y..Y))",
        ]),
        encoding="utf-8",
    )

    result = JCAMPReader(base_config).read(
        record_id="1",
        dataset_path=tmp_path,
        file_path=path,
    )

    row = result.spectral_records[0]
    assert row["modality"] == "IR"
    assert row["num_spectral_channels"] == 1479
    assert row["spectral_range_original_min"] == 3800
    assert row["spectral_range_original_max"] == 950
    assert row["wavenumber_min_cm1"] == 950
    assert row["wavenumber_max_cm1"] == 3800

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from storage.parquet_writer import SPECTRAL_SCHEMA
from validation.range_validator import validate_record


HC_EV_NM = 1239.841984  # nm * eV
EV_TO_CM1 = 8065.543937

# (parquet column, key in the <batch>_details R2 dicts)
DETAIL_COLUMNS = [
    ("Record ID", None),
    ("Dataset Format", "fmt"),
    ("No. of Data points", "npts"),
    ("Any Missing Data?", "missing"),
    ("Is the Data Preprocessed?", "prep"),
    ("If Preprocessed Mentioned the methods in order", "prep_methods"),
    ("Target of Interest", "target"),
    ("Mode of Collection", "mode"),
    ("Wavelength Range (nm)", "wl"),
    ("Resolution (nm)", "res"),
    ("Make of the Instrument", "make"),
    ("Pathlength Information", "path"),
    ("Is it Time Series Data", "ts"),
    ("Is a Chemometric Model Available?", "chemo"),
    ("Any Relevant Reference Papers?", "refs"),
    ("Remarks", "remarks"),
    ("Condition in which the data was collected", "cond"),
    ("Absorptivity", "absorb"),
    ("Reference Measurement", "refm"),
    ("Gold standard instrument used if any", "gold"),
    ("Peak Information (bonds)", "peaks"),
    ("SMILES / Props / 3D/2D structures information", "struct"),
]
DETAILS_SCHEMA = pa.schema([(column, pa.string()) for column, _ in DETAIL_COLUMNS])


def load_batch(batch: str) -> tuple[dict[str, dict], dict[str, dict]]:
    spectral = importlib.import_module(f"curation.{batch}_spectral").R
    details = importlib.import_module(f"curation.{batch}_details").R2
    return spectral, details


def derive_spectral_fields(record: dict[str, Any]) -> None:
    """Fill nm / cm-1 columns from the original range (explicit values win)."""
    low = record.get("spectral_range_original_min")
    high = record.get("spectral_range_original_max")
    unit = record.get("spectral_range_original_unit")
    if low is None or high is None or unit is None:
        return
    if unit == "meV":
        low, high, unit = low / 1000.0, high / 1000.0, "eV"

    if unit == "cm-1":
        record.setdefault("wavenumber_min_cm1", low)
        record.setdefault("wavenumber_max_cm1", high)
        if low > 0:
            record.setdefault("wavelength_min_nm", 1e7 / high)
            record.setdefault("wavelength_max_nm", 1e7 / low)
        return
    if unit == "eV":
        record.setdefault("wavenumber_max_cm1", high * EV_TO_CM1)
        record.setdefault("wavelength_min_nm", HC_EV_NM / high)
        if low > 0:  # energy-loss axis may start below zero
            record.setdefault("wavenumber_min_cm1", low * EV_TO_CM1)
            record.setdefault("wavelength_max_nm", HC_EV_NM / low)
        return

    scale = {"nm": 1.0, "um": 1000.0, "Angstrom": 0.1}.get(unit)
    if scale is None:
        return
    record.setdefault("wavelength_min_nm", low * scale)
    record.setdefault("wavelength_max_nm", high * scale)
    if record["wavelength_min_nm"] > 0:
        record.setdefault("wavenumber_min_cm1", 1e7 / record["wavelength_max_nm"])
        record.setdefault("wavenumber_max_cm1", 1e7 / record["wavelength_min_nm"])


def _sort_by_record_id(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    # Numeric record ids sort numerically; non-numeric ids (new batches with
    # free folder names) follow in name order.
    keys = frame[column].astype(str).map(lambda v: (0, int(v), "") if v.isdigit() else (1, 0, v))
    order = sorted(range(len(frame)), key=lambda i: keys.iloc[i])
    return frame.iloc[order].reset_index(drop=True)


def build_spectroscopy_table(records: dict[str, dict]) -> tuple[pa.Table, list[str]]:
    columns = SPECTRAL_SCHEMA.names
    rows, problems = [], []
    for record_id, curated in records.items():
        row = dict(curated)
        row["record_id"] = str(record_id)
        derive_spectral_fields(row)
        if (
            row.get("num_spectral_values") is None
            and row.get("num_spectra")
            and row.get("num_spectral_channels")
        ):
            row["num_spectral_values"] = row["num_spectra"] * row["num_spectral_channels"]
        for key in ("wavelength_min_nm", "wavelength_max_nm", "wavenumber_min_cm1", "wavenumber_max_cm1"):
            if row.get(key) is not None:
                row[key] = round(float(row[key]), 4)

        unknown = set(row) - set(columns)
        if unknown:
            raise ValueError(f"{record_id}: unknown spectral fields {sorted(unknown)}")
        problems += [f"{record_id}: {p}" for p in validate_record(row)]
        rows.append({column: row.get(column) for column in columns})

    frame = _sort_by_record_id(pd.DataFrame(rows, columns=columns), "record_id")
    table = pa.Table.from_pandas(frame, preserve_index=False).cast(SPECTRAL_SCHEMA)
    return table, problems


def build_details_table(details: dict[str, dict]) -> pa.Table:
    rows = []
    for record_id, curated in details.items():
        missing = [key for _, key in DETAIL_COLUMNS[1:] if key not in curated]
        if missing:
            raise ValueError(f"{record_id}: missing detail fields {missing}")
        row = {"Record ID": str(record_id)}
        for column, key in DETAIL_COLUMNS[1:]:
            value = curated[key]
            row[column] = value if value not in ("", None) else "None"
        rows.append(row)

    frame = _sort_by_record_id(pd.DataFrame(rows), "Record ID")
    return pa.Table.from_pandas(frame, schema=DETAILS_SCHEMA, preserve_index=False)


def load_llm_batch(directory: str | Path) -> tuple[dict[str, dict], dict[str, dict], dict[str, str]]:
    """Read ``<record_id>.json`` files written by ``llm_curation.runner``.

    Returns (spectral R, details R2, NO_SPECTRA) in the same shape as the
    hand-curated modules; records without spectra only go to NO_SPECTRA.
    """
    import json

    spectral, details, no_spectra = {}, {}, {}
    for path in sorted(Path(directory).glob("*.json")):
        if path.name.startswith("_"):  # _failures.json and other run bookkeeping
            continue
        result = json.loads(path.read_text(encoding="utf-8"))
        record_id = str(result["record_id"])
        if not result.get("has_spectra"):
            no_spectra[record_id] = result.get("no_spectra_reason") or "no spectra"
            continue
        spectral[record_id] = dict(result["spectral"])
        details[record_id] = dict(result["details"])
    return spectral, details, no_spectra


def write_batch(batch: str, output_directory: str | Path, *, csv_preview: bool = True) -> dict[str, Any]:
    spectral, details = load_batch(batch)
    no_spectra = getattr(importlib.import_module(f"curation.{batch}_spectral"), "NO_SPECTRA", {})
    return write_tables(batch, spectral, details, output_directory, csv_preview=csv_preview, no_spectra=no_spectra)


def write_tables(
    batch: str,
    spectral: dict[str, dict],
    details: dict[str, dict],
    output_directory: str | Path,
    *,
    csv_preview: bool = True,
    no_spectra: dict[str, str] | None = None,
) -> dict[str, Any]:
    if set(spectral) != set(details):
        raise ValueError(
            f"{batch}: record ids differ between spectral and details modules: "
            f"{sorted(set(spectral) ^ set(details))}"
        )

    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    spectral_table, problems = build_spectroscopy_table(spectral)
    details_table = build_details_table(details)

    written = {}
    for name, table in (
        (f"{batch}_spectroscopy_metadata", spectral_table),
        (f"{batch}_dataset_details", details_table),
    ):
        path = output / f"{name}.parquet"
        temporary = path.with_suffix(".parquet.tmp")
        pq.write_table(table, temporary, compression="zstd")
        temporary.replace(path)
        written[name] = path
        if csv_preview:
            table.to_pandas().to_csv(output / f"{name}_preview.csv", index=False)

    if no_spectra:
        path = output / f"{batch}_no_spectra.csv"
        pd.DataFrame(
            sorted(no_spectra.items(), key=lambda item: int(item[0]) if item[0].isdigit() else 0),
            columns=["record_id", "reason"],
        ).to_csv(path, index=False)
        written[f"{batch}_no_spectra"] = path

    return {
        "records": spectral_table.num_rows,
        "files": written,
        "validation_problems": problems,
    }

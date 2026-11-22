"""Reader for ExoMol line-list definition files (``*.def``).

ExoMol datasets ship ``<iso>__<dataset>.states/.trans`` (bz2) plus a ``.def``
file whose lines are ``value   # description``. The ``.def`` already states
the totals, so the (often large) transition files need not be parsed::

    (39K)(35Cl)            # IsoFormula
    60741                  # No. of states in .states file
    1326765                # Total number of transitions
    2927.25                # Maximum wavenumber (in cm-1)
"""

from __future__ import annotations

from pathlib import Path

from evidence.provenance import add_field_with_evidence
from models import ReaderResult, empty_spectral_record
from readers.base_reader import BaseReader


FIELDS = {
    "isoformula": "iso_formula",
    "iso-slug": "iso_slug",
    "isotopologue dataset name": "dataset_name",
    "version number": "version",
    "maximum temperature of linelist": "max_temperature_k",
    "no. of states in .states file": "n_states",
    "total number of transitions": "n_transitions",
    "maximum wavenumber": "max_wavenumber",
}


def parse_def(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if "#" not in line:
            continue
        value, description = line.split("#", 1)
        description = description.strip().lower()
        for prefix, key in FIELDS.items():
            if description.startswith(prefix) and key not in values:
                values[key] = value.strip()
    return values


class ExoMolReader(BaseReader):
    extensions = {".def"}

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() == ".def"

    def read(self, *, record_id: str, dataset_path: Path, file_path: Path) -> ReaderResult:
        result = ReaderResult()
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
            if not text.lstrip().upper().startswith("EXOMOL"):
                return result
            values = parse_def(text)
            if "max_wavenumber" not in values:
                return result

            row = empty_spectral_record(record_id)
            row["source_file"] = str(file_path)
            evidence = result.evidence_records
            iso = values.get("iso_formula", "?")
            name = values.get("dataset_name", "?")

            def put(field, value, note, origin="author_provided", confidence=0.95):
                add_field_with_evidence(
                    row, evidence, field_name=field, value=value, record_id=record_id,
                    source_file=file_path, source_type="spectral_file",
                    evidence_text=f"ExoMol .def: {note}", dataset_path=dataset_path,
                    extraction_method="exomol_def", confidence=confidence,
                    value_origin=origin,
                )

            max_wn = float(values["max_wavenumber"])
            put("modality", f"Molecular line list (ExoMol {name}) for {iso}", "IsoFormula / dataset name")
            put("spectral_range_original_max", max_wn, f"Maximum wavenumber = {max_wn} cm-1")
            put("spectral_range_original_unit", "cm^-1", "wavenumbers in cm-1 by ExoMol convention")
            put("wavenumber_max_cm1", max_wn, "Maximum wavenumber", "file_derived")
            if max_wn > 0:
                put("wavelength_min_nm", 1e7 / max_wn, "1e7 / maximum wavenumber", "calculated", 1.0)
            if "n_transitions" in values:
                put("num_spectral_values", int(float(values["n_transitions"])),
                    "Total number of transitions (one value per line)")
            put("num_samples", 1, "one isotopologue per line list", "inferred", 0.9)
            states = values.get("n_states")
            put(
                "spectral_target_relationship",
                f"Line list for {iso}: {states} states, {values.get('n_transitions')} transitions, "
                f"T_max {values.get('max_temperature_k')} K -> forward modelling of hot atmospheres",
                "summary of .def totals", "file_derived", 0.9,
            )
            row["confidence"] = 0.9
            result.spectral_records.append(row)
        except Exception as exc:
            result.errors.append({
                "record_id": record_id,
                "source_file": str(file_path),
                "reader": type(self).__name__,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            })
        return result

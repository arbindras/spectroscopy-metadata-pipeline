from __future__ import annotations

import re
from pathlib import Path

from evidence.provenance import add_field_with_evidence
from models import ReaderResult, empty_spectral_record
from normalization.spectral_units import normalize_spectral_bounds
from readers.base_reader import BaseReader
from readers.spectral_helpers import modality_from_text, unit_from_text


HEADER_PATTERN = re.compile(r"^##([^=]+)=(.*)$")


def parse_number(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value.strip())
    except ValueError:
        return None


class JCAMPReader(BaseReader):
    extensions = {".jdx", ".dx"}

    def read(
        self,
        *,
        record_id: str,
        dataset_path: Path,
        file_path: Path,
    ) -> ReaderResult:
        result = ReaderResult()
        max_bytes = int(
            self.reader_config.get("jcamp_max_header_bytes", 4194304)
        )

        headers: dict[str, str] = {}

        try:
            consumed = 0
            with file_path.open("r", encoding="utf-8", errors="replace") as stream:
                for line in stream:
                    consumed += len(line.encode("utf-8", errors="ignore"))
                    if consumed > max_bytes:
                        break

                    stripped = line.strip()
                    match = HEADER_PATTERN.match(stripped)
                    if not match:
                        continue

                    key = match.group(1).strip().upper()
                    value = match.group(2).strip()
                    headers[key] = value

                    if key in {"XYDATA", "XYPOINTS", "PEAK TABLE", "PEAKTABLE"}:
                        break

            first_x = parse_number(headers.get("FIRSTX"))
            last_x = parse_number(headers.get("LASTX"))
            npoints_value = parse_number(headers.get("NPOINTS"))
            delta_x = parse_number(headers.get("DELTAX"))
            unit = unit_from_text(headers.get("XUNITS"))
            modality = modality_from_text(
                " ".join(
                    filter(
                        None,
                        (
                            headers.get("DATA TYPE"),
                            headers.get("SPECTROMETER/DATA SYSTEM"),
                            headers.get("ORIGIN"),
                        ),
                    )
                )
            )

            if first_x is None and last_x is None and npoints_value is None:
                return result

            row = empty_spectral_record(record_id)
            row["source_file"] = str(file_path)
            row["confidence"] = 0.99
            evidence: list[dict] = []
            prefix = "JCAMP-DX header"

            fields = (
                ("spectral_range_original_min", first_x, "FIRSTX"),
                ("spectral_range_original_max", last_x, "LASTX"),
                (
                    "num_spectral_channels",
                    int(npoints_value) if npoints_value is not None else None,
                    "NPOINTS",
                ),
                ("sampling_interval", abs(delta_x) if delta_x is not None else None, "DELTAX"),
            )

            for field_name, value, header_name in fields:
                add_field_with_evidence(
                    row,
                    evidence,
                    field_name=field_name,
                    value=value,
                    record_id=record_id,
                    source_file=file_path,
                    source_type="spectral_file",
                    evidence_text=f"{prefix} {header_name}={headers.get(header_name)}",
                    dataset_path=dataset_path,
                    extraction_method="jcamp_header_parser",
                    confidence=0.99,
                    value_origin="author_provided",
                )

            if unit:
                for field_name in (
                    "spectral_range_original_unit",
                    "sampling_interval_unit",
                ):
                    if field_name == "sampling_interval_unit" and delta_x is None:
                        continue
                    add_field_with_evidence(
                        row,
                        evidence,
                        field_name=field_name,
                        value=unit,
                        record_id=record_id,
                        source_file=file_path,
                        source_type="spectral_file",
                        evidence_text=f"{prefix} XUNITS={headers.get('XUNITS')}",
                        dataset_path=dataset_path,
                        extraction_method="jcamp_header_parser",
                        confidence=0.99,
                        value_origin="author_provided",
                    )

            if modality:
                add_field_with_evidence(
                    row,
                    evidence,
                    field_name="modality",
                    value=modality,
                    record_id=record_id,
                    source_file=file_path,
                    source_type="spectral_file",
                    evidence_text=(
                        f"DATA TYPE={headers.get('DATA TYPE')}; "
                        f"ORIGIN={headers.get('ORIGIN')}"
                    ),
                    dataset_path=dataset_path,
                    extraction_method="jcamp_header_parser",
                    confidence=0.99,
                    value_origin="author_provided",
                )

            if first_x is not None and last_x is not None and unit:
                normalized = normalize_spectral_bounds(first_x, last_x, unit)
                for field_name, value in normalized.items():
                    if value is None:
                        continue
                    add_field_with_evidence(
                        row,
                        evidence,
                        field_name=field_name,
                        value=value,
                        record_id=record_id,
                        source_file=file_path,
                        source_type="derived_from_data",
                        evidence_text=(
                            f"Calculated from FIRSTX={first_x}, "
                            f"LASTX={last_x}, XUNITS={unit}"
                        ),
                        dataset_path=dataset_path,
                        extraction_method="spectral_unit_conversion",
                        confidence=1.0,
                        value_origin="calculated",
                    )

            result.spectral_records.append(row)
            result.evidence_records.extend(evidence)

        except Exception as exc:
            result.errors.append({
                "record_id": record_id,
                "source_file": str(file_path),
                "reader": type(self).__name__,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            })

        return result

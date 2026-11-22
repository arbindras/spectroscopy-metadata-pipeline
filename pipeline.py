from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml
from tqdm import tqdm

from evidence.provenance import add_field_with_evidence, make_evidence
from models import ReaderResult, empty_spectral_record
from readers.csv_reader import CSVReader
from readers.envi_reader import ENVIReader
from readers.exomol_reader import ExoMolReader
from readers.fits_reader import FITSReader
from readers.hdf5_reader import HDF5Reader
from readers.jcamp_reader import JCAMPReader
from readers.mat_reader import MATReader
from readers.netcdf_reader import NetCDFReader
from normalization.spectral_units import normalize_spectral_bounds, normalize_spectral_unit
from readers.spectral_helpers import modality_from_text, unit_from_text
from readers.text_reader import TextReader
from readers.xlsx_reader import XLSXReader
from scanner import archive_access
from scanner.dataset_scanner import DatasetMapper
from scanner.file_indexer import FileIndexer
from storage.parquet_writer import ParquetStore


READERS = [
    CSVReader,
    XLSXReader,
    HDF5Reader,
    NetCDFReader,
    MATReader,
    JCAMPReader,
    FITSReader,
    ExoMolReader,
    ENVIReader,
    TextReader,
]

README_NAMES = ("readme", "read_me", "description", "about")
README_EXTENSIONS = {"", ".txt", ".md", ".rst", ".rtf"}
README_MAX_BYTES = 2 * 1024 * 1024


def load_config(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def load_metadata(config: dict) -> pd.DataFrame:
    path = Path(config["paths"]["metadata_file"]).resolve()
    suffix = path.suffix.lower()

    if suffix == ".parquet":
        frame = pd.read_parquet(path)
    elif suffix in {".csv", ".tsv"}:
        frame = pd.read_csv(
            path,
            sep="\t" if suffix == ".tsv" else ",",
            dtype={"record_id": "string"},
        )
    else:
        raise ValueError(
            "Unsupported metadata file format "
            f"{path.suffix!r}. Use a .parquet, .csv, or .tsv file."
        )

    if "record_id" not in frame.columns:
        raise ValueError("Metadata file does not contain record_id")

    # Copy in memory and normalize only the pipeline lookup key.
    # The source Parquet file is never modified.
    frame = frame.copy()
    frame["record_id"] = frame["record_id"].astype(str)
    return frame


class StateManager:
    def __init__(self, output_directory: str | Path):
        self.path = Path(output_directory) / "extraction_state.parquet"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def read(self) -> pd.DataFrame:
        if not self.path.exists():
            return pd.DataFrame(columns=[
                "record_id",
                "status",
                "dataset_local_path",
                "mapping_status",
                "started_at",
                "finished_at",
                "processing_seconds",
                "error_message",
            ])
        return pd.read_parquet(self.path)

    def status(self, record_id: str) -> str | None:
        frame = self.read()
        matches = frame[frame["record_id"].astype(str) == str(record_id)]
        if matches.empty:
            return None
        return str(matches.iloc[-1]["status"])

    def stats(self) -> None:
        state = self.read()
        if state.empty:
            print("No extraction state.")
            return
        print(state["status"].value_counts(dropna=False).to_string())

    def update(self, record_id: str, **values) -> None:
        frame = self.read()
        record_id = str(record_id)
        frame = frame[frame["record_id"].astype(str) != record_id]

        row = {
            "record_id": record_id,
            "status": values.get("status"),
            "dataset_local_path": values.get("dataset_local_path"),
            "mapping_status": values.get("mapping_status"),
            "started_at": values.get("started_at"),
            "finished_at": values.get("finished_at"),
            "processing_seconds": values.get("processing_seconds"),
            "error_message": values.get("error_message"),
        }

        frame = pd.concat([frame, pd.DataFrame([row])], ignore_index=True)
        temporary = self.path.with_suffix(".parquet.tmp")
        frame.to_parquet(temporary, index=False)
        os.replace(temporary, self.path)


class Pipeline:
    def __init__(self, config: dict):
        self.config = config
        self.metadata = load_metadata(config)
        self.mapper = DatasetMapper(config)
        self.indexer = FileIndexer(config)
        self.store = ParquetStore(config["paths"]["output_directory"])
        self.state = StateManager(config["paths"]["output_directory"])
        self.readers = [reader(config) for reader in READERS]
        papers = config["paths"].get("papers_directory")
        self.papers_directory = Path(papers) if papers else None
        self._pdf_extractor = None

    def selected_record_ids(self) -> list[str]:
        """Records for ``--all``: every metadata row, or (default when the
        metadata file covers far more records than are on disk) only those
        with a resolvable local dataset."""
        ids = self.metadata["record_id"].astype(str).tolist()
        if self.config.get("pipeline", {}).get("only_mapped_records", False):
            local = self.mapper.local_record_ids()
            ids = [rid for rid in ids if rid in local]
        return ids

    def process_record(
        self,
        record_id: str,
        *,
        force: bool = False,
        index_only: bool = False,
    ) -> None:
        record_id = str(record_id)
        matches = self.metadata[self.metadata["record_id"] == record_id]
        if matches.empty:
            raise KeyError(f"Unknown record_id: {record_id}")

        if not force and self.state.status(record_id) == "completed":
            return

        metadata_row = matches.iloc[0].to_dict()
        mapping = self.mapper.map_dataset(metadata_row)

        if mapping["dataset_local_path"] is None:
            self.state.update(
                record_id,
                status="unresolved",
                mapping_status=mapping["mapping_status"],
                error_message=mapping["mapping_evidence"],
            )
            return

        dataset_path = Path(mapping["dataset_local_path"])
        started_at = datetime.now(timezone.utc)
        started_clock = time.monotonic()

        self.state.update(
            record_id,
            status="processing",
            dataset_local_path=str(dataset_path),
            mapping_status=mapping["mapping_status"],
            started_at=started_at,
        )

        try:
            file_rows = self.indexer.scan(record_id, dataset_path)
            self.store.write_fragment(
                "dataset_file_index",
                record_id,
                file_rows,
            )

            if index_only:
                status = "completed"
            else:
                spectral_rows = []
                evidence_rows = []
                error_rows = []

                prefetch_dir = Path(tempfile.mkdtemp(prefix="spectro_tar_"))
                try:
                    prefetched = self._prefetch_tar_members(file_rows, prefetch_dir, error_rows)
                    for file_row in file_rows:
                        if "::" in file_row["file_path"]:
                            result = self._read_archive_member(
                                record_id, dataset_path, file_row,
                                local_file=prefetched.get(file_row["file_path"]),
                            )
                        else:
                            result = self._read_file(
                                record_id, dataset_path, Path(file_row["file_path"])
                            )
                        if result is None:
                            continue
                        spectral_rows.extend(result.spectral_records)
                        evidence_rows.extend(result.evidence_records)
                        error_rows.extend(result.errors)
                finally:
                    archive_access.close_cached()
                    shutil.rmtree(prefetch_dir, ignore_errors=True)

                spectral_rows, evidence_rows = self._deduplicate(
                    spectral_rows, evidence_rows
                )
                self._fill_axis_unit_from_readme(
                    record_id, dataset_path, spectral_rows, evidence_rows, file_rows
                )
                self._fill_modality_from_readme(
                    record_id, dataset_path, spectral_rows, evidence_rows, file_rows
                )
                self._add_paper_evidence(
                    record_id, dataset_path, spectral_rows, evidence_rows, error_rows
                )

                no_spectral_data = not spectral_rows
                if no_spectral_data:
                    # Make the reason visible instead of silently writing an
                    # all-NULL row and marking the dataset "completed".
                    extensions = Counter(
                        (row["extension"] or "<none>") for row in file_rows
                    )
                    supported = sorted(
                        {ext for reader in self.readers for ext in reader.extensions}
                    )
                    error_rows.append({
                        "record_id": record_id,
                        "source_file": str(dataset_path),
                        "reader": "pipeline",
                        "error_type": "NoSpectralDataFound",
                        "error_message": (
                            "No reader produced a spectral record. "
                            f"File extensions in dataset: {dict(extensions.most_common(15))}. "
                            f"Supported extensions: {supported}"
                        ),
                    })
                    if self.config.get("pipeline", {}).get(
                        "write_empty_spectral_row", True
                    ):
                        spectral_rows = [empty_spectral_record(record_id)]

                self.store.write_fragment(
                    "spectroscopy_metadata",
                    record_id,
                    spectral_rows,
                )
                self.store.write_fragment(
                    "evidence",
                    record_id,
                    evidence_rows,
                )
                self.store.write_fragment(
                    "extraction_errors",
                    record_id,
                    error_rows,
                )

                if no_spectral_data:
                    status = "no_spectral_data"
                else:
                    status = "partial" if error_rows else "completed"

            finished_at = datetime.now(timezone.utc)
            self.state.update(
                record_id,
                status=status,
                dataset_local_path=str(dataset_path),
                mapping_status=mapping["mapping_status"],
                started_at=started_at,
                finished_at=finished_at,
                processing_seconds=time.monotonic() - started_clock,
            )

        except Exception as exc:
            self.state.update(
                record_id,
                status="failed",
                dataset_local_path=str(dataset_path),
                mapping_status=mapping["mapping_status"],
                started_at=started_at,
                finished_at=datetime.now(timezone.utc),
                processing_seconds=time.monotonic() - started_clock,
                error_message=f"{type(exc).__name__}: {exc}",
            )

    # ------------------------------------------------------------------ #
    # File reading helpers
    # ------------------------------------------------------------------ #
    def _reader_for(self, path: Path):
        for reader in self.readers:
            if reader.supports(path):
                return reader
        return None

    def _read_file(self, record_id: str, dataset_path: Path, file_path: Path):
        reader = self._reader_for(file_path)
        if reader is None:
            return None
        return reader.read(
            record_id=record_id,
            dataset_path=dataset_path,
            file_path=file_path,
        )

    def _wanted_member(self, file_row: dict) -> bool:
        member = archive_access.split_virtual(file_row["file_path"])[1][-1]
        if archive_access.archive_kind(member) or self._reader_for(Path(member)) is None:
            return False
        pipeline_config = self.config.get("pipeline", {})
        max_mb = float(pipeline_config.get("archive_member_max_mb", 2048))
        return (file_row.get("file_size_bytes") or 0) <= max_mb * 1024 * 1024

    def _prefetch_tar_members(
        self, file_rows: list[dict], target_dir: Path, error_rows: list[dict]
    ) -> dict[str, Path]:
        """One sequential pass per compressed tar for all readable members."""
        if not self.config.get("pipeline", {}).get("extract_archive_members", True):
            return {}
        groups: dict[str, set[str]] = {}
        for row in file_rows:
            path = row["file_path"]
            if "::" not in path or not self._wanted_member(row):
                continue
            container, _, member = path.rpartition("::")
            if archive_access.is_streaming_container(container):
                groups.setdefault(container, set()).add(member)

        local: dict[str, Path] = {}
        for container, members in groups.items():
            try:
                extracted = archive_access.extract_tar_members(container, members, target_dir)
            except Exception as exc:
                error_rows.append({
                    "record_id": file_rows[0]["record_id"],
                    "source_file": container,
                    "reader": "tar_prefetch",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                })
                continue
            local.update({f"{container}::{name}": path for name, path in extracted.items()})
        return local

    def _read_archive_member(
        self,
        record_id: str,
        dataset_path: Path,
        file_row: dict,
        local_file: Path | None = None,
    ):
        """Extract one supported archive member to a temp dir and read it.

        The member may sit in nested containers (``a.zip::b.zip::c.txt``),
        a tar/tgz or rar, or a damaged zip recovered by local headers. Only
        members with a supported extension are extracted, and only up to
        ``pipeline.archive_member_max_mb`` (default 2048 MB) each.
        """
        member = archive_access.split_virtual(file_row["file_path"])[1][-1]
        member_path = Path(member)
        if archive_access.archive_kind(member):
            return None  # nested archive itself: its members have own rows
        reader = self._reader_for(member_path)
        if reader is None:
            return None

        pipeline_config = self.config.get("pipeline", {})
        if not pipeline_config.get("extract_archive_members", True):
            return None
        max_mb = float(pipeline_config.get("archive_member_max_mb", 2048))
        size = file_row.get("file_size_bytes") or 0
        if size > max_mb * 1024 * 1024:
            return None

        temp_dir = Path(tempfile.mkdtemp(prefix="spectro_"))
        # Member names may hold characters Windows forbids in file names (e.g. "<45um").
        target = local_file or temp_dir / re.sub(r'[<>:"/\\|?*]', "_", member_path.name)
        try:
            if local_file is None:
                archive_access.extract_member(file_row["file_path"], target, keep_open=True)
            result = reader.read(
                record_id=record_id,
                dataset_path=dataset_path,
                file_path=target,
            )
        except Exception as exc:
            result = ReaderResult(errors=[{
                "record_id": record_id,
                "source_file": file_row["file_path"],
                "reader": "archive_extraction",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }])
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        # Point provenance at the archive member, not the deleted temp file.
        virtual = file_row["file_path"]
        temp_text = str(target)
        for collection in (result.spectral_records, result.evidence_records, result.errors):
            for item in collection:
                if item.get("source_file") == temp_text:
                    item["source_file"] = virtual
        return result

    @staticmethod
    def _deduplicate(
        spectral_rows: list[dict],
        evidence_rows: list[dict],
    ) -> tuple[list[dict], list[dict]]:
        """Drop spectra that are the same data in two formats, e.g.
        ``J0001.fits`` and ``J0001.txt`` with identical axis ranges."""

        def stem(source: str | None) -> str:
            source = (source or "").split("::")[-1]
            return Path(source.replace("\\", "/")).stem.lower()

        def rounded(value):
            # 5 significant digits: tolerant of float32 (FITS) vs text precision.
            return None if value is None else f"{float(value):.5g}"

        seen: set[tuple] = set()
        kept: list[dict] = []
        dropped_sources: set[str] = set()
        for row in spectral_rows:
            key = (
                stem(row.get("source_file")),
                row.get("num_spectral_channels"),
                rounded(row.get("wavelength_min_nm") or row.get("spectral_range_original_min")),
                rounded(row.get("wavelength_max_nm") or row.get("spectral_range_original_max")),
            )
            if key in seen:
                dropped_sources.add(row.get("source_file"))
                continue
            seen.add(key)
            kept.append(row)

        kept_sources = {row.get("source_file") for row in kept}
        dropped_sources -= kept_sources
        evidence = [
            item for item in evidence_rows
            if item.get("source_file") not in dropped_sources
        ]
        return kept, evidence

    def _find_readme(
        self, dataset_path: Path, file_rows: list[dict] | None
    ) -> tuple[str, str] | None:
        """Return (source, text) of the dataset README, looking in the
        dataset folder first and then inside archives (Batch1 datasets are
        often a single zip holding ``README.txt``)."""
        if dataset_path.is_dir():
            for path in sorted(dataset_path.iterdir()):
                if path.is_file() and path.stem.lower().startswith(README_NAMES):
                    try:
                        return str(path), path.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        return None

        candidates = [
            row for row in (file_rows or [])
            if "::" in row["file_path"]
            and (
                Path(row["file_name"]).stem.lower().startswith(README_NAMES)
                or "readme" in Path(row["file_name"]).stem.lower()  # e.g. RSC-README.txt
            )
            and row["extension"] in README_EXTENSIONS
            and (row.get("file_size_bytes") or 0) <= README_MAX_BYTES
        ]
        # Prefer the shallowest README (fewest nested containers).
        candidates.sort(key=lambda row: (row["file_path"].count("::"), len(row["file_path"])))
        for row in candidates:
            try:
                data = archive_access.read_member_bytes(row["file_path"], README_MAX_BYTES)
            except Exception:
                continue
            return row["file_path"], data.decode("utf-8", errors="replace")
        return None

    def _fill_axis_unit_from_readme(
        self,
        record_id: str,
        dataset_path: Path,
        spectral_rows: list[dict],
        evidence_rows: list[dict],
        file_rows: list[dict] | None = None,
    ) -> None:
        """Give unit-less axes (bare number columns) the unit the README
        states for the first column, e.g. "column 1 (x) is in increasing
        wavenumber (cm^-1)". Only applied when the range is plausible for
        that unit."""
        missing = [
            row for row in spectral_rows
            if row.get("spectral_range_original_unit") is None
            and row.get("spectral_range_original_min") is not None
            and row.get("spectral_range_original_max") is not None
        ]
        if not missing:
            return
        found = self._find_readme(dataset_path, file_rows)
        if found is None:
            return
        source, text = found

        unit, quote = None, None
        lines = [line.strip() for line in text[:50000].splitlines() if line.strip()]
        ranked = sorted(
            lines,
            key=lambda line: 0 if re.search(r"col(?:umn)?\s*1|first column|\bx\b", line, re.I) else 1,
        )
        for line in ranked:
            if re.search(r"wavenumber|wavelength|cm\^?-1|cm-1|\bnm\b|micron", line, re.I):
                unit = normalize_spectral_unit(unit_from_text(line))
                if unit:
                    quote = line[:300]
                    break
        if unit is None:
            return

        plausible = {"cm^-1": (1.0, 60000.0), "nm": (100.0, 100000.0), "um": (0.1, 1000.0)}[unit]
        for row in missing:
            low, high = sorted((row["spectral_range_original_min"], row["spectral_range_original_max"]))
            if not (plausible[0] <= low and high <= plausible[1]):
                continue
            common = dict(
                record_id=record_id,
                source_file=source,
                source_type="readme",
                dataset_path=dataset_path,
                extraction_method="readme_axis_unit",
            )
            add_field_with_evidence(
                row, evidence_rows, field_name="spectral_range_original_unit", value=unit,
                evidence_text=f"README: {quote}", confidence=0.75, value_origin="author_provided",
                **common,
            )
            if row.get("sampling_interval") is not None:
                add_field_with_evidence(
                    row, evidence_rows, field_name="sampling_interval_unit", value=unit,
                    evidence_text="Sampling interval uses README axis unit", confidence=0.75,
                    value_origin="calculated", **common,
                )
            bounds = normalize_spectral_bounds(
                row["spectral_range_original_min"], row["spectral_range_original_max"], unit
            )
            for field, value in bounds.items():
                if value is not None:
                    add_field_with_evidence(
                        row, evidence_rows, field_name=field, value=value,
                        evidence_text=f"Converted with README axis unit {unit}",
                        confidence=0.75, value_origin="calculated", **common,
                    )

    def _fill_modality_from_readme(
        self,
        record_id: str,
        dataset_path: Path,
        spectral_rows: list[dict],
        evidence_rows: list[dict],
        file_rows: list[dict] | None = None,
    ) -> None:
        """Use the dataset's README text for rows whose modality is unknown
        (or only inferred from the wavelength range)."""
        missing = [
            row for row in spectral_rows
            if row.get("modality") is None
        ]
        if not missing:
            return

        found = self._find_readme(dataset_path, file_rows)
        if found is None:
            return
        source, text = found
        modality = modality_from_text(text[:20000])
        if not modality:
            return

        for row in missing:
            add_field_with_evidence(
                row,
                evidence_rows,
                field_name="modality",
                value=modality,
                record_id=record_id,
                source_file=source,
                source_type="readme",
                evidence_text=f"Modality keyword found in {Path(source.split('::')[-1]).name}",
                dataset_path=dataset_path,
                extraction_method="readme_keyword",
                confidence=0.85,
                value_origin="author_provided",
            )

    def _paper_for(self, record_id: str) -> Path | None:
        if self.papers_directory is None:
            return None
        # Papers are <record_id>.pdf or a JATS article <record_id>.xml (PMC).
        for suffix in (".pdf", ".xml", ".nxml"):
            path = self.papers_directory / f"{record_id}{suffix}"
            if path.is_file():
                return path
        return None

    def _add_paper_evidence(
        self,
        record_id: str,
        dataset_path: Path,
        spectral_rows: list[dict],
        evidence_rows: list[dict],
        error_rows: list[dict],
    ) -> None:
        """Attach regex candidates from the record's paper (papers/<id>.pdf)
        as ``source_type='pdf'`` evidence. Paper values never overwrite file
        values; the paper's dominant modality only fills rows that have none.
        """
        paper = self._paper_for(record_id)
        if paper is None:
            return
        try:
            if self._pdf_extractor is None:
                from extraction.extractor import PDFSpectralExtractor

                self._pdf_extractor = PDFSpectralExtractor()
            candidates = self._pdf_extractor.extract(paper)
        except Exception as exc:
            error_rows.append({
                "record_id": record_id,
                "source_file": str(paper),
                "reader": "PDFSpectralExtractor",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            })
            return

        limit = int(self.config.get("pipeline", {}).get("paper_evidence_max", 500))
        for candidate in candidates[:limit]:
            if candidate.value is None:
                continue
            evidence_rows.append(make_evidence(
                record_id=record_id,
                field_name=candidate.field_name,
                field_value=candidate.value,
                source_file=paper,
                source_type="pdf",
                evidence_text=candidate.evidence_text[:2000],
                dataset_path=dataset_path,
                extraction_method=f"pdf_{candidate.extraction_method}",
                confidence=candidate.confidence,
                value_origin="author_provided",
                page_number=candidate.page_number,
            ))

        modalities = Counter(
            c.value for c in candidates if c.field_name == "modality" and c.value
        )
        if not modalities:
            return
        modality, count = modalities.most_common(1)[0]
        for row in spectral_rows:
            if row.get("modality") is None and row.get("source_file"):
                add_field_with_evidence(
                    row,
                    evidence_rows,
                    field_name="modality",
                    value=modality,
                    record_id=record_id,
                    source_file=paper,
                    source_type="pdf",
                    evidence_text=f"Most frequent modality keyword in paper ({count} pages)",
                    dataset_path=dataset_path,
                    extraction_method="pdf_modality_majority",
                    confidence=0.6,
                    value_origin="inferred",
                )

    def consolidate(self) -> None:
        for table_name in (
            "dataset_file_index",
            "spectroscopy_metadata",
            "evidence",
            "extraction_errors",
        ):
            self.store.consolidate(table_name)

    def report(self, record_id: str) -> None:
        output = Path(self.config["paths"]["output_directory"])
        spectral_path = output / "spectroscopy_metadata.parquet"
        evidence_path = output / "evidence.parquet"

        metadata = self.metadata[
            self.metadata["record_id"] == str(record_id)
        ].iloc[0]

        spectral = (
            pd.read_parquet(spectral_path)
            if spectral_path.exists()
            else pd.DataFrame()
        )
        evidence = (
            pd.read_parquet(evidence_path)
            if evidence_path.exists()
            else pd.DataFrame()
        )

        spectral = spectral[spectral["record_id"] == str(record_id)]
        evidence = evidence[evidence["record_id"] == str(record_id)]

        print(f"Dataset: {metadata.get('title')}")
        print(f"record_id: {record_id}")
        print()

        if spectral.empty:
            print("No spectral metadata established.")
            return

        for index, row in spectral.iterrows():
            print(f"Spectral record {index}:")
            print(f"  modality: {row.get('modality')}")
            print(
                "  original range: "
                f"{row.get('spectral_range_original_min')} -> "
                f"{row.get('spectral_range_original_max')} "
                f"{row.get('spectral_range_original_unit')}"
            )
            print(f"  channels: {row.get('num_spectral_channels')}")
            print(f"  spectra: {row.get('num_spectra')}")
            print(
                f"  image dimensions: "
                f"{row.get('image_height')} x {row.get('image_width')}"
            )
            print(f"  source: {row.get('source_file')}")
            print()

        print(f"Evidence records: {len(evidence)}")

    def stats(self) -> None:
        self.state.stats()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="config/config.yaml",
    )

    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--record-id")
    selection.add_argument("--all", action="store_true")
    selection.add_argument("--failed", action="store_true")

    parser.add_argument("--force", action="store_true")
    parser.add_argument("--index-files", action="store_true")
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--report", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)

    if args.stats:
        # Statistics only depend on the persisted extraction state. Do not
        # initialize metadata or dataset mapping for a reporting-only run.
        StateManager(config["paths"]["output_directory"]).stats()
        return 0

    pipeline = Pipeline(config)

    if args.record_id:
        record_ids = [str(args.record_id)]
    elif args.failed:
        state = pipeline.state.read()
        record_ids = state.loc[
            state["status"].isin(["failed", "partial", "no_spectral_data"]),
            "record_id",
        ].astype(str).tolist()
    elif args.all:
        record_ids = pipeline.selected_record_ids()
    else:
        raise SystemExit(
            "Specify --record-id, --all, --failed, or --stats"
        )

    for record_id in tqdm(record_ids, desc="Datasets"):
        pipeline.process_record(
            record_id,
            force=args.force,
            index_only=args.index_files,
        )

    pipeline.consolidate()

    if args.report and len(record_ids) == 1:
        pipeline.report(record_ids[0])

    return 0


if __name__ == "__main__":
    sys.exit(main())

from __future__ import annotations

import bz2
import gzip
import tarfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Iterator

from scanner import archive_access


DOCUMENT_EXTENSIONS = {
    ".txt", ".md", ".rst", ".json", ".yaml", ".yml", ".xml", ".html", ".pdf"
}
TABULAR_EXTENSIONS = {
    ".csv", ".tsv", ".xlsx", ".xls", ".parquet", ".feather"
}
SPECTRAL_EXTENSIONS = {
    ".jdx", ".dx", ".spc", ".opus", ".wdf", ".sif", ".mat", ".h5", ".hdf5",
    ".nc", ".nc4", ".cdf", ".zarr", ".dat", ".srs", ".irs", ".ir", ".raman",
    ".mzml", ".sdf", ".mol", ".fits", ".fit", ".fts", ".nc4", ".he5",
    ".dpt", ".asc", ".spa", ".states", ".trans", ".def", ".kta", ".hdr",
}
IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".tif", ".tiff"
}
ARCHIVE_EXTENSIONS = {
    ".zip", ".7z", ".tar", ".gz", ".bz2", ".tgz", ".tbz2", ".rar"
}


def effective_extension(path: Path | PurePosixPath) -> str:
    name = path.name.lower()
    for compound in (".tar.gz", ".tar.bz2", ".tar.xz"):
        if name.endswith(compound):
            return compound
    return path.suffix.lower()


def classify_extension(extension: str) -> dict[str, bool]:
    simple = extension.lower()
    archive = simple in ARCHIVE_EXTENSIONS or simple.startswith(".tar.")
    return {
        "is_archive": archive,
        "is_document": simple in DOCUMENT_EXTENSIONS,
        "is_spectral": simple in SPECTRAL_EXTENSIONS,
        "is_tabular": simple in TABULAR_EXTENSIONS,
        "is_image": simple in IMAGE_EXTENSIONS,
    }


def make_file_row(
    *,
    record_id: str,
    file_path: str,
    relative_path: str,
    file_name: str,
    extension: str,
    file_size_bytes: int | None,
    parent_directory: str,
    scan_status: str,
) -> dict:
    return {
        "record_id": str(record_id),
        "file_path": file_path,
        "relative_path": relative_path,
        "file_name": file_name,
        "extension": extension,
        "file_size_bytes": file_size_bytes,
        "parent_directory": parent_directory,
        **classify_extension(extension),
        "scan_status": scan_status,
    }


class FileIndexer:
    def __init__(self, config: dict):
        scanner_config = config.get("scanner", {})
        self.inspect_archives = bool(scanner_config.get("inspect_archives", True))
        self.max_archive_members = int(
            scanner_config.get("max_archive_members", 100000)
        )
        # Archives inside archives (zip-in-zip is common on Zenodo/Dryad).
        self.max_archive_depth = int(scanner_config.get("max_archive_depth", 3))
        self.nested_archive_max_mb = float(
            scanner_config.get("nested_archive_max_mb", 4096)
        )
        self.skip_junk = bool(scanner_config.get("skip_junk_members", True))

    def scan(self, record_id: str, dataset_path: str | Path) -> list[dict]:
        root = Path(dataset_path).resolve()
        rows: list[dict] = []

        # A dataset may be a single archive file (e.g. "<id>_<title>.zip").
        if root.is_file():
            files, base = [root], root.parent
        else:
            files, base = sorted(root.rglob("*")), root

        for path in files:
            if not path.is_file():
                continue
            if self.skip_junk and archive_access.is_junk(path.name):
                continue

            relative = path.relative_to(base).as_posix()
            extension = effective_extension(path)
            row = make_file_row(
                record_id=record_id,
                file_path=str(path),
                relative_path=relative,
                file_name=path.name,
                extension=extension,
                file_size_bytes=path.stat().st_size,
                parent_directory=path.parent.relative_to(base).as_posix(),
                scan_status="indexed",
            )
            rows.append(row)

            if row["is_archive"] and self.inspect_archives:
                try:
                    if archive_access.archive_kind(path.name):
                        archive_rows = list(
                            self._inspect_nested(record_id, base, path, row)
                        )
                    else:
                        archive_rows = list(
                            self._inspect_archive(record_id, base, path)
                        )
                    rows.extend(archive_rows)
                except Exception as exc:
                    row["scan_status"] = f"archive_inspection_error:{type(exc).__name__}"

        return rows

    def _inspect_nested(
        self,
        record_id: str,
        root: Path,
        archive_path: Path,
        archive_row: dict,
    ) -> Iterator[dict]:
        """Index zip/tar/rar members recursively (archive-in-archive).

        Damaged zips are walked by local headers; their rows are marked
        ``archive_member_recovered`` and the archive row
        ``archive_partially_recovered``.
        """
        relative_archive = archive_path.relative_to(root).as_posix()
        budget = [self.max_archive_members]

        def walk(container, virtual: str, relative: str, depth: int, owner: dict):
            if container.recovered:
                owner["scan_status"] = "archive_partially_recovered"
            for member in container.members():
                if budget[0] <= 0:
                    return
                if self.skip_junk and archive_access.is_junk(member.name):
                    continue
                posix = PurePosixPath(member.name)
                row = make_file_row(
                    record_id=record_id,
                    file_path=f"{virtual}::{posix.as_posix()}",
                    relative_path=f"{relative}::{posix.as_posix()}",
                    file_name=posix.name,
                    extension=effective_extension(posix),
                    file_size_bytes=member.size,
                    parent_directory=posix.parent.as_posix(),
                    scan_status=(
                        "archive_member_recovered" if member.recovered
                        else "archive_member_indexed"
                    ),
                )
                budget[0] -= 1
                yield row

                too_big = (member.size or 0) > self.nested_archive_max_mb * 1024 * 1024
                if member.is_archive and depth < self.max_archive_depth and not too_big:
                    try:
                        child = container.open_child(member.name, member.size)
                    except Exception as exc:
                        row["scan_status"] = f"archive_inspection_error:{type(exc).__name__}"
                        continue
                    try:
                        yield from walk(
                            child,
                            row["file_path"],
                            row["relative_path"],
                            depth + 1,
                            row,
                        )
                    except Exception as exc:
                        row["scan_status"] = f"archive_inspection_error:{type(exc).__name__}"
                    finally:
                        child.close()

        container = archive_access.Container(archive_path, archive_path.name)
        try:
            yield from walk(container, str(archive_path), relative_archive, 1, archive_row)
        finally:
            container.close()

    def _inspect_archive(
        self,
        record_id: str,
        root: Path,
        archive_path: Path,
    ) -> Iterator[dict]:
        relative_archive = archive_path.relative_to(root).as_posix()
        extension = effective_extension(archive_path)
        count = 0

        def convert(name: str, size: int | None) -> dict:
            member = PurePosixPath(name)
            member_extension = effective_extension(member)
            virtual_path = f"{archive_path}::{member.as_posix()}"
            virtual_relative = f"{relative_archive}::{member.as_posix()}"

            return make_file_row(
                record_id=record_id,
                file_path=virtual_path,
                relative_path=virtual_relative,
                file_name=member.name,
                extension=member_extension,
                file_size_bytes=size,
                parent_directory=member.parent.as_posix(),
                scan_status="archive_member_indexed",
            )

        if extension == ".zip":
            with zipfile.ZipFile(archive_path) as archive:
                for info in archive.infolist():
                    if info.is_dir():
                        continue
                    if count >= self.max_archive_members:
                        break
                    yield convert(info.filename, info.file_size)
                    count += 1
            return

        if extension in {".tar", ".tar.gz", ".tar.bz2", ".tar.xz", ".tgz", ".tbz2"}:
            with tarfile.open(archive_path, mode="r:*") as archive:
                for member in archive:
                    if not member.isfile():
                        continue
                    if count >= self.max_archive_members:
                        break
                    yield convert(member.name, member.size)
                    count += 1
            return

        if extension == ".7z":
            try:
                import py7zr
            except ImportError:
                return

            with py7zr.SevenZipFile(archive_path, mode="r") as archive:
                for name, info in archive.list():
                    if getattr(info, "is_directory", False):
                        continue
                    if count >= self.max_archive_members:
                        break
                    yield convert(name, getattr(info, "uncompressed", None))
                    count += 1
            return

        # Plain .gz and .bz2 are single compressed streams, not directory
        # archives. Open enough to verify validity but do not decompress.
        if extension == ".gz":
            with gzip.open(archive_path, "rb") as stream:
                stream.read(1)
        elif extension == ".bz2":
            with bz2.open(archive_path, "rb") as stream:
                stream.read(1)

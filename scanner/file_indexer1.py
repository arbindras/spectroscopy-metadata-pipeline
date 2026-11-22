from __future__ import annotations

import bz2
import gzip
import tarfile
import zipfile

from pathlib import Path, PurePosixPath
from typing import Iterator


# ============================================================
# FILE TYPE DEFINITIONS
# ============================================================

DOCUMENT_EXTENSIONS = {

    ".txt",
    ".md",
    ".rst",
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".html",
    ".htm",
    ".pdf"

}


TABULAR_EXTENSIONS = {

    ".csv",
    ".tsv",
    ".xlsx",
    ".xls",
    ".parquet",
    ".feather"

}


SPECTRAL_EXTENSIONS = {

    ".jdx",
    ".dx",
    ".spc",
    ".opus",
    ".wdf",
    ".sif",
    ".mat",
    ".h5",
    ".hdf5",
    ".hdf",
    ".nc",
    ".nc4",
    ".cdf",
    ".zarr",
    ".dat",
    ".srs",
    ".irs",
    ".ir",
    ".raman",
    ".mzml",
    ".sdf",
    ".mol"

}


IMAGE_EXTENSIONS = {

    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
    ".bmp"

}


ARCHIVE_EXTENSIONS = {

    ".zip",
    ".7z",
    ".tar",
    ".gz",
    ".bz2",
    ".tgz",
    ".tbz2"

}


# ============================================================
# EXTENSION HELPERS
# ============================================================

def effective_extension(
    path: Path | PurePosixPath
) -> str:

    name = path.name.lower()

    compound_extensions = [

        ".tar.gz",
        ".tar.bz2",
        ".tar.xz"

    ]

    for extension in compound_extensions:

        if name.endswith(extension):

            return extension

    return path.suffix.lower()


def classify_extension(
    extension: str
) -> dict[str, bool]:

    extension = extension.lower()

    is_archive = (

        extension
        in ARCHIVE_EXTENSIONS

        or extension.startswith(
            ".tar."
        )

    )

    return {

        "is_archive":
            is_archive,

        "is_document":
            extension
            in DOCUMENT_EXTENSIONS,

        "is_spectral":
            extension
            in SPECTRAL_EXTENSIONS,

        "is_tabular":
            extension
            in TABULAR_EXTENSIONS,

        "is_image":
            extension
            in IMAGE_EXTENSIONS

    }


# ============================================================
# FILE ROW
# ============================================================

def make_file_row(

    *,
    record_id: str,
    file_path: str,
    relative_path: str,
    file_name: str,
    extension: str,
    file_size_bytes: int | None,
    parent_directory: str,
    scan_status: str

) -> dict:

    return {

        "record_id":
            str(record_id),

        "file_path":
            file_path,

        "relative_path":
            relative_path,

        "file_name":
            file_name,

        "extension":
            extension,

        "file_size_bytes":
            file_size_bytes,

        "parent_directory":
            parent_directory,

        **classify_extension(
            extension
        ),

        "scan_status":
            scan_status

    }


# ============================================================
# FILE INDEXER
# ============================================================

class FileIndexer:

    def __init__(
        self,
        config: dict
    ):

        scanner_config = config.get(
            "scanner",
            {}
        )

        self.inspect_archives = bool(

            scanner_config.get(
                "inspect_archives",
                True
            )

        )

        self.max_archive_members = int(

            scanner_config.get(
                "max_archive_members",
                5000
            )

        )

    # ========================================================
    # SCAN DATASET
    # ========================================================

    def scan(

        self,
        record_id: str,
        dataset_path: str | Path

    ) -> list[dict]:

        root = Path(
            dataset_path
        ).resolve()

        if not root.exists():

            raise FileNotFoundError(
                f"Dataset path not found:\n"
                f"{root}"
            )

        if not root.is_dir():

            raise NotADirectoryError(
                f"Dataset path is not a directory:\n"
                f"{root}"
            )

        rows: list[dict] = []

        print(
            f"Scanning dataset {record_id}"
        )

        # ----------------------------------------------------
        # RECURSIVELY INDEX FILES
        # ----------------------------------------------------

        for path in root.rglob("*"):

            if not path.is_file():

                continue

            try:

                relative_path = (

                    path
                    .relative_to(root)
                    .as_posix()

                )

                parent_directory = (

                    path.parent
                    .relative_to(root)
                    .as_posix()

                )

            except ValueError:

                continue

            extension = effective_extension(
                path
            )

            try:

                file_size = (
                    path.stat().st_size
                )

            except OSError:

                file_size = None

            row = make_file_row(

                record_id=record_id,

                file_path=str(
                    path
                ),

                relative_path=relative_path,

                file_name=path.name,

                extension=extension,

                file_size_bytes=file_size,

                parent_directory=parent_directory,

                scan_status="indexed"

            )

            rows.append(
                row
            )

            # ------------------------------------------------
            # ARCHIVE INSPECTION
            # ------------------------------------------------

            if (

                row["is_archive"]

                and self.inspect_archives

            ):

                try:

                    archive_rows = list(

                        self._inspect_archive(

                            record_id=record_id,

                            root=root,

                            archive_path=path

                        )

                    )

                    rows.extend(
                        archive_rows
                    )

                except Exception as exc:

                    row["scan_status"] = (

                        "archive_inspection_error:"

                        f"{type(exc).__name__}"

                    )

        return rows

    # ========================================================
    # INSPECT ARCHIVES
    # ========================================================

    def _inspect_archive(

        self,
        record_id: str,
        root: Path,
        archive_path: Path

    ) -> Iterator[dict]:

        relative_archive = (

            archive_path
            .relative_to(root)
            .as_posix()

        )

        extension = effective_extension(
            archive_path
        )

        count = 0


        def convert(

            name: str,
            size: int | None

        ) -> dict:

            member = PurePosixPath(
                name
            )

            member_extension = (
                effective_extension(
                    member
                )
            )

            virtual_path = (

                f"{archive_path}"

                f"::"

                f"{member.as_posix()}"

            )

            virtual_relative = (

                f"{relative_archive}"

                f"::"

                f"{member.as_posix()}"

            )

            return make_file_row(

                record_id=record_id,

                file_path=virtual_path,

                relative_path=virtual_relative,

                file_name=member.name,

                extension=member_extension,

                file_size_bytes=size,

                parent_directory=(
                    member.parent
                    .as_posix()
                ),

                scan_status=(
                    "archive_member_indexed"
                )

            )


        # ----------------------------------------------------
        # ZIP
        # ----------------------------------------------------

        if extension == ".zip":

            with zipfile.ZipFile(
                archive_path
            ) as archive:

                for info in archive.infolist():

                    if info.is_dir():

                        continue

                    if (
                        count
                        >= self.max_archive_members
                    ):

                        break

                    yield convert(

                        info.filename,

                        info.file_size

                    )

                    count += 1

            return


        # ----------------------------------------------------
        # TAR
        # ----------------------------------------------------

        if extension in {

            ".tar",
            ".tar.gz",
            ".tar.bz2",
            ".tar.xz",
            ".tgz",
            ".tbz2"

        }:

            with tarfile.open(

                archive_path,

                mode="r:*"

            ) as archive:

                for member in archive:

                    if not member.isfile():

                        continue

                    if (
                        count
                        >= self.max_archive_members
                    ):

                        break

                    yield convert(

                        member.name,

                        member.size

                    )

                    count += 1

            return


        # ----------------------------------------------------
        # 7Z
        # ----------------------------------------------------

        if extension == ".7z":

            try:

                import py7zr

            except ImportError:

                return

            with py7zr.SevenZipFile(

                archive_path,

                mode="r"

            ) as archive:

                for info in archive.list():

                    name = info.filename

                    is_directory = getattr(

                        info,

                        "is_directory",

                        False

                    )

                    if is_directory:

                        continue

                    if (
                        count
                        >= self.max_archive_members
                    ):

                        break

                    size = getattr(

                        info,

                        "uncompressed",

                        None

                    )

                    yield convert(
                        name,
                        size
                    )

                    count += 1

            return


        # ----------------------------------------------------
        # GZIP
        # ----------------------------------------------------

        if extension == ".gz":

            with gzip.open(

                archive_path,

                "rb"

            ) as stream:

                stream.read(1)

            return


        # ----------------------------------------------------
        # BZIP2
        # ----------------------------------------------------

        if extension == ".bz2":

            with bz2.open(

                archive_path,

                "rb"

            ) as stream:

                stream.read(1)

            return
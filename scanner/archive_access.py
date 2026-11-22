"""Uniform access to (possibly nested) archive members.

Virtual paths chain containers with ``::``, e.g.::

    D:/Batch1/123_x.zip::inner.zip::data/spectrum.txt

Supported containers: zip (incl. zip64 and *stored* nested zips, which are
read without copying), tar/tar.gz/tgz/tar.bz2/tar.xz, and rar (optional
``rarfile`` + UnRAR). Zips whose central directory is missing (truncated or
zero-filled downloads) are walked by their local file headers so that intact
leading members can still be indexed and read.
"""

from __future__ import annotations

import io
import os
import shutil
import struct
import tarfile
import zipfile
import zlib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Iterator

SEPARATOR = "::"
JUNK_PARTS = ("__MACOSX",)
JUNK_NAMES = (".ds_store", "thumbs.db", "desktop.ini")
TAR_SUFFIXES = (".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz")
UNRAR_CANDIDATES = (
    r"C:\Program Files\WinRAR\UnRAR.exe",
    r"C:\Program Files (x86)\WinRAR\UnRAR.exe",
)


@dataclass(frozen=True)
class Member:
    name: str              # path inside its immediate container (posix)
    size: int | None       # uncompressed size when known
    is_archive: bool
    recovered: bool = False  # found by local-header walk of a damaged zip


def is_junk(name: str) -> bool:
    parts = PurePosixPath(name.replace("\\", "/")).parts
    return any(part in JUNK_PARTS for part in parts) or (
        bool(parts) and (parts[-1].lower() in JUNK_NAMES or parts[-1].startswith("._"))
    )


def archive_kind(name: str) -> str | None:
    lowered = name.lower()
    if lowered.endswith(".zip"):
        return "zip"
    if lowered.endswith(TAR_SUFFIXES):
        return "tar"
    if lowered.endswith(".rar"):
        return "rar"
    return None


def split_virtual(path: str) -> tuple[str, list[str]]:
    parts = str(path).split(SEPARATOR)
    return parts[0], parts[1:]


# --------------------------------------------------------------------- #
# Damaged zip recovery
# --------------------------------------------------------------------- #
def _walk_local_headers(stream: BinaryIO, size: int) -> Iterator[tuple[str, int, int, int, int]]:
    """Yield (name, data_offset, compressed_size, uncompressed_size, method)."""
    position = 0
    while position + 30 <= size:
        stream.seek(position)
        header = stream.read(30)
        if header[:4] != b"PK\x03\x04":
            return
        flags, method = struct.unpack("<HH", header[6:10])
        compressed, uncompressed, name_length, extra_length = struct.unpack("<IIHH", header[18:30])
        name = stream.read(name_length).decode("utf-8", "replace")
        extra = stream.read(extra_length)
        if 0xFFFFFFFF in (compressed, uncompressed):
            offset = 0
            while offset + 4 <= len(extra):
                header_id, header_size = struct.unpack("<HH", extra[offset:offset + 4])
                if header_id == 1:
                    uncompressed, compressed = struct.unpack("<QQ", extra[offset + 4:offset + 20])
                    break
                offset += 4 + header_size
        data_offset = position + 30 + name_length + extra_length
        if data_offset + compressed > size:
            return  # member truncated
        if flags & 0x08 and compressed == 0:
            return  # streamed member without sizes: cannot continue safely
        yield name, data_offset, compressed, uncompressed, method
        position = data_offset + compressed


class _RecoveredZip:
    """Minimal read-only view of members recovered from a damaged zip."""

    def __init__(self, stream: BinaryIO, size: int):
        self.stream = stream
        self.entries = {
            name: (offset, compressed, uncompressed, method)
            for name, offset, compressed, uncompressed, method in _walk_local_headers(stream, size)
            if not name.endswith("/")
        }

    def read(self, name: str) -> bytes:
        offset, compressed, _uncompressed, method = self.entries[name]
        self.stream.seek(offset)
        data = self.stream.read(compressed)
        if method == 8:
            return zlib.decompressobj(-15).decompress(data)
        if method == 0:
            return data
        raise NotImplementedError(f"zip compression method {method}")


# --------------------------------------------------------------------- #
# Container opening
# --------------------------------------------------------------------- #
def _unrar_tool() -> str | None:
    for candidate in UNRAR_CANDIDATES:
        if os.path.exists(candidate):
            return candidate
    return shutil.which("unrar")


class Container:
    """An opened archive (zip/tar/rar or recovered zip)."""

    def __init__(self, source: str | Path | BinaryIO, name: str, size: int | None = None):
        self.name = name
        self.kind = archive_kind(name)
        self.recovered = False
        self._handle = None
        if self.kind == "zip":
            try:
                self._handle = zipfile.ZipFile(source)
            except zipfile.BadZipFile:
                stream = open(source, "rb") if isinstance(source, (str, Path)) else source
                if size is None:
                    stream.seek(0, io.SEEK_END)
                    size = stream.tell()
                self._handle = _RecoveredZip(stream, size)
                self.recovered = True
        elif self.kind == "tar":
            if isinstance(source, (str, Path)):
                self._handle = tarfile.open(source, mode="r:*")
            else:
                self._handle = tarfile.open(fileobj=source, mode="r:*")
        elif self.kind == "rar":
            import rarfile  # optional dependency

            tool = _unrar_tool()
            if tool:
                rarfile.UNRAR_TOOL = tool
            if not isinstance(source, (str, Path)):
                source = io.BytesIO(source.read())
            self._handle = rarfile.RarFile(source)
        else:
            raise ValueError(f"Not an archive: {name}")

    def members(self) -> Iterator[Member]:
        if self.recovered:
            for name, (_o, _c, uncompressed, _m) in self._handle.entries.items():
                yield Member(name, uncompressed, archive_kind(name) is not None, True)
        elif self.kind == "zip":
            for info in self._handle.infolist():
                if not info.is_dir():
                    yield Member(info.filename, info.file_size, archive_kind(info.filename) is not None)
        elif self.kind == "tar":
            for info in self._handle:
                if info.isfile():
                    yield Member(info.name, info.size, archive_kind(info.name) is not None)
        else:
            for info in self._handle.infolist():
                if not info.is_dir():
                    yield Member(info.filename, info.file_size, archive_kind(info.filename) is not None)

    def open_stream(self, name: str) -> BinaryIO:
        """Readable (seekable when possible) stream of one member."""
        if self.recovered:
            return io.BytesIO(self._handle.read(name))
        if self.kind == "zip":
            info = self._handle.getinfo(name)
            stream = self._handle.open(info)
            # Stored members are seekable in place: no need to buffer GBs.
            if info.compress_type == zipfile.ZIP_STORED:
                return stream
            return io.BytesIO(stream.read())
        if self.kind == "tar":
            extracted = self._handle.extractfile(name)
            if extracted is None:
                raise FileNotFoundError(name)
            return extracted
        return io.BytesIO(self._handle.read(name))

    def open_child(self, name: str, size: int | None = None) -> "Container":
        return Container(self.open_stream(name), name, size)

    def close(self) -> None:
        close = getattr(self._handle, "close", None)
        if close:
            close()


def open_chain(path: str) -> tuple[Container, str | None, list[Container]]:
    """Open every container of a virtual path.

    Returns ``(innermost_container, final_member_name, opened_containers)``.
    ``final_member_name`` is None when the virtual path itself names an
    archive (e.g. ``outer.zip::inner.zip``).
    """
    outer, chain = split_virtual(path)
    opened = [Container(outer, Path(outer).name)]
    for index, member in enumerate(chain):
        last = index == len(chain) - 1
        if last and archive_kind(member) is None:
            return opened[-1], member, opened
        opened.append(opened[-1].open_child(member))
    return opened[-1], None, opened


# Zip chain kept open between extract_member(keep_open=True) calls:
# (virtual container path, opened containers). Re-opening a zip parses its
# whole central directory, which is quadratic for IODP-style archives with
# tens of thousands of members read one by one.
_cached_chain: tuple[str, list[Container]] | None = None


def close_cached() -> None:
    """Close the zip chain kept open by ``extract_member(keep_open=True)``."""
    global _cached_chain
    if _cached_chain is not None:
        for item in reversed(_cached_chain[1]):
            item.close()
        _cached_chain = None


def extract_member(path: str, target: Path, chunk: int = 1024 * 1024, *, keep_open: bool = False) -> Path:
    """Copy the member named by a virtual path into ``target``.

    With ``keep_open`` the opened zip chain is reused for the next member of
    the same container; call ``close_cached()`` when done.
    """
    global _cached_chain
    key = path.rpartition(SEPARATOR)[0]
    if keep_open and _cached_chain is not None and _cached_chain[0] == key:
        container, member, opened = _cached_chain[1][-1], split_virtual(path)[1][-1], None
    else:
        if keep_open:
            close_cached()
        container, member, opened = open_chain(path)
        if keep_open and member is not None and all(item.kind == "zip" for item in opened):
            _cached_chain, opened = (key, opened), None
    try:
        if member is None:
            raise IsADirectoryError(f"{path} is an archive, not a file")
        with container.open_stream(member) as source, target.open("wb") as sink:
            shutil.copyfileobj(source, sink, chunk)
    finally:
        for item in reversed(opened or []):
            item.close()
    return target


def is_streaming_container(virtual_container: str) -> bool:
    """Compressed tars have no random access: reading N members one by one
    re-decompresses from the start N times."""
    name = split_virtual(virtual_container)[1][-1] if SEPARATOR in virtual_container else virtual_container
    return name.lower().endswith((".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz"))


def extract_tar_members(virtual_container: str, names: set[str], target_dir: Path,
                        chunk: int = 1024 * 1024) -> dict[str, Path]:
    """Extract ``names`` from a (nested) tar container in one sequential pass."""
    outer, chain = split_virtual(virtual_container)
    opened = [Container(outer, Path(outer).name)]
    extracted: dict[str, Path] = {}
    try:
        for member in chain:
            opened.append(opened[-1].open_child(member))
        tar = opened[-1]._handle
        if not isinstance(tar, tarfile.TarFile):
            raise ValueError(f"{virtual_container} is not a tar archive")
        for index, info in enumerate(tar):
            if not info.isfile() or info.name not in names:
                continue
            source = tar.extractfile(info)
            if source is None:
                continue
            target = target_dir / f"{index:06d}_{PurePosixPath(info.name).name}"
            with source, target.open("wb") as sink:
                shutil.copyfileobj(source, sink, chunk)
            extracted[info.name] = target
            if len(extracted) == len(names):
                break
    finally:
        for item in reversed(opened):
            item.close()
    return extracted


def read_member_bytes(path: str, limit: int | None = None) -> bytes:
    container, member, opened = open_chain(path)
    try:
        if member is None:
            raise IsADirectoryError(path)
        with container.open_stream(member) as source:
            return source.read() if limit is None else source.read(limit)
    finally:
        for item in reversed(opened):
            item.close()

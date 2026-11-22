from __future__ import annotations

import html
import io
import re
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

import pandas as pd

from scanner import archive_access


TEXT_EXTENSIONS = {
    ".csv", ".tsv", ".txt", ".dat", ".asc", ".dpt", ".xy", ".prn", ".jdx", ".dx",
    ".md", ".json", ".ini", ".log", ".out", ".spe", ".sp", ".csv2", ".tab", ".rtf",
    ".m", ".py", ".r", ".yaml", ".yml", ".hdr", "",
}
SHEET_EXTENSIONS = {".xlsx", ".xlsm", ".xls"}
ARRAY_EXTENSIONS = {".mat", ".h5", ".hdf5", ".nc", ".nc4", ".he5"}
# Binary formats previewed by their printable strings (Origin projects,
# Thermo/Galactic SPC, Bruker OPUS .0/.1, Ocean/Avantes and similar).
BINARY_STRING_EXTENSIONS = {
    ".opj", ".opju", ".spa", ".spc", ".sbm", ".dsx", ".emd", ".wdf", ".sif",
    ".spe", ".cdx", ".pck", ".docx",
}
TEXT_EXTENSIONS |= {".tabular", ".xyz", ".spectrum", ".esp", ".itx"}
DOC_HINTS = ("readme", "read_me", "description", "about", "metadata", "data_dictionary", "codebook")
SPECTRAL_NAME = re.compile(
    r"spectr|raman|ftir|ft-ir|\bir\b|uv|vis|nir|absorb|fluoresc|emission|reflect|transmi|wavenumber|wavelength",
    re.I,
)
PAPER_PRIORITY = re.compile(
    r"method|experiment|material|instrument|spectro|measure|characteri|data|sample|"
    r"preparation|analysis|abstract|availability|supporting|supplement|caption",
    re.I,
)


def strip_html(text: Any) -> str:
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    text = re.sub(r"<br\s*/?>|</p>|</li>", "\n", str(text), flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return "\n".join(" ".join(line.split()) for line in text.splitlines() if line.strip())


def _size(n: Any) -> str:
    if n is None or pd.isna(n):
        return "?"
    n = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit] + f"\n... [truncated, {len(text) - limit} more chars]"


class BatchTables:
    """Automated pipeline outputs for one batch (output/<batch>/*.parquet)."""

    def __init__(self, output_directory: str | Path):
        self.directory = Path(output_directory)
        self.files = self._read("dataset_file_index")
        self.spectral = self._read("spectroscopy_metadata")
        self.errors = self._read("extraction_errors")

    def _read(self, name: str) -> pd.DataFrame:
        path = self.directory / f"{name}.parquet"
        if not path.exists():
            return pd.DataFrame()
        frame = pd.read_parquet(path)
        frame["record_id"] = frame["record_id"].astype(str)
        return frame

    def rows(self, frame: pd.DataFrame, record_id: str) -> pd.DataFrame:
        if frame.empty:
            return frame
        return frame[frame["record_id"] == str(record_id)]


# ---------------------------------------------------------------------- #
# Dataset inventory and previews
# ---------------------------------------------------------------------- #
def scan_files(record_id: str, dataset_path: Path, config: dict) -> list[dict]:
    from scanner.file_indexer import FileIndexer

    return FileIndexer(config).scan(record_id, dataset_path)


def inventory_section(file_rows: list[dict], max_lines: int = 60) -> str:
    if not file_rows:
        return "No files found in the dataset folder."
    files = [r for r in file_rows if not (r.get("is_archive") and "::" not in r["file_path"])]
    containers = [r for r in file_rows if r.get("is_archive")]
    total = sum((r.get("file_size_bytes") or 0) for r in file_rows if "::" not in r["file_path"])
    ext = Counter((r.get("extension") or "<none>") for r in files)
    lines = [
        f"Files on disk + archive members: {len(file_rows)} entries "
        f"({sum('::' not in r['file_path'] for r in file_rows)} on disk, total {_size(total)}); "
        f"archives: {len(containers)}",
        "Extensions: " + ", ".join(f"{e} x{n}" for e, n in ext.most_common(25)),
    ]
    bad = [r for r in file_rows if str(r.get("scan_status", "")).startswith("archive_inspection_error")
           or r.get("scan_status") == "archive_partially_recovered"]
    for row in bad[:10]:
        lines.append(f"WARNING {row['scan_status']}: {row['relative_path']}")

    if len(file_rows) <= max_lines:
        lines.append("Listing (relative path | size):")
        lines += [f"  {r['relative_path']} | {_size(r.get('file_size_bytes'))}" for r in file_rows]
        return "\n".join(lines)

    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in file_rows:
        rel = row["relative_path"]
        parent = rel.rsplit("/", 1)[0] if "/" in rel else "."
        groups[(parent, row.get("extension") or "")].append(row)
    lines.append(f"Listing grouped by folder and extension ({len(groups)} groups):")
    for (parent, extension), rows in sorted(groups.items())[:max_lines]:
        size = sum((r.get("file_size_bytes") or 0) for r in rows)
        sample = ", ".join(r["file_name"] for r in rows[:3])
        lines.append(f"  {parent}/*{extension} x{len(rows)} ({_size(size)}), e.g. {sample}")
    if len(groups) > max_lines:
        lines.append(f"  ... {len(groups) - max_lines} more groups")
    return "\n".join(lines)


def _read_bytes(row: dict, limit: int | None) -> bytes:
    path = row["file_path"]
    if "::" in path:
        return archive_access.read_member_bytes(path, limit)
    with open(path, "rb") as stream:
        return stream.read() if limit is None else stream.read(limit)


def _decode(data: bytes) -> str:
    for encoding in ("utf-8", "utf-16") if data[:2] in (b"\xff\xfe", b"\xfe\xff") else ("utf-8",):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1", errors="replace")


def _clipped(line: str, width: int, complete: bool) -> str:
    """Cut a long line for display but keep its field count, so a wide
    row-per-spectrum file still shows how many channels each row holds."""
    if len(line) <= width:
        return line
    fields = len([f for f in re.split(r"[,;\t ]+", line.strip()) if f])
    return line[:width] + (f" ... [{fields} fields]" if complete else " ... [line continues]")


def preview_text(row: dict, head_lines: int = 14, width: int = 240) -> str:
    data = _read_bytes(row, 256 * 1024)
    if b"\x00" in data[:4096] and not data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return "(binary content)"
    text = _decode(data)
    lines = text.splitlines()
    whole = len(data) < 256 * 1024  # otherwise the last line read may be cut
    shown = [
        _clipped(line, width, complete=whole or i < len(lines) - 1)
        for i, line in enumerate(lines[:head_lines])
    ]
    size = row.get("file_size_bytes") or 0
    if size and size <= 256 * 1024:
        total = f"{len(lines)} lines"
    elif "::" not in row["file_path"] and size <= 64 * 1024 * 1024:
        with open(row["file_path"], "rb") as stream:
            total = f"{sum(1 for _ in stream)} lines"
    else:
        avg = max(1, len(data) // max(1, len(lines)))
        total = f"~{size // avg} lines (estimated)"
    tail = ""
    if len(lines) > head_lines and size <= 256 * 1024:
        tail = "\n  ...\n  " + "\n  ".join(_clipped(line, width, True) for line in lines[-2:])
    return f"[{total}]\n  " + "\n  ".join(shown) + tail


def preview_sheet(row: dict, max_rows: int = 6, max_cols: int = 14) -> str:
    size = row.get("file_size_bytes") or 0
    if size > 60 * 1024 * 1024:
        return "(workbook too large to preview)"
    data = io.BytesIO(_read_bytes(row, None))
    sheets = pd.read_excel(data, sheet_name=None, header=None)
    out = [f"{len(sheets)} sheets: " + ", ".join(
        f"'{name}' ({frame.shape[0]}x{frame.shape[1]})" for name, frame in list(sheets.items())[:60]
    )]
    for name, frame in list(sheets.items())[:12]:
        frame = frame.dropna(how="all").dropna(axis=1, how="all")
        out.append(f"sheet '{name}': {frame.shape[0]} non-empty rows x {frame.shape[1]} cols")
        for values in frame.iloc[:max_rows, :max_cols].values.tolist():
            cells = ["" if pd.isna(v) else str(v)[:30] for v in values]
            more = f" ... (+{frame.shape[1] - max_cols} cols)" if frame.shape[1] > max_cols else ""
            out.append("  " + " | ".join(cells) + more)
        out.extend(_numeric_summary(frame))
    if len(sheets) > 12:
        out.append(f"... {len(sheets) - 12} more sheets: " + ", ".join(list(sheets)[12:40]))
    return "\n".join(out)


def _numeric_summary(frame: pd.DataFrame) -> list[str]:
    """Axis hints for wide or long spectral tables: numeric range of each of
    the first columns and of the most numeric row (wavelength header rows)."""
    lines = []
    numeric = frame.apply(pd.to_numeric, errors="coerce")
    for position in range(min(3, numeric.shape[1])):
        column = numeric.iloc[:, position].dropna()
        if len(column) >= 10:
            lines.append(
                f"  col{position + 1} numeric: n={len(column)} min={column.min():.6g} max={column.max():.6g} "
                f"first={column.iloc[0]:.6g} last={column.iloc[-1]:.6g}"
            )
    counts = numeric.notna().sum(axis=1)
    if len(counts) and counts.max() >= 10:
        best = counts.idxmax()
        values = numeric.loc[best].dropna()
        lines.append(
            f"  most numeric row (index {best}): n={len(values)} min={values.min():.6g} max={values.max():.6g}; "
            f"rows with >=10 numbers: {(counts >= 10).sum()}; numeric cells total: {int(counts.sum())}"
        )
    return lines


def preview_array(row: dict) -> str:
    if "::" in row["file_path"]:
        return "(array file inside archive - structure not previewed)"
    path = row["file_path"]
    out = []
    try:
        import h5py

        if h5py.is_hdf5(path):
            with h5py.File(path, "r") as handle:
                def visit(name, obj):
                    if len(out) < 40 and isinstance(obj, h5py.Dataset):
                        out.append(f"  {name}: shape={obj.shape} dtype={obj.dtype}")
                handle.visititems(visit)
            return "HDF5 datasets:\n" + "\n".join(out)
    except Exception as exc:  # pragma: no cover - diagnostic only
        out.append(f"(h5py: {type(exc).__name__})")
    if row.get("extension") == ".mat":
        from scipy.io import whosmat

        variables = whosmat(path)
        return "MAT variables:\n" + "\n".join(f"  {n}: shape={s} class={c}" for n, s, c in variables[:40])
    if row.get("extension") in {".nc", ".nc4"}:
        import netCDF4

        with netCDF4.Dataset(path) as handle:
            return "NetCDF variables:\n" + "\n".join(
                f"  {n}: dims={v.dimensions} shape={v.shape}" for n, v in list(handle.variables.items())[:40]
            )
    return "\n".join(out) or "(not previewed)"


def preview_strings(row: dict, limit: int = 2 * 1024 * 1024, max_strings: int = 120) -> str:
    """Printable strings of a binary instrument / Origin file: worksheet and
    column names, units and instrument settings often survive as text."""
    data = _read_bytes(row, limit)
    found, seen = [], set()
    for match in re.finditer(rb"[\x20-\x7e]{5,}", data):
        text = match.group().decode("ascii").strip()
        if len(text) < 5 or text in seen or not re.search(r"[A-Za-z]{3}", text):
            continue
        seen.add(text)
        found.append(text[:120])
        if len(found) >= max_strings:
            break
    return "printable strings: " + " | ".join(found) if found else "(binary, no readable strings)"


def preview_pdf(row: dict, max_chars: int = 2500) -> str:
    """Text of a PDF inside the dataset. Supplementary 'data' PDFs are often
    printed tables (x / y columns), which count as spectra."""
    import fitz

    with fitz.open(stream=_read_bytes(row, 64 * 1024 * 1024), filetype="pdf") as document:
        pages = [page.get_text() for page in document]
    text = "\n".join(pages)
    numbers = re.findall(r"(?m)^\s*-?\d+(?:[.,]\d+)?(?:[eE][-+]?\d+)?\s*$", text)
    head = " | ".join(line.strip() for line in text.splitlines() if line.strip())
    return (
        f"[{len(pages)} pages, {len(numbers)} lines holding a single number]\n  "
        + _clip(head, max_chars)
    )


def _preview(row: dict) -> str:
    extension = row.get("extension") or ""
    if extension == ".pdf":
        return preview_pdf(row)
    if extension in SHEET_EXTENSIONS:
        try:
            return preview_sheet(row)
        except Exception as exc:
            # Mislabelled workbooks: .xls that is HTML/TSV text, .xlsx that is BIFF.
            fallback = preview_text(row)
            if fallback == "(binary content)":
                fallback = preview_strings(row)
            return f"(not a readable workbook: {type(exc).__name__}) {fallback}"
    if extension in ARRAY_EXTENSIONS:
        try:
            return preview_array(row)
        except Exception as exc:
            return f"(array structure not readable: {type(exc).__name__}) {preview_strings(row, max_strings=60)}"
    if extension in TEXT_EXTENSIONS:
        return preview_text(row)
    if extension == ".docx":
        import zipfile

        with zipfile.ZipFile(io.BytesIO(_read_bytes(row, None))) as document:
            xml = document.read("word/document.xml").decode("utf-8", errors="replace")
        xml = re.sub(r"</w:p>", "\n", xml)
        return _clip(strip_html(xml), 6000)
    if extension in BINARY_STRING_EXTENSIONS or re.fullmatch(r"\.\d+", extension):
        return preview_strings(row)
    return ""


def choose_previews(file_rows: list[dict], max_files: int) -> list[dict]:
    """Docs first, then one file per (folder, extension) group, largest
    groups first, so a 2,000-file dataset is shown by a handful of examples."""
    readable = [
        r for r in file_rows
        if not r.get("is_archive")
        and (
            (r.get("extension") or "") in TEXT_EXTENSIONS | SHEET_EXTENSIONS | ARRAY_EXTENSIONS | BINARY_STRING_EXTENSIONS | {".pdf"}
            or re.fullmatch(r"\.\d+", r.get("extension") or "")
        )
        and (r.get("file_size_bytes") or 0) > 0
    ]
    docs = [r for r in readable if any(h in r["file_name"].lower() for h in DOC_HINTS)]
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in readable:
        if row in docs:
            continue
        rel = row["relative_path"]
        parent = rel.rsplit("/", 1)[0] if "/" in rel else "."
        groups[(parent, row.get("extension") or "")].append(row)
    for rows in groups.values():  # spectrum-like names first within a group
        rows.sort(key=lambda r: SPECTRAL_NAME.search(r["file_name"]) is None)
    ordered = sorted(groups.values(), key=lambda rows: -len(rows))
    picks = docs[:4] + [rows[0] for rows in ordered]
    # Small groups (a handful of workbooks per figure) are all shown.
    picks += [row for rows in ordered if len(rows) <= 4 for row in rows[1:]]
    # A second example from the biggest groups helps judge consistency.
    picks += [rows[-1] for rows in ordered[:3] if len(rows) > 1]
    seen, result = set(), []
    for row in picks:
        if row["file_path"] not in seen:
            seen.add(row["file_path"])
            result.append(row)
    return result[:max_files]


def _layout_signature(body: str) -> str:
    """Preview text with numbers blanked: files that only differ in their
    values (per-sample spectra, per-scan info files) share a signature."""
    return re.sub(r"[-+]?\d[\d.eE+-]*", "#", body[:600])


def previews_section(file_rows: list[dict], max_chars: int, max_files: int = 18) -> str:
    out, used = [], 0
    seen: dict[str, str] = {}
    for row in choose_previews(file_rows, max_files):
        try:
            body = _preview(row)
        except Exception as exc:
            body = f"(preview failed: {type(exc).__name__}: {str(exc)[:120]})"
        if not body:
            continue
        signature = _layout_signature(body)
        if signature in seen:
            out.append(f"--- {row['relative_path']}: same layout as {seen[signature]}")
            continue
        seen[signature] = row["relative_path"]
        doc = any(h in row["file_name"].lower() for h in DOC_HINTS)
        limit = 12000 if doc else 3500
        block = f"--- {row['relative_path']} ({_size(row.get('file_size_bytes'))})\n{_clip(body, limit)}"
        if used + len(block) > max_chars:
            out.append(f"... further previews omitted (budget {max_chars} chars)")
            break
        out.append(block)
        used += len(block)
    return "\n".join(out) if out else "No previewable data files."


# ---------------------------------------------------------------------- #
# Automated extraction results
# ---------------------------------------------------------------------- #
def automated_section(spectral: pd.DataFrame, errors: pd.DataFrame, dataset_path: Path, max_rows: int = 30) -> str:
    if spectral.empty:
        return "Automated extraction has not been run for this record."
    spectral = spectral[spectral["source_file"].notna()]
    lines = []
    if spectral.empty:
        lines.append("Automated readers found NO spectral records.")
    else:
        def short(path: str) -> str:
            text = str(path).replace("\\", "/")
            root = str(dataset_path).replace("\\", "/")
            return text[len(root) + 1:] if text.startswith(root) else text.rsplit("/", 1)[-1]

        frame = spectral.copy()
        frame["file"] = frame["source_file"].map(short)
        total_spectra = int(frame["num_spectra"].fillna(1).sum())
        lines.append(
            f"Automated readers produced {len(frame)} spectral records "
            f"(sum of num_spectra = {total_spectra}; sum of num_spectral_values = "
            f"{int(frame['num_spectral_values'].fillna(0).sum())})."
        )
        cols = ["modality", "spectral_range_original_min", "spectral_range_original_max",
                "spectral_range_original_unit", "num_spectral_channels", "num_spectra",
                "sampling_interval", "confidence"]

        def fmt(row) -> str:
            lo, hi = row["spectral_range_original_min"], row["spectral_range_original_max"]
            rng = "range ?" if pd.isna(lo) else f"{lo:.6g}-{hi:.6g} {row['spectral_range_original_unit'] or '(no unit)'}"
            step = "" if pd.isna(row["sampling_interval"]) else f", step {row['sampling_interval']:.4g}"
            return (f"{rng}, channels {row['num_spectral_channels']}, spectra {row['num_spectra']}{step}, "
                    f"modality {row['modality']}, conf {row['confidence']}")

        if len(frame) <= max_rows:
            for _, row in frame.iterrows():
                lines.append(f"  {row['file']}: {fmt(row)}")
        else:
            def group_key(r) -> str:
                lo, hi = r["spectral_range_original_min"], r["spectral_range_original_max"]
                rng = "?" if pd.isna(lo) else f"{lo:.3g}-{hi:.3g}"
                return f"{r['modality']}|{rng}|{r['spectral_range_original_unit']}|{r['num_spectral_channels']}"

            frame["key"] = frame.apply(group_key, axis=1)
            lines.append(
                f"Grouped by range (3 significant digits) and channels: {frame['key'].nunique()} groups "
                "(count, example file):"
            )
            for _, group in sorted(frame.groupby("key"), key=lambda kv: -len(kv[1]))[:max_rows]:
                row = group.iloc[0]
                lines.append(f"  x{len(group)} e.g. {row['file']}: {fmt(row)}")
    if not errors.empty:
        counts = Counter(errors["error_type"].astype(str))
        lines.append("Extraction errors: " + ", ".join(f"{k} x{v}" for k, v in counts.most_common(8)))
        for _, row in errors.head(5).iterrows():
            lines.append(f"  {row['error_type']}: {str(row['error_message'])[:300]}")
    return "\n".join(lines)


# ---------------------------------------------------------------------- #
# Paper
# ---------------------------------------------------------------------- #
def find_paper(record_id: str, papers_directory: Path | None) -> Path | None:
    if papers_directory is None:
        return None
    for suffix in (".pdf", ".xml", ".nxml"):
        path = Path(papers_directory) / f"{record_id}{suffix}"
        if path.is_file():
            return path
    return None


def _compact_lines(text: str) -> str:
    """PDF tables and plot axes come out one number per line; join runs of
    short lines so they cost a line instead of a hundred."""
    out: list[str] = []
    run: list[str] = []
    for line in text.splitlines():
        if len(line) <= 14:
            run.append(line.strip())
            continue
        if run:
            out.append(" ".join(run) if len(run) > 2 else "\n".join(run))
            run = []
        out.append(line)
    if run:
        out.append(" ".join(run) if len(run) > 2 else "\n".join(run))
    return "\n".join(out)


def paper_section(paper: Path | None, max_chars: int) -> str:
    if paper is None:
        return "No paper available for this record."
    from pdf.jats_reader import read_paper

    try:
        document = read_paper(paper)
    except Exception as exc:
        return f"Paper {paper.name} could not be read: {type(exc).__name__}: {exc}"
    pages = [type(p)(page_number=p.page_number, text=_compact_lines(p.text)) for p in document.pages]
    if not pages:
        return f"Paper {paper.name} has no extractable text (scanned PDF?)."
    total = sum(len(p.text) for p in pages)
    label = "section" if paper.suffix.lower() != ".pdf" else "page"
    if total <= max_chars:
        chosen = pages
    else:
        # Keep the first two units (title/abstract/intro), then the units that
        # talk about methods, data and instruments, in document order.
        ranked = sorted(pages[2:], key=lambda p: -len(PAPER_PRIORITY.findall(p.text[:4000])))
        budget = max_chars - sum(len(p.text) for p in pages[:2])
        keep = {p.page_number for p in pages[:2]}
        for page in ranked:
            if budget - len(page.text) < 0:
                continue
            keep.add(page.page_number)
            budget -= len(page.text)
        chosen = [p for p in pages if p.page_number in keep]
    body = "\n\n".join(f"[{label} {p.page_number}]\n{p.text}" for p in chosen)
    note = "" if len(chosen) == len(pages) else (
        f"(showing {len(chosen)} of {len(pages)} {label}s; {total} chars in full paper)\n"
    )
    return f"Paper file: {paper.name}\n{note}{_clip(body, max_chars)}"


_NUMBER_LINE = re.compile(r"^\s*-?\d+(?:[.,]\d+)?(?:[eE][-+]?\d+)?\s*$")


def _text_shape(row: dict) -> str | None:
    data = _read_bytes(row, 64 * 1024 * 1024)
    if b"\x00" in data[:4096] and data[:2] not in (b"\xff\xfe", b"\xfe\xff"):
        return "binary"
    lines = [line for line in _decode(data).splitlines() if line.strip()]
    widths = Counter(
        len([f for f in re.split(r"[,;\t ]+", line.strip()) if f])
        for line in lines
        if re.search(r"\d", line)
    )
    if not widths:
        return f"{len(lines)} lines, no numeric rows"
    width, rows = widths.most_common(1)[0]
    return f"{len(lines)} lines, {rows} numeric rows x {width} fields"


def _pdf_shape(row: dict) -> str:
    import fitz

    with fitz.open(stream=_read_bytes(row, 64 * 1024 * 1024), filetype="pdf") as document:
        text = "\n".join(page.get_text() for page in document)
        pages = document.page_count
    numbers = sum(1 for line in text.splitlines() if _NUMBER_LINE.match(line))
    head = " | ".join(line.strip() for line in text.splitlines() if line.strip())[:90]
    return f"{pages} pages, {numbers} single-number lines; starts '{head}'"


def shape_section(file_rows: list[dict], max_files: int = 4000, max_bytes: int = 400 * 1024 * 1024) -> str:
    """Lines x fields of every text data file (and numbers in every PDF),
    grouped, so the model can count spectra in files it was not shown."""
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    budget, checked, skipped = max_bytes, 0, 0
    for row in file_rows:
        extension = row.get("extension") or ""
        size = row.get("file_size_bytes") or 0
        if row.get("is_archive") or size <= 0 or extension not in (TEXT_EXTENSIONS - {""}) | {".pdf"}:
            continue
        if checked >= max_files or size > budget or extension in {".m", ".py", ".r", ".md", ".json"}:
            skipped += 1
            continue
        try:
            shape = _pdf_shape(row) if extension == ".pdf" else _text_shape(row)
        except Exception as exc:  # unreadable file: report, keep going
            shape = f"unreadable ({type(exc).__name__})"
        budget -= size
        checked += 1
        if extension == ".pdf":
            groups[(extension, row["relative_path"])].append(shape)  # PDFs differ: one line each
        else:
            groups[(extension, shape)].append(row["relative_path"])
    if not groups:
        return "No text or PDF data files."
    lines = []
    for (extension, key), values in sorted(groups.items(), key=lambda item: -len(item[1])):
        if extension == ".pdf":
            lines.append(f"  {key}: {values[0]}")
        else:
            examples = ", ".join(PurePosixPath(v).name for v in values[:3])
            lines.append(f"  x{len(values)} {extension}: {key} (e.g. {examples})")
    note = f"\n  ({skipped} files not checked: size/count budget or code files)" if skipped else ""
    return f"{checked} files checked\n" + "\n".join(lines[:80]) + note


# ---------------------------------------------------------------------- #
# Pack
# ---------------------------------------------------------------------- #
def metadata_section(row: dict[str, Any]) -> str:
    keys = ["record_id", "doi", "title", "publication_date", "resource_type", "creators",
            "keywords", "license", "file_count", "total_size_mb", "html_url"]
    lines = [f"{key}: {row.get(key)}" for key in keys if row.get(key) is not None and not pd.isna(row.get(key))]
    description = strip_html(row.get("description"))
    if description:
        lines.append("description:\n" + _clip(description, 6000))
    return "\n".join(lines)


def build_pack(
    *,
    record_id: str,
    metadata_row: dict[str, Any],
    dataset_path: Path,
    file_rows: list[dict],
    tables: BatchTables | None,
    papers_directory: Path | None,
    paper_max_chars: int = 120000,
    dataset_max_chars: int = 60000,
) -> str:
    spectral = tables.rows(tables.spectral, record_id) if tables else pd.DataFrame()
    errors = tables.rows(tables.errors, record_id) if tables else pd.DataFrame()
    paper = find_paper(record_id, papers_directory)
    sections = [
        f"# RECORD {record_id}",
        f"Dataset folder: {dataset_path.name}",
        "## 1. Repository metadata (Zenodo)\n" + metadata_section(metadata_row),
        "## 2. Dataset file inventory\n" + inventory_section(file_rows),
        "## 3. Automated extraction results (pipeline readers)\n"
        + automated_section(spectral, errors, dataset_path),
        "## 4. File previews (first lines / sheet heads / array shapes)\n"
        + previews_section(file_rows, dataset_max_chars),
        "## 4b. File shapes (all text / PDF data files)\n" + shape_section(file_rows),
        "## 5. Paper text\n" + paper_section(paper, paper_max_chars),
    ]
    return "\n\n".join(sections)

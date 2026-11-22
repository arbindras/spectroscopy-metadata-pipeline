"""Reader for 1-D astronomical spectra stored as FITS.

Supported layouts (no astropy required for these):

1. Primary image with a linear/log WCS on axis 1
   (CRVAL1 + CDELT1/CD1_1 [+ CRPIX1], CTYPE1/CUNIT1 give the unit).
2. Primary image of shape (k, N) with k <= 6 where row 0 holds the
   wavelength, as written by IDL/SpeX/Firehose tools. Requires a header
   comment such as "Dimension 1 is the wavelength (microns)" or a
   WAVEUNIT/XUNITS keyword so we never guess.

If astropy is installed, binary-table extensions with a wavelength column
(WAVE, WAVELENGTH, LAMBDA, LOGLAM ...) are read as well.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import numpy as np

from models import ReaderResult
from readers.base_reader import BaseReader
from readers.spectral_helpers import (
    is_monotonic,
    make_axis_spectral_record,
    modality_from_text,
    unit_from_text,
)


BLOCK = 2880
BITPIX_DTYPES = {
    8: ">u1",
    16: ">i2",
    32: ">i4",
    64: ">i8",
    -32: ">f4",
    -64: ">f8",
}
TABLE_AXIS_COLUMNS = ("wavelength", "wave", "lambda", "loglam", "wavenumber", "wl")


def _parse_value(text: str) -> Any:
    text = text.strip()
    if text.startswith("'"):
        end = text.find("'", 1)
        while end != -1 and end + 1 < len(text) and text[end + 1] == "'":
            end = text.find("'", end + 2)
        return text[1:end].replace("''", "'").strip() if end != -1 else text[1:]
    value = text.split("/", 1)[0].strip()
    if value in {"T", "F"}:
        return value == "T"
    try:
        if re.fullmatch(r"[-+]?\d+", value):
            return int(value)
        return float(value.replace("D", "E"))
    except ValueError:
        return value or None


def read_primary_header(stream) -> tuple[dict[str, Any], list[str], int]:
    """Return (keywords, comment lines, header size in bytes)."""
    header: dict[str, Any] = {}
    comments: list[str] = []
    size = 0
    while True:
        block = stream.read(BLOCK)
        if len(block) < BLOCK:
            raise ValueError("Truncated FITS header")
        size += BLOCK
        text = block.decode("ascii", errors="replace")
        for i in range(0, BLOCK, 80):
            card = text[i:i + 80]
            key = card[:8].strip()
            if key == "END":
                return header, comments, size
            if key in {"COMMENT", "HISTORY", ""}:
                body = card[8:].strip()
                if body:
                    comments.append(body)
                continue
            if card[8:10] == "= ":
                header[key] = _parse_value(card[10:])
        if size > 1000 * BLOCK:
            raise ValueError("FITS header has no END card")


class FITSReader(BaseReader):
    extensions = {".fits", ".fit", ".fts"}

    def read(
        self,
        *,
        record_id: str,
        dataset_path: Path,
        file_path: Path,
    ) -> ReaderResult:
        result = ReaderResult()
        max_mb = float(self.reader_config.get("fits_max_mb", 512))

        try:
            with file_path.open("rb") as stream:
                if stream.read(6) != b"SIMPLE":
                    return result
                stream.seek(0)
                header, comments, header_size = read_primary_header(stream)

                naxis = int(header.get("NAXIS", 0) or 0)
                shape_fits = [int(header.get(f"NAXIS{i}", 0) or 0) for i in range(1, naxis + 1)]
                n_elements = int(np.prod(shape_fits)) if shape_fits else 0
                bitpix = int(header.get("BITPIX", 0))
                dtype = BITPIX_DTYPES.get(bitpix)

                data = None
                if (
                    n_elements > 0
                    and dtype
                    and n_elements * abs(bitpix) // 8 <= max_mb * 1024 * 1024
                ):
                    stream.seek(header_size)
                    raw = np.frombuffer(
                        stream.read(n_elements * abs(bitpix) // 8), dtype=dtype
                    )
                    if raw.size == n_elements:
                        data = raw.astype(float).reshape(shape_fits[::-1])
                        data = data * float(header.get("BSCALE", 1.0)) + float(
                            header.get("BZERO", 0.0)
                        )

            comment_text = "\n".join(comments)
            modality = modality_from_text(
                " ".join(
                    str(header.get(k, ""))
                    for k in ("INSTRUME", "INSTR", "MODE", "OBJECT", "TELESCOP")
                )
                + "\n"
                + comment_text
            )

            record = self._primary_wcs(header, shape_fits, comment_text)
            if record is None and data is not None:
                record = self._wavelength_row(header, data, comments)

            if record is not None:
                axis_values, unit, num_spectra, prefix, method = record
                row, evidence = make_axis_spectral_record(
                    record_id=record_id,
                    dataset_path=dataset_path,
                    file_path=file_path,
                    axis_values=axis_values,
                    unit=unit,
                    source_type="spectral_file",
                    evidence_prefix=prefix,
                    extraction_method=method,
                    confidence=0.97,
                    modality=modality,
                    num_spectra=num_spectra,
                )
                result.spectral_records.append(row)
                result.evidence_records.extend(evidence)
                return result

            # Fall back to binary tables via astropy when available.
            result_from_tables = self._read_tables(
                record_id, dataset_path, file_path, modality
            )
            if result_from_tables is not None:
                return result_from_tables

        except Exception as exc:
            result.errors.append({
                "record_id": record_id,
                "source_file": str(file_path),
                "reader": type(self).__name__,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            })

        return result

    # ------------------------------------------------------------------ #
    @staticmethod
    def _primary_wcs(header, shape_fits, comment_text):
        if not shape_fits or shape_fits[0] < 2:
            return None
        crval = header.get("CRVAL1")
        cdelt = header.get("CDELT1", header.get("CD1_1"))
        if not isinstance(crval, (int, float)) or not isinstance(cdelt, (int, float)):
            return None
        if cdelt == 0:
            return None
        crpix = float(header.get("CRPIX1", 1.0) or 1.0)
        n = shape_fits[0]
        axis = crval + (np.arange(1, n + 1) - crpix) * cdelt

        ctype = str(header.get("CTYPE1", ""))
        cunit = str(header.get("CUNIT1", header.get("WAT1_001", "")))
        if "LOG" in ctype.upper() or int(header.get("DC-FLAG", 0) or 0) == 1:
            axis = 10.0 ** axis

        unit = unit_from_text(f"{ctype} {cunit}")
        if unit is None and ("WAVE" in ctype.upper() or "LAMBDA" in ctype.upper()):
            # FITS standard default for wavelength axes is metres, but IRAF
            # spectra almost always use Angstrom. Only accept when the
            # magnitude makes that unambiguous.
            if 900 <= np.nanmin(axis) and np.nanmax(axis) <= 300000:
                unit = "angstrom"
        if unit is None:
            return None

        num_spectra = int(np.prod(shape_fits[1:])) if len(shape_fits) > 1 else 1
        prefix = (
            f"FITS primary WCS CRVAL1={crval}, CDELT1={cdelt}, CRPIX1={crpix}, "
            f"CTYPE1={ctype!r}, CUNIT1={cunit!r}, NAXIS1={n}"
        )
        return axis, unit, num_spectra, prefix, "fits_primary_wcs"

    @staticmethod
    def _wavelength_row(header, data, comments):
        if data.ndim != 2 or data.shape[0] > 6 or data.shape[1] < 2:
            return None

        unit = None
        evidence_line = None
        for text in comments:
            lowered = text.lower()
            if re.search(r"(dimension|row|axis|column)\s*1\b.*wave", lowered) or (
                "wavelength" in lowered and unit_from_text(text)
            ):
                unit = unit_from_text(text)
                evidence_line = text
                if unit:
                    break
        for key in ("WAVEUNIT", "XUNITS", "WUNITS", "CUNIT1"):
            if unit is None and header.get(key):
                unit = unit_from_text(str(header[key]))
                evidence_line = f"{key}={header[key]}"
        if unit is None:
            return None

        axis = data[0]
        if not is_monotonic(axis):
            return None

        flux_rows = 1
        prefix = (
            f"FITS primary image shape={data.shape}, row 0 = spectral axis "
            f"({evidence_line})"
        )
        return axis, unit, flux_rows, prefix, "fits_wavelength_row"

    def _read_tables(self, record_id, dataset_path, file_path, modality):
        try:
            from astropy.io import fits  # optional dependency
        except ImportError:
            return None

        result = ReaderResult()
        with fits.open(file_path, memmap=True) as hdul:
            for index, hdu in enumerate(hdul[1:], start=1):
                columns = getattr(getattr(hdu, "columns", None), "names", None)
                if not columns:
                    continue
                lookup = {c.lower(): c for c in columns}
                axis_name = next(
                    (lookup[c] for c in TABLE_AXIS_COLUMNS if c in lookup), None
                )
                if axis_name is None:
                    continue
                values = np.asarray(hdu.data[axis_name], dtype=float).reshape(-1)
                column = hdu.columns[axis_name]
                if axis_name.lower() == "loglam":
                    values = 10.0 ** values
                    unit = "angstrom"
                else:
                    unit = unit_from_text(f"{axis_name} {column.unit or ''}")
                if unit is None or not is_monotonic(values):
                    continue
                row, evidence = make_axis_spectral_record(
                    record_id=record_id,
                    dataset_path=dataset_path,
                    file_path=file_path,
                    axis_values=values,
                    unit=unit,
                    source_type="spectral_file",
                    evidence_prefix=f"FITS HDU {index} column {axis_name!r} unit={column.unit!r}",
                    extraction_method="fits_table_axis_column",
                    confidence=0.97,
                    modality=modality,
                    num_spectra=1,
                )
                result.spectral_records.append(row)
                result.evidence_records.extend(evidence)
        return result if result.spectral_records else None

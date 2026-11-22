from __future__ import annotations

import re
from typing import Iterable

from .candidates import ExtractionCandidate


NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"
SEP = r"(?:-|–|—|to|until)"

# Keep these patterns intentionally conservative. The goal is high precision;
# semantic/LLM extraction can handle ambiguous prose later.
RANGE_RE = re.compile(
    rf"(?P<a>{NUMBER})\s*{SEP}\s*(?P<b>{NUMBER})\s*"
    rf"(?P<unit>nm|nanometers?|µm|μm|um|micrometers?|cm(?:\s*[-−]?\s*1|⁻¹|\\-1))",
    re.IGNORECASE,
)

RESOLUTION_RE = re.compile(
    rf"(?:spectral\s+)?resolution\s*(?:of|was|is|=|:)?\s*"
    rf"(?P<value>{NUMBER})\s*(?P<unit>nm|µm|μm|um|cm(?:\s*[-−]?\s*1|⁻¹|\\-1))",
    re.IGNORECASE,
)

INTERVAL_RE = re.compile(
    rf"(?:sampling|spectral|wavelength|spectral\s+sampling)\s*"
    rf"(?:interval|step|spacing)\s*(?:of|was|is|=|:)?\s*"
    rf"(?P<value>{NUMBER})\s*(?P<unit>nm|µm|μm|um|cm(?:\s*[-−]?\s*1|⁻¹|\\-1))",
    re.IGNORECASE,
)

EVERY_RE = re.compile(
    rf"(?:sampled|recorded|measured|acquired)\s+every\s+"
    rf"(?P<value>{NUMBER})\s*(?P<unit>nm|µm|μm|um|cm(?:\s*[-−]?\s*1|⁻¹|\\-1))",
    re.IGNORECASE,
)

SPECTRA_RE = re.compile(
    rf"(?P<n>{NUMBER})\s+(?:individual\s+)?spectra\b", re.IGNORECASE
)

SAMPLES_RE = re.compile(
    rf"(?:a\s+total\s+of\s+)?(?P<n>{NUMBER})\s+samples\b", re.IGNORECASE
)

CHANNEL_RE = re.compile(
    rf"(?P<n>{NUMBER})\s+(?:spectral\s+)?(?:channels|bands|wavelengths)\b",
    re.IGNORECASE,
)

MODALITY_PATTERNS = [
    (re.compile(r"\bnear[-\s]?infrared\b|\bNIR\b", re.I), "NIR"),
    (re.compile(r"\bmid[-\s]?infrared\b|\bMIR\b|\bFTIR\b", re.I), "MIR/FTIR"),
    (re.compile(r"\bUV[-\s]?Vis\b|\bUV[-\s]?visible\b", re.I), "UV-Vis"),
    (re.compile(r"\bRaman\b", re.I), "Raman"),
    (re.compile(r"\bhyperspectral\b", re.I), "hyperspectral"),
]


def normalize_unit(unit: str) -> str:
    u = unit.lower().replace(" ", "")
    if u in {"nm", "nanometer", "nanometers"}:
        return "nm"
    if u in {"µm", "μm", "um", "micrometer", "micrometers"}:
        return "um"
    return "cm-1"


def to_nm(value: float, unit: str) -> float | None:
    unit = normalize_unit(unit)
    if unit == "nm":
        return value
    if unit == "um":
        return value * 1000.0
    return None


def to_cm1(value: float, unit: str) -> float | None:
    unit = normalize_unit(unit)
    if unit == "cm-1":
        return value
    if unit == "nm":
        return 1e7 / value if value else None
    if unit == "um":
        return 1e4 / value if value else None
    return None


def _is_xray_raman(text: str, start: int) -> bool:
    """"X-ray Raman scattering" (XRS) is an X-ray energy-loss technique, not
    optical Raman; PDF text may break the line between the two words."""
    return bool(re.search(r"x[\s\-‐-―]*ray[\s\-‐-―]*$", text[max(0, start - 14):start], re.I))


def _candidate(field, value, source_file, page_number, evidence, confidence=0.95):
    return ExtractionCandidate(
        field_name=field,
        value=value,
        source_type="pdf",
        source_file=source_file,
        page_number=page_number,
        evidence_text=evidence,
        extraction_method="regex",
        confidence=confidence,
    )


def extract_spectral_candidates(
    text: str,
    page_number: int | None = None,
    source_file: str = "",
) -> list[ExtractionCandidate]:
    """Extract high-precision spectral metadata candidates from one text block."""

    out: list[ExtractionCandidate] = []

    for m in RANGE_RE.finditer(text):
        a, b = float(m.group("a")), float(m.group("b"))
        unit = normalize_unit(m.group("unit"))
        evidence = m.group(0)

        # Canonical ranges use ascending physical coordinate values.
        lo, hi = min(a, b), max(a, b)

        if unit in {"nm", "um"}:
            lo_nm, hi_nm = to_nm(lo, unit), to_nm(hi, unit)
            out.append(_candidate("wavelength_min_nm", lo_nm, source_file, page_number, evidence))
            out.append(_candidate("wavelength_max_nm", hi_nm, source_file, page_number, evidence))
        else:
            lo_cm, hi_cm = min(a, b), max(a, b)
            out.append(_candidate("wavenumber_min_cm1", lo_cm, source_file, page_number, evidence))
            out.append(_candidate("wavenumber_max_cm1", hi_cm, source_file, page_number, evidence))

    for pattern in (RESOLUTION_RE, INTERVAL_RE, EVERY_RE):
        for m in pattern.finditer(text):
            value = float(m.group("value"))
            unit = normalize_unit(m.group("unit"))
            evidence = m.group(0)

            field = (
                "spectral_resolution"
                if pattern is RESOLUTION_RE
                else "sampling_interval"
            )
            out.append(_candidate(
                field, value, source_file, page_number, evidence, confidence=0.92
            ))
            unit_field = (
                "spectral_resolution_unit"
                if field == "spectral_resolution"
                else "sampling_interval_unit"
            )
            out.append(_candidate(
                unit_field, unit, source_file, page_number, evidence, confidence=0.99
            ))

    for m in SPECTRA_RE.finditer(text):
        out.append(_candidate(
            "num_spectra", int(float(m.group("n").replace(",", ""))),
            source_file, page_number, m.group(0), 0.90
        ))

    for m in SAMPLES_RE.finditer(text):
        out.append(_candidate(
            "num_samples", int(float(m.group("n").replace(",", ""))),
            source_file, page_number, m.group(0), 0.90
        ))

    for m in CHANNEL_RE.finditer(text):
        out.append(_candidate(
            "num_spectral_channels", int(float(m.group("n").replace(",", ""))),
            source_file, page_number, m.group(0), 0.90
        ))

    # Modality is a candidate rather than a final assertion.
    for pattern, modality in MODALITY_PATTERNS:
        m = next(
            (match for match in pattern.finditer(text)
             if not (modality == "Raman" and _is_xray_raman(text, match.start()))),
            None,
        )
        if m:
            out.append(_candidate(
                "modality", modality, source_file, page_number,
                m.group(0), 0.80
            ))

    return out

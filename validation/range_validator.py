from __future__ import annotations

from typing import Any


def validate_record(record: dict[str, Any]) -> list[str]:
    """Lightweight deterministic validation.

    Returns human-readable errors/warnings. It never silently changes values.
    """

    problems: list[str] = []

    wmin = record.get("wavelength_min_nm")
    wmax = record.get("wavelength_max_nm")
    if wmin is not None and wmax is not None and wmin > wmax:
        problems.append("wavelength_min_nm > wavelength_max_nm")

    kmin = record.get("wavenumber_min_cm1")
    kmax = record.get("wavenumber_max_cm1")
    if kmin is not None and kmax is not None and kmin > kmax:
        problems.append("wavenumber_min_cm1 > wavenumber_max_cm1")

    channels = record.get("num_spectral_channels")
    if channels is not None and channels <= 0:
        problems.append("num_spectral_channels must be positive")

    spectra = record.get("num_spectra")
    if spectra is not None and spectra <= 0:
        problems.append("num_spectra must be positive")

    samples = record.get("num_samples")
    if samples is not None and samples <= 0:
        problems.append("num_samples must be positive")

    return problems

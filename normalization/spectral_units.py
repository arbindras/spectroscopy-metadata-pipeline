from __future__ import annotations

import math
import re
from typing import Any


def normalize_spectral_unit(unit: Any) -> str | None:
    if unit is None:
        return None

    value = str(unit).strip().lower()
    value = value.replace("−", "-").replace("⁻", "-")
    value = re.sub(r"\s+", "", value)

    aliases = {
        "nm": "nm",
        "nanometer": "nm",
        "nanometers": "nm",
        "nanometre": "nm",
        "nanometres": "nm",
        "um": "um",
        "µm": "um",
        "μm": "um",
        "micrometer": "um",
        "micrometers": "um",
        "cm-1": "cm^-1",
        "cm^-1": "cm^-1",
        "1/cm": "cm^-1",
        "cm^{-1}": "cm^-1",
        "wavenumber": "cm^-1",
    }
    return aliases.get(value)


def finite_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def normalize_spectral_bounds(
    start: Any,
    end: Any,
    unit: Any,
) -> dict[str, float | None]:
    start_value = finite_float(start)
    end_value = finite_float(end)
    normalized_unit = normalize_spectral_unit(unit)

    result = {
        "wavelength_min_nm": None,
        "wavelength_max_nm": None,
        "wavenumber_min_cm1": None,
        "wavenumber_max_cm1": None,
    }

    if start_value is None or end_value is None:
        return result

    if normalized_unit == "nm":
        low_nm, high_nm = sorted((start_value, end_value))
        result["wavelength_min_nm"] = low_nm
        result["wavelength_max_nm"] = high_nm

        if low_nm > 0:
            converted = sorted((1e7 / low_nm, 1e7 / high_nm))
            result["wavenumber_min_cm1"] = converted[0]
            result["wavenumber_max_cm1"] = converted[1]

    elif normalized_unit == "um":
        low_nm, high_nm = sorted((start_value * 1000, end_value * 1000))
        result["wavelength_min_nm"] = low_nm
        result["wavelength_max_nm"] = high_nm

        if low_nm > 0:
            converted = sorted((1e7 / low_nm, 1e7 / high_nm))
            result["wavenumber_min_cm1"] = converted[0]
            result["wavenumber_max_cm1"] = converted[1]

    elif normalized_unit == "cm^-1":
        low_cm1, high_cm1 = sorted((start_value, end_value))
        result["wavenumber_min_cm1"] = low_cm1
        result["wavenumber_max_cm1"] = high_cm1

        if low_cm1 > 0:
            converted = sorted((1e7 / low_cm1, 1e7 / high_cm1))
            result["wavelength_min_nm"] = converted[0]
            result["wavelength_max_nm"] = converted[1]

    return result

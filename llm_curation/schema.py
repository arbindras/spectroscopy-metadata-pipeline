from __future__ import annotations

from typing import Any

from curation.build import DETAIL_COLUMNS


# Spectral fields the model fills (SPECTRAL_SCHEMA minus record_id).
# wavelength_*/wavenumber_* are derived by curation/build.py from the original
# range when the unit is nm/um/Angstrom/cm-1/eV/meV; the model only sets them
# for other units.
SPECTRAL_FIELDS: dict[str, str] = {
    "modality": "string",
    "spectral_range_original_min": "number",
    "spectral_range_original_max": "number",
    "spectral_range_original_unit": "string",
    "wavelength_min_nm": "number",
    "wavelength_max_nm": "number",
    "wavenumber_min_cm1": "number",
    "wavenumber_max_cm1": "number",
    "num_spectral_channels": "integer",
    "spectral_resolution": "number",
    "spectral_resolution_unit": "string",
    "sampling_interval": "number",
    "sampling_interval_unit": "string",
    "num_samples": "integer",
    "num_spectra": "integer",
    "num_images": "integer",
    "num_pixels": "integer",
    "num_spectral_values": "integer",
    "image_height": "integer",
    "image_width": "integer",
    "spatial_resolution": "number",
    "spatial_resolution_unit": "string",
    "spectral_target_relationship": "string",
    "source_file": "string",
    "confidence": "number",
}

DETAIL_KEYS: list[str] = [key for _, key in DETAIL_COLUMNS[1:]]


def _nullable(kind: str) -> dict[str, Any]:
    return {"anyOf": [{"type": kind}, {"type": "null"}]}


def output_schema() -> dict[str, Any]:
    """JSON schema accepted by both Claude structured outputs and OpenAI
    strict json_schema (every property required, nulls via anyOf)."""
    spectral = {
        "type": "object",
        "properties": {name: _nullable(kind) for name, kind in SPECTRAL_FIELDS.items()},
        "required": list(SPECTRAL_FIELDS),
        "additionalProperties": False,
    }
    details = {
        "type": "object",
        "properties": {key: {"type": "string"} for key in DETAIL_KEYS},
        "required": DETAIL_KEYS,
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "record_id": {"type": "string"},
            "has_spectra": {"type": "boolean"},
            "no_spectra_reason": _nullable("string"),
            "spectral": spectral,
            "details": details,
            "curator_notes": {"type": "string"},
        },
        "required": ["record_id", "has_spectra", "no_spectra_reason", "spectral", "details", "curator_notes"],
        "additionalProperties": False,
    }


def clean_result(result: dict[str, Any]) -> dict[str, Any]:
    """Normalise a model answer: drop null spectral keys (build.py derives or
    fills them), coerce integer fields, keep detail strings."""
    spectral = {}
    for name, kind in SPECTRAL_FIELDS.items():
        value = (result.get("spectral") or {}).get(name)
        if value is None or value == "":
            continue
        if kind == "integer":
            try:
                value = int(round(float(value)))
            except (TypeError, ValueError):
                continue
        elif kind == "number":
            try:
                value = float(value)
            except (TypeError, ValueError):
                continue
        spectral[name] = value
    details = {key: str((result.get("details") or {}).get(key) or "None") for key in DETAIL_KEYS}
    return {
        "record_id": str(result.get("record_id")),
        "has_spectra": bool(result.get("has_spectra")),
        "no_spectra_reason": result.get("no_spectra_reason"),
        "spectral": spectral,
        "details": details,
        "curator_notes": result.get("curator_notes") or "",
    }

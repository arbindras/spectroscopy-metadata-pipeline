from __future__ import annotations

import importlib
import json
from typing import Any

from curation.build import DETAIL_COLUMNS


SYSTEM_PROMPT = """\
You are curating a spectroscopy dataset catalogue. For one repository record
you receive an evidence pack: the Zenodo metadata, the dataset file inventory,
the results of automated file readers, previews of data files, and the text of
the associated paper. You return one JSON object describing the record.

Work like a careful data curator who has opened the files and read the paper:

* Decide first whether the dataset itself contains spectra (measured or
  computed spectral curves / spectral tables / spectral images that a user
  could load). Spectra shown only as figures in a PDF, derived products
  (maps, indices, single concentrations, classification results), article
  PDFs only, empty or failed downloads, non-spectral data (microscopy
  images, XRD-only, chromatography-only, mechanical tests, genomic data) do
  not count. XRD, NMR, mass spectra, XPS, EDX, DLS are not optical
  spectroscopy; when a dataset holds optical/vibrational/electronic spectra
  (UV-Vis, NIR, MIR/FTIR, Raman, fluorescence, photoluminescence,
  reflectance, absorbance, ellipsometry, THz, LIBS, hyperspectral, XAS/EELS
  in eV) alongside them, describe the optical spectra and mention the rest.
  When has_spectra is false, give a short no_spectra_reason in the style
  "article PDF only (topic, journal)" or "<what the files are> - no
  spectra", fill the spectral object with nulls (source_file may still list
  the files) and still fill the details object as far as possible.
* Prefer what the data files show (axis ranges, number of points, number of
  spectra) over what the paper says; use the paper for instrument, method,
  preprocessing, sample and target information. When paper and files
  disagree, report the file values and note the paper value in parentheses.
* The paper may be unrelated to the dataset (wrong PDF attached). Say so in
  source_file / Remarks and lower confidence.
* Count carefully. num_spectra = number of individual spectra in the
  dataset (columns of a wide table, files of a per-spectrum folder, pixels of
  a spectral image only when stored as spectra). num_samples = number of
  distinct physical samples/specimens/conditions. num_spectral_channels =
  points per spectrum (if spectra differ, leave null and explain in
  sampling_interval_unit or npts). num_spectral_values = total numeric
  intensity values (spectra x channels, summed over parts). Use the
  automated reader totals when they are consistent; do not invent precise
  counts you cannot support - an approximate count is marked "approx." in
  a details field.
* Counts describe what is deposited, not what the paper reports: never take
  num_spectra from the paper, and never compute channels or values from a
  nominal instrument range. Take channels from the axis rows/columns shown
  ("[N fields]" gives the length of a clipped row; "[N lines]" the length of
  a file) and spectra from rows/columns/files. Section 4b lists the shape of
  every text/PDF data file; use it to add up spectra and values across
  files you were not shown. Repeated scans stored in a
  file are spectra. A file that sits among same-kind spectrum files but is
  unreadable (e.g. a binary saved with a text extension) still counts as a
  spectrum; say so in Remarks.
* Numeric x/y tables printed into PDF files (supplementary "electronic data"
  PDFs) are deposited spectra: has_spectra is true and their columns count.
  Only PDFs showing plotted figures or article text do not count.
* Never fabricate instrument makes, resolutions or references. Use
  "Not reported" when a value is unknown and "Not applicable" when the field
  does not apply.

SPECTRAL OBJECT (one row per record, the dominant spectroscopic data):
- modality: descriptive string: technique (instrument model, geometry /
  accessory, excitation) of what samples, e.g. "ATR-FTIR spectroscopy (Bruker
  Alpha II, diamond ATR) of PLGA nanoparticles loaded with ...". Several
  techniques: list the main one first joined with " + ".
- spectral_range_original_min / _max / _unit: overall axis range of the
  spectra in the unit used in the files. Unit must be one of "nm", "um",
  "cm-1", "eV", "meV", "Angstrom", or another literal unit string (e.g.
  "ppm", "GHz", "THz", "keV") when the axis is not convertible. For Raman use
  the Raman shift in cm-1. min < max.
- wavelength_min_nm, wavelength_max_nm, wavenumber_min_cm1,
  wavenumber_max_cm1: leave null (computed automatically) unless the unit is
  not nm/um/cm-1/eV/meV/Angstrom.
- num_spectral_channels, spectral_resolution (+ _unit, e.g. "cm-1", "nm",
  "nm (spectral bandwidth)"), sampling_interval (+ _unit, the data point
  spacing; the unit string may carry a short explanation of other parts,
  e.g. "cm-1 (FTIR; UV-Vis 200-800 nm at 1 nm)").
- num_samples, num_spectra, num_spectral_values (integers).
- num_images, num_pixels, image_height, image_width, spatial_resolution
  (+ _unit): only for imaging / hyperspectral data, else null.
- spectral_target_relationship: one dense sentence on what spectral features
  are related to which target property, and how (calibration, PCA/PLS,
  band assignment, kinetics ...): "<bands/features> vs <target> -> <purpose
  / finding>".
- source_file: "<record_id>.<pdf|xml> (Authors Year Journal Volume:pages,
  doi:...); <short description of the data files with counts>".
- confidence: 0-1, your confidence in the record as a whole (0.85-0.9 clean
  and consistent; 0.7-0.8 some counts approximate or paper partly
  mismatched; <=0.6 major uncertainty).

DETAILS OBJECT (22 descriptive columns; every value is a string, never
empty; use "Not reported" / "Not applicable"):
""" + "\n".join(f"- {key}: {column}" for column, key in DETAIL_COLUMNS[1:]) + """

Detail field conventions:
- fmt: file formats and layout ("3 xlsx (one sheet each): ...; 20 csv
  (wavenumber, absorbance) ...").
- npts: "<spectra> spectra x <points> points (<range>) = <values> values"
  plus any other parts.
- missing: missing values, gaps, NaNs, files that could not be read, data the
  paper mentions but the deposit lacks; "No" when complete.
- prep: "Yes (...)" / "No (...)" / "Partly (...)"; prep_methods: numbered
  steps "1) ...; 2) ...".
- target: the target property / analyte / question.
- mode: measurement mode (transmission, ATR, diffuse reflectance, Raman
  backscattering, fluorescence emission ...), with sample presentation.
- wl: wavelength range in nm, e.g. "2,500-25,000 (4,000-400 cm-1)" or
  "200-800"; "Not applicable" for non-optical axes.
- res: spectral resolution with unit, or "Not reported".
- make: instrument manufacturer and model (+ detector/accessory).
- path: pathlength / cuvette / cell information, or "Not applicable".
- ts: "Yes (...)" when spectra are a time series (kinetics, monitoring),
  else "No".
- chemo: "Yes - <model, e.g. PLS-R, PCA-LDA, CNN; performance>" or "No".
- refs: full reference of the paper (Authors (Year) Title, Journal
  volume:pages, doi) and other key references mentioned for the data.
- remarks: anything a user must know (paper mismatch, sites, sample origin).
- cond: measurement conditions (temperature, atmosphere, laser power,
  scans ...).
- absorb: absorptivity / molar absorption coefficients if reported, else
  "Not reported" / "Not applicable".
- refm: reference (non-spectroscopic) measurements that give the target
  values (HPLC, titration, ICP, wet chemistry ...).
- gold: gold-standard instrument / method for the reference values, or
  "Not applicable".
- peaks: assigned band positions with assignments ("1650 cm-1 amide I; ...").
- struct: chemical identity / SMILES / formula / structure information of the
  analytes or materials.

curator_notes: brief notes on uncertainties and what you checked.

Write plain ASCII-friendly text (cm-1, um, deg, x), no markdown. Be specific
and dense like the examples.
"""


DEFAULT_EXAMPLES = [
    ("batch7", "18783909"),
    ("batch7", "20061737"),
    ("batch7", "18943633"),
]


def _example(batch: str, record_id: str) -> dict[str, Any] | None:
    try:
        spectral = importlib.import_module(f"curation.{batch}_spectral")
        details = importlib.import_module(f"curation.{batch}_details").R2
    except ImportError:
        return None
    if record_id not in spectral.R or record_id not in details:
        return None
    from llm_curation.schema import SPECTRAL_FIELDS

    row = spectral.R[record_id]
    return {
        "record_id": record_id,
        "has_spectra": True,
        "no_spectra_reason": None,
        "spectral": {name: row.get(name) for name in SPECTRAL_FIELDS},
        "details": dict(details[record_id]),
        "curator_notes": "(example)",
    }


def examples_block(examples: list[tuple[str, str]] | None = None) -> str:
    """Curated records from earlier batches, shown as the expected output style."""
    blocks = []
    for batch, record_id in examples or DEFAULT_EXAMPLES:
        example = _example(batch, record_id)
        if example:
            blocks.append(json.dumps(example, ensure_ascii=False, indent=1))
    no_spectra = []
    for batch in ("batch7", "batch6"):
        try:
            module = importlib.import_module(f"curation.{batch}_spectral")
        except ImportError:
            continue
        no_spectra += list(getattr(module, "NO_SPECTRA", {}).values())[:6]
    text = "EXAMPLES OF CURATED RECORDS (style and density to match):\n" + "\n\n".join(blocks)
    if no_spectra:
        text += "\n\nEXAMPLES OF no_spectra_reason:\n" + "\n".join(f"- {r}" for r in no_spectra[:10])
    return text


def user_message(pack: str) -> str:
    return (
        pack
        + "\n\n## TASK\nReturn the JSON object for this record (record_id exactly as above)."
    )

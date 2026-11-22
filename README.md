# Spectroscopy dataset metadata pipeline

This pipeline turns a folder of downloaded datasets plus their papers into two
curated tables per batch:

* `output/<batch>_spectroscopy_metadata.parquet`: one row per record with spectra (26 columns: modality, range, channels, spectra/value counts and so on)
* `output/<batch>_dataset_details.parquet`: one row per record (22 columns: format, instrument, preprocessing, references and so on)
* `output/<batch>_no_spectra.csv`: records that hold no spectra, with the reason

## Input layout

```
<Datasets>/<record_id>_<title>/...   one folder (or archive) per Zenodo record
<papers>/<record_id>.pdf | .xml      the paper (PDF or PMC JATS XML)
```

The Zenodo metadata CSV (default `D:/zenodo_metadata.csv`, change it with
`--metadata`) adds the title, DOI, description and creators. Records that are
missing from it get a title taken from the folder name.

## Running a new batch

Put the API key in the environment or in a `.env` file in this folder:

```
ANTHROPIC_API_KEY=...
# or
OPENAI_API_KEY=...
```

Then run:

```bash
python run_batch.py --batch batch9 --datasets E:/Batch9/Datasets --papers E:/Batch9/papers --provider anthropic
```

```bash
python run_batch.py --batch batch9 --datasets E:/Batch9/Datasets --papers E:/Batch9/papers --provider openai --model gpt-5.1
```

The first run writes `config/config_batch9.yaml`. Later runs can use
`--config config/config_batch9.yaml`.

The run has four steps; `--steps` picks a subset:

| step | what it does | output |
|---|---|---|
| `extract` | automated readers (CSV/TXT/XLS(X)/JCAMP/HDF5/MAT/NetCDF/OPUS-dpt/... including archive members) | `output/<batch>/{dataset_file_index,spectroscopy_metadata,evidence,extraction_errors,extraction_state}.parquet` |
| `packs` | evidence pack per record: metadata, file inventory, file previews, automated results, paper methods | `output/<batch>/llm_packs/<id>.md` |
| `curate` | Claude or OpenAI reads each pack and returns schema-checked JSON | `output/<batch>/llm_curation/<id>.json` |
| `build` | curated parquet tables + no-spectra list | `output/<batch>_*.parquet` |

Useful options:

* `--record-id 4984607` (repeatable) runs only those records.
* `--force` redoes records that already have results. Without it, curation can be resumed after an interruption.
* `--source llm|module` forces the build to read LLM JSON or hand-curated `curation/<batch>_*.py` modules. The default `auto` uses a module when one exists.

LLM settings live in the `llm:` block of the config: provider, model (default
`claude-opus-5-5` / `gpt-5.1`), effort, token limits, pack sizes and
concurrency. Failed records are listed in `llm_curation/_failures.json`. Re-run
with the same command to retry them.

## Reproducing batches 3-8

Batches 3-8 were curated by hand into `curation/<batch>_spectral.py` (dict `R`,
`NO_SPECTRA`) and `curation/<batch>_details.py`. Rebuild them with:

```bash
python run_batch.py --config config/config_batch8.yaml --batch batch8 --steps build
```

```bash
python build_curated_parquet.py --batch batch8 --output-dir output
```

## Curation conventions (also given to the LLM)

* `num_spectra` counts individual spectra. `num_spectral_values` is spectra × channels. Approximate counts are marked "approx." in a code comment or remark.
* nm and cm-1 ranges are derived from the original range for the units nm, um, Angstrom, cm-1, eV and meV.
* Records with only non-optical data (XRD, NMR, MS, EIS, images, summary tables) go to `NO_SPECTRA`.
* Data that exists only in Origin `.opj/.opju` projects is recorded with modality and context but null ranges and low confidence. These files cannot be parsed here.

## Known reader limitations

* Origin `.opj/.opju`, PerkinElmer `.sp`, Bruker OPUS binaries and other vendor binaries are previewed as strings only. The LLM gets their names and context, not their values.
* Wide tables whose header line starts with `#` can be transposed by the automated text reader (seen in Batch8 record 1134664). The curated numbers come from the files, not from the automated row.
* The XLSX reader misses spectra laid out as several x/y column blocks per sheet. Evidence packs include sheet previews and numeric summaries so the LLM can count them.

## Tests

```bash
python -m pytest tests -q
```

`tests/test_llm_curation.py` runs the whole chain (extract → packs → curate →
build) on a small synthetic dataset with a fake provider, so it needs no API key.

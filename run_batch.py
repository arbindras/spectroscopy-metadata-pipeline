"""End-to-end batch run: automated extraction -> LLM curation -> curated parquet.

New batch from two folders (a config file is written for you):

    python run_batch.py --batch batch9 --datasets E:/Batch9/Datasets --papers E:/Batch9/papers --provider anthropic
    python run_batch.py --batch batch9 --datasets E:/Batch9/Datasets --papers E:/Batch9/papers --provider openai --model gpt-5.5

Existing config:

    python run_batch.py --config config/config_batch8.yaml --batch batch8

Steps (``--steps``, default all): extract, packs, curate, build.

* extract - pipeline.py readers over every dataset folder ->
  ``<output>/<batch>/{dataset_file_index,spectroscopy_metadata,evidence,extraction_errors,extraction_state}.parquet``
* packs   - evidence pack per record -> ``<output>/<batch>/llm_packs/<id>.md`` (no API calls)
* curate  - Claude / OpenAI reads each pack -> ``<output>/<batch>/llm_curation/<id>.json``
* build   - ``<output>/<batch>_spectroscopy_metadata.parquet``, ``<batch>_dataset_details.parquet``,
  ``<batch>_no_spectra.csv`` (+ CSV previews). Uses the hand-curated
  ``curation/<batch>_*.py`` modules when they exist (``--source auto``),
  otherwise the LLM JSON.

Dataset folders are expected as ``<record_id>_<title>`` (Zenodo download
layout) and papers as ``<record_id>.pdf`` or ``<record_id>.xml`` (JATS).
Records missing from the Zenodo metadata file get a minimal metadata row from
the folder name. The API key comes from ANTHROPIC_API_KEY / OPENAI_API_KEY in
the environment or a ``.env`` file in this folder.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

import pandas as pd
import yaml
from tqdm import tqdm

PROJECT = Path(__file__).resolve().parent
DEFAULT_METADATA = "D:/zenodo_metadata.csv"
STEPS = ("extract", "packs", "curate", "build")


def folder_record_id(name: str) -> str:
    match = re.match(r"^(\d+)(?:_|\.|$)", name)
    return match.group(1) if match else name


def make_config(args) -> dict:
    template = yaml.safe_load((PROJECT / "config" / "config_batch8.yaml").read_text(encoding="utf-8"))
    output_root = Path(args.output_root or PROJECT / "output")
    template["paths"] = {
        "dataset_roots": [str(Path(args.datasets).resolve().as_posix())],
        "metadata_file": args.metadata or DEFAULT_METADATA,
        "papers_directory": str(Path(args.papers).resolve().as_posix()) if args.papers else None,
        "output_directory": str((output_root / args.batch).as_posix()),
    }
    return template


def prepare_inputs(config: dict, batch: str) -> dict:
    """Make sure every local dataset folder has a metadata row and a mapping."""
    output = Path(config["paths"]["output_directory"])
    output.mkdir(parents=True, exist_ok=True)

    entries = []
    for root in config["paths"]["dataset_roots"]:
        for entry in sorted(Path(root).iterdir()):
            if entry.is_dir() or entry.suffix.lower() in {".zip", ".7z", ".rar", ".tar", ".gz", ".tgz"}:
                entries.append((folder_record_id(entry.name), entry))
    if not entries:
        raise SystemExit(f"No dataset folders under {config['paths']['dataset_roots']}")

    source = Path(config["paths"].get("metadata_file") or "")
    known = pd.DataFrame()
    if source.is_file():
        known = pd.read_csv(source, dtype=str) if source.suffix.lower() != ".parquet" else pd.read_parquet(source)
        known["record_id"] = known["record_id"].astype(str)
    ids = [rid for rid, _ in entries]
    rows = known[known["record_id"].isin(ids)] if not known.empty else pd.DataFrame(columns=["record_id"])
    missing = [(rid, path) for rid, path in entries if rid not in set(rows["record_id"])]
    if missing:
        extra = pd.DataFrame([
            {"record_id": rid, "title": re.sub(r"^\d+_", "", path.name).replace("_", " ")}
            for rid, path in missing
        ])
        rows = pd.concat([rows, extra], ignore_index=True)
        print(f"{len(missing)} records not in {source.name or 'metadata'}: titles taken from folder names")

    metadata_path = output / "metadata.csv"
    rows.to_csv(metadata_path, index=False)
    mapping_path = output / "mapping.csv"
    pd.DataFrame(
        [{"record_id": rid, "folder_name": path.name, "dataset_local_path": str(path)} for rid, path in entries]
    ).to_csv(mapping_path, index=False)

    config["paths"]["metadata_file"] = str(metadata_path.as_posix())
    config.setdefault("mapping", {})["mapping_file"] = str(mapping_path.as_posix())
    config.setdefault("pipeline", {})["only_mapped_records"] = True
    print(f"{len(entries)} dataset folders; metadata -> {metadata_path}; mapping -> {mapping_path}")
    return config


def step_extract(config: dict, force: bool) -> None:
    from pipeline import Pipeline

    pipeline = Pipeline(config)
    for record_id in tqdm(pipeline.selected_record_ids(), desc="Datasets"):
        pipeline.process_record(record_id, force=force)
    pipeline.consolidate()
    pipeline.stats()


def step_build(config: dict, batch: str, source: str, output_root: Path) -> None:
    from curation.build import load_batch, load_llm_batch, write_tables

    has_module = importlib.util.find_spec(f"curation.{batch}_spectral") is not None
    if source == "module" or (source == "auto" and has_module):
        spectral, details = load_batch(batch)
        module = importlib.import_module(f"curation.{batch}_spectral")
        no_spectra = getattr(module, "NO_SPECTRA", {})
        origin = f"curation/{batch}_*.py"
    else:
        directory = Path(config["paths"]["output_directory"]) / "llm_curation"
        spectral, details, no_spectra = load_llm_batch(directory)
        origin = str(directory)
    summary = write_tables(batch, spectral, details, output_root, no_spectra=no_spectra)
    print(f"built from {origin}: {summary['records']} records with spectra, {len(no_spectra)} without")
    for name, path in summary["files"].items():
        print(f"  wrote {path}")
    for problem in summary["validation_problems"]:
        print(f"  validation: {problem}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--batch", required=True, help="batch name used in output file names, e.g. batch9")
    parser.add_argument("--config", help="existing config yaml (otherwise built from --datasets/--papers)")
    parser.add_argument("--datasets", help="folder holding one sub-folder per dataset")
    parser.add_argument("--papers", help="folder holding <record_id>.pdf / .xml papers")
    parser.add_argument("--metadata", help=f"Zenodo metadata csv/parquet (default {DEFAULT_METADATA})")
    parser.add_argument("--output-root", help="output folder (default <project>/output)")
    parser.add_argument("--provider", choices=["anthropic", "openai"], help="LLM provider (default from config)")
    parser.add_argument("--model", help="model id (default claude-opus-5-5 / gpt-5.5)")
    parser.add_argument("--steps", default=",".join(STEPS), help="comma list of: " + ", ".join(STEPS))
    parser.add_argument("--record-id", action="append", help="limit to these record ids (repeatable)")
    parser.add_argument("--source", choices=["auto", "llm", "module"], default="auto", help="curation source for build")
    parser.add_argument("--force", action="store_true", help="redo records that already have results")
    args = parser.parse_args()

    from llm_curation.providers import load_dotenv_if_present

    load_dotenv_if_present(PROJECT, Path.cwd())

    if args.config:
        config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    elif args.datasets:
        config = make_config(args)
        path = PROJECT / "config" / f"config_{args.batch}.yaml"
        if not path.exists():
            path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
            print(f"wrote {path}")
    else:
        parser.error("give --config or --datasets (and --papers)")
    if args.output_root:
        config["paths"]["output_directory"] = str((Path(args.output_root) / args.batch).as_posix())
    output_root = Path(config["paths"]["output_directory"]).parent

    steps = [s.strip() for s in args.steps.split(",") if s.strip()]
    unknown = set(steps) - set(STEPS)
    if unknown:
        parser.error(f"unknown steps {sorted(unknown)}")

    config = prepare_inputs(config, args.batch)

    if "extract" in steps:
        step_extract(config, args.force)
    if "packs" in steps and "curate" not in steps:
        from llm_curation.runner import write_packs

        written = write_packs(config, args.record_id)
        print(f"wrote {len(written)} evidence packs to {written[0].parent if written else '-'}")
    if "curate" in steps:
        from llm_curation.runner import curate_batch

        summary = curate_batch(config, provider=args.provider, model=args.model,
                               record_ids=args.record_id, force=args.force)
        print(json.dumps({k: v for k, v in summary.items() if k != "failed"}))
        for record_id, error in summary["failed"].items():
            print(f"  FAILED {record_id}: {error}")
    if "build" in steps:
        step_build(config, args.batch, args.source, output_root)
    return 0


if __name__ == "__main__":
    sys.exit(main())

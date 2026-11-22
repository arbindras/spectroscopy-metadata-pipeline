"""Build the curated per-batch parquet tables.

    python build_curated_parquet.py --batch batch1 --output-dir D:/output

writes ``batch1_spectroscopy_metadata.parquet`` (SPECTRAL_SCHEMA, one row per
record) and ``batch1_dataset_details.parquet`` (22 descriptive columns) plus
CSV previews. Records live in ``curation/<batch>_spectral.py`` and
``curation/<batch>_details.py``.
"""

from __future__ import annotations

import argparse
import sys

from curation.build import write_batch


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--batch", required=True, help="e.g. batch0, batch1")
    parser.add_argument("--output-dir", default="D:/output")
    parser.add_argument("--no-csv", action="store_true", help="skip CSV previews")
    args = parser.parse_args()

    summary = write_batch(args.batch, args.output_dir, csv_preview=not args.no_csv)
    for name, path in summary["files"].items():
        if name.endswith("_no_spectra"):
            print(f"wrote {path} (records without spectra)")
        else:
            print(f"wrote {path} ({summary['records']} rows)")
    for problem in summary["validation_problems"]:
        print(f"validation: {problem}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

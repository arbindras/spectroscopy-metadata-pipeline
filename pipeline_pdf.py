from __future__ import annotations

import argparse
import json
from pathlib import Path

from extraction.extractor import PDFSpectralExtractor
from metadata.metadata_merger import detect_conflicts, resolve_candidates
from validation.range_validator import validate_record


def candidates_to_record(record_id: str, resolved):
    record = {"record_id": str(record_id)}
    for field, candidate in resolved.items():
        record[field] = candidate.value
    return record


def main():
    parser = argparse.ArgumentParser(description="Extract spectral metadata from a PDF.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--record-id", required=True)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    extractor = PDFSpectralExtractor()
    candidates = extractor.extract(args.pdf)

    resolved = resolve_candidates(candidates)
    record = candidates_to_record(args.record_id, resolved)

    result = {
        "record": record,
        "conflicts": detect_conflicts(candidates),
        "validation_problems": validate_record(record),
        "evidence": [c.as_dict() for c in candidates],
    }

    output = json.dumps(result, indent=2, ensure_ascii=False)

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()

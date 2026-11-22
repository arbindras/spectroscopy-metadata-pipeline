from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tqdm import tqdm

from llm_curation.evidence_pack import BatchTables, build_pack, scan_files
from llm_curation.prompts import SYSTEM_PROMPT, examples_block, user_message
from llm_curation.providers import CurationError, complete_with_retry, make_provider
from llm_curation.schema import clean_result, output_schema


def curation_directory(config: dict) -> Path:
    return Path(config["paths"]["output_directory"]) / "llm_curation"


def pack_directory(config: dict) -> Path:
    return Path(config["paths"]["output_directory"]) / "llm_packs"


def _file_rows(tables: BatchTables, record_id: str, dataset_path: Path, config: dict) -> list[dict]:
    rows = tables.rows(tables.files, record_id)
    if not rows.empty:
        return rows.to_dict("records")
    return scan_files(record_id, dataset_path, config)


def write_packs(config: dict, record_ids: list[str] | None = None) -> list[Path]:
    """Build the evidence pack of every mapped record (no API calls)."""
    from pipeline import load_metadata
    from scanner.dataset_scanner import DatasetMapper

    llm = config.get("llm", {})
    metadata = load_metadata(config)
    mapper = DatasetMapper(config)
    tables = BatchTables(config["paths"]["output_directory"])
    papers = config["paths"].get("papers_directory")
    papers = Path(papers) if papers else None
    out = pack_directory(config)
    out.mkdir(parents=True, exist_ok=True)

    if record_ids is None:
        local = mapper.local_record_ids()
        record_ids = [rid for rid in metadata["record_id"].astype(str) if rid in local]

    written = []
    for record_id in tqdm(record_ids, desc="Evidence packs"):
        rows = metadata[metadata["record_id"] == record_id]
        if rows.empty:
            continue
        meta = rows.iloc[0].to_dict()
        mapping = mapper.map_dataset(meta)
        if mapping["dataset_local_path"] is None:
            continue
        dataset_path = Path(mapping["dataset_local_path"])
        pack = build_pack(
            record_id=record_id,
            metadata_row=meta,
            dataset_path=dataset_path,
            file_rows=_file_rows(tables, record_id, dataset_path, config),
            tables=tables,
            papers_directory=papers,
            paper_max_chars=int(llm.get("paper_max_chars", 120000)),
            dataset_max_chars=int(llm.get("dataset_max_chars", 60000)),
        )
        path = out / f"{record_id}.md"
        path.write_text(pack, encoding="utf-8")
        written.append(path)
    return written


def curate_batch(
    config: dict,
    *,
    provider: str | None = None,
    model: str | None = None,
    record_ids: list[str] | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Pack -> LLM -> ``output/<batch>/llm_curation/<record_id>.json``.

    Existing JSON files are kept unless ``force`` (resumable runs).
    """
    llm = config.get("llm", {})
    provider_name = provider or llm.get("provider", "anthropic")
    client = make_provider(
        provider_name,
        model or llm.get("model"),
        effort=llm.get("effort", "high"),
        max_output_tokens=int(llm.get("max_output_tokens", 32000)),
    )
    packs = write_packs(config, record_ids)
    out = curation_directory(config)
    out.mkdir(parents=True, exist_ok=True)

    system = SYSTEM_PROMPT + "\n\n" + examples_block()
    schema = output_schema()
    todo = [p for p in packs if force or not (out / f"{p.stem}.json").exists()]
    summary = {"curated": 0, "skipped": len(packs) - len(todo), "failed": {}}

    def work(pack_path: Path) -> tuple[str, str | None]:
        record_id = pack_path.stem
        started = time.monotonic()
        try:
            completion = complete_with_retry(
                client, system, user_message(pack_path.read_text(encoding="utf-8")), schema
            )
        except (CurationError, Exception) as exc:  # keep going on one bad record
            return record_id, f"{type(exc).__name__}: {exc}"
        result = clean_result(completion.data)
        result["record_id"] = record_id
        result["_provenance"] = {
            "provider": client.name,
            "model": completion.model,
            "input_tokens": completion.input_tokens,
            "output_tokens": completion.output_tokens,
            "seconds": round(time.monotonic() - started, 1),
            "curated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "pack": str(pack_path),
        }
        target = out / f"{record_id}.json"
        temporary = target.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        temporary.replace(target)
        return record_id, None

    workers = max(1, int(llm.get("concurrency", 4)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(work, path) for path in todo]
        for future in tqdm(as_completed(futures), total=len(futures), desc=f"LLM curation ({client.name})"):
            record_id, error = future.result()
            if error:
                summary["failed"][record_id] = error
            else:
                summary["curated"] += 1

    (out / "_failures.json").write_text(json.dumps(summary["failed"], indent=1), encoding="utf-8")
    return summary

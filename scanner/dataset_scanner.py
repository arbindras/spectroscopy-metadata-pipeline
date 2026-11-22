from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd


ARCHIVE_SUFFIXES = (".zip", ".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tar.xz", ".7z", ".rar")


def is_archive_name(name: str) -> bool:
    return name.lower().endswith(ARCHIVE_SUFFIXES)


def normalize_identifier(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


class DatasetMapper:
    def __init__(self, config: dict):
        self.config = config
        self.roots = [
            Path(path).expanduser().resolve()
            for path in config["paths"]["dataset_roots"]
        ]
        self.mapping_config = config.get("mapping", {})
        self.explicit_mapping = self._load_explicit_mapping()
        self.directory_candidates = self._discover_candidates()
        self.prefix_index = self._index_record_id_prefixes()

    def _index_record_id_prefixes(self) -> dict[str, list[Path]]:
        """``<record_id>_<title>`` folders or archive files directly under a root.

        Batch downloads name each dataset after its Zenodo record, either as
        a folder or as a single archive, e.g. ``5218787_Surface_char....zip``.
        """
        index: dict[str, list[Path]] = {}
        if not self.mapping_config.get("allow_record_id_prefix_match", True):
            return index
        for root in self.roots:
            if not root.is_dir():
                continue
            for entry in root.iterdir():
                match = re.match(r"^(\d+)(?:_|\.|$)", entry.name)
                if not match:
                    continue
                if entry.is_dir() or (entry.is_file() and is_archive_name(entry.name)):
                    index.setdefault(match.group(1), []).append(entry.resolve())
        return index

    def local_record_ids(self) -> set[str]:
        """Record ids that resolve to an existing local dataset."""
        ids = {rid for rid, path in self.explicit_mapping.items() if path.exists()}
        ids |= set(self.prefix_index)
        for root in self.roots:
            if root.is_dir():
                ids |= {p.name for p in root.iterdir() if p.is_dir() and p.name.isdigit()}
        return ids

    def _load_explicit_mapping(self) -> dict[str, Path]:
        mapping_file = self.mapping_config.get("mapping_file")
        if not mapping_file:
            return {}

        path = Path(mapping_file).expanduser().resolve()
        if path.suffix.lower() == ".parquet":
            frame = pd.read_parquet(path)
        else:
            frame = pd.read_csv(path, dtype={"record_id": "string"})

        required = {"record_id", "dataset_local_path"}
        if not required.issubset(frame.columns):
            raise ValueError(f"Mapping file must contain {sorted(required)}")

        result: dict[str, Path] = {}
        for row in frame.itertuples(index=False):
            dataset_path = Path(row.dataset_local_path).expanduser()

            # Folder-name mappings are commonly generated from a directory
            # listing, e.g. ``19060_Spectra_from_BANYAN_VII``.  Such values
            # are relative to a configured dataset root, not to the process
            # working directory that happens to run pipeline.py.
            if not dataset_path.is_absolute():
                root_matches = [
                    root / dataset_path
                    for root in self.roots
                    if (root / dataset_path).is_dir()
                ]
                if len(root_matches) == 1:
                    dataset_path = root_matches[0]
                elif len(root_matches) == 0 and len(self.roots) == 1:
                    # Preserve a useful, root-relative missing-path message.
                    dataset_path = self.roots[0] / dataset_path

            result[str(row.record_id)] = dataset_path.resolve()
        return result

    def _discover_candidates(self) -> list[Path]:
        max_depth = int(self.mapping_config.get("search_depth", 2))
        candidates: list[Path] = []

        for root in self.roots:
            if not root.exists():
                continue

            candidates.append(root)
            for path in root.rglob("*"):
                if not path.is_dir():
                    continue

                depth = len(path.relative_to(root).parts)
                if depth <= max_depth:
                    candidates.append(path)

        return sorted(set(candidates))

    def map_dataset(self, metadata_row: dict[str, Any]) -> dict[str, Any]:
        record_id = str(metadata_row["record_id"])

        explicit = self.explicit_mapping.get(record_id)
        if explicit is not None:
            if explicit.is_dir() or (explicit.is_file() and is_archive_name(explicit.name)):
                return {
                    "record_id": record_id,
                    "dataset_local_path": str(explicit),
                    "mapping_status": "resolved_explicit",
                    "mapping_evidence": "Explicit configurable mapping",
                }
            return {
                "record_id": record_id,
                "dataset_local_path": None,
                "mapping_status": "unresolved",
                "mapping_evidence": f"Explicit path does not exist: {explicit}",
            }

        direct_matches = []
        for root in self.roots:
            candidate = root / record_id
            if candidate.is_dir():
                direct_matches.append(candidate.resolve())

        direct_matches = sorted(set(direct_matches))
        if len(direct_matches) == 1:
            return {
                "record_id": record_id,
                "dataset_local_path": str(direct_matches[0]),
                "mapping_status": "resolved_record_id",
                "mapping_evidence": "Exact root/record_id directory match",
            }
        if len(direct_matches) > 1:
            return {
                "record_id": record_id,
                "dataset_local_path": None,
                "mapping_status": "unresolved",
                "mapping_evidence": "Multiple exact record_id directory matches",
            }

        prefixed = sorted(set(self.prefix_index.get(record_id, [])))
        if len(prefixed) == 1:
            kind = "directory" if prefixed[0].is_dir() else "archive file"
            return {
                "record_id": record_id,
                "dataset_local_path": str(prefixed[0]),
                "mapping_status": "resolved_record_id_prefix",
                "mapping_evidence": f"Root entry named '<record_id>_...' ({kind})",
            }
        if len(prefixed) > 1:
            return {
                "record_id": record_id,
                "dataset_local_path": None,
                "mapping_status": "unresolved",
                "mapping_evidence": (
                    "Multiple '<record_id>_...' root entries: "
                    + ", ".join(p.name for p in prefixed[:5])
                ),
            }

        keys: list[tuple[str, str]] = []

        if self.mapping_config.get("allow_exact_doi_directory_match", True):
            doi_key = normalize_identifier(metadata_row.get("doi"))
            if doi_key:
                keys.append(("doi", doi_key))

        if self.mapping_config.get("allow_exact_title_directory_match", True):
            title_key = normalize_identifier(metadata_row.get("title"))
            if title_key:
                keys.append(("title", title_key))

        for field_name, key in keys:
            matches = [
                path for path in self.directory_candidates
                if normalize_identifier(path.name) == key
            ]
            matches = sorted(set(matches))

            if len(matches) == 1:
                return {
                    "record_id": record_id,
                    "dataset_local_path": str(matches[0]),
                    "mapping_status": f"resolved_exact_{field_name}",
                    "mapping_evidence": f"Exact normalized {field_name} match",
                }

            if len(matches) > 1:
                return {
                    "record_id": record_id,
                    "dataset_local_path": None,
                    "mapping_status": "unresolved",
                    "mapping_evidence": f"Ambiguous exact {field_name} match",
                }

        return {
            "record_id": record_id,
            "dataset_local_path": None,
            "mapping_status": "unresolved",
            "mapping_evidence": "No confident local mapping found",
        }

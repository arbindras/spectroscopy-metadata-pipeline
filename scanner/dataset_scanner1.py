from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd


def normalize_identifier(value: Any) -> str:
    """
    Normalize an identifier for comparison.

    Example:
        '10.5281/zenodo.1234567'
        becomes
        '105281zenodo1234567'
    """

    if value is None or pd.isna(value):
        return ""

    return re.sub(
        r"[^a-z0-9]+",
        "",
        str(value).lower()
    )


class DatasetMapper:
    """
    Maps Zenodo record IDs to locally downloaded dataset folders.

    Mapping priority:

    1. Explicit mapping file
    2. Exact folder named record_id
    3. Optional DOI match
    4. Optional title match
    """

    def __init__(self, config: dict):

        self.config = config

        paths_config = config.get("paths", {})

        dataset_roots = paths_config.get(
            "dataset_roots",
            []
        )

        self.roots = [
            Path(path).expanduser().resolve()
            for path in dataset_roots
        ]

        self.mapping_config = config.get(
            "mapping",
            {}
        )

        self.explicit_mapping = (
            self._load_explicit_mapping()
        )

        self.directory_candidates = (
            self._discover_candidates()
        )

    # ========================================================
    # EXPLICIT MAPPING
    # ========================================================

    def _load_explicit_mapping(
        self
    ) -> dict[str, Path]:

        mapping_file = self.mapping_config.get(
            "mapping_file"
        )

        if not mapping_file:
            return {}

        mapping_path = (
            Path(mapping_file)
            .expanduser()
            .resolve()
        )

        if not mapping_path.exists():

            raise FileNotFoundError(
                f"Mapping file not found:\n"
                f"{mapping_path}"
            )

        if mapping_path.suffix.lower() == ".parquet":

            frame = pd.read_parquet(
                mapping_path
            )

        else:

            frame = pd.read_csv(
                mapping_path,
                dtype={
                    "record_id": "string"
                }
            )

        required_columns = {
            "record_id",
            "dataset_local_path"
        }

        missing_columns = (
            required_columns
            - set(frame.columns)
        )

        if missing_columns:

            raise ValueError(
                "Mapping file is missing required columns:\n"
                f"{sorted(missing_columns)}"
            )

        result: dict[str, Path] = {}

        for _, row in frame.iterrows():

            record_id = str(
                row["record_id"]
            ).strip()

            dataset_path = Path(
                row["dataset_local_path"]
            ).expanduser()

            result[record_id] = (
                dataset_path.resolve()
            )

        return result

    # ========================================================
    # DIRECTORY DISCOVERY
    # ========================================================

    def _discover_candidates(
        self
    ) -> list[Path]:

        max_depth = int(
            self.mapping_config.get(
                "search_depth",
                1
            )
        )

        candidates: list[Path] = []

        for root in self.roots:

            if not root.exists():

                continue

            candidates.append(
                root.resolve()
            )

            for path in root.rglob("*"):

                if not path.is_dir():

                    continue

                try:

                    depth = len(
                        path
                        .relative_to(root)
                        .parts
                    )

                except ValueError:

                    continue

                if depth <= max_depth:

                    candidates.append(
                        path.resolve()
                    )

        return sorted(
            set(candidates)
        )

    # ========================================================
    # MAIN MAPPING FUNCTION
    # ========================================================

    def map_dataset(
        self,
        metadata_row: dict[str, Any]
    ) -> dict[str, Any]:

        record_id = str(
            metadata_row.get(
                "record_id",
                ""
            )
        ).strip()

        # ----------------------------------------------------
        # 1. EXPLICIT MAPPING
        # ----------------------------------------------------

        explicit_path = (
            self.explicit_mapping.get(
                record_id
            )
        )

        if explicit_path is not None:

            if explicit_path.is_dir():

                return {

                    "record_id":
                        record_id,

                    "dataset_local_path":
                        str(explicit_path),

                    "mapping_status":
                        "resolved_explicit",

                    "mapping_evidence":
                        "Found in explicit mapping file"
                }

            else:

                return {

                    "record_id":
                        record_id,

                    "dataset_local_path":
                        None,

                    "mapping_status":
                        "unresolved",

                    "mapping_evidence":
                        f"Mapped path does not exist: "
                        f"{explicit_path}"
                }

        # ----------------------------------------------------
        # 2. EXACT ROOT / RECORD ID MATCH
        # ----------------------------------------------------

        direct_matches = []

        for root in self.roots:

            candidate = (
                root / record_id
            )

            if candidate.is_dir():

                direct_matches.append(
                    candidate.resolve()
                )

        direct_matches = sorted(
            set(direct_matches)
        )

        if len(direct_matches) == 1:

            return {

                "record_id":
                    record_id,

                "dataset_local_path":
                    str(direct_matches[0]),

                "mapping_status":
                    "resolved_record_id",

                "mapping_evidence":
                    "Exact directory match"
            }

        if len(direct_matches) > 1:

            return {

                "record_id":
                    record_id,

                "dataset_local_path":
                    None,

                "mapping_status":
                    "unresolved",

                "mapping_evidence":
                    "Multiple directories matched record_id"
            }

        # ----------------------------------------------------
        # 3. DOI MATCH
        # ----------------------------------------------------

        if self.mapping_config.get(
            "allow_exact_doi_directory_match",
            False
        ):

            doi_key = normalize_identifier(
                metadata_row.get("doi")
            )

            if doi_key:

                matches = [

                    path

                    for path
                    in self.directory_candidates

                    if normalize_identifier(
                        path.name
                    ) == doi_key

                ]

                matches = sorted(
                    set(matches)
                )

                if len(matches) == 1:

                    return {

                        "record_id":
                            record_id,

                        "dataset_local_path":
                            str(matches[0]),

                        "mapping_status":
                            "resolved_exact_doi",

                        "mapping_evidence":
                            "Exact DOI directory match"
                    }

        # ----------------------------------------------------
        # 4. TITLE MATCH
        # ----------------------------------------------------

        if self.mapping_config.get(
            "allow_exact_title_directory_match",
            False
        ):

            title_key = normalize_identifier(
                metadata_row.get("title")
            )

            if title_key:

                matches = [

                    path

                    for path
                    in self.directory_candidates

                    if normalize_identifier(
                        path.name
                    ) == title_key

                ]

                matches = sorted(
                    set(matches)
                )

                if len(matches) == 1:

                    return {

                        "record_id":
                            record_id,

                        "dataset_local_path":
                            str(matches[0]),

                        "mapping_status":
                            "resolved_exact_title",

                        "mapping_evidence":
                            "Exact title directory match"
                    }

        # ----------------------------------------------------
        # UNRESOLVED
        # ----------------------------------------------------

        return {

            "record_id":
                record_id,

            "dataset_local_path":
                None,

            "mapping_status":
                "unresolved",

            "mapping_evidence":
                "No confident local dataset mapping found"
        }
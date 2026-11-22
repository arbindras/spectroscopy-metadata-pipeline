from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from models import ReaderResult


class BaseReader(ABC):
    extensions: set[str] = set()

    def __init__(self, config: dict):
        self.config = config
        self.reader_config = config.get("readers", {})

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in self.extensions

    @abstractmethod
    def read(
        self,
        *,
        record_id: str,
        dataset_path: Path,
        file_path: Path,
    ) -> ReaderResult:
        raise NotImplementedError

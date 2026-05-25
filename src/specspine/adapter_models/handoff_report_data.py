from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .handoff_entry_model import AdapterFeatureHandoffEntry

__all__ = [
    "AdapterFeatureHandoffReportData",
]


@dataclass(frozen=True)
class AdapterFeatureHandoffReportData:
    root: Path
    feature_id: str
    status: str
    ready: bool
    sources: dict[str, dict[str, object]]
    source_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    gaps: tuple[dict[str, str], ...]
    blocking_checks: tuple[Any, ...]
    feature_summary: dict[str, object]
    adapters: dict[str, AdapterFeatureHandoffEntry]
    recommended_commands: tuple[str, ...]

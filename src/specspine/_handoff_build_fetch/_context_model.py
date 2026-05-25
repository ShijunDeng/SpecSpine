from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..feature_bundle import FeatureTraceReport

__all__ = ["HandoffBuildContext"]


@dataclass(frozen=True)
class HandoffBuildContext:
    slug: str
    resolved_root: Path
    has_native_files: bool
    trace_report: FeatureTraceReport
    task_summary: dict[str, int]
    ready_report: object
    release_readiness: str
    metadata: dict[str, str]

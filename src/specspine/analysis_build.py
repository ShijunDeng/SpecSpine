from __future__ import annotations

from pathlib import Path

from .analysis_build_feature_selection import (
    resolve_feature_filter,
    discover_and_select_features,
)
from .analysis_build_report_assembly import assemble_analysis_report
from .analysis_models import (
    AnalysisIssue,
    FeatureAnalysis,
    AnalysisReport,
    _PendingIssue,
)
from .analysis_build_commands import _dedupe_commands
from .analysis_build_core import (
    _build_missing_feature_analysis,
    _build_feature_analysis,
    _assign_issue_ids,
    _summary,
)

__all__ = [
    "_dedupe_commands",
    "_build_missing_feature_analysis",
    "_build_feature_analysis",
    "_assign_issue_ids",
    "_summary",
    "resolve_feature_filter",
    "discover_and_select_features",
    "assemble_analysis_report",
    "build_analysis_report",
]


def build_analysis_report(
    root: Path,
    *,
    feature_filter: str | None = None,
) -> AnalysisReport:
    resolved_root = root.expanduser().resolve()
    feature_filter = resolve_feature_filter(feature_filter)
    selected = discover_and_select_features(resolved_root, feature_filter)
    return assemble_analysis_report(resolved_root, selected, feature_filter)

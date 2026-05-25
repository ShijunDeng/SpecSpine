from __future__ import annotations

from pathlib import Path

from .analysis_models import (
    FeatureAnalysis,
    _PendingIssue,
)
from .features import FeatureBundleNotFoundError
from .analysis_build_feature_missing import _build_missing_feature_analysis
from ._analysis_assembly_coverage import (
    gather_feature_analysis_data,
)
from ._analysis_assembly_issues import (
    collect_feature_issues,
    build_feature_analysis_result,
)

__all__ = [
    "_build_feature_analysis",
]


def _build_feature_analysis(
    root: Path,
    feature: dict[str, object],
) -> tuple[FeatureAnalysis, list[_PendingIssue]]:
    slug = str(feature["slug"])
    try:
        data = gather_feature_analysis_data(root, slug)
    except FeatureBundleNotFoundError:
        return _build_missing_feature_analysis(root, slug)

    pending_issues = collect_feature_issues(data)
    return build_feature_analysis_result(feature, data, pending_issues)

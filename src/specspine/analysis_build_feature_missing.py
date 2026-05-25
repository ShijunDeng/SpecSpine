from __future__ import annotations

from pathlib import Path

from .features import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
)
from .analysis_models import (
    FeatureAnalysis,
    _PendingIssue,
)

__all__ = [
    "_build_missing_feature_analysis",
]


def _build_missing_feature_analysis(root: Path, slug: str) -> tuple[FeatureAnalysis, list[_PendingIssue]]:
    missing_files = tuple(
        relative_path.format(slug=slug)
        for relative_path in FEATURE_FILE_PATHS.values()
    )
    issue = _PendingIssue(
        feature_id=slug,
        severity="critical",
        category="artifact",
        code="feature.missing_bundle",
        message=f"No native feature files found for '{slug}'.",
        source_file=missing_files[0],
        evidence={"missing_files": list(missing_files)},
        recommended_command=f"specspine feature new {slug} .",
    )
    metrics: dict[str, int | bool] = {
        "acceptance_criteria_total": 0,
        "coverage_links_total": 0,
        "covered_acceptance_criteria": 0,
        "quality_checks_total": 0,
        "ready": False,
        "readiness_blocking_checks": 1,
        "tasks_total": 0,
        "test_plan_total": 0,
    }
    analysis = FeatureAnalysis(
        feature_id=slug,
        status="unknown",
        ready=False,
        source_files=missing_files,
        missing_files=missing_files,
        metrics=metrics,
        issues=(),
        recommended_commands=(f"specspine feature new {slug} .",),
    )
    return analysis, [issue]

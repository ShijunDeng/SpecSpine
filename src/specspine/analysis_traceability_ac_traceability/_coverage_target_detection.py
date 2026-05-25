from __future__ import annotations

from ..features import (
    FeatureTestCoverageLink,
)
from ..analysis_models import _PendingIssue
from ..analysis_traceability_commands import (
    _feature_tests_command,
)

__all__ = [
    "_detect_missing_targets",
]


def _detect_missing_targets(
    slug: str,
    coverage_links: tuple[FeatureTestCoverageLink, ...],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    for link in coverage_links:
        if link.target_path and not link.target_exists:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="high",
                    category="coverage",
                    code="coverage.missing_target",
                    message=f"{link.id} target does not exist: {link.target_path}",
                    source_file=link.source_file,
                    line=link.line,
                    evidence={
                        "coverage_link_id": link.id,
                        "target_path": link.target_path,
                    },
                    recommended_command=_feature_tests_command(slug),
                )
            )
    return issues

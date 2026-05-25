from __future__ import annotations

from ..features import FeatureTestCoverageLink
from ..analysis_models import _PendingIssue
from ..analysis_traceability_commands import _feature_tests_command
from ..analysis_traceability_ac_helpers import _coverage_ac_id

__all__ = [
    "_detect_unknown_criterion_links",
]


def _detect_unknown_criterion_links(
    slug: str,
    coverage_links: tuple[FeatureTestCoverageLink, ...],
    known_ids: set[str],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    for link in coverage_links:
        link_ac_id = _coverage_ac_id(link)
        if link_ac_id not in known_ids:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="medium",
                    category="coverage",
                    code="coverage.unknown_acceptance_criterion",
                    message=(
                        f"{link.id} points to unknown acceptance criterion "
                        f"{link_ac_id}."
                    ),
                    source_file=link.source_file,
                    line=link.line,
                    evidence={
                        "acceptance_criterion_id": link_ac_id,
                        "coverage_link_id": link.id,
                    },
                    recommended_command=_feature_tests_command(slug),
                )
            )
    return issues

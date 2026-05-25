from __future__ import annotations

from .features import (
    FeatureTask,
    FeatureTestCoverageLink,
    FeatureTraceChecklistItem,
)
from .analysis_models import _PendingIssue
from .analysis_traceability_commands import (
    _feature_ready_command,
    _feature_tests_command,
    _feature_trace_command,
)
from .analysis_traceability_ac_helpers import (
    _normalize_ac_id,
    _referenced_ac_ids,
    _coverage_ac_id,
)

__all__ = [
    "_ac_traceability_issues",
]


def _ac_traceability_issues(
    slug: str,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    tasks: tuple[FeatureTask, ...],
    coverage_links: tuple[FeatureTestCoverageLink, ...],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    task_refs = set().union(*(_referenced_ac_ids(task.text) for task in tasks)) if tasks else set()
    coverage_refs = {_coverage_ac_id(link) for link in coverage_links}
    covered_refs = {
        _coverage_ac_id(link)
        for link in coverage_links
        if link.done and link.target_exists
    }
    known_ids = {criterion.id for criterion in acceptance_criteria}

    for criterion in acceptance_criteria:
        if criterion.id not in task_refs:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="medium",
                    category="traceability",
                    code="acceptance.no_task_reference",
                    message=(
                        f"{criterion.id} has no execution task reference by AC id."
                    ),
                    source_file=criterion.source_file,
                    line=criterion.line,
                    evidence={"acceptance_criterion_id": criterion.id},
                    recommended_command=_feature_trace_command(slug),
                )
            )
        if criterion.id not in coverage_refs:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="medium",
                    category="coverage",
                    code="acceptance.no_coverage_link",
                    message=f"{criterion.id} has no Test Coverage link.",
                    source_file=criterion.source_file,
                    line=criterion.line,
                    evidence={"acceptance_criterion_id": criterion.id},
                    recommended_command=_feature_tests_command(slug),
                )
            )
        elif criterion.id not in covered_refs:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="medium",
                    category="coverage",
                    code="acceptance.no_completed_coverage",
                    message=(
                        f"{criterion.id} lacks a checked Test Coverage link to an "
                        "existing local target."
                    ),
                    source_file=criterion.source_file,
                    line=criterion.line,
                    evidence={"acceptance_criterion_id": criterion.id},
                    recommended_command=_feature_ready_command(slug),
                )
            )

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
        if not link.done and link_ac_id in known_ids:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="low",
                    category="coverage",
                    code="coverage.open_link",
                    message=f"{link.id} is not checked for {link_ac_id}.",
                    source_file=link.source_file,
                    line=link.line,
                    evidence={
                        "acceptance_criterion_id": link_ac_id,
                        "coverage_link_id": link.id,
                    },
                    recommended_command=_feature_ready_command(slug),
                )
            )

    return issues

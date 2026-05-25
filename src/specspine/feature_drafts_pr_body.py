from __future__ import annotations

from .feature_bundle import (
    FeatureMetadata,
    FeatureReadyCheck,
    FeatureTask,
    FeatureTraceChecklistItem,
    FeatureTraceTestPlanItem,
)
from .feature_drafts_pr_header import _render_pr_header_lines
from .feature_drafts_pr_checklist import _render_pr_checklist_sections
from .feature_drafts_pr_trailing import _render_pr_trailing_sections

__all__ = [
    "_render_pull_request_body",
]


def _render_pull_request_body(
    *,
    feature_id: str,
    status: str,
    ready: bool,
    summary: dict[str, object],
    why: str,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    tasks: tuple[FeatureTask, ...],
    test_plan: tuple[FeatureTraceTestPlanItem, ...],
    release_readiness: tuple[FeatureTraceChecklistItem, ...],
    readiness_checks: tuple[FeatureReadyCheck, ...],
    source_files: tuple[str, ...],
    missing_files: tuple[str, ...],
    gaps: tuple[dict[str, str], ...],
    recommended_commands: tuple[str, ...],
    metadata: FeatureMetadata,
) -> str:
    lines = _render_pr_header_lines(
        feature_id=feature_id,
        status=status,
        ready=ready,
        summary=summary,
        why=why,
        metadata=metadata,
    )
    lines.extend(
        _render_pr_checklist_sections(
            acceptance_criteria=acceptance_criteria,
            tasks=tasks,
            test_plan=test_plan,
            release_readiness=release_readiness,
            readiness_checks=readiness_checks,
        )
    )
    lines.extend(
        _render_pr_trailing_sections(
            gaps=gaps,
            source_files=source_files,
            missing_files=missing_files,
            recommended_commands=recommended_commands,
        )
    )
    return "\n".join(lines).strip() + "\n"

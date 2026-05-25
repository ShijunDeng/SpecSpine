from __future__ import annotations

from .features import FEATURE_FILE_PATHS
from ._proposer_intent_resolver import _resolve_proposal_inputs
from .proposer_build_spec import build_spec_content
from .proposer_build_execution import build_execution_content
from .proposer_build_quality import build_quality_content

__all__ = [
    "build_proposal_content",
]


def build_proposal_content(
    slug: str,
    intent: str,
    *,
    priority: str = "medium",
    owner: str = "unassigned",
    milestone: str = "unassigned",
    target_release: str = "unassigned",
    project: str = "unassigned",
    effort: str = "unknown",
) -> dict[str, str]:
    resolved_slug, title, intent, parsed, criteria, tasks, quality_checks = _resolve_proposal_inputs(slug, intent)

    spec_content = build_spec_content(
        resolved_slug=resolved_slug,
        title=title,
        parsed=parsed,
        criteria=criteria,
        priority=priority,
        owner=owner,
        milestone=milestone,
        target_release=target_release,
        project=project,
        effort=effort,
        intent=intent,
    )

    execution_content = build_execution_content(
        resolved_slug=resolved_slug,
        title=title,
        parsed=parsed,
        tasks=tasks,
        intent=intent,
    )

    quality_content = build_quality_content(
        resolved_slug=resolved_slug,
        title=title,
        parsed=parsed,
        criteria=criteria,
        quality_checks=quality_checks,
        intent=intent,
    )

    return {
        FEATURE_FILE_PATHS["spec"].format(slug=resolved_slug): spec_content,
        FEATURE_FILE_PATHS["execution"].format(slug=resolved_slug): execution_content,
        FEATURE_FILE_PATHS["quality"].format(slug=resolved_slug): quality_content,
    }

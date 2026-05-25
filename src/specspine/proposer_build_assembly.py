from __future__ import annotations

from .features import FEATURE_FILE_PATHS
from .workspace import normalize_template
from .proposer_intent import validate_intent, parse_intent
from .proposer_slug import _slug_to_title
from .proposer_criteria import generate_ears_criteria, generate_tasks, generate_quality_checks
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
    intent = validate_intent(intent)
    resolved_slug = slug
    title = _slug_to_title(resolved_slug)
    parsed = parse_intent(intent)
    criteria = generate_ears_criteria(parsed)
    tasks = generate_tasks(parsed, criteria)
    quality_checks = generate_quality_checks(criteria)

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

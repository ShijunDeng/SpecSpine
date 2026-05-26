from __future__ import annotations

from ..feature_bundle import FeatureMetadata
from ._render_issue_header import _render_issue_header
from ._render_issue_content import _render_issue_content
from ._render_issue_files import _render_issue_files

__all__ = [
    "_render_issue_body",
]


def _render_issue_body(
    *,
    feature_id: str,
    status: str,
    why: str,
    acceptance_criteria: str,
    tasks: str,
    test_plan: str,
    source_files: tuple[str, ...],
    missing_files: tuple[str, ...],
    metadata: FeatureMetadata,
) -> str:
    lines: list[str] = []
    lines.extend(
        _render_issue_header(
            feature_id=feature_id,
            status=status,
            metadata=metadata,
        )
    )
    lines.extend(
        _render_issue_content(
            why=why,
            acceptance_criteria=acceptance_criteria,
            tasks=tasks,
            test_plan=test_plan,
        )
    )
    lines.extend(
        _render_issue_files(
            source_files=source_files,
            missing_files=missing_files,
        )
    )
    return "\n".join(lines).strip() + "\n"

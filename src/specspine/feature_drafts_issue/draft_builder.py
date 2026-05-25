from __future__ import annotations

from pathlib import Path

from ..feature_bundle import (
    FEATURE_FILE_PATHS,
    IssueDraft,
    read_feature_metadata,
    validate_feature_slug,
)
from .body_renderer import _render_issue_body
from .draft_content_loader import (
    load_feature_contents,
    extract_draft_sections,
)
from .draft_rendering import (
    render_issue_json,
    render_issue_text,
)

__all__ = [
    "build_issue_draft",
    "render_issue_json",
    "render_issue_text",
    "load_feature_contents",
    "extract_draft_sections",
]


def build_issue_draft(root: Path, slug: str) -> IssueDraft:
    slug = validate_feature_slug(slug)
    resolved_root, contents, source_files, missing_files = load_feature_contents(root, slug)

    relative_paths = {
        kind: relative_path.format(slug=slug)
        for kind, relative_path in FEATURE_FILE_PATHS.items()
    }

    title, status, why, acceptance_criteria, tasks, test_plan = extract_draft_sections(
        contents, relative_paths, slug
    )

    metadata = read_feature_metadata(resolved_root, slug)
    body = _render_issue_body(
        feature_id=slug,
        status=status,
        why=why,
        acceptance_criteria=acceptance_criteria,
        tasks=tasks,
        test_plan=test_plan,
        source_files=tuple(source_files),
        missing_files=tuple(missing_files),
        metadata=metadata,
    )

    return IssueDraft(
        title=title,
        body=body,
        feature_id=slug,
        source_files=tuple(source_files),
        missing_files=tuple(missing_files),
        status=status,
        metadata=metadata,
    )

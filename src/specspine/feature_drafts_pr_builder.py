from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    PullRequestDraft,
    _first_line_h1,
    _relative_feature_paths,
    _why_or_placeholder,
    feature_bundle_paths,
    feature_title,
    read_feature_metadata,
    validate_feature_slug,
)
from .feature_drafts_render import (
    _pull_request_title,
    _recommended_pr_commands,
    _render_pull_request_body,
)
from .feature_handoff import build_feature_handoff_report
from .feature_ready import build_feature_ready_report

__all__ = [
    "build_pull_request_draft",
]


def build_pull_request_draft(root: Path, slug: str) -> PullRequestDraft:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)

    contents: dict[str, str] = {}
    source_files: list[str] = []
    missing_files: list[str] = []
    missing_paths: list[Path] = []

    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        relative_path = relative_paths[kind]
        if path.exists():
            contents[kind] = path.read_text(encoding="utf-8")
            source_files.append(relative_path)
            continue

        missing_files.append(relative_path)
        missing_paths.append(path)

    if not contents:
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(missing_paths),
        )

    spec_content = contents.get("spec", "")
    base_title = _first_line_h1(spec_content) or feature_title(slug)
    title = _pull_request_title(base_title)
    why = _why_or_placeholder(contents, relative_path=relative_paths["spec"])
    handoff = build_feature_handoff_report(resolved_root, slug)
    ready_report = build_feature_ready_report(resolved_root, slug)
    metadata = read_feature_metadata(resolved_root, slug)
    recommended_commands = _recommended_pr_commands(slug)
    summary = {
        **handoff.summary,
        "source_files": {"total": len(source_files)},
        "missing_files": {"total": len(missing_files)},
    }

    body = _render_pull_request_body(
        feature_id=slug,
        status=handoff.status,
        ready=handoff.ready,
        summary=summary,
        why=why,
        acceptance_criteria=handoff.acceptance_criteria,
        tasks=handoff.tasks,
        test_plan=handoff.test_plan,
        release_readiness=handoff.release_readiness,
        readiness_checks=ready_report.checks,
        source_files=tuple(source_files),
        missing_files=tuple(missing_files),
        gaps=handoff.gaps,
        recommended_commands=recommended_commands,
        metadata=metadata,
    )

    return PullRequestDraft(
        title=title,
        body=body,
        feature_id=slug,
        status=handoff.status,
        ready=handoff.ready,
        source_files=tuple(source_files),
        missing_files=tuple(missing_files),
        gaps=handoff.gaps,
        blocking_checks=handoff.blocking_checks,
        summary=summary,
        recommended_commands=recommended_commands,
        metadata=metadata,
    )

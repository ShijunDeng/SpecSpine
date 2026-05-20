from __future__ import annotations

import json
from pathlib import Path

from .feature_bundle import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    FeatureHandoffReport,
    FeatureMetadata,
    FeatureReadyCheck,
    FeatureReadyReport,
    FeatureTask,
    FeatureTraceChecklistItem,
    FeatureTraceTestPlanItem,
    IssueDraft,
    PullRequestDraft,
    _first_line_h1,
    _first_scalar,
    _relative_feature_paths,
    _render_metadata_lines,
    _section_or_placeholder,
    _why_or_placeholder,
    feature_bundle_paths,
    feature_title,
    get_feature_status,
    read_feature_metadata,
    validate_feature_slug,
)
from .feature_handoff import build_feature_handoff_report
from .feature_ready import build_feature_ready_report

__all__ = [
    "IssueDraft",
    "PullRequestDraft",
    "_render_issue_body",
    "build_issue_draft",
    "render_issue_json",
    "render_issue_text",
    "_render_pull_request_body",
    "build_pull_request_draft",
    "render_pull_request_json",
    "render_pull_request_text",
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
    lines = [
        "## Feature",
        "",
        f"- Feature ID: `{feature_id}`",
        f"- Status: {status}",
        "",
        "## Metadata",
        "",
        *_render_metadata_lines(metadata),
        "",
        "## Why",
        "",
        why,
        "",
        "## Acceptance Criteria",
        "",
        acceptance_criteria,
        "",
        "## Tasks",
        "",
        tasks,
        "",
        "## Test Plan",
        "",
        test_plan,
        "",
        "## Source Files",
        "",
    ]

    lines.extend(f"- {relative_path}" for relative_path in source_files)
    lines.extend(["", "## Missing Files", ""])
    if missing_files:
        lines.append(
            "This draft was generated from an incomplete feature bundle. "
            "Add these files before treating the issue as ready:"
        )
        lines.append("")
        lines.extend(f"- {relative_path}" for relative_path in missing_files)
    else:
        lines.append("None.")

    return "\n".join(lines).strip() + "\n"


def build_issue_draft(root: Path, slug: str) -> IssueDraft:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = {
        kind: relative_path.format(slug=slug)
        for kind, relative_path in FEATURE_FILE_PATHS.items()
    }

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
    title = _first_line_h1(spec_content) or feature_title(slug)
    status = _first_scalar(contents, "Status") or "TODO: Confirm feature status."
    metadata = read_feature_metadata(resolved_root, slug)
    why = _why_or_placeholder(contents, relative_path=relative_paths["spec"])
    acceptance_criteria = _section_or_placeholder(
        contents,
        kind="spec",
        heading="Acceptance Criteria",
        relative_path=relative_paths["spec"],
    )
    tasks = _section_or_placeholder(
        contents,
        kind="execution",
        heading="Tasks",
        relative_path=relative_paths["execution"],
    )
    test_plan = _section_or_placeholder(
        contents,
        kind="quality",
        heading="Test Plan",
        relative_path=relative_paths["quality"],
    )
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


def render_issue_json(draft: IssueDraft) -> str:
    return json.dumps(draft.as_dict(), indent=2, sort_keys=True) + "\n"


def render_issue_text(draft: IssueDraft) -> str:
    return f"Title: {draft.title}\n\n{draft.body}"


def _recommended_pr_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature pr {slug} . --json",
        f"specspine feature handoff {slug} . --json",
        f"specspine feature trace {slug} . --json",
        f"specspine feature ready {slug} . --json",
        "specspine validate . --fusion --features",
    )


def _pull_request_title(base_title: str) -> str:
    title = base_title.strip() or "Feature"
    if title.lower().startswith("implement "):
        return title
    return f"Implement {title}"


def _render_pr_checklist_items(
    items: tuple[FeatureTraceChecklistItem, ...] | tuple[FeatureTask, ...],
    *,
    empty_text: str,
) -> list[str]:
    if not items:
        return [f"- [ ] {empty_text}"]

    lines: list[str] = []
    for item in items:
        marker = "x" if item.done else " "
        lines.append(
            f"- [{marker}] {item.id} {item.source_file}:{item.line} {item.text}"
        )
    return lines


def _render_pr_test_plan_items(
    items: tuple[FeatureTraceTestPlanItem, ...],
    *,
    empty_text: str,
) -> list[str]:
    if not items:
        return [f"- {empty_text}"]

    return [
        f"- {item.id} {item.source_file}:{item.line} {item.text}"
        for item in items
    ]


def _render_pr_ready_checks(
    checks: tuple[FeatureReadyCheck, ...],
) -> list[str]:
    if not checks:
        return ["- [ ] Run `specspine feature ready` before opening the PR."]

    lines: list[str] = []
    for check in checks:
        marker = "x" if check.status == "pass" else " "
        lines.append(f"- [{marker}] {check.id}: {check.message}")
    return lines


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
    trace = summary["trace"]
    ready_summary = summary["ready"]
    task_summary = summary["tasks"]
    lines = [
        "## Summary",
        "",
        f"- Feature ID: `{feature_id}`",
        f"- Status: {status}",
        f"- Ready: {'yes' if ready else 'no'}",
        (
            "- Trace: "
            f"total={trace['total']} "
            f"done={trace['done']} "
            f"open={trace['open']}"
        ),
        (
            "- Tasks: "
            f"total={task_summary['total']} "
            f"done={task_summary['done']} "
            f"open={task_summary['open']}"
        ),
        (
            "- Readiness: "
            f"pass={ready_summary['pass']} "
            f"fail={ready_summary['fail']} "
            f"total={ready_summary['total']}"
        ),
        "",
        "## Metadata",
        "",
        *_render_metadata_lines(metadata),
        "",
        "## Feature",
        "",
        "- This is an offline Pull Request draft generated from local SpecSpine feature artifacts.",
        "- No remote PR is created by this command.",
        "",
        "## Why",
        "",
        why,
        "",
        "## Acceptance Criteria",
        "",
    ]
    lines.extend(
        _render_pr_checklist_items(
            acceptance_criteria,
            empty_text="Add acceptance criteria checklist items before review.",
        )
    )

    lines.extend(["", "## Tasks", ""])
    lines.extend(
        _render_pr_checklist_items(
            tasks,
            empty_text="Add execution task checklist items before review.",
        )
    )

    lines.extend(["", "## Test Plan", ""])
    lines.extend(
        _render_pr_test_plan_items(
            test_plan,
            empty_text="Add a concrete test plan before review.",
        )
    )

    lines.extend(["", "## Release Readiness", ""])
    lines.extend(
        _render_pr_checklist_items(
            release_readiness,
            empty_text="Add release readiness checklist items before review.",
        )
    )

    lines.extend(["", "## Readiness / Blocking Checks", ""])
    lines.extend(_render_pr_ready_checks(readiness_checks))

    lines.extend(["", "## Gaps", ""])
    if gaps:
        lines.extend(
            f"- [ ] {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in gaps
        )
    else:
        lines.append("- [x] None.")

    lines.extend(["", "## Source Files", ""])
    if source_files:
        lines.extend(f"- {relative_path}" for relative_path in source_files)
    else:
        lines.append("- None.")

    lines.extend(["", "## Missing Files", ""])
    if missing_files:
        lines.extend(f"- [ ] {relative_path}" for relative_path in missing_files)
    else:
        lines.append("- [x] None.")

    lines.extend(["", "## Key Commands", ""])
    lines.extend(f"- `{command}`" for command in recommended_commands)

    return "\n".join(lines).strip() + "\n"


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


def render_pull_request_json(draft: PullRequestDraft) -> str:
    return json.dumps(draft.as_dict(), indent=2, sort_keys=True) + "\n"


def render_pull_request_text(draft: PullRequestDraft) -> str:
    return f"Title: {draft.title}\n\n{draft.body}"

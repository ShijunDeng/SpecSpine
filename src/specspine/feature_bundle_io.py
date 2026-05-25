from __future__ import annotations

from pathlib import Path

from .workspace import normalize_template

from .feature_bundle_models import (
    FEATURE_DIRECTORIES,
    FEATURE_FILE_PATHS,
    FeatureBundleExistsError,
    FeatureBundleNotFoundError,
    FeatureMetadata,
    FeatureStatusReport,
)
from .feature_bundle_render import _extract_scalar
from .feature_bundle_validation import (
    normalize_feature_assignment,
    normalize_feature_effort,
    normalize_feature_owner,
    normalize_feature_priority,
    validate_feature_slug,
)

__all__ = [
    "_feature_why",
    "build_feature_files",
    "feature_bundle_paths",
    "create_feature_bundle",
    "get_feature_status",
    "list_feature_bundles",
    "read_feature_metadata",
    "get_feature_files",
    "_relative_feature_paths",
    "_transition_payload",
    "_trace_gap",
    "_path_as_posix",
    "_sync_body_source",
    "build_proposal_files",
    "create_proposal_bundle",
]


def _feature_why(why: str | None = None) -> str:
    if why and why.strip():
        return why.strip()
    return "TODO: Explain the problem this feature solves and why it matters now."


def build_feature_files(
    slug: str,
    *,
    title: str | None = None,
    why: str | None = None,
) -> dict[str, str]:
    from .feature_bundle_validation import feature_title

    slug = validate_feature_slug(slug)
    resolved_title = feature_title(slug, title)
    resolved_why = _feature_why(why)

    return {
        FEATURE_FILE_PATHS["spec"].format(slug=slug): f"""
            # {resolved_title}

            Feature ID: {slug}
            Status: proposed
            Priority: medium
            Owner: unassigned
            Milestone: unassigned
            Target Release: unassigned
            Project: unassigned
            Effort: unknown

            ## Why

            {resolved_why}

            ## Users

            - TODO: Identify the users or roles that benefit from this feature.

            ## Scope

            - TODO: Describe the behavior, workflows, and boundaries included in this feature.

            ## Non-Goals

            - TODO: Record what this feature intentionally will not address.

            ## Acceptance Criteria

            - [ ] TODO: Define one observable outcome that can be mapped directly to a test case.

            ## Edge Cases

            - TODO: Capture boundary, error, permission, migration, or rollback cases reviewers should check.

            ## Constraints

            - TODO: Note technical, operational, policy, compatibility, or timing constraints.

            ## Traceability Notes

            - TODO: Link acceptance criteria to tasks, tests, docs, rollout evidence, or review notes as work progresses.
        """,
        FEATURE_FILE_PATHS["execution"].format(slug=slug): f"""
            # {resolved_title} Execution

            Feature ID: {slug}
            Status: proposed
            Why: {resolved_why}

            ## Milestones

            - TODO: List the meaningful delivery checkpoints.

            ## Tasks

            - [ ] TODO: Break the work into implementation tasks.

            ## Dependencies

            - TODO: Note upstream decisions, systems, people, or artifacts needed first.

            ## Open Questions

            - TODO: Track questions that must be answered before or during implementation.

            ## Agent Handoff

            - Run `specspine feature handoff {slug} . --json` before implementation or review handoff.
            - Run `specspine adapters handoff {slug} . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
            - Run `specspine feature tasks {slug} . --json` for the focused implementation checklist.
            - Run `specspine feature task-issues {slug} . --json` to draft one local GitHub issue per execution task.
            - Run `specspine feature trace {slug} . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
            - Run `specspine feature tests {slug} . --json` to build the acceptance-test packet.
            - Run `specspine tests impact . --feature {slug} --json` to inspect local source-to-test impact recommendations.
            - Run `specspine consistency scan . --feature {slug} --json` to inspect local spec-code-test-doc drift.
            - Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
            - Run `specspine retrospective report . --json` before planning the next iteration.
            - Run `specspine coverage plan . --feature {slug} --json` when missing AC coverage needs read-only remediation steps.
            - Run `specspine verify matrix {slug} . --json` to inspect AC-level verification evidence.
            - Run `specspine change risk . --feature {slug} --json` to inspect local changed-path risk evidence.
            - Run `specspine security cues . --feature {slug} --json` to inspect local security-sensitive review cues.
            - Run `specspine provenance manifest . --feature {slug} --json` to hash local evidence artifacts before review or archive.
            - Run `specspine review packet . --feature {slug} --json` to compose local pre-merge review evidence.
            - Run `specspine feature ready {slug} . --json` after implementation evidence is complete.
            - Run `specspine feature pr {slug} . --json` to draft local Pull Request review notes.
            - Run `specspine feature sync-plan {slug} . --json` to review GitHub CLI sync intent without executing it.
            - Run `specspine feature sync-plan {slug} . --output-dir .specspine/sync-plan/{slug}` to materialize local sync review artifacts.
            - Run `specspine feature archive {slug} . --json` to package local archive evidence before lifecycle closure.
            - Run `specspine validate . --fusion --features` before handoff or release.
        """,
        FEATURE_FILE_PATHS["quality"].format(slug=slug): f"""
            # {resolved_title} Quality

            Feature ID: {slug}
            Status: proposed
            Why: {resolved_why}

            ## Required Checks

            - [ ] TODO: Acceptance criteria are reviewed against implementation evidence.
            - [ ] TODO: Test coverage proves the changed behavior and edge cases.
            - [ ] TODO: Documentation, release notes, or PR draft reflect user-facing behavior.
            - [ ] TODO: `specspine feature ready {slug} . --json` has no blocking checks after evidence is complete.
            - [ ] TODO: `specspine validate . --fusion --features` passes.

            ## Test Coverage

            Use `- [ ] AC001 -> tests/...` to link existing local test files or test selectors.

            - [ ] AC001 -> tests/...

            ## Test Plan

            - TODO: Add unit, integration, CLI, manual, or exploratory checks that prove each acceptance criterion.

            ## Review Notes

            - TODO: Capture review findings, decisions, and follow-up work.

            ## Release Readiness

            - [ ] TODO: Acceptance criteria, tasks, required checks, and test plan evidence are complete.
            - [ ] TODO: Docs, release notes, or `specspine feature pr {slug} . --json` output are ready for reviewers.
            - [ ] TODO: `specspine tests impact . --feature {slug} --json` has been reviewed for focused local test commands.
            - [ ] TODO: `specspine consistency scan . --feature {slug} --json` has been reviewed for local spec-code-test-doc drift.
            - [ ] TODO: `specspine hygiene scan . --json` has been reviewed for generated artifacts and denylisted repository residue.
            - [ ] TODO: `specspine retrospective report . --json` has been reviewed for local feature improvement signals.
            - [ ] TODO: `specspine coverage plan . --feature {slug} --json` has been reviewed if missing AC coverage remains.
            - [ ] TODO: `specspine verify matrix {slug} . --json` has been reviewed for AC-level verification evidence.
            - [ ] TODO: `specspine change risk . --feature {slug} --json` has been reviewed for changed-path risk evidence.
            - [ ] TODO: `specspine security cues . --feature {slug} --json` has been reviewed for security-sensitive cues.
            - [ ] TODO: `specspine provenance manifest . --feature {slug} --json` has been reviewed for local evidence hashes.
            - [ ] TODO: `specspine review packet . --feature {slug} --json` has been reviewed for local pre-merge evidence.
            - [ ] TODO: `specspine feature sync-plan {slug} . --json` or `--output-dir .specspine/sync-plan/{slug}` has been reviewed before any remote GitHub sync.
            - [ ] TODO: `specspine feature archive {slug} . --json` has been reviewed before marking status archived.
            - [ ] TODO: `specspine feature ready {slug} . --json` and `specspine validate . --fusion --features` have been run.
            - [ ] TODO: No known blockers remain, or blockers are documented in review notes.
        """,
    }


def feature_bundle_paths(root: Path, slug: str) -> dict[str, Path]:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    return {
        kind: resolved_root / relative_path.format(slug=slug)
        for kind, relative_path in FEATURE_FILE_PATHS.items()
    }


def create_feature_bundle(
    root: Path,
    slug: str,
    *,
    title: str | None = None,
    why: str | None = None,
    force: bool = False,
) -> list[Path]:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    files = build_feature_files(slug, title=title, why=why)
    targets = {
        relative_path: resolved_root / relative_path
        for relative_path in files
    }
    existing_paths = tuple(path for path in targets.values() if path.exists())

    if existing_paths and not force:
        raise FeatureBundleExistsError(slug=slug, existing_paths=existing_paths)

    written: list[Path] = []
    for relative_path, content in files.items():
        target = targets[relative_path]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(normalize_template(content), encoding="utf-8")
        written.append(target)

    return written


def _relative_feature_paths(slug: str) -> dict[str, str]:
    return {
        kind: relative_path.format(slug=slug)
        for kind, relative_path in FEATURE_FILE_PATHS.items()
    }


def _transition_payload(
    *,
    from_status: str | None,
    to_status: str,
    enforced: bool,
    allowed: bool,
    reason: str | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "allowed": allowed,
        "enforced": enforced,
        "from": from_status,
        "to": to_status,
    }
    if reason:
        payload["reason"] = reason
    return payload


def _trace_gap(gap_id: str, source_file: str, message: str) -> dict[str, str]:
    return {
        "id": gap_id,
        "message": message,
        "source_file": source_file,
    }


def _path_as_posix(path: Path) -> str:
    return path.as_posix()


def _sync_body_source(slug: str, filename: str) -> str:
    return str(Path(".specspine") / "sync-plan" / slug / filename)


def get_feature_status(root: Path, slug: str) -> FeatureStatusReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)

    files: dict[str, dict[str, object]] = {}
    missing_files: list[str] = []
    statuses: list[str] = []
    status_missing = False

    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        relative_path = relative_paths[kind]
        entry: dict[str, object] = {
            "exists": path.exists(),
            "path": relative_path,
            "status": None,
        }
        if path.exists():
            content = path.read_text(encoding="utf-8")
            status = _extract_scalar(content, "Status")
            entry["status"] = status
            if status:
                statuses.append(status)
            else:
                status_missing = True
        else:
            missing_files.append(relative_path)

        files[kind] = entry

    unique_statuses = sorted(set(statuses))
    current_status = unique_statuses[0] if len(unique_statuses) == 1 else None
    if len(unique_statuses) > 1:
        current_status = "mixed"

    existing_count = len(FEATURE_FILE_PATHS) - len(missing_files)
    consistent = existing_count > 0 and not status_missing and len(unique_statuses) == 1

    return FeatureStatusReport(
        feature_id=slug,
        status=current_status,
        consistent=consistent,
        files=files,
        missing_files=tuple(missing_files),
    )


def list_feature_bundles(root: Path) -> list[dict[str, object]]:
    from .feature_bundle_models import InvalidFeatureSlug

    resolved_root = root.expanduser().resolve()
    by_slug: dict[str, dict[str, str]] = {}

    for kind, directory_name in FEATURE_DIRECTORIES.items():
        directory = resolved_root / directory_name
        if not directory.exists():
            continue

        for path in sorted(directory.glob("*.md")):
            slug = path.stem
            relative_path = str(path.relative_to(resolved_root))
            by_slug.setdefault(slug, {})[kind] = relative_path

    features: list[dict[str, object]] = []
    required_kinds = set(FEATURE_FILE_PATHS)
    for slug in sorted(by_slug):
        files = by_slug[slug]
        try:
            status_report = get_feature_status(resolved_root, slug)
            status = status_report.status
            status_consistent = status_report.consistent
            missing_files = list(status_report.missing_files)
        except InvalidFeatureSlug:
            status = None
            status_consistent = False
            missing_files = [
                relative_path.format(slug=slug)
                for kind, relative_path in FEATURE_FILE_PATHS.items()
                if kind not in files
            ]
        features.append(
            {
                "slug": slug,
                "complete": set(files) == required_kinds,
                "files": dict(sorted(files.items())),
                "status": status,
                "status_consistent": status_consistent,
                "missing_files": missing_files,
            }
        )

    return features


def read_feature_metadata(root: Path, slug: str) -> FeatureMetadata:
    slug = validate_feature_slug(slug)
    spec_path = feature_bundle_paths(root, slug)["spec"]
    if not spec_path.exists():
        return FeatureMetadata(
            priority="unknown",
            owner="unassigned",
            milestone="unassigned",
            target_release="unassigned",
            project="unassigned",
            effort="unknown",
        )

    content = spec_path.read_text(encoding="utf-8")
    return FeatureMetadata(
        priority=normalize_feature_priority(_extract_scalar(content, "Priority")),
        owner=normalize_feature_owner(_extract_scalar(content, "Owner")),
        milestone=normalize_feature_assignment(_extract_scalar(content, "Milestone")),
        target_release=normalize_feature_assignment(
            _extract_scalar(content, "Target Release")
        ),
        project=normalize_feature_assignment(_extract_scalar(content, "Project")),
        effort=normalize_feature_effort(_extract_scalar(content, "Effort")),
    )


def get_feature_files(root: Path, slug: str) -> dict[str, Path]:
    return feature_bundle_paths(root, slug)


def build_proposal_files(
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
    from .proposer import build_proposal_content

    slug = validate_feature_slug(slug)
    return build_proposal_content(
        slug,
        intent,
        priority=priority,
        owner=owner,
        milestone=milestone,
        target_release=target_release,
        project=project,
        effort=effort,
    )


def create_proposal_bundle(
    root: Path,
    slug: str,
    intent: str,
    *,
    priority: str = "medium",
    owner: str = "unassigned",
    milestone: str = "unassigned",
    target_release: str = "unassigned",
    project: str = "unassigned",
    effort: str = "unknown",
    force: bool = False,
) -> list[Path]:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    files = build_proposal_files(
        slug,
        intent,
        priority=priority,
        owner=owner,
        milestone=milestone,
        target_release=target_release,
        project=project,
        effort=effort,
    )
    targets = {
        relative_path: resolved_root / relative_path
        for relative_path in files
    }
    existing_paths = tuple(path for path in targets.values() if path.exists())

    if existing_paths and not force:
        raise FeatureBundleExistsError(slug=slug, existing_paths=existing_paths)

    written: list[Path] = []
    for relative_path, content in files.items():
        target = targets[relative_path]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(normalize_template(content), encoding="utf-8")
        written.append(target)

    return written

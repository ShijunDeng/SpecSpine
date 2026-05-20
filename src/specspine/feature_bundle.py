from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .workspace import normalize_template

__all__ = [
    "FEATURE_SLUG_RE",
    "FEATURE_FILE_PATHS",
    "FEATURE_STATUSES",
    "FEATURE_PRIORITIES",
    "FEATURE_TRANSITIONS",
    "FEATURE_DIRECTORIES",
    "InvalidFeatureSlug",
    "InvalidFeatureStatus",
    "FeatureBundleExistsError",
    "FeatureBundleNotFoundError",
    "FeatureSyncPlanArtifactExistsError",
    "FeatureStatusTransitionError",
    "FeatureMetadata",
    "FeatureTask",
    "FeatureTraceChecklistItem",
    "FeatureTraceTestPlanItem",
    "FeatureAcceptanceTestCase",
    "FeatureTestCoverageLink",
    "FeatureTraceReport",
    "FeatureReadyCheck",
    "FeatureReadyReport",
    "FeatureTasksReport",
    "FeatureTaskIssueDraft",
    "FeatureTaskIssuesReport",
    "FeatureHandoffReport",
    "FeatureTestsReport",
    "FeatureSyncPlanCommand",
    "FeatureSyncPlan",
    "FeatureSyncPlanArtifacts",
    "IssueDraft",
    "PullRequestDraft",
    "FeatureStatusReport",
    "validate_feature_slug",
    "validate_feature_status",
    "normalize_feature_priority",
    "normalize_feature_owner",
    "normalize_feature_assignment",
    "normalize_feature_effort",
    "feature_title",
    "build_feature_files",
    "feature_bundle_paths",
    "create_feature_bundle",
    "get_feature_status",
    "list_feature_bundles",
    "read_feature_metadata",
    "parse_acceptance_criteria",
    "parse_feature_tasks",
    "parse_quality_checks",
    "parse_test_coverage",
    "parse_test_plan",
    "parse_release_readiness",
    "get_feature_files",
    "_path_as_posix",
    "_sync_body_source",
    "_extract_markdown_section",
    "_extract_markdown_section_lines",
    "_first_line_h1",
    "_markdown_heading",
    "_extract_scalar",
    "_first_scalar",
    "_section_placeholder",
    "_section_or_placeholder",
    "_why_or_placeholder",
    "_feature_why",
    "_relative_feature_paths",
    "_transition_payload",
    "_trace_gap",
    "_render_metadata_lines",
    "_empty_trace_summary",
    "_feature_sources_from_status",
    "build_proposal_files",
    "create_proposal_bundle",
]


FEATURE_SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
FEATURE_FILE_PATHS = {
    "spec": "specs/features/{slug}.md",
    "execution": "execution/features/{slug}.md",
    "quality": "quality/features/{slug}.md",
}
FEATURE_STATUSES = (
    "proposed",
    "planned",
    "in-progress",
    "implemented",
    "validated",
    "archived",
)
FEATURE_PRIORITIES = ("high", "medium", "low")
FEATURE_TRANSITIONS = {
    "proposed": ("planned", "archived"),
    "planned": ("in-progress", "archived"),
    "in-progress": ("implemented", "planned", "archived"),
    "implemented": ("validated", "in-progress", "archived"),
    "validated": ("archived", "implemented"),
    "archived": (),
}
FEATURE_DIRECTORIES = {
    kind: str(Path(pattern.format(slug="__feature__")).parent)
    for kind, pattern in FEATURE_FILE_PATHS.items()
}


class InvalidFeatureSlug(ValueError):
    """Raised when a feature slug cannot be used as a feature id."""


class InvalidFeatureStatus(ValueError):
    """Raised when a feature lifecycle status is not supported."""


@dataclass(frozen=True)
class FeatureMetadata:
    priority: str
    owner: str
    milestone: str
    target_release: str
    project: str
    effort: str

    def as_dict(self) -> dict[str, str]:
        return {
            "effort": self.effort,
            "milestone": self.milestone,
            "owner": self.owner,
            "priority": self.priority,
            "project": self.project,
            "target_release": self.target_release,
        }


@dataclass(frozen=True)
class FeatureBundleExistsError(FileExistsError):
    slug: str
    existing_paths: tuple[Path, ...]

    def __str__(self) -> str:
        return (
            f"Feature bundle '{self.slug}' already has existing files. "
            "Use --force to overwrite them."
        )


@dataclass(frozen=True)
class FeatureBundleNotFoundError(FileNotFoundError):
    slug: str
    root: Path
    missing_paths: tuple[Path, ...]

    def __str__(self) -> str:
        return (
            f"No feature files found for '{self.slug}' at {self.root}. "
            "Expected at least one native feature file."
        )


@dataclass(frozen=True)
class FeatureSyncPlanArtifactExistsError(FileExistsError):
    output_dir: Path
    existing_paths: tuple[Path, ...]

    def __str__(self) -> str:
        return (
            f"Sync plan artifact files already exist in {self.output_dir}. "
            "Use --force to overwrite files written by this command."
        )


@dataclass(frozen=True)
class FeatureStatusTransitionError(ValueError):
    feature_id: str
    error: str
    transition: dict[str, object]
    message: str
    blocking_checks: tuple[dict[str, str], ...] = ()
    gaps: tuple[dict[str, str], ...] = ()
    missing_files: tuple[str, ...] = ()

    def __str__(self) -> str:
        return self.message

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "error": self.error,
            "feature_id": self.feature_id,
            "transition": dict(self.transition),
        }
        if self.blocking_checks:
            payload["blocking_checks"] = [dict(check) for check in self.blocking_checks]
        if self.gaps:
            payload["gaps"] = [dict(gap) for gap in self.gaps]
        if self.missing_files:
            payload["missing_files"] = list(self.missing_files)
        return payload


@dataclass(frozen=True)
class IssueDraft:
    title: str
    body: str
    feature_id: str
    source_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    status: str
    metadata: FeatureMetadata

    def as_dict(self) -> dict[str, object]:
        return {
            "body": self.body,
            "feature_id": self.feature_id,
            "metadata": self.metadata.as_dict(),
            "missing_files": list(self.missing_files),
            "source_files": list(self.source_files),
            "status": self.status,
            "title": self.title,
        }


@dataclass(frozen=True)
class PullRequestDraft:
    title: str
    body: str
    feature_id: str
    status: str
    ready: bool
    source_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    gaps: tuple[dict[str, str], ...]
    blocking_checks: tuple[FeatureReadyCheck, ...]
    summary: dict[str, object]
    recommended_commands: tuple[str, ...]
    metadata: FeatureMetadata

    def as_dict(self) -> dict[str, object]:
        return {
            "blocking_checks": [
                check.as_dict() for check in self.blocking_checks
            ],
            "body": self.body,
            "feature_id": self.feature_id,
            "gaps": [dict(gap) for gap in self.gaps],
            "metadata": self.metadata.as_dict(),
            "missing_files": list(self.missing_files),
            "ready": self.ready,
            "recommended_commands": list(self.recommended_commands),
            "source_files": list(self.source_files),
            "status": self.status,
            "summary": self.summary,
            "title": self.title,
        }


@dataclass(frozen=True)
class FeatureSyncPlanCommand:
    id: str
    kind: str
    description: str
    argv: tuple[str, ...]
    body_source: str
    body: str
    creates_remote: bool = True
    requires_token: bool = True
    requires_network: bool = True
    safe_to_auto_run: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "argv": list(self.argv),
            "body": self.body,
            "body_source": self.body_source,
            "creates_remote": self.creates_remote,
            "description": self.description,
            "id": self.id,
            "kind": self.kind,
            "requires_network": self.requires_network,
            "requires_token": self.requires_token,
            "safe_to_auto_run": self.safe_to_auto_run,
        }


@dataclass(frozen=True)
class FeatureSyncPlan:
    feature_id: str
    status: str
    ready: bool
    source_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    gaps: tuple[dict[str, str], ...]
    blocking_checks: tuple[FeatureReadyCheck, ...]
    metadata: FeatureMetadata
    commands: tuple[FeatureSyncPlanCommand, ...]
    notes: tuple[str, ...]
    recommended_commands: tuple[str, ...]

    @property
    def summary(self) -> dict[str, int]:
        issue_commands = sum(1 for command in self.commands if command.kind == "issue")
        task_issue_commands = sum(
            1 for command in self.commands if command.kind == "task-issue"
        )
        pull_request_commands = sum(
            1 for command in self.commands if command.kind == "pull-request"
        )
        return {
            "commands_total": len(self.commands),
            "issue_commands": issue_commands,
            "notes_total": len(self.notes),
            "pull_request_commands": pull_request_commands,
            "task_issue_commands": task_issue_commands,
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "blocking_checks": [
                check.as_dict() for check in self.blocking_checks
            ],
            "commands": [command.as_dict() for command in self.commands],
            "feature_id": self.feature_id,
            "gaps": [dict(gap) for gap in self.gaps],
            "metadata": self.metadata.as_dict(),
            "missing_files": list(self.missing_files),
            "notes": list(self.notes),
            "ready": self.ready,
            "recommended_commands": list(self.recommended_commands),
            "source_files": list(self.source_files),
            "status": self.status,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class FeatureSyncPlanArtifacts:
    output_dir: Path
    manifest_path: Path
    commands_path: Path
    body_paths: tuple[Path, ...]
    written_paths: tuple[Path, ...]
    manifest: dict[str, object]


@dataclass(frozen=True)
class FeatureTask:
    id: str
    text: str
    done: bool
    source_file: str
    line: int

    def as_dict(self) -> dict[str, object]:
        return {
            "done": self.done,
            "id": self.id,
            "line": self.line,
            "source_file": self.source_file,
            "text": self.text,
        }


@dataclass(frozen=True)
class FeatureTraceChecklistItem:
    id: str
    text: str
    done: bool
    source_file: str
    line: int

    def as_dict(self) -> dict[str, object]:
        return {
            "done": self.done,
            "id": self.id,
            "line": self.line,
            "source_file": self.source_file,
            "text": self.text,
        }


@dataclass(frozen=True)
class FeatureTraceTestPlanItem:
    id: str
    text: str
    source_file: str
    line: int

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "line": self.line,
            "source_file": self.source_file,
            "text": self.text,
        }


@dataclass(frozen=True)
class FeatureAcceptanceTestCase:
    id: str
    acceptance_criterion_id: str
    acceptance_criterion_text: str
    source_file: str
    line: int
    behavior: str
    status: str = "pending"
    coverage: tuple[FeatureTestCoverageLink, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "acceptance_criterion_id": self.acceptance_criterion_id,
            "acceptance_criterion_text": self.acceptance_criterion_text,
            "behavior": self.behavior,
            "coverage": [link.as_dict() for link in self.coverage],
            "id": self.id,
            "line": self.line,
            "source_file": self.source_file,
            "status": self.status,
        }


@dataclass(frozen=True)
class FeatureTestCoverageLink:
    id: str
    acceptance_criterion_id: str
    target: str
    target_path: str
    target_exists: bool
    done: bool
    text: str
    source_file: str
    line: int

    def as_dict(self) -> dict[str, object]:
        return {
            "acceptance_criterion_id": self.acceptance_criterion_id,
            "done": self.done,
            "id": self.id,
            "line": self.line,
            "source_file": self.source_file,
            "target": self.target,
            "target_exists": self.target_exists,
            "target_path": self.target_path,
            "text": self.text,
        }


@dataclass(frozen=True)
class FeatureTraceReport:
    feature_id: str
    status: str
    sources: dict[str, dict[str, object]]
    missing_files: tuple[str, ...]
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...]
    tasks: tuple[FeatureTask, ...]
    quality_checks: tuple[FeatureTraceChecklistItem, ...]
    test_plan: tuple[FeatureTraceTestPlanItem, ...]
    gaps: tuple[dict[str, str], ...]

    @property
    def summary(self) -> dict[str, object]:
        def checklist_counts(
            items: tuple[FeatureTraceChecklistItem, ...] | tuple[FeatureTask, ...],
        ) -> dict[str, int]:
            done = sum(1 for item in items if item.done)
            total = len(items)
            return {
                "done": done,
                "open": total - done,
                "total": total,
            }

        acceptance_criteria = checklist_counts(self.acceptance_criteria)
        tasks = checklist_counts(self.tasks)
        quality_checks = checklist_counts(self.quality_checks)
        total = (
            acceptance_criteria["total"]
            + tasks["total"]
            + quality_checks["total"]
        )
        done = (
            acceptance_criteria["done"]
            + tasks["done"]
            + quality_checks["done"]
        )

        return {
            "acceptance_criteria": acceptance_criteria,
            "done": done,
            "open": total - done,
            "quality_checks": quality_checks,
            "tasks": tasks,
            "test_plan": {"total": len(self.test_plan)},
            "total": total,
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "acceptance_criteria": [
                item.as_dict() for item in self.acceptance_criteria
            ],
            "feature_id": self.feature_id,
            "gaps": [dict(gap) for gap in self.gaps],
            "missing_files": list(self.missing_files),
            "quality_checks": [item.as_dict() for item in self.quality_checks],
            "sources": self.sources,
            "status": self.status,
            "summary": self.summary,
            "tasks": [task.as_dict() for task in self.tasks],
            "test_plan": [item.as_dict() for item in self.test_plan],
        }


@dataclass(frozen=True)
class FeatureReadyCheck:
    id: str
    status: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "message": self.message,
            "status": self.status,
        }


@dataclass(frozen=True)
class FeatureReadyReport:
    feature_id: str
    ready: bool
    status: str
    checks: tuple[FeatureReadyCheck, ...]
    missing_files: tuple[str, ...]
    gaps: tuple[dict[str, str], ...]
    coverage_required: bool = False
    policy_applied: bool = False
    coverage_required_by_policy: bool = False
    policy_source: str | None = None

    @property
    def blocking_checks(self) -> tuple[FeatureReadyCheck, ...]:
        return tuple(check for check in self.checks if check.status == "fail")

    @property
    def summary(self) -> dict[str, int]:
        passed = sum(1 for check in self.checks if check.status == "pass")
        total = len(self.checks)
        return {
            "fail": total - passed,
            "pass": passed,
            "total": total,
        }

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "blocking_checks": [
                check.as_dict() for check in self.blocking_checks
            ],
            "checks": [check.as_dict() for check in self.checks],
            "feature_id": self.feature_id,
            "gaps": [dict(gap) for gap in self.gaps],
            "missing_files": list(self.missing_files),
            "ready": self.ready,
            "status": self.status,
            "summary": self.summary,
        }
        if self.coverage_required:
            payload["coverage_required"] = True
        if self.policy_applied:
            payload["coverage_required_by_policy"] = self.coverage_required_by_policy
            payload["policy_applied"] = True
            payload["policy_source"] = self.policy_source
        return payload


@dataclass(frozen=True)
class FeatureTasksReport:
    feature_id: str
    status: str
    source_file: str
    source_missing: bool
    tasks: tuple[FeatureTask, ...]
    missing_files: tuple[str, ...]

    @property
    def summary(self) -> dict[str, int]:
        done = sum(1 for task in self.tasks if task.done)
        total = len(self.tasks)
        return {
            "done": done,
            "open": total - done,
            "total": total,
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "feature_id": self.feature_id,
            "missing_files": list(self.missing_files),
            "source_file": self.source_file,
            "source_missing": self.source_missing,
            "status": self.status,
            "summary": self.summary,
            "tasks": [task.as_dict() for task in self.tasks],
        }


@dataclass(frozen=True)
class FeatureTaskIssueDraft:
    title: str
    body: str
    feature_id: str
    task_id: str
    task_text: str
    task_done: bool
    source_file: str
    line: int

    def as_dict(self) -> dict[str, object]:
        return {
            "body": self.body,
            "feature_id": self.feature_id,
            "line": self.line,
            "source_file": self.source_file,
            "task_done": self.task_done,
            "task_id": self.task_id,
            "task_text": self.task_text,
            "title": self.title,
        }


@dataclass(frozen=True)
class FeatureTaskIssuesReport:
    feature_id: str
    status: str
    source_file: str
    source_missing: bool
    missing_files: tuple[str, ...]
    issues: tuple[FeatureTaskIssueDraft, ...]
    task_summary: dict[str, int]
    recommended_commands: tuple[str, ...]

    @property
    def summary(self) -> dict[str, int]:
        return {
            "done": self.task_summary["done"],
            "issue_total": len(self.issues),
            "open": self.task_summary["open"],
            "total": self.task_summary["total"],
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "feature_id": self.feature_id,
            "issues": [issue.as_dict() for issue in self.issues],
            "missing_files": list(self.missing_files),
            "recommended_commands": list(self.recommended_commands),
            "source_file": self.source_file,
            "source_missing": self.source_missing,
            "status": self.status,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class FeatureHandoffReport:
    feature_id: str
    status: str
    ready: bool
    sources: dict[str, dict[str, object]]
    missing_files: tuple[str, ...]
    gaps: tuple[dict[str, str], ...]
    blocking_checks: tuple[FeatureReadyCheck, ...]
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...]
    tasks: tuple[FeatureTask, ...]
    quality_checks: tuple[FeatureTraceChecklistItem, ...]
    test_plan: tuple[FeatureTraceTestPlanItem, ...]
    release_readiness: tuple[FeatureTraceChecklistItem, ...]
    trace_summary: dict[str, object]
    ready_summary: dict[str, int]
    task_summary: dict[str, int]
    recommended_commands: tuple[str, ...]
    next_actions: tuple[str, ...]
    has_native_files: bool
    metadata: FeatureMetadata

    @property
    def summary(self) -> dict[str, object]:
        return {
            "blocking_checks": {"total": len(self.blocking_checks)},
            "gaps": {"total": len(self.gaps)},
            "ready": dict(self.ready_summary),
            "tasks": dict(self.task_summary),
            "trace": dict(self.trace_summary),
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "acceptance_criteria": [
                item.as_dict() for item in self.acceptance_criteria
            ],
            "blocking_checks": [
                check.as_dict() for check in self.blocking_checks
            ],
            "feature_id": self.feature_id,
            "gaps": [dict(gap) for gap in self.gaps],
            "missing_files": list(self.missing_files),
            "metadata": self.metadata.as_dict(),
            "next_actions": list(self.next_actions),
            "quality_checks": [item.as_dict() for item in self.quality_checks],
            "ready": self.ready,
            "recommended_commands": list(self.recommended_commands),
            "release_readiness": [
                item.as_dict() for item in self.release_readiness
            ],
            "sources": self.sources,
            "status": self.status,
            "summary": self.summary,
            "tasks": [task.as_dict() for task in self.tasks],
            "test_plan": [item.as_dict() for item in self.test_plan],
        }


@dataclass(frozen=True)
class FeatureTestsReport:
    feature_id: str
    status: str
    ready: bool
    source_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    gaps: tuple[dict[str, str], ...]
    blocking_checks: tuple[FeatureReadyCheck, ...]
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...]
    test_plan: tuple[FeatureTraceTestPlanItem, ...]
    test_cases: tuple[FeatureAcceptanceTestCase, ...]
    quality_checks: tuple[FeatureTraceChecklistItem, ...]
    ready_summary: dict[str, int]
    recommended_commands: tuple[str, ...]
    has_native_files: bool
    metadata: FeatureMetadata
    test_coverage: tuple[FeatureTestCoverageLink, ...] = ()

    @property
    def summary(self) -> dict[str, object]:
        def checklist_counts(
            items: tuple[FeatureTraceChecklistItem, ...],
        ) -> dict[str, int]:
            done = sum(1 for item in items if item.done)
            total = len(items)
            return {
                "done": done,
                "open": total - done,
                "total": total,
            }

        return {
            "acceptance_criteria": checklist_counts(self.acceptance_criteria),
            "blocking_checks": {"total": len(self.blocking_checks)},
            "gaps": {"total": len(self.gaps)},
            "missing_files": {"total": len(self.missing_files)},
            "quality_checks": checklist_counts(self.quality_checks),
            "ready": dict(self.ready_summary),
            "source_files": {"total": len(self.source_files)},
            "test_cases": {"total": len(self.test_cases)},
            "test_coverage": checklist_counts(self.test_coverage),
            "test_plan": {"total": len(self.test_plan)},
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "acceptance_criteria": [
                item.as_dict() for item in self.acceptance_criteria
            ],
            "blocking_checks": [
                check.as_dict() for check in self.blocking_checks
            ],
            "feature_id": self.feature_id,
            "gaps": [dict(gap) for gap in self.gaps],
            "missing_files": list(self.missing_files),
            "metadata": self.metadata.as_dict(),
            "quality_checks": [item.as_dict() for item in self.quality_checks],
            "ready": self.ready,
            "recommended_commands": list(self.recommended_commands),
            "source_files": list(self.source_files),
            "status": self.status,
            "summary": self.summary,
            "test_cases": [test_case.as_dict() for test_case in self.test_cases],
            "test_coverage": [link.as_dict() for link in self.test_coverage],
            "test_plan": [item.as_dict() for item in self.test_plan],
        }


@dataclass(frozen=True)
class FeatureStatusReport:
    feature_id: str
    status: str | None
    consistent: bool
    files: dict[str, dict[str, object]]
    missing_files: tuple[str, ...]
    updated_files: tuple[str, ...] = ()
    transition: dict[str, object] | None = None

    def as_dict(self, *, include_updated: bool = False) -> dict[str, object]:
        payload: dict[str, object] = {
            "consistent": self.consistent,
            "feature_id": self.feature_id,
            "files": self.files,
            "missing_files": list(self.missing_files),
            "status": self.status,
        }
        if include_updated:
            payload["updated_files"] = list(self.updated_files)
        if self.transition is not None:
            payload["transition"] = dict(self.transition)
        return payload


def validate_feature_slug(slug: str) -> str:
    if FEATURE_SLUG_RE.fullmatch(slug):
        return slug

    raise InvalidFeatureSlug(
        f"Invalid feature slug '{slug}'. Use lowercase letters, numbers, and "
        "hyphens only; start and end with a letter or number."
    )


def validate_feature_status(status: str) -> str:
    if status in FEATURE_STATUSES:
        return status

    allowed = ", ".join(FEATURE_STATUSES)
    raise InvalidFeatureStatus(
        f"Invalid feature status '{status}'. Use one of: {allowed}."
    )


def normalize_feature_priority(priority: str | None) -> str:
    if priority is None:
        return "unknown"

    normalized = priority.strip().lower()
    if normalized in FEATURE_PRIORITIES:
        return normalized

    return "unknown"


def normalize_feature_owner(owner: str | None) -> str:
    if owner is None:
        return "unassigned"

    normalized = owner.strip()
    if not normalized:
        return "unassigned"
    if normalized.lower() == "unassigned":
        return "unassigned"

    return normalized


def normalize_feature_assignment(value: str | None) -> str:
    if value is None:
        return "unassigned"

    normalized = value.strip()
    if not normalized:
        return "unassigned"
    if normalized.lower() == "unassigned":
        return "unassigned"

    return normalized


def normalize_feature_effort(effort: str | None) -> str:
    if effort is None:
        return "unknown"

    normalized = effort.strip()
    if not normalized:
        return "unknown"
    if normalized.lower() == "unknown":
        return "unknown"

    return normalized


def feature_title(slug: str, title: str | None = None) -> str:
    if title and title.strip():
        return title.strip()
    return slug.replace("-", " ").title()


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


def _extract_scalar(content: str, key: str) -> str | None:
    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue

        current_key, value = stripped.split(":", 1)
        if current_key.strip().lower() != key.lower():
            continue

        value = value.strip()
        if value:
            return value

    return None


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


def _first_line_h1(content: str) -> str | None:
    first_line = content.splitlines()[0].strip() if content.splitlines() else ""
    match = re.fullmatch(r"#\s+(.+?)\s*#*", first_line)
    if not match:
        return None

    title = match.group(1).strip()
    return title or None


def _markdown_heading(raw_line: str) -> tuple[int, str] | None:
    match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", raw_line.strip())
    if not match:
        return None

    return len(match.group(1)), match.group(2).strip()


def _extract_markdown_section(content: str, heading: str) -> str | None:
    lines = content.splitlines()
    section_start: int | None = None
    section_level: int | None = None

    for index, raw_line in enumerate(lines):
        parsed = _markdown_heading(raw_line)
        if parsed is None:
            continue

        level, text = parsed
        if section_start is None:
            if level >= 2 and text.lower() == heading.lower():
                section_start = index + 1
                section_level = level
            continue

        if section_level is not None and level <= section_level:
            section = "\n".join(lines[section_start:index]).strip()
            return section or None

    if section_start is None:
        return None

    section = "\n".join(lines[section_start:]).strip()
    return section or None


def _extract_markdown_section_lines(content: str, heading: str) -> list[tuple[int, str]]:
    lines = content.splitlines()
    section_start: int | None = None
    section_level: int | None = None

    for index, raw_line in enumerate(lines):
        parsed = _markdown_heading(raw_line)
        if parsed is None:
            continue

        level, text = parsed
        if section_start is None:
            if level >= 2 and text.lower() == heading.lower():
                section_start = index + 1
                section_level = level
            continue

        if section_level is not None and level <= section_level:
            return [
                (line_number, line)
                for line_number, line in enumerate(
                    lines[section_start:index],
                    start=section_start + 1,
                )
            ]

    if section_start is None:
        return []

    return [
        (line_number, line)
        for line_number, line in enumerate(
            lines[section_start:],
            start=section_start + 1,
        )
    ]


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


def _render_metadata_lines(metadata: FeatureMetadata) -> list[str]:
    return [
        f"- Priority: {metadata.priority}",
        f"- Owner: {metadata.owner}",
        f"- Milestone: {metadata.milestone}",
        f"- Target Release: {metadata.target_release}",
        f"- Project: {metadata.project}",
        f"- Effort: {metadata.effort}",
    ]


def _empty_trace_summary() -> dict[str, object]:
    return {
        "acceptance_criteria": {"done": 0, "open": 0, "total": 0},
        "done": 0,
        "open": 0,
        "quality_checks": {"done": 0, "open": 0, "total": 0},
        "tasks": {"done": 0, "open": 0, "total": 0},
        "test_plan": {"total": 0},
        "total": 0,
    }


def _feature_sources_from_status(
    status_report: FeatureStatusReport,
) -> dict[str, dict[str, object]]:
    return {
        kind: {
            "exists": file["exists"],
            "path": file["path"],
        }
        for kind, file in status_report.files.items()
    }


def _first_scalar(contents: dict[str, str], key: str) -> str | None:
    for kind in FEATURE_FILE_PATHS:
        content = contents.get(kind)
        if content is None:
            continue

        value = _extract_scalar(content, key)
        if value:
            return value

    return None


def _section_placeholder(kind: str, heading: str, relative_path: str) -> str:
    if kind == "missing_file":
        return f"TODO: Add `{relative_path}` with a `## {heading}` section."
    return f"TODO: Add a `## {heading}` section to `{relative_path}`."


def _section_or_placeholder(
    contents: dict[str, str],
    *,
    kind: str,
    heading: str,
    relative_path: str,
) -> str:
    content = contents.get(kind)
    if content is None:
        return _section_placeholder("missing_file", heading, relative_path)

    section = _extract_markdown_section(content, heading)
    if section:
        return section

    return _section_placeholder(kind, heading, relative_path)


def _why_or_placeholder(
    contents: dict[str, str],
    *,
    relative_path: str,
) -> str:
    spec = contents.get("spec")
    if spec is not None:
        section = _extract_markdown_section(spec, "Why")
        if section:
            return section

    scalar = _first_scalar(contents, "Why")
    if scalar:
        return scalar

    if spec is None:
        return _section_placeholder("missing_file", "Why", relative_path)

    return _section_placeholder("spec", "Why", relative_path)


CHECKBOX_TASK_RE = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(.+?)\s*$")
AC_ID_RE = re.compile(r"\bAC\d{3,}\b", re.IGNORECASE)


def _parse_trace_checklist_items(
    content: str,
    *,
    heading: str,
    prefix: str,
    source_file: str,
) -> tuple[FeatureTraceChecklistItem, ...]:
    items: list[FeatureTraceChecklistItem] = []

    for line_number, raw_line in _extract_markdown_section_lines(content, heading):
        match = CHECKBOX_TASK_RE.match(raw_line)
        if match is None:
            continue

        marker, text = match.groups()
        items.append(
            FeatureTraceChecklistItem(
                id=f"{prefix}{len(items) + 1:03d}",
                text=text.strip(),
                done=marker.lower() == "x",
                source_file=source_file,
                line=line_number,
            )
        )

    return tuple(items)


def parse_acceptance_criteria(
    content: str,
    *,
    source_file: str,
) -> tuple[FeatureTraceChecklistItem, ...]:
    return _parse_trace_checklist_items(
        content,
        heading="Acceptance Criteria",
        prefix="AC",
        source_file=source_file,
    )


def parse_feature_tasks(
    content: str,
    *,
    source_file: str,
) -> tuple[FeatureTask, ...]:
    tasks: list[FeatureTask] = []

    for line_number, raw_line in _extract_markdown_section_lines(content, "Tasks"):
        match = CHECKBOX_TASK_RE.match(raw_line)
        if match is None:
            continue

        task_id = f"T{len(tasks) + 1:03d}"
        marker, text = match.groups()
        tasks.append(
            FeatureTask(
                id=task_id,
                text=text.strip(),
                done=marker.lower() == "x",
                source_file=source_file,
                line=line_number,
            )
        )

    return tuple(tasks)


def parse_quality_checks(
    content: str,
    *,
    source_file: str,
) -> tuple[FeatureTraceChecklistItem, ...]:
    return _parse_trace_checklist_items(
        content,
        heading="Required Checks",
        prefix="Q",
        source_file=source_file,
    )


def _strip_markdown_code(text: str) -> str:
    stripped = text.strip()
    if len(stripped) >= 2 and stripped.startswith("`") and stripped.endswith("`"):
        return stripped[1:-1].strip()
    return stripped


def _test_coverage_target_path(target: str) -> str:
    return _strip_markdown_code(target).split("::", 1)[0].strip()


def parse_test_coverage(
    content: str,
    *,
    source_file: str,
    root: Path,
) -> tuple[FeatureTestCoverageLink, ...]:
    links: list[FeatureTestCoverageLink] = []
    resolved_root = root.expanduser().resolve()

    for line_number, raw_line in _extract_markdown_section_lines(content, "Test Coverage"):
        match = CHECKBOX_TASK_RE.match(raw_line)
        if match is None:
            continue

        marker, text = match.groups()
        normalized_text = text.strip()
        ac_match = AC_ID_RE.search(normalized_text)
        acceptance_criterion_id = (
            ac_match.group(0).upper() if ac_match is not None else "unknown"
        )
        target = ""
        if "->" in normalized_text:
            _left, right = normalized_text.split("->", 1)
            target = _strip_markdown_code(right)
        target_path = _test_coverage_target_path(target)
        target_path_obj = Path(target_path)
        target_exists = (
            bool(target_path)
            and not target_path_obj.is_absolute()
            and (resolved_root / target_path_obj).exists()
        )
        links.append(
            FeatureTestCoverageLink(
                id=f"COV{len(links) + 1:03d}",
                acceptance_criterion_id=acceptance_criterion_id,
                target=target,
                target_path=target_path,
                target_exists=target_exists,
                done=marker.lower() == "x",
                text=normalized_text,
                source_file=source_file,
                line=line_number,
            )
        )

    return tuple(links)


def parse_test_plan(
    content: str,
    *,
    source_file: str,
) -> tuple[FeatureTraceTestPlanItem, ...]:
    items: list[FeatureTraceTestPlanItem] = []

    for line_number, raw_line in _extract_markdown_section_lines(content, "Test Plan"):
        text = raw_line.strip()
        if not text:
            continue

        items.append(
            FeatureTraceTestPlanItem(
                id=f"TP{len(items) + 1:03d}",
                text=text,
                source_file=source_file,
                line=line_number,
            )
        )

    return tuple(items)


def parse_release_readiness(
    content: str,
    *,
    source_file: str,
) -> tuple[FeatureTraceChecklistItem, ...]:
    return _parse_trace_checklist_items(
        content,
        heading="Release Readiness",
        prefix="RR",
        source_file=source_file,
    )


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

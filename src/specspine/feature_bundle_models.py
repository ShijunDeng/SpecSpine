from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "FEATURE_SLUG_RE",
    "FEATURE_FILE_PATHS",
    "FEATURE_STATUSES",
    "FEATURE_PRIORITIES",
    "FEATURE_TRANSITIONS",
    "FEATURE_DIRECTORIES",
    "CHECKBOX_TASK_RE",
    "AC_ID_RE",
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

CHECKBOX_TASK_RE = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(.+?)\s*$")
AC_ID_RE = re.compile(r"\bAC\d{3,}\b", re.IGNORECASE)


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
    blocking_checks: tuple["FeatureReadyCheck", ...]
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
    blocking_checks: tuple["FeatureReadyCheck", ...]
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
    coverage: tuple["FeatureTestCoverageLink", ...] = ()

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

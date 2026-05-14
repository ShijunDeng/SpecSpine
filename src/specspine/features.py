from __future__ import annotations

import json
import re
import shlex
from dataclasses import dataclass
from pathlib import Path

from .workspace import normalize_template


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

    def as_dict(self) -> dict[str, str]:
        return {
            "owner": self.owner,
            "priority": self.priority,
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

    def as_dict(self) -> dict[str, object]:
        return {
            "body": self.body,
            "feature_id": self.feature_id,
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

    def as_dict(self) -> dict[str, object]:
        return {
            "blocking_checks": [
                check.as_dict() for check in self.blocking_checks
            ],
            "body": self.body,
            "feature_id": self.feature_id,
            "gaps": [dict(gap) for gap in self.gaps],
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
            - Run `specspine feature ready {slug} . --json` after implementation evidence is complete.
            - Run `specspine feature pr {slug} . --json` to draft local Pull Request review notes.
            - Run `specspine feature sync-plan {slug} . --json` to review GitHub CLI sync intent without executing it.
            - Run `specspine feature sync-plan {slug} . --output-dir .specspine/sync-plan/{slug}` to materialize local sync review artifacts.
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
            - [ ] TODO: `specspine feature sync-plan {slug} . --json` or `--output-dir .specspine/sync-plan/{slug}` has been reviewed before any remote GitHub sync.
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


def _replace_or_insert_status_line(content: str, status: str) -> str:
    lines = content.splitlines(keepends=True)
    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue

        current_key, _value = stripped.split(":", 1)
        if current_key.strip().lower() == "status":
            newline = "\n" if raw_line.endswith("\n") else ""
            lines[index] = f"Status: {status}{newline}"
            return "".join(lines)

    insert_at = 0
    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if not stripped or ":" not in stripped:
            continue

        current_key, _value = stripped.split(":", 1)
        if current_key.strip().lower() == "feature id":
            insert_at = index + 1
            break

    lines.insert(insert_at, f"Status: {status}\n")
    return "".join(lines)


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


def _validate_enforced_feature_transition(
    root: Path,
    slug: str,
    to_status: str,
    status_report: FeatureStatusReport,
) -> dict[str, object]:
    from_status = status_report.status
    if not status_report.consistent or from_status in {None, "mixed"}:
        reason = "Current peer-file statuses are missing or inconsistent."
        raise FeatureStatusTransitionError(
            feature_id=slug,
            error="current_status_inconsistent",
            transition=_transition_payload(
                from_status=from_status,
                to_status=to_status,
                enforced=True,
                allowed=False,
                reason=reason,
            ),
            message=(
                f"Cannot update feature {slug} status with enforced transition: "
                f"current status is {from_status or 'unknown'}; {reason}"
            ),
            missing_files=status_report.missing_files,
        )

    if from_status not in FEATURE_TRANSITIONS:
        reason = f"Current status '{from_status}' is not a supported lifecycle status."
        raise FeatureStatusTransitionError(
            feature_id=slug,
            error="current_status_invalid",
            transition=_transition_payload(
                from_status=from_status,
                to_status=to_status,
                enforced=True,
                allowed=False,
                reason=reason,
            ),
            message=(
                f"Cannot update feature {slug} status with enforced transition: "
                f"{reason}"
            ),
            missing_files=status_report.missing_files,
        )

    allowed_targets = FEATURE_TRANSITIONS[from_status]
    if to_status not in allowed_targets:
        if from_status == "archived":
            reason = "Archived is terminal and cannot transition to another status."
        else:
            reason = (
                f"Transition {from_status} -> {to_status} is not allowed; "
                f"allowed targets are: {', '.join(allowed_targets)}."
            )
        raise FeatureStatusTransitionError(
            feature_id=slug,
            error="transition_not_allowed",
            transition=_transition_payload(
                from_status=from_status,
                to_status=to_status,
                enforced=True,
                allowed=False,
                reason=reason,
            ),
            message=(
                f"Cannot update feature {slug} status with enforced transition: "
                f"{reason}"
            ),
            missing_files=status_report.missing_files,
        )

    transition = _transition_payload(
        from_status=from_status,
        to_status=to_status,
        enforced=True,
        allowed=True,
    )
    if to_status == "archived":
        ready_report = build_feature_ready_report(root, slug)
        if not ready_report.ready:
            reason = "Archive requires feature ready gate to pass first."
            raise FeatureStatusTransitionError(
                feature_id=slug,
                error="archive_not_ready",
                transition=_transition_payload(
                    from_status=from_status,
                    to_status=to_status,
                    enforced=True,
                    allowed=True,
                    reason=reason,
                ),
                message=(
                    f"Cannot archive feature {slug}: {reason} "
                    "Run feature ready and resolve blocking checks."
                ),
                blocking_checks=tuple(
                    check.as_dict() for check in ready_report.blocking_checks
                ),
                gaps=ready_report.gaps,
                missing_files=ready_report.missing_files,
            )

    return transition


def set_feature_status(
    root: Path,
    slug: str,
    status: str,
    *,
    enforce_transition: bool = False,
) -> FeatureStatusReport:
    slug = validate_feature_slug(slug)
    status = validate_feature_status(status)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)

    before = get_feature_status(resolved_root, slug)
    existing_paths = [path for path in paths.values() if path.exists()]
    if not existing_paths:
        if enforce_transition:
            reason = "Current peer-file statuses are missing or inconsistent."
            raise FeatureStatusTransitionError(
                feature_id=slug,
                error="current_status_inconsistent",
                transition=_transition_payload(
                    from_status=before.status,
                    to_status=status,
                    enforced=True,
                    allowed=False,
                    reason=reason,
                ),
                message=(
                    f"Cannot update feature {slug} status with enforced transition: "
                    f"current status is unknown; {reason}"
                ),
                missing_files=before.missing_files,
            )
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(paths.values()),
        )

    if enforce_transition:
        transition = _validate_enforced_feature_transition(
            resolved_root,
            slug,
            status,
            before,
        )
    else:
        transition = _transition_payload(
            from_status=before.status,
            to_status=status,
            enforced=False,
            allowed=True,
        )

    updated_files: list[str] = []
    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        if not path.exists():
            continue

        content = path.read_text(encoding="utf-8")
        path.write_text(_replace_or_insert_status_line(content, status), encoding="utf-8")
        updated_files.append(relative_paths[kind])

    report = get_feature_status(resolved_root, slug)
    return FeatureStatusReport(
        feature_id=report.feature_id,
        status=report.status,
        consistent=report.consistent,
        files=report.files,
        missing_files=report.missing_files,
        updated_files=tuple(updated_files),
        transition=transition,
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


def read_feature_metadata(root: Path, slug: str) -> FeatureMetadata:
    slug = validate_feature_slug(slug)
    spec_path = feature_bundle_paths(root, slug)["spec"]
    if not spec_path.exists():
        return FeatureMetadata(priority="unknown", owner="unassigned")

    content = spec_path.read_text(encoding="utf-8")
    return FeatureMetadata(
        priority=normalize_feature_priority(_extract_scalar(content, "Priority")),
        owner=normalize_feature_owner(_extract_scalar(content, "Owner")),
    )


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
) -> str:
    lines = [
        "## Feature",
        "",
        f"- Feature ID: `{feature_id}`",
        f"- Status: {status}",
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
    )

    return IssueDraft(
        title=title,
        body=body,
        feature_id=slug,
        source_files=tuple(source_files),
        missing_files=tuple(missing_files),
        status=status,
    )


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


def build_feature_tasks_report(root: Path, slug: str) -> FeatureTasksReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)

    contents: dict[str, str] = {}
    missing_files: list[str] = []
    missing_paths: list[Path] = []

    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        relative_path = relative_paths[kind]
        if path.exists():
            contents[kind] = path.read_text(encoding="utf-8")
            continue

        missing_files.append(relative_path)
        missing_paths.append(path)

    if not contents:
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(missing_paths),
        )

    source_file = relative_paths["execution"]
    execution_content = contents.get("execution")
    tasks: tuple[FeatureTask, ...] = ()
    if execution_content is not None:
        tasks = parse_feature_tasks(execution_content, source_file=source_file)

    status_report = get_feature_status(resolved_root, slug)

    return FeatureTasksReport(
        feature_id=slug,
        status=status_report.status or "unknown",
        source_file=source_file,
        source_missing=execution_content is None,
        tasks=tasks,
        missing_files=tuple(missing_files),
    )


def _trace_gap(gap_id: str, source_file: str, message: str) -> dict[str, str]:
    return {
        "id": gap_id,
        "message": message,
        "source_file": source_file,
    }


def build_feature_trace_report(root: Path, slug: str) -> FeatureTraceReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)

    contents: dict[str, str] = {}
    missing_files: list[str] = []
    missing_paths: list[Path] = []
    sources: dict[str, dict[str, object]] = {}

    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        relative_path = relative_paths[kind]
        exists = path.exists()
        sources[kind] = {
            "exists": exists,
            "path": relative_path,
        }
        if exists:
            contents[kind] = path.read_text(encoding="utf-8")
            continue

        missing_files.append(relative_path)
        missing_paths.append(path)

    if not contents:
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(missing_paths),
        )

    spec_file = relative_paths["spec"]
    execution_file = relative_paths["execution"]
    quality_file = relative_paths["quality"]

    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...] = ()
    tasks: tuple[FeatureTask, ...] = ()
    quality_checks: tuple[FeatureTraceChecklistItem, ...] = ()
    test_plan: tuple[FeatureTraceTestPlanItem, ...] = ()

    spec_content = contents.get("spec")
    if spec_content is not None:
        acceptance_criteria = parse_acceptance_criteria(
            spec_content,
            source_file=spec_file,
        )

    execution_content = contents.get("execution")
    if execution_content is not None:
        tasks = parse_feature_tasks(execution_content, source_file=execution_file)

    quality_content = contents.get("quality")
    if quality_content is not None:
        quality_checks = parse_quality_checks(
            quality_content,
            source_file=quality_file,
        )
        test_plan = parse_test_plan(quality_content, source_file=quality_file)

    gaps: list[dict[str, str]] = []
    for relative_path in missing_files:
        gaps.append(
            _trace_gap(
                "missing_file",
                relative_path,
                f"Missing native feature file: {relative_path}",
            )
        )
    if not acceptance_criteria:
        gaps.append(
            _trace_gap(
                "missing_acceptance_criteria",
                spec_file,
                "No acceptance criteria checklist items found.",
            )
        )
    if not tasks:
        gaps.append(
            _trace_gap(
                "missing_tasks",
                execution_file,
                "No task checklist items found.",
            )
        )
    if not quality_checks:
        gaps.append(
            _trace_gap(
                "missing_required_checks",
                quality_file,
                "No required check checklist items found.",
            )
        )
    if not test_plan:
        gaps.append(
            _trace_gap(
                "missing_test_plan",
                quality_file,
                "No non-empty test plan content found.",
            )
        )

    status_report = get_feature_status(resolved_root, slug)

    return FeatureTraceReport(
        feature_id=slug,
        status=status_report.status or "unknown",
        sources=sources,
        missing_files=tuple(missing_files),
        acceptance_criteria=acceptance_criteria,
        tasks=tasks,
        quality_checks=quality_checks,
        test_plan=test_plan,
        gaps=tuple(gaps),
    )


def render_feature_trace_json(report: FeatureTraceReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def _render_trace_checklist_item(
    item: FeatureTraceChecklistItem | FeatureTask,
) -> str:
    marker = "x" if item.done else " "
    return f"- [{marker}] {item.id} {item.source_file}:{item.line} {item.text}"


def render_feature_trace_text(report: FeatureTraceReport) -> str:
    summary = report.summary
    lines = [
        f"Feature trace: {report.feature_id}",
        f"Status: {report.status}",
        "Sources:",
    ]
    for kind, source in report.sources.items():
        marker = "ok" if source["exists"] else "missing"
        lines.append(f"- [{marker}] {kind}: {source['path']}")

    lines.extend(
        [
            (
                "Summary: "
                f"total={summary['total']} "
                f"done={summary['done']} "
                f"open={summary['open']}"
            ),
            (
                "Counts: "
                f"ac={summary['acceptance_criteria']['total']} "
                f"tasks={summary['tasks']['total']} "
                f"quality={summary['quality_checks']['total']} "
                f"test_plan={summary['test_plan']['total']}"
            ),
            "",
            "Gaps:",
        ]
    )

    if report.gaps:
        lines.extend(
            f"- {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in report.gaps
        )
    else:
        lines.append("- None.")

    lines.extend(["", "Acceptance Criteria:"])
    if report.acceptance_criteria:
        lines.extend(
            _render_trace_checklist_item(item)
            for item in report.acceptance_criteria
        )
    else:
        lines.append("- None found.")

    lines.extend(["", "Tasks:"])
    if report.tasks:
        lines.extend(_render_trace_checklist_item(task) for task in report.tasks)
    else:
        lines.append("- None found.")

    lines.extend(["", "Quality Checks:"])
    if report.quality_checks:
        lines.extend(
            _render_trace_checklist_item(item)
            for item in report.quality_checks
        )
    else:
        lines.append("- None found.")

    lines.extend(["", "Test Plan:"])
    if report.test_plan:
        lines.extend(
            f"- {item.id} {item.source_file}:{item.line} {item.text}"
            for item in report.test_plan
        )
    else:
        lines.append("- None found.")

    return "\n".join(lines) + "\n"


def _ready_check(check_id: str, passed: bool, message: str) -> FeatureReadyCheck:
    return FeatureReadyCheck(
        id=check_id,
        status="pass" if passed else "fail",
        message=message,
    )


def _checklist_ready_message(
    *,
    label: str,
    items: tuple[FeatureTraceChecklistItem, ...] | tuple[FeatureTask, ...],
) -> tuple[bool, str]:
    total = len(items)
    done = sum(1 for item in items if item.done)
    open_count = total - done
    if total == 0:
        return False, f"No {label} checklist items found."
    if open_count:
        return False, f"{label.title()} incomplete: {open_count} open of {total}."
    return True, f"{label.title()} complete: {done} of {total} done."


def _coverage_ready_message(
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    test_coverage: tuple[FeatureTestCoverageLink, ...],
) -> tuple[bool, str]:
    missing_ids = []
    for criterion in acceptance_criteria:
        has_completed_local_link = any(
            link.acceptance_criterion_id == criterion.id
            and link.done
            and link.target_exists
            for link in test_coverage
        )
        if not has_completed_local_link:
            missing_ids.append(criterion.id)

    if missing_ids:
        return (
            False,
            "Missing completed local test coverage for acceptance criteria: "
            + ", ".join(missing_ids)
            + ".",
        )

    return (
        True,
        "Completed local test coverage links exist for all acceptance criteria.",
    )


def build_feature_ready_report(
    root: Path,
    slug: str,
    *,
    require_coverage: bool = False,
    policy_applied: bool = False,
    coverage_required_by_policy: bool = False,
    policy_source: str | None = None,
) -> FeatureReadyReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    relative_paths = _relative_feature_paths(slug)
    status_report = get_feature_status(resolved_root, slug)

    try:
        trace_report = build_feature_trace_report(resolved_root, slug)
        status = trace_report.status
        missing_files = trace_report.missing_files
        gaps = trace_report.gaps
        acceptance_criteria = trace_report.acceptance_criteria
        tasks = trace_report.tasks
        quality_checks = trace_report.quality_checks
        test_plan = trace_report.test_plan
    except FeatureBundleNotFoundError:
        status = status_report.status or "unknown"
        missing_files = tuple(relative_paths[kind] for kind in FEATURE_FILE_PATHS)
        gaps = tuple(
            _trace_gap(
                "missing_file",
                relative_path,
                f"Missing native feature file: {relative_path}",
            )
            for relative_path in missing_files
        )
        acceptance_criteria = ()
        tasks = ()
        quality_checks = ()
        test_plan = ()

    quality_path = feature_bundle_paths(resolved_root, slug)["quality"]
    release_readiness: tuple[FeatureTraceChecklistItem, ...] = ()
    test_coverage: tuple[FeatureTestCoverageLink, ...] = ()
    if quality_path.exists():
        quality_content = quality_path.read_text(encoding="utf-8")
        release_readiness = parse_release_readiness(
            quality_content,
            source_file=relative_paths["quality"],
        )
        if require_coverage:
            test_coverage = parse_test_coverage(
                quality_content,
                source_file=relative_paths["quality"],
                root=resolved_root,
            )

    checks: list[FeatureReadyCheck] = []

    checks.append(
        _ready_check(
            "feature.bundle_files",
            not missing_files,
            (
                "All native feature peer files are present."
                if not missing_files
                else "Missing native feature peer files: "
                + ", ".join(missing_files)
            ),
        )
    )

    checks.append(
        _ready_check(
            "feature.status_consistency",
            status_report.consistent,
            (
                f"Peer-file status is consistent: {status_report.status}."
                if status_report.consistent
                else "Peer-file statuses are missing or inconsistent."
            ),
        )
    )

    lifecycle_ready = status in {"implemented", "validated"}
    checks.append(
        _ready_check(
            "feature.lifecycle_status",
            lifecycle_ready,
            (
                f"Lifecycle status is releasable: {status}."
                if lifecycle_ready
                else "Lifecycle status must be implemented or validated; "
                f"found {status}."
            ),
        )
    )

    gap_ids = sorted({gap["id"] for gap in gaps})
    checks.append(
        _ready_check(
            "feature.trace_gaps",
            not gaps,
            (
                "Trace gaps are empty."
                if not gaps
                else "Trace gaps present: " + ", ".join(gap_ids)
            ),
        )
    )

    for check_id, label, items in (
        ("feature.acceptance_criteria", "acceptance criteria", acceptance_criteria),
        ("feature.tasks", "tasks", tasks),
        ("feature.required_checks", "required checks", quality_checks),
    ):
        passed, message = _checklist_ready_message(label=label, items=items)
        checks.append(_ready_check(check_id, passed, message))

    checks.append(
        _ready_check(
            "feature.test_plan",
            bool(test_plan),
            (
                f"Test plan has {len(test_plan)} non-empty line(s)."
                if test_plan
                else "No non-empty test plan content found."
            ),
        )
    )

    passed, message = _checklist_ready_message(
        label="release readiness",
        items=release_readiness,
    )
    checks.append(_ready_check("feature.release_readiness", passed, message))

    if require_coverage:
        passed, message = _coverage_ready_message(
            acceptance_criteria,
            test_coverage,
        )
        checks.append(_ready_check("feature.test_coverage", passed, message))

    ready = all(check.status == "pass" for check in checks)
    return FeatureReadyReport(
        feature_id=slug,
        ready=ready,
        status=status,
        checks=tuple(checks),
        missing_files=missing_files,
        gaps=gaps,
        coverage_required=require_coverage,
        policy_applied=policy_applied,
        coverage_required_by_policy=coverage_required_by_policy,
        policy_source=policy_source,
    )


def render_feature_ready_json(report: FeatureReadyReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_feature_ready_text(report: FeatureReadyReport) -> str:
    summary = report.summary
    lines = [
        f"Feature readiness: {report.feature_id}",
        f"Status: {report.status}",
        f"Ready: {'yes' if report.ready else 'no'}",
        (
            "Summary: "
            f"pass={summary['pass']} "
            f"fail={summary['fail']} "
            f"total={summary['total']}"
        ),
        "Blocking checks:",
    ]
    if report.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in report.blocking_checks
        )
    else:
        lines.append("- None.")

    return "\n".join(lines) + "\n"


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


def _recommended_handoff_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature handoff {slug} . --json",
        f"specspine feature tasks {slug} . --json",
        f"specspine feature task-issues {slug} . --json",
        f"specspine feature trace {slug} . --json",
        f"specspine feature tests {slug} . --json",
        f"specspine feature ready {slug} . --json",
        f"specspine feature pr {slug} . --json",
        "specspine validate . --fusion --features",
    )


def _append_unique(items: list[str], item: str) -> None:
    if item not in items:
        items.append(item)


def _handoff_next_actions(
    *,
    slug: str,
    has_native_files: bool,
    missing_files: tuple[str, ...],
    gaps: tuple[dict[str, str], ...],
    tasks: tuple[FeatureTask, ...],
    blocking_checks: tuple[FeatureReadyCheck, ...],
    ready: bool,
) -> tuple[str, ...]:
    actions: list[str] = []

    if not has_native_files:
        _append_unique(
            actions,
            (
                "Create or restore the native feature bundle: "
                f"specspine feature new {slug} . --title \"...\" --why \"...\""
            ),
        )
        return tuple(actions)

    if missing_files:
        _append_unique(
            actions,
            "Add missing peer file(s): " + ", ".join(missing_files),
        )

    section_gap_ids = tuple(
        gap["id"] for gap in gaps if gap["id"] != "missing_file"
    )
    if section_gap_ids:
        _append_unique(
            actions,
            "Fill missing trace section(s): " + ", ".join(section_gap_ids),
        )

    open_task_ids = tuple(task.id for task in tasks if not task.done)
    if open_task_ids:
        _append_unique(
            actions,
            "Complete open task(s): " + ", ".join(open_task_ids),
        )

    blocking_ids = tuple(check.id for check in blocking_checks)
    if blocking_ids:
        _append_unique(
            actions,
            "Resolve blocking readiness check(s): " + ", ".join(blocking_ids),
        )

    if ready:
        _append_unique(
            actions,
            "Review, merge, or archive the ready feature bundle.",
        )

    return tuple(actions)


def build_feature_handoff_report(
    root: Path,
    slug: str,
    *,
    require_coverage: bool = False,
) -> FeatureHandoffReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    status_report = get_feature_status(resolved_root, slug)
    has_native_files = any(file["exists"] for file in status_report.files.values())

    try:
        trace_report = build_feature_trace_report(resolved_root, slug)
    except FeatureBundleNotFoundError:
        missing_files = status_report.missing_files
        gaps = tuple(
            _trace_gap(
                "missing_file",
                relative_path,
                f"Missing native feature file: {relative_path}",
            )
            for relative_path in missing_files
        )
        trace_report = FeatureTraceReport(
            feature_id=slug,
            status=status_report.status or "unknown",
            sources=_feature_sources_from_status(status_report),
            missing_files=missing_files,
            acceptance_criteria=(),
            tasks=(),
            quality_checks=(),
            test_plan=(),
            gaps=gaps,
        )

    try:
        tasks_report = build_feature_tasks_report(resolved_root, slug)
        task_summary = tasks_report.summary
    except FeatureBundleNotFoundError:
        task_summary = {"done": 0, "open": 0, "total": 0}

    ready_report = build_feature_ready_report(
        resolved_root,
        slug,
        require_coverage=require_coverage,
    )

    relative_paths = _relative_feature_paths(slug)
    quality_path = feature_bundle_paths(resolved_root, slug)["quality"]
    release_readiness: tuple[FeatureTraceChecklistItem, ...] = ()
    if quality_path.exists():
        release_readiness = parse_release_readiness(
            quality_path.read_text(encoding="utf-8"),
            source_file=relative_paths["quality"],
        )

    next_actions = _handoff_next_actions(
        slug=slug,
        has_native_files=has_native_files,
        missing_files=trace_report.missing_files,
        gaps=trace_report.gaps,
        tasks=trace_report.tasks,
        blocking_checks=ready_report.blocking_checks,
        ready=ready_report.ready,
    )

    return FeatureHandoffReport(
        feature_id=slug,
        status=trace_report.status,
        ready=ready_report.ready,
        sources=trace_report.sources,
        missing_files=trace_report.missing_files,
        gaps=trace_report.gaps,
        blocking_checks=ready_report.blocking_checks,
        acceptance_criteria=trace_report.acceptance_criteria,
        tasks=trace_report.tasks,
        quality_checks=trace_report.quality_checks,
        test_plan=trace_report.test_plan,
        release_readiness=release_readiness,
        trace_summary=trace_report.summary if has_native_files else _empty_trace_summary(),
        ready_summary=ready_report.summary,
        task_summary=task_summary,
        recommended_commands=_recommended_handoff_commands(slug),
        next_actions=next_actions,
        has_native_files=has_native_files,
    )


def render_feature_handoff_json(report: FeatureHandoffReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_feature_handoff_text(report: FeatureHandoffReport) -> str:
    summary = report.summary
    trace = summary["trace"]
    ready = summary["ready"]
    tasks = summary["tasks"]
    lines = [
        f"Feature handoff: {report.feature_id}",
        f"Status: {report.status}",
        f"Ready: {'yes' if report.ready else 'no'}",
        (
            "Counts: "
            f"trace={trace['total']}/{trace['done']}/{trace['open']} "
            f"ready={ready['pass']}/{ready['fail']}/{ready['total']} "
            f"tasks={tasks['total']}/{tasks['done']}/{tasks['open']} "
            f"gaps={summary['gaps']['total']} "
            f"blocking={summary['blocking_checks']['total']}"
        ),
        "Sources:",
    ]
    for kind, source in report.sources.items():
        marker = "ok" if source["exists"] else "missing"
        lines.append(f"- [{marker}] {kind}: {source['path']}")

    lines.extend(["", "Next actions:"])
    if report.next_actions:
        lines.extend(f"- {action}" for action in report.next_actions)
    else:
        lines.append("- None.")

    open_tasks = tuple(task for task in report.tasks if not task.done)
    lines.extend(["", "Open tasks:"])
    if open_tasks:
        lines.extend(
            f"- {task.id} {task.source_file}:{task.line} {task.text}"
            for task in open_tasks
        )
    else:
        lines.append("- None.")

    lines.extend(["", "Blocking checks:"])
    if report.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in report.blocking_checks
        )
    else:
        lines.append("- None.")

    lines.extend(["", "Key commands:"])
    lines.extend(f"- {command}" for command in report.recommended_commands)

    return "\n".join(lines) + "\n"


def _recommended_task_issue_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature task-issues {slug} . --json",
        f"specspine feature tasks {slug} . --json",
        f"specspine feature trace {slug} . --json",
        f"specspine feature handoff {slug} . --json",
        "specspine validate . --fusion --features",
    )


def _truncate_issue_title_text(text: str, *, limit: int = 80) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def _feature_task_issue_title(slug: str, task: FeatureTask) -> str:
    return f"[{slug}] {task.id}: {_truncate_issue_title_text(task.text)}"


def _render_task_issue_acceptance_criteria(
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
) -> list[str]:
    if not acceptance_criteria:
        return ["- [ ] Add acceptance criteria checklist items before opening this issue."]

    lines: list[str] = []
    for item in acceptance_criteria:
        marker = "x" if item.done else " "
        lines.append(
            f"- [{marker}] {item.id} {item.source_file}:{item.line} {item.text}"
        )
    return lines


def _render_task_issue_commands(commands: tuple[str, ...]) -> list[str]:
    return [f"- `{command}`" for command in commands]


def _render_task_issue_body(
    *,
    feature_id: str,
    status: str,
    task: FeatureTask,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    recommended_commands: tuple[str, ...],
) -> str:
    marker = "x" if task.done else " "
    lines = [
        "## Feature",
        "",
        f"- Feature ID: `{feature_id}`",
        f"- Status: {status}",
        "",
        "## Task",
        "",
        f"- [{marker}] {task.id}: {task.text}",
        "",
        "## Status / Done",
        "",
        f"- Done: {'yes' if task.done else 'no'}",
        "",
        "## Source",
        "",
        f"- {task.source_file}:{task.line}",
        "",
        "## Acceptance Criteria",
        "",
    ]
    lines.extend(_render_task_issue_acceptance_criteria(acceptance_criteria))
    lines.extend(["", "## Key Commands", ""])
    lines.extend(_render_task_issue_commands(recommended_commands))
    return "\n".join(lines).strip() + "\n"


def build_feature_task_issues_report(root: Path, slug: str) -> FeatureTaskIssuesReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    tasks_report = build_feature_tasks_report(resolved_root, slug)
    try:
        trace_report = build_feature_trace_report(resolved_root, slug)
        acceptance_criteria = trace_report.acceptance_criteria
    except FeatureBundleNotFoundError:
        acceptance_criteria = ()

    recommended_commands = _recommended_task_issue_commands(slug)
    issues = tuple(
        FeatureTaskIssueDraft(
            title=_feature_task_issue_title(slug, task),
            body=_render_task_issue_body(
                feature_id=slug,
                status=tasks_report.status,
                task=task,
                acceptance_criteria=acceptance_criteria,
                recommended_commands=recommended_commands,
            ),
            feature_id=slug,
            task_id=task.id,
            task_text=task.text,
            task_done=task.done,
            source_file=task.source_file,
            line=task.line,
        )
        for task in tasks_report.tasks
    )

    return FeatureTaskIssuesReport(
        feature_id=slug,
        status=tasks_report.status,
        source_file=tasks_report.source_file,
        source_missing=tasks_report.source_missing,
        missing_files=tasks_report.missing_files,
        issues=issues,
        task_summary=tasks_report.summary,
        recommended_commands=recommended_commands,
    )


def render_feature_task_issues_json(report: FeatureTaskIssuesReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_feature_task_issues_text(report: FeatureTaskIssuesReport) -> str:
    summary = report.summary
    lines = [
        f"Feature task issue drafts: {report.feature_id}",
        f"Status: {report.status}",
        f"Source: {report.source_file}",
        (
            "Summary: "
            f"tasks={summary['total']} "
            f"done={summary['done']} "
            f"open={summary['open']} "
            f"issues={summary['issue_total']}"
        ),
        "",
        "Issues:",
    ]

    if report.issues:
        for index, issue in enumerate(report.issues, start=1):
            if index > 1:
                lines.append("")
            lines.extend(
                [
                    f"### Issue {index}: {issue.task_id}",
                    "",
                    f"Title: {issue.title}",
                    "",
                    issue.body.rstrip(),
                ]
            )
    elif report.source_missing:
        lines.append(
            "No issue drafts generated because source file is missing: "
            f"{report.source_file}"
        )
    else:
        lines.append(f"No checklist tasks found in {report.source_file}.")

    if report.missing_files:
        lines.extend(["", "Missing feature files:"])
        lines.extend(f"- {relative_path}" for relative_path in report.missing_files)

    lines.extend(["", "Key Commands:"])
    lines.extend(f"- {command}" for command in report.recommended_commands)

    return "\n".join(lines) + "\n"


def _recommended_test_packet_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature tests {slug} . --json",
        f"specspine feature trace {slug} . --json",
        f"specspine feature ready {slug} . --json",
        f"specspine feature handoff {slug} . --json",
        "specspine validate . --fusion --features",
    )


def _acceptance_test_cases(
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    test_coverage: tuple[FeatureTestCoverageLink, ...],
) -> tuple[FeatureAcceptanceTestCase, ...]:
    test_cases: list[FeatureAcceptanceTestCase] = []
    for index, criterion in enumerate(acceptance_criteria, start=1):
        coverage = tuple(
            link
            for link in test_coverage
            if link.acceptance_criterion_id == criterion.id
        )
        if any(link.done for link in coverage):
            status = "covered"
        elif coverage:
            status = "planned"
        else:
            status = "pending"
        test_cases.append(
            FeatureAcceptanceTestCase(
                id=f"TC{index:03d}",
                acceptance_criterion_id=criterion.id,
                acceptance_criterion_text=criterion.text,
                source_file=criterion.source_file,
                line=criterion.line,
                behavior=f"Pending behavior to test: {criterion.text}",
                coverage=coverage,
                status=status,
            )
        )
    return tuple(test_cases)


def build_feature_tests_report(root: Path, slug: str) -> FeatureTestsReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    handoff = build_feature_handoff_report(resolved_root, slug)
    source_files = tuple(
        source["path"]
        for source in handoff.sources.values()
        if bool(source["exists"])
    )
    test_coverage: tuple[FeatureTestCoverageLink, ...] = ()
    relative_paths = _relative_feature_paths(slug)
    quality_path = feature_bundle_paths(resolved_root, slug)["quality"]
    if quality_path.exists():
        test_coverage = parse_test_coverage(
            quality_path.read_text(encoding="utf-8"),
            source_file=relative_paths["quality"],
            root=resolved_root,
        )

    return FeatureTestsReport(
        feature_id=slug,
        status=handoff.status,
        ready=handoff.ready,
        source_files=source_files,
        missing_files=handoff.missing_files,
        gaps=handoff.gaps,
        blocking_checks=handoff.blocking_checks,
        acceptance_criteria=handoff.acceptance_criteria,
        test_plan=handoff.test_plan,
        test_coverage=test_coverage,
        test_cases=_acceptance_test_cases(
            handoff.acceptance_criteria,
            test_coverage,
        ),
        quality_checks=handoff.quality_checks,
        ready_summary=handoff.ready_summary,
        recommended_commands=_recommended_test_packet_commands(slug),
        has_native_files=handoff.has_native_files,
    )


def render_feature_tests_json(report: FeatureTestsReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_feature_tests_text(report: FeatureTestsReport) -> str:
    summary = report.summary
    lines = [
        f"Feature test packet: {report.feature_id}",
        f"Feature: {report.feature_id}",
        f"Status: {report.status}",
        f"Ready: {'yes' if report.ready else 'no'}",
        "Sources:",
    ]
    if report.source_files:
        lines.extend(f"- [ok] {relative_path}" for relative_path in report.source_files)
    if report.missing_files:
        lines.extend(
            f"- [missing] {relative_path}"
            for relative_path in report.missing_files
        )
    if not report.source_files and not report.missing_files:
        lines.append("- None.")

    lines.extend(
        [
            (
                "Summary: "
                f"acceptance_criteria={summary['acceptance_criteria']['total']} "
                f"test_cases={summary['test_cases']['total']} "
                f"test_coverage={summary['test_coverage']['total']} "
                f"test_plan={summary['test_plan']['total']} "
                f"quality_checks={summary['quality_checks']['total']} "
                f"gaps={summary['gaps']['total']} "
                f"blocking={summary['blocking_checks']['total']}"
            ),
            "",
            "Test Cases:",
        ]
    )
    if report.test_cases:
        for test_case in report.test_cases:
            linked_targets = (
                ", ".join(link.target for link in test_case.coverage if link.target)
                or "None linked"
            )
            lines.append(
                f"- [ ] {test_case.id} -> "
                f"{test_case.acceptance_criterion_id} "
                f"[{test_case.status}; links={linked_targets}] "
                f"{test_case.source_file}:{test_case.line} "
                f"{test_case.behavior}"
            )
    else:
        lines.append(
            "- [ ] Add acceptance criteria checklist items before testing behavior."
        )

    lines.extend(["", "Test Coverage:"])
    if report.test_coverage:
        for link in report.test_coverage:
            marker = "x" if link.done else " "
            exists = "exists" if link.target_exists else "missing"
            target = link.target or "None linked"
            lines.append(
                f"- [{marker}] {link.id} -> "
                f"{link.acceptance_criterion_id} {target} "
                f"({exists}) {link.source_file}:{link.line}"
            )
    else:
        lines.append("- None linked.")

    lines.extend(["", "Existing Test Plan:"])
    if report.test_plan:
        lines.extend(
            f"- {item.id} {item.source_file}:{item.line} {item.text}"
            for item in report.test_plan
        )
    else:
        lines.append("- None found.")

    lines.extend(["", "Quality Checks:"])
    if report.quality_checks:
        lines.extend(
            _render_trace_checklist_item(item)
            for item in report.quality_checks
        )
    else:
        lines.append("- None found.")

    lines.extend(["", "Gaps:"])
    if report.gaps:
        lines.extend(
            f"- {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in report.gaps
        )
    else:
        lines.append("- None.")

    lines.extend(["", "Blocking Checks:"])
    if report.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in report.blocking_checks
        )
    else:
        lines.append("- None.")

    lines.extend(["", "Key Commands:"])
    lines.extend(f"- {command}" for command in report.recommended_commands)

    return "\n".join(lines) + "\n"


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
    )


def render_pull_request_json(draft: PullRequestDraft) -> str:
    return json.dumps(draft.as_dict(), indent=2, sort_keys=True) + "\n"


def render_pull_request_text(draft: PullRequestDraft) -> str:
    return f"Title: {draft.title}\n\n{draft.body}"


def _recommended_sync_plan_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature sync-plan {slug} . --json",
        f"specspine feature issue {slug} . --json",
        f"specspine feature task-issues {slug} . --json",
        f"specspine feature pr {slug} . --json",
        f"specspine feature ready {slug} . --json",
        "specspine adapters lifecycle . --json",
        "specspine validate . --fusion --features",
    )


def _github_label_args(labels: tuple[str, ...]) -> tuple[str, ...]:
    args: list[str] = []
    for label in labels:
        args.extend(("--label", label))
    return tuple(args)


def _sync_body_source(slug: str, filename: str) -> str:
    return str(Path(".specspine") / "sync-plan" / slug / filename)


def _feature_issue_labels(slug: str, status: str, priority: str) -> tuple[str, ...]:
    return (
        "specspine",
        f"feature:{slug}",
        f"status:{status}",
        f"priority:{priority}",
    )


def _task_issue_labels(slug: str, status: str) -> tuple[str, ...]:
    return (
        "specspine",
        f"feature:{slug}",
        "task",
        f"status:{status}",
    )


def _pull_request_labels(slug: str, status: str) -> tuple[str, ...]:
    return (
        "specspine",
        f"feature:{slug}",
        f"status:{status}",
    )


def _sync_command(
    *,
    command_id: str,
    kind: str,
    description: str,
    argv: tuple[str, ...],
    body_source: str,
    body: str,
) -> FeatureSyncPlanCommand:
    return FeatureSyncPlanCommand(
        id=command_id,
        kind=kind,
        description=description,
        argv=argv,
        body_source=body_source,
        body=body,
    )


def _sync_plan_notes(metadata: FeatureMetadata) -> tuple[str, ...]:
    notes = [
        (
            "SpecSpine generated this as a local review plan only; it did not "
            "execute gh, call GitHub APIs, read tokens, or access the network."
        ),
        (
            "Every command would create remote GitHub resources if a human runs "
            "it, so review the argv list, labels, and draft body first."
        ),
        (
            "A human must authenticate GitHub CLI before running these commands; "
            "adding issues or pull requests to Projects may require the gh "
            "project scope."
        ),
        (
            "Do not rely on gh pr create dry-run as an automatic safety mode; "
            "GitHub CLI documentation says dry-run may still push git changes."
        ),
        (
            f"Priority is represented as the compatible label "
            f"priority:{metadata.priority}; this plan does not call GitHub Issue "
            "Fields APIs."
        ),
    ]
    if metadata.owner == "unassigned":
        notes.append(
            "Owner is unassigned; local owner metadata is not automatically "
            "mapped to --assignee."
        )
    else:
        notes.append(
            f"Owner '{metadata.owner}' is local SpecSpine metadata and is not "
            "automatically mapped to --assignee."
        )
    return tuple(notes)


def build_feature_sync_plan(root: Path, slug: str) -> FeatureSyncPlan:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    status_report = get_feature_status(resolved_root, slug)
    has_native_files = any(file["exists"] for file in status_report.files.values())
    if not has_native_files:
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(feature_bundle_paths(resolved_root, slug).values()),
        )

    metadata = read_feature_metadata(resolved_root, slug)
    issue_draft = build_issue_draft(resolved_root, slug)
    task_issues = build_feature_task_issues_report(resolved_root, slug)
    pull_request = build_pull_request_draft(resolved_root, slug)
    handoff = build_feature_handoff_report(resolved_root, slug)

    commands: list[FeatureSyncPlanCommand] = []

    feature_issue_body_source = _sync_body_source(slug, "feature-issue.md")
    feature_issue_labels = _feature_issue_labels(
        slug,
        handoff.status,
        metadata.priority,
    )
    commands.append(
        _sync_command(
            command_id="github.issue.feature",
            kind="issue",
            description="Create one GitHub issue for the feature-level specification.",
            argv=(
                "gh",
                "issue",
                "create",
                "--title",
                issue_draft.title,
                "--body-file",
                feature_issue_body_source,
                *_github_label_args(feature_issue_labels),
            ),
            body_source=feature_issue_body_source,
            body=issue_draft.body,
        )
    )

    for task_issue in task_issues.issues:
        body_source = _sync_body_source(
            slug,
            f"task-issues/{task_issue.task_id}.md",
        )
        commands.append(
            _sync_command(
                command_id=f"github.task_issue.{task_issue.task_id}",
                kind="task-issue",
                description=(
                    f"Create one GitHub issue for execution task "
                    f"{task_issue.task_id}."
                ),
                argv=(
                    "gh",
                    "issue",
                    "create",
                    "--title",
                    task_issue.title,
                    "--body-file",
                    body_source,
                    *_github_label_args(
                        _task_issue_labels(slug, task_issues.status)
                    ),
                ),
                body_source=body_source,
                body=task_issue.body,
            )
        )

    pull_request_body_source = _sync_body_source(slug, "pull-request.md")
    commands.append(
        _sync_command(
            command_id="github.pull_request",
            kind="pull-request",
            description="Create a draft GitHub Pull Request from local feature evidence.",
            argv=(
                "gh",
                "pr",
                "create",
                "--title",
                pull_request.title,
                "--body-file",
                pull_request_body_source,
                "--draft",
                *_github_label_args(_pull_request_labels(slug, pull_request.status)),
            ),
            body_source=pull_request_body_source,
            body=pull_request.body,
        )
    )

    source_files = tuple(
        source["path"]
        for source in handoff.sources.values()
        if bool(source["exists"])
    )

    return FeatureSyncPlan(
        feature_id=slug,
        status=handoff.status,
        ready=handoff.ready,
        source_files=source_files,
        missing_files=handoff.missing_files,
        gaps=handoff.gaps,
        blocking_checks=handoff.blocking_checks,
        metadata=metadata,
        commands=tuple(commands),
        notes=_sync_plan_notes(metadata),
        recommended_commands=_recommended_sync_plan_commands(slug),
    )


def render_feature_sync_plan_json(plan: FeatureSyncPlan) -> str:
    return json.dumps(plan.as_dict(), indent=2, sort_keys=True) + "\n"


def _path_as_posix(path: Path) -> str:
    return path.as_posix()


def _sync_artifact_relative_path(command: FeatureSyncPlanCommand) -> Path:
    body_source = Path(command.body_source)
    if command.kind == "issue":
        return Path("feature-issue.md")
    if command.kind == "pull-request":
        return Path("pull-request.md")
    if command.kind == "task-issue":
        return Path("task-issues") / body_source.name
    return Path(body_source.name)


def _argv_with_local_body_file(
    argv: tuple[str, ...],
    body_file: str,
) -> tuple[str, ...]:
    updated = list(argv)
    for index, arg in enumerate(updated[:-1]):
        if arg == "--body-file":
            updated[index + 1] = body_file
            return tuple(updated)
    return (*argv, "--body-file", body_file)


def _sync_plan_artifact_manifest(
    plan: FeatureSyncPlan,
) -> tuple[dict[str, object], dict[str, Path]]:
    payload = plan.as_dict()
    artifact_paths: dict[str, Path] = {}
    commands: list[dict[str, object]] = []
    task_issue_artifacts: list[dict[str, str]] = []

    for command in plan.commands:
        relative_path = _sync_artifact_relative_path(command)
        artifact_paths[command.id] = relative_path
        artifact_path = _path_as_posix(relative_path)
        command_payload = command.as_dict()
        command_payload["artifact_path"] = artifact_path
        command_payload["body_file"] = artifact_path
        commands.append(command_payload)

        if command.kind == "task-issue":
            task_issue_artifacts.append(
                {
                    "command_id": command.id,
                    "path": artifact_path,
                    "task_id": command.id.rsplit(".", 1)[-1],
                }
            )

    payload["commands"] = commands
    payload["artifact_version"] = 1
    payload["artifact_root"] = "."
    payload["artifacts"] = {
        "commands": "commands.sh",
        "feature_issue": "feature-issue.md",
        "manifest": "manifest.json",
        "pull_request": "pull-request.md",
        "task_issues": task_issue_artifacts,
    }
    return payload, artifact_paths


def _render_sync_plan_commands_sh(
    plan: FeatureSyncPlan,
    artifact_paths: dict[str, Path],
) -> str:
    lines = [
        "# SpecSpine GitHub sync plan artifacts",
        "# review-only / do not run blindly",
        "# SpecSpine did not execute gh, read tokens, call GitHub APIs, or use the network.",
        "# Review manifest.json and the body files before manually running any command.",
        "",
    ]

    for command in plan.commands:
        body_file = _path_as_posix(artifact_paths[command.id])
        argv = _argv_with_local_body_file(command.argv, body_file)
        lines.extend(
            [
                f"# {command.id}: {command.description}",
                shlex.join(argv),
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def write_feature_sync_plan_artifacts(
    plan: FeatureSyncPlan,
    output_dir: Path,
    *,
    force: bool = False,
) -> FeatureSyncPlanArtifacts:
    resolved_output_dir = output_dir.expanduser().resolve()
    if resolved_output_dir.exists() and not resolved_output_dir.is_dir():
        raise NotADirectoryError(f"Output path is not a directory: {resolved_output_dir}")

    manifest, artifact_paths = _sync_plan_artifact_manifest(plan)
    body_targets = tuple(
        resolved_output_dir / relative_path
        for relative_path in artifact_paths.values()
    )
    manifest_path = resolved_output_dir / "manifest.json"
    commands_path = resolved_output_dir / "commands.sh"
    write_targets = (*body_targets, manifest_path, commands_path)

    parent_conflicts = tuple(
        path.parent
        for path in write_targets
        if path.parent.exists() and not path.parent.is_dir()
    )
    if parent_conflicts:
        first_conflict = parent_conflicts[0]
        raise NotADirectoryError(f"Output artifact parent is not a directory: {first_conflict}")

    existing_paths = tuple(path for path in write_targets if path.exists())
    if existing_paths and not force:
        raise FeatureSyncPlanArtifactExistsError(
            output_dir=resolved_output_dir,
            existing_paths=existing_paths,
        )

    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    for command in plan.commands:
        target = resolved_output_dir / artifact_paths[command.id]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(command.body, encoding="utf-8")

    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    commands_path.write_text(
        _render_sync_plan_commands_sh(plan, artifact_paths),
        encoding="utf-8",
    )

    return FeatureSyncPlanArtifacts(
        output_dir=resolved_output_dir,
        manifest_path=manifest_path,
        commands_path=commands_path,
        body_paths=body_targets,
        written_paths=write_targets,
        manifest=manifest,
    )


def render_feature_sync_plan_text(plan: FeatureSyncPlan) -> str:
    summary = plan.summary
    lines = [
        f"# GitHub Sync Plan: {plan.feature_id}",
        "",
        "## Summary",
        "",
        f"- Status: {plan.status}",
        f"- Ready: {'yes' if plan.ready else 'no'}",
        (
            "- Commands: "
            f"total={summary['commands_total']} "
            f"feature_issues={summary['issue_commands']} "
            f"task_issues={summary['task_issue_commands']} "
            f"pull_requests={summary['pull_request_commands']}"
        ),
        f"- Notes: {summary['notes_total']}",
        "",
        "## Metadata",
        "",
        f"- Priority: {plan.metadata.priority}",
        f"- Owner: {plan.metadata.owner}",
        "",
        "## Notes",
        "",
    ]
    lines.extend(f"- {note}" for note in plan.notes)

    lines.extend(["", "## Sources", ""])
    if plan.source_files:
        lines.extend(f"- [ok] {relative_path}" for relative_path in plan.source_files)
    else:
        lines.append("- None.")

    lines.extend(["", "## Missing Files", ""])
    if plan.missing_files:
        lines.extend(f"- [missing] {relative_path}" for relative_path in plan.missing_files)
    else:
        lines.append("- None.")

    lines.extend(["", "## Gaps", ""])
    if plan.gaps:
        lines.extend(
            f"- {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in plan.gaps
        )
    else:
        lines.append("- None.")

    lines.extend(["", "## Blocking Checks", ""])
    if plan.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in plan.blocking_checks
        )
    else:
        lines.append("- None.")

    lines.extend(["", "## Commands", ""])
    for command in plan.commands:
        lines.extend(
            [
                f"### {command.id}",
                "",
                f"- Kind: {command.kind}",
                f"- Description: {command.description}",
                f"- Body source: {command.body_source}",
                f"- Creates remote: {'yes' if command.creates_remote else 'no'}",
                f"- Requires token: {'yes' if command.requires_token else 'no'}",
                f"- Requires network: {'yes' if command.requires_network else 'no'}",
                (
                    "- Safe to auto-run: "
                    f"{'yes' if command.safe_to_auto_run else 'no'}"
                ),
                f"- Command: `{shlex.join(command.argv)}`",
                "",
            ]
        )

    lines.extend(["## Recommended Local Commands", ""])
    lines.extend(f"- `{command}`" for command in plan.recommended_commands)

    return "\n".join(lines).rstrip() + "\n"


def render_feature_tasks_json(report: FeatureTasksReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_feature_tasks_text(report: FeatureTasksReport) -> str:
    summary = report.summary
    lines = [
        f"Feature tasks: {report.feature_id}",
        f"Status: {report.status}",
        f"Source: {report.source_file}",
        (
            "Summary: "
            f"total={summary['total']} "
            f"done={summary['done']} "
            f"open={summary['open']}"
        ),
        "",
        "Tasks:",
    ]

    if report.tasks:
        for task in report.tasks:
            marker = "x" if task.done else " "
            lines.append(
                f"- [{marker}] {task.id} {task.source_file}:{task.line} {task.text}"
            )
    elif report.source_missing:
        lines.append(f"No tasks found because source file is missing: {report.source_file}")
    else:
        lines.append(f"No checklist tasks found in {report.source_file}.")

    if report.missing_files:
        lines.extend(["", "Missing feature files:"])
        lines.extend(f"- {relative_path}" for relative_path in report.missing_files)

    return "\n".join(lines) + "\n"


def render_issue_json(draft: IssueDraft) -> str:
    return json.dumps(draft.as_dict(), indent=2, sort_keys=True) + "\n"


def render_issue_text(draft: IssueDraft) -> str:
    return f"Title: {draft.title}\n\n{draft.body}"

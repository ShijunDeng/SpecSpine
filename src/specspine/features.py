from __future__ import annotations

import json
import re
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
FEATURE_DIRECTORIES = {
    kind: str(Path(pattern.format(slug="__feature__")).parent)
    for kind, pattern in FEATURE_FILE_PATHS.items()
}


class InvalidFeatureSlug(ValueError):
    """Raised when a feature slug cannot be used as a feature id."""


class InvalidFeatureStatus(ValueError):
    """Raised when a feature lifecycle status is not supported."""


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
        return {
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
class FeatureStatusReport:
    feature_id: str
    status: str | None
    consistent: bool
    files: dict[str, dict[str, object]]
    missing_files: tuple[str, ...]
    updated_files: tuple[str, ...] = ()

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

            ## Why

            {resolved_why}

            ## Users

            - TODO: Identify the users or roles that benefit from this feature.

            ## Scope

            - TODO: Describe the behavior, workflows, and boundaries included in this feature.

            ## Non-Goals

            - TODO: Record what this feature intentionally will not address.

            ## Acceptance Criteria

            - [ ] TODO: Define the observable outcomes required before this feature is complete.
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
        """,
        FEATURE_FILE_PATHS["quality"].format(slug=slug): f"""
            # {resolved_title} Quality

            Feature ID: {slug}
            Status: proposed
            Why: {resolved_why}

            ## Required Checks

            - [ ] TODO: Acceptance criteria are reviewed against the final implementation.
            - [ ] TODO: Tests cover the changed behavior.
            - [ ] TODO: Documentation or release notes are updated when needed.

            ## Test Plan

            - TODO: Describe unit, integration, manual, or exploratory checks.

            ## Review Notes

            - TODO: Capture review findings, decisions, and follow-up work.

            ## Release Readiness

            - [ ] TODO: Confirm the feature is ready to ship or explicitly record blockers.
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


def set_feature_status(root: Path, slug: str, status: str) -> FeatureStatusReport:
    slug = validate_feature_slug(slug)
    status = validate_feature_status(status)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)

    existing_paths = [path for path in paths.values() if path.exists()]
    if not existing_paths:
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(paths.values()),
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


def build_feature_ready_report(root: Path, slug: str) -> FeatureReadyReport:
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
    if quality_path.exists():
        quality_content = quality_path.read_text(encoding="utf-8")
        release_readiness = parse_release_readiness(
            quality_content,
            source_file=relative_paths["quality"],
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

    ready = all(check.status == "pass" for check in checks)
    return FeatureReadyReport(
        feature_id=slug,
        ready=ready,
        status=status,
        checks=tuple(checks),
        missing_files=missing_files,
        gaps=gaps,
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
        f"specspine feature trace {slug} . --json",
        f"specspine feature ready {slug} . --json",
        "specspine validate . --features",
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


def build_feature_handoff_report(root: Path, slug: str) -> FeatureHandoffReport:
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

    ready_report = build_feature_ready_report(resolved_root, slug)

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

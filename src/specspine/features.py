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

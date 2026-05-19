from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .dependency import build_dependency_graph
from .features import (
    FEATURE_FILE_PATHS,
    InvalidFeatureSlug,
    build_feature_trace_report,
    build_feature_tests_report,
    feature_bundle_paths,
    list_feature_bundles,
    validate_feature_slug,
)

AC_ID_RE = re.compile(r"(AC\d{3})")
TASK_ID_RE = re.compile(r"(T\d{3})")
COV_ID_RE = re.compile(r"(COV\d{3})")
QUALITY_CHECK_RE = re.compile(r"(QC\d{3})")
FEATURE_ID_RE = re.compile(r"Feature\s+ID:\s*([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE)
DEPENDENCY_PATTERNS = [
    re.compile(r"depends\s+on\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"after\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"blocked\s+by\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"requires\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
]


@dataclass(frozen=True)
class DiffFileHunk:
    path: str
    diff_hunks: list[str]
    added_lines: int
    removed_lines: int
    modified_lines: int

    def as_dict(self) -> dict[str, object]:
        return {
            "added_lines": self.added_lines,
            "diff_hunks": self.diff_hunks,
            "modified_lines": self.modified_lines,
            "path": self.path,
            "removed_lines": self.removed_lines,
        }


@dataclass(frozen=True)
class DiffResult:
    slug: str
    files: list[DiffFileHunk]

    @property
    def summary(self) -> dict[str, int]:
        total_added = sum(f.added_lines for f in self.files)
        total_removed = sum(f.removed_lines for f in self.files)
        total_modified = sum(f.modified_lines for f in self.files)
        return {
            "files_changed": len(self.files),
            "total_added": total_added,
            "total_modified": total_modified,
            "total_removed": total_removed,
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "files": [f.as_dict() for f in self.files],
            "slug": self.slug,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class ClassifiedChange:
    change_id: str
    change_type: str
    category: str
    file: str
    line: int
    before: str | None
    after: str | None

    def as_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "category": self.category,
            "change_id": self.change_id,
            "change_type": self.change_type,
            "file": self.file,
            "line": self.line,
        }
        if self.before is not None:
            result["before"] = self.before
        if self.after is not None:
            result["after"] = self.after
        return result


@dataclass(frozen=True)
class ClassificationResult:
    slug: str
    changes: list[ClassifiedChange]

    @property
    def summary(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for change in self.changes:
            key = f"{change.category}_{change.change_type}"
            counts[key] = counts.get(key, 0) + 1
        return counts

    def as_dict(self) -> dict[str, object]:
        return {
            "changes": [c.as_dict() for c in self.changes],
            "slug": self.slug,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class ImpactEntry:
    change_id: str
    affected_type: str
    affected_id: str
    severity: str

    def as_dict(self) -> dict[str, str]:
        return {
            "affected_id": self.affected_id,
            "affected_type": self.affected_type,
            "change_id": self.change_id,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class ImpactResult:
    slug: str
    impacts: list[ImpactEntry]

    @property
    def summary(self) -> dict[str, int]:
        return {
            "breaking": sum(1 for i in self.impacts if i.severity == "breaking"),
            "info": sum(1 for i in self.impacts if i.severity == "info"),
            "total": len(self.impacts),
            "warning": sum(1 for i in self.impacts if i.severity == "warning"),
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "impacts": [i.as_dict() for i in self.impacts],
            "slug": self.slug,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class RemediationAction:
    action_id: str
    description: str
    priority: int
    target_file: str

    def as_dict(self) -> dict[str, object]:
        return {
            "action_id": self.action_id,
            "description": self.description,
            "priority": self.priority,
            "target_file": self.target_file,
        }


@dataclass(frozen=True)
class EvolutionEntry:
    commit_hash: str
    date: str
    author: str
    message: str
    change_count: int
    categories: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "author": self.author,
            "categories": self.categories,
            "change_count": self.change_count,
            "commit_hash": self.commit_hash,
            "date": self.date,
            "message": self.message,
        }


class GitDiffError(Exception):
    pass


class InvalidGitBaseError(ValueError):
    pass


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=30,
    )


def _get_peer_files(slug: str, root: Path) -> dict[str, Path]:
    paths = feature_bundle_paths(root, slug)
    return {
        kind: path
        for kind, path in paths.items()
        if path.exists()
    }


def _parse_diff_hunks(raw_diff: str) -> list[str]:
    hunks: list[str] = []
    current_hunk: list[str] = []
    for line in raw_diff.splitlines():
        if line.startswith("@@"):
            if current_hunk:
                hunks.append("\n".join(current_hunk))
            current_hunk = [line]
        else:
            current_hunk.append(line)
    if current_hunk:
        hunks.append("\n".join(current_hunk))
    return hunks


def _count_lines_in_hunks(hunks: list[str]) -> tuple[int, int]:
    added = 0
    removed = 0
    for hunk in hunks:
        for line in hunk.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                added += 1
            elif line.startswith("-") and not line.startswith("---"):
                removed += 1
    return added, removed


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def get_git_diff(
    slug: str,
    root: Path,
    base: str | None = None,
    unstaged: bool = False,
) -> DiffResult:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    peer_files = _get_peer_files(slug, resolved_root)

    if not peer_files:
        return DiffResult(slug=slug, files=[])

    file_results: list[DiffFileHunk] = []
    for kind, file_path in sorted(peer_files.items()):
        rel_path = _relative_path(file_path, resolved_root)
        git_args: list[str] = ["diff"]
        if base is not None:
            base_result = _run_git(["rev-parse", "--verify", base], resolved_root)
            if base_result.returncode != 0:
                raise InvalidGitBaseError(
                    f"Invalid git base reference: {base}"
                )
            git_args.append(base)
        if unstaged:
            git_args.append("--")
        git_args.append(rel_path)

        result = _run_git(git_args, resolved_root)
        if result.returncode == 0 and result.stdout.strip():
            hunks = _parse_diff_hunks(result.stdout)
            added, removed = _count_lines_in_hunks(hunks)
            file_results.append(
                DiffFileHunk(
                    path=rel_path,
                    diff_hunks=hunks,
                    added_lines=added,
                    removed_lines=removed,
                    modified_lines=added + removed,
                )
            )
        else:
            file_results.append(
                DiffFileHunk(
                    path=rel_path,
                    diff_hunks=[],
                    added_lines=0,
                    removed_lines=0,
                    modified_lines=0,
                )
            )

    return DiffResult(slug=slug, files=file_results)


def _extract_ac_ids(text: str) -> list[str]:
    return AC_ID_RE.findall(text)


def _extract_task_ids(text: str) -> list[str]:
    return TASK_ID_RE.findall(text)


def _extract_feature_refs(text: str) -> list[str]:
    refs: list[str] = []
    for pattern in DEPENDENCY_PATTERNS:
        refs.extend(pattern.findall(text))
    refs.extend(FEATURE_ID_RE.findall(text))
    return sorted(set(refs))


def _find_line_number(content: str, search_text: str) -> int:
    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        if search_text.strip() in line:
            return i
    return 0


def _parse_section_ids(content: str, pattern: re.Pattern) -> list[tuple[str, int]]:
    results: list[tuple[str, int]] = []
    for i, line in enumerate(content.splitlines(), 1):
        for match in pattern.finditer(line):
            results.append((match.group(1), i))
    return results


def _build_versioned_content(
    root: Path,
    slug: str,
    base: str | None = None,
) -> dict[str, str | None]:
    contents: dict[str, str | None] = {}
    for kind in FEATURE_FILE_PATHS:
        rel_path = FEATURE_FILE_PATHS[kind].format(slug=slug)
        file_path = root / rel_path
        if not file_path.exists():
            contents[kind] = None
            continue

        if base is None:
            contents[kind] = file_path.read_text(encoding="utf-8")
        else:
            result = _run_git(
                ["show", f"{base}:{rel_path}"],
                root,
            )
            if result.returncode == 0:
                contents[kind] = result.stdout
            else:
                contents[kind] = None
    return contents


def classify_changes(
    diff_result: DiffResult,
    slug: str,
    root: Path,
) -> ClassificationResult:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()

    base_contents = _build_versioned_content(resolved_root, slug)
    current_contents: dict[str, str | None] = {}
    for kind in FEATURE_FILE_PATHS:
        rel_path = FEATURE_FILE_PATHS[kind].format(slug=slug)
        file_path = resolved_root / rel_path
        if file_path.exists():
            current_contents[kind] = file_path.read_text(encoding="utf-8")
        else:
            current_contents[kind] = None

    changes: list[ClassifiedChange] = []
    change_counter = 0

    for kind in ("spec", "execution", "quality"):
        rel_path = FEATURE_FILE_PATHS[kind].format(slug=slug)
        before = base_contents.get(kind)
        after = current_contents.get(kind)

        if before is None and after is None:
            continue

        if before is None and after is not None:
            ac_ids = _parse_section_ids(after, AC_ID_RE)
            for ac_id, line in ac_ids:
                change_counter += 1
                changes.append(
                    ClassifiedChange(
                        change_id=f"CHG{change_counter:03d}",
                        change_type="added",
                        category="ac",
                        file=rel_path,
                        line=line,
                        before=None,
                        after=ac_id,
                    )
                )
            task_ids = _parse_section_ids(after, TASK_ID_RE)
            for task_id, line in task_ids:
                change_counter += 1
                changes.append(
                    ClassifiedChange(
                        change_id=f"CHG{change_counter:03d}",
                        change_type="added",
                        category="task",
                        file=rel_path,
                        line=line,
                        before=None,
                        after=task_id,
                    )
                )
            continue

        if before is not None and after is None:
            ac_ids = _parse_section_ids(before, AC_ID_RE)
            for ac_id, line in ac_ids:
                change_counter += 1
                changes.append(
                    ClassifiedChange(
                        change_id=f"CHG{change_counter:03d}",
                        change_type="removed",
                        category="ac",
                        file=rel_path,
                        line=line,
                        before=ac_id,
                        after=None,
                    )
                )
            task_ids = _parse_section_ids(before, TASK_ID_RE)
            for task_id, line in task_ids:
                change_counter += 1
                changes.append(
                    ClassifiedChange(
                        change_id=f"CHG{change_counter:03d}",
                        change_type="removed",
                        category="task",
                        file=rel_path,
                        line=line,
                        before=task_id,
                        after=None,
                    )
                )
            continue

        before_ac = set(_extract_ac_ids(before or ""))
        after_ac = set(_extract_ac_ids(after or ""))
        before_tasks = set(_extract_task_ids(before or ""))
        after_tasks = set(_extract_task_ids(after or ""))

        for ac_id in sorted(after_ac - before_ac):
            change_counter += 1
            line = _find_line_number(after or "", ac_id)
            changes.append(
                ClassifiedChange(
                    change_id=f"CHG{change_counter:03d}",
                    change_type="added",
                    category="ac",
                    file=rel_path,
                    line=line,
                    before=None,
                    after=ac_id,
                )
            )

        for ac_id in sorted(before_ac - after_ac):
            change_counter += 1
            line = _find_line_number(before or "", ac_id)
            changes.append(
                ClassifiedChange(
                    change_id=f"CHG{change_counter:03d}",
                    change_type="removed",
                    category="ac",
                    file=rel_path,
                    line=line,
                    before=ac_id,
                    after=None,
                )
            )

        for task_id in sorted(after_tasks - before_tasks):
            change_counter += 1
            line = _find_line_number(after or "", task_id)
            changes.append(
                ClassifiedChange(
                    change_id=f"CHG{change_counter:03d}",
                    change_type="added",
                    category="task",
                    file=rel_path,
                    line=line,
                    before=None,
                    after=task_id,
                )
            )

        for task_id in sorted(before_tasks - after_tasks):
            change_counter += 1
            line = _find_line_number(before or "", task_id)
            changes.append(
                ClassifiedChange(
                    change_id=f"CHG{change_counter:03d}",
                    change_type="removed",
                    category="task",
                    file=rel_path,
                    line=line,
                    before=task_id,
                    after=None,
                )
            )

        if before != after:
            for file_hunk in diff_result.files:
                if file_hunk.path == rel_path and file_hunk.diff_hunks:
                    change_counter += 1
                    changes.append(
                        ClassifiedChange(
                            change_id=f"CHG{change_counter:03d}",
                            change_type="modified",
                            category=kind,
                            file=rel_path,
                            line=0,
                            before=f"{len((before or '').splitlines())} lines",
                            after=f"{len((after or '').splitlines())} lines",
                        )
                    )
                    break

    if base_contents.get("spec") != current_contents.get("spec"):
        before_meta = _extract_metadata(base_contents.get("spec") or "")
        after_meta = _extract_metadata(current_contents.get("spec") or "")
        if before_meta != after_meta:
            change_counter += 1
            changes.append(
                ClassifiedChange(
                    change_id=f"CHG{change_counter:03d}",
                    change_type="modified",
                    category="metadata",
                    file=FEATURE_FILE_PATHS["spec"].format(slug=slug),
                    line=0,
                    before=str(before_meta),
                    after=str(after_meta),
                )
            )

    return ClassificationResult(slug=slug, changes=changes)


def _extract_metadata(content: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    keys = {"Priority", "Owner", "Milestone", "Target Release", "Project", "Effort", "Status"}
    for line in content.splitlines():
        stripped = line.strip()
        if ":" in stripped and not stripped.startswith("#"):
            key, _, value = stripped.partition(":")
            key = key.strip()
            if key in keys:
                metadata[key] = value.strip()
    return metadata


def _find_downstream_references(
    slug: str,
    root: Path,
) -> dict[str, list[dict[str, str]]]:
    resolved_root = root.expanduser().resolve()
    all_features = list_feature_bundles(resolved_root)
    references: dict[str, list[dict[str, str]]] = {
        "tasks": [],
        "coverage": [],
        "dependent_features": [],
    }

    for feature in all_features:
        feature_slug = feature["slug"]
        if feature_slug == slug:
            continue
        try:
            trace = build_feature_trace_report(resolved_root, feature_slug)
            for ac in trace.acceptance_criteria:
                if slug.lower() in ac.text.lower():
                    references["tasks"].append({
                        "feature_id": feature_slug,
                        "item_id": ac.id,
                        "text": ac.text,
                    })
        except (InvalidFeatureSlug, OSError):
            continue

        try:
            tests_report = build_feature_tests_report(resolved_root, feature_slug)
            for coverage_link in tests_report.test_coverage:
                if slug.lower() in coverage_link.text.lower():
                    references["coverage"].append({
                        "feature_id": feature_slug,
                        "coverage_id": coverage_link.id,
                        "text": coverage_link.text,
                    })
        except (InvalidFeatureSlug, OSError):
            continue

        for file_kind in FEATURE_FILE_PATHS:
            file_path = resolved_root / FEATURE_FILE_PATHS[file_kind].format(slug=feature_slug)
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                feature_refs = _extract_feature_refs(content)
                if slug in feature_refs:
                    references["dependent_features"].append({
                        "feature_id": feature_slug,
                        "reference_type": file_kind,
                    })

    return references


def resolve_impact(
    changes: list[ClassifiedChange],
    slug: str,
    root: Path,
) -> ImpactResult:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()

    downstream = _find_downstream_references(slug, resolved_root)
    impacts: list[ImpactEntry] = []
    impact_counter = 0

    change_has_refs: dict[str, list[str]] = {}
    for ref_type, refs in downstream.items():
        for ref in refs:
            feature_id = ref.get("feature_id", "")
            for change in changes:
                if change.change_type in ("removed", "modified"):
                    if feature_id not in change_has_refs:
                        change_has_refs[change.change_id] = []
                    if feature_id not in change_has_refs[change.change_id]:
                        change_has_refs[change.change_id].append(feature_id)

    for change in changes:
        if change.change_type == "removed" and change.category == "ac":
            refs = change_has_refs.get(change.change_id, [])
            for ref_feature in refs:
                impact_counter += 1
                impacts.append(
                    ImpactEntry(
                        change_id=change.change_id,
                        affected_type="feature",
                        affected_id=ref_feature,
                        severity="breaking",
                    )
                )
            coverage_refs = downstream.get("coverage", [])
            for cov_ref in coverage_refs:
                if cov_ref.get("feature_id") in [r.get("feature_id") for r in refs]:
                    impact_counter += 1
                    impacts.append(
                        ImpactEntry(
                            change_id=change.change_id,
                            affected_type="coverage",
                            affected_id=cov_ref.get("coverage_id", "unknown"),
                            severity="breaking",
                        )
                    )

            impact_counter += 1
            impacts.append(
                ImpactEntry(
                    change_id=change.change_id,
                    affected_type="ac",
                    affected_id=change.after or change.before or "unknown",
                    severity="warning",
                )
            )

        elif change.change_type == "modified" and change.category == "ac":
            refs = change_has_refs.get(change.change_id, [])
            for ref_feature in refs:
                impact_counter += 1
                impacts.append(
                    ImpactEntry(
                        change_id=change.change_id,
                        affected_type="feature",
                        affected_id=ref_feature,
                        severity="warning",
                    )
                )
            if not refs:
                impact_counter += 1
                impacts.append(
                    ImpactEntry(
                        change_id=change.change_id,
                        affected_type="ac",
                        affected_id=change.after or change.before or "unknown",
                        severity="info",
                    )
                )

        elif change.change_type == "removed" and change.category == "task":
            refs = change_has_refs.get(change.change_id, [])
            for ref_feature in refs:
                impact_counter += 1
                impacts.append(
                    ImpactEntry(
                        change_id=change.change_id,
                        affected_type="feature",
                        affected_id=ref_feature,
                        severity="breaking",
                    )
                )
            impact_counter += 1
            impacts.append(
                ImpactEntry(
                    change_id=change.change_id,
                    affected_type="task",
                    affected_id=change.before or "unknown",
                    severity="warning",
                )
            )

        elif change.change_type == "added":
            impact_counter += 1
            impacts.append(
                ImpactEntry(
                    change_id=change.change_id,
                    affected_type=change.category,
                    affected_id=change.after or "unknown",
                    severity="info",
                )
            )

        elif change.change_type == "modified" and change.category == "metadata":
            impact_counter += 1
            impacts.append(
                ImpactEntry(
                    change_id=change.change_id,
                    affected_type="metadata",
                    affected_id=slug,
                    severity="info",
                )
            )

        elif change.change_type == "modified" and change.category in ("spec", "execution", "quality"):
            refs = change_has_refs.get(change.change_id, [])
            if refs:
                for ref_feature in refs:
                    impact_counter += 1
                    impacts.append(
                        ImpactEntry(
                            change_id=change.change_id,
                            affected_type="feature",
                            affected_id=ref_feature,
                            severity="warning",
                        )
                    )
            else:
                impact_counter += 1
                impacts.append(
                    ImpactEntry(
                        change_id=change.change_id,
                        affected_type=change.category,
                        affected_id=slug,
                        severity="info",
                    )
                )

    return ImpactResult(slug=slug, impacts=impacts)


def calculate_risk_level(change: ClassifiedChange, impact: ImpactEntry) -> str:
    if change.change_type == "removed" and change.category == "ac":
        if impact.severity in ("breaking", "warning"):
            return "breaking"
    if change.change_type == "modified" and change.category == "ac":
        if impact.severity == "warning":
            return "warning"
    if change.change_type == "removed" and change.category == "task":
        if impact.severity == "breaking":
            return "breaking"
        return "warning"
    if change.change_type == "modified" and impact.severity == "warning":
        return "warning"
    return "info"


def generate_remediation_plan(
    changes: list[ClassifiedChange],
    impacts: list[ImpactEntry],
) -> list[RemediationAction]:
    actions: list[RemediationAction] = []
    action_counter = 0

    impact_by_change: dict[str, list[ImpactEntry]] = {}
    for impact in impacts:
        if impact.severity == "info":
            continue
        if impact.change_id not in impact_by_change:
            impact_by_change[impact.change_id] = []
        impact_by_change[impact.change_id].append(impact)

    for change in changes:
        relevant_impacts = impact_by_change.get(change.change_id, [])
        if not relevant_impacts:
            continue

        if change.change_type == "removed" and change.category == "ac":
            ac_id = change.before or "unknown"
            action_counter += 1
            actions.append(
                RemediationAction(
                    action_id=f"ACT{action_counter:03d}",
                    description=f"Update downstream features referencing removed AC {ac_id}",
                    priority=1,
                    target_file=change.file,
                )
            )
            for impact in relevant_impacts:
                if impact.affected_type == "coverage":
                    action_counter += 1
                    actions.append(
                        RemediationAction(
                            action_id=f"ACT{action_counter:03d}",
                            description=f"Remove coverage link {impact.affected_id} from quality file",
                            priority=2,
                            target_file=FEATURE_FILE_PATHS["quality"].format(slug=change.file.split("/")[-1].replace(".md", "")),
                        )
                    )
                elif impact.affected_type == "feature":
                    action_counter += 1
                    actions.append(
                        RemediationAction(
                            action_id=f"ACT{action_counter:03d}",
                            description=f"Re-validate feature {impact.affected_id} that depends on removed AC",
                            priority=1,
                            target_file=FEATURE_FILE_PATHS["spec"].format(slug=impact.affected_id),
                        )
                    )

        elif change.change_type == "modified" and change.category == "ac":
            ac_id = change.after or change.before or "unknown"
            for impact in relevant_impacts:
                if impact.affected_type == "feature":
                    action_counter += 1
                    actions.append(
                        RemediationAction(
                            action_id=f"ACT{action_counter:03d}",
                            description=f"Re-validate feature {impact.affected_id} for modified AC {ac_id}",
                            priority=2,
                            target_file=FEATURE_FILE_PATHS["quality"].format(slug=impact.affected_id),
                        )
                    )

        elif change.change_type == "removed" and change.category == "task":
            task_id = change.before or "unknown"
            action_counter += 1
            actions.append(
                RemediationAction(
                    action_id=f"ACT{action_counter:03d}",
                    description=f"Update execution file for removed task {task_id}",
                    priority=1,
                    target_file=FEATURE_FILE_PATHS["execution"].format(
                        slug=change.file.split("/")[-1].replace(".md", "")
                    ),
                )
            )

        elif change.change_type == "added" and change.category == "task":
            task_id = change.after or "unknown"
            action_counter += 1
            actions.append(
                RemediationAction(
                    action_id=f"ACT{action_counter:03d}",
                    description=f"Add test coverage for new task {task_id}",
                    priority=3,
                    target_file=FEATURE_FILE_PATHS["quality"].format(
                        slug=change.file.split("/")[-1].replace(".md", "")
                    ),
                )
            )

    actions.sort(key=lambda a: a.priority)
    return actions


def build_evolution_timeline(
    slug: str,
    root: Path,
    limit: int = 20,
) -> list[EvolutionEntry]:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()

    peer_files = _get_peer_files(slug, resolved_root)
    if not peer_files:
        return []

    paths = [_relative_path(p, resolved_root) for p in peer_files.values()]
    git_args = [
        "log",
        "--format=%H|%ai|%an|%s",
        "--",
    ] + paths

    result = _run_git(git_args, resolved_root)
    if result.returncode != 0:
        return []

    entries: list[EvolutionEntry] = []
    for line in result.stdout.strip().splitlines()[:limit]:
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        commit_hash, date, author, message = parts

        diff_args = ["diff", "--stat", f"{commit_hash}^..{commit_hash}", "--"] + paths
        diff_result = _run_git(diff_args, resolved_root)
        if diff_result.returncode == 0 and diff_result.stdout.strip():
            lines = diff_result.stdout.strip().splitlines()
            change_count = len([l for l in lines if "|" in l])
            summary_line = lines[-1] if lines else ""
            categories = []
            if "insertion" in summary_line or "add" in summary_line.lower():
                categories.append("added")
            if "deletion" in summary_line or "remove" in summary_line.lower():
                categories.append("removed")
            if not categories:
                categories.append("modified")
        else:
            change_count = 0
            categories = ["unknown"]

        entries.append(
            EvolutionEntry(
                commit_hash=commit_hash,
                date=date,
                author=author,
                message=message,
                change_count=change_count,
                categories=categories,
            )
        )

    return entries


def render_diff_json(result: DiffResult) -> str:
    return json.dumps(result.as_dict(), indent=2, sort_keys=False) + "\n"


def render_diff_text(result: DiffResult) -> str:
    lines: list[str] = []
    lines.append(f"Spec diff for feature '{result.slug}'")
    lines.append("")

    summary = result.summary
    lines.append(
        f"Files changed: {summary['files_changed']}, "
        f"Added: {summary['total_added']}, "
        f"Removed: {summary['total_removed']}, "
        f"Modified: {summary['total_modified']}"
    )
    lines.append("")

    if not result.files:
        lines.append("No changes detected.")
        return "\n".join(lines) + "\n"

    for file_hunk in result.files:
        lines.append(f"  {file_hunk.path}")
        lines.append(
            f"    +{file_hunk.added_lines} -{file_hunk.removed_lines} "
            f"~{file_hunk.modified_lines}"
        )
        for hunk in file_hunk.diff_hunks[:5]:
            for hunk_line in hunk.splitlines()[:10]:
                lines.append(f"    {hunk_line}")
            if len(hunk.splitlines()) > 10:
                lines.append("    ...")
        lines.append("")

    return "\n".join(lines) + "\n"


def render_evolution_json(result: dict[str, object]) -> str:
    return json.dumps(result, indent=2, sort_keys=False) + "\n"


def render_evolution_text(result: dict[str, object]) -> str:
    lines: list[str] = []
    slug = result.get("slug", "unknown")
    lines.append(f"Evolution timeline for feature '{slug}'")
    lines.append("")

    diff_summary = result.get("diff_summary", {})
    if diff_summary:
        lines.append("Diff Summary:")
        lines.append(
            f"  Files changed: {diff_summary.get('files_changed', 0)}, "
            f"Added: {diff_summary.get('total_added', 0)}, "
            f"Removed: {diff_summary.get('total_removed', 0)}"
        )
        lines.append("")

    classification = result.get("classification", {})
    changes = classification.get("changes", [])
    if changes:
        lines.append(f"Changes ({len(changes)}):")
        for change in changes:
            change_type = change.get("change_type", "unknown")
            category = change.get("category", "unknown")
            file_path = change.get("file", "")
            lines.append(f"  [{change_type}] {category}: {file_path}")
        lines.append("")

    impact = result.get("impact", {})
    impact_summary = impact.get("summary", {})
    if impact_summary.get("total", 0):
        lines.append("Impact Summary:")
        lines.append(
            f"  Total: {impact_summary.get('total', 0)}, "
            f"Breaking: {impact_summary.get('breaking', 0)}, "
            f"Warning: {impact_summary.get('warning', 0)}, "
            f"Info: {impact_summary.get('info', 0)}"
        )
        lines.append("")

    remediation = result.get("remediation", [])
    if remediation:
        lines.append(f"Remediation Actions ({len(remediation)}):")
        for action in remediation:
            lines.append(f"  [P{action['priority']}] {action['description']}")
        lines.append("")

    timeline = result.get("timeline", [])
    if timeline:
        lines.append(f"Timeline ({len(timeline)} commits):")
        for entry in timeline:
            lines.append(
                f"  {entry['commit_hash'][:8]} {entry['date'][:10]} "
                f"{entry['author']}: {entry['message']}"
            )
        lines.append("")

    return "\n".join(lines) + "\n"

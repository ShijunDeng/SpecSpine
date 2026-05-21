from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .evolution_git import DiffResult, _build_versioned_content
from .features import (
    FEATURE_FILE_PATHS,
    validate_feature_slug,
)

AC_ID_RE = re.compile(r"(AC\d{3})")
TASK_ID_RE = re.compile(r"(T\d{3})")

__all__ = [
    "AC_ID_RE",
    "TASK_ID_RE",
    "ClassifiedChange",
    "ClassificationResult",
    "classify_changes",
]


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


def _extract_ac_ids(text: str) -> list[str]:
    return AC_ID_RE.findall(text)


def _extract_task_ids(text: str) -> list[str]:
    return TASK_ID_RE.findall(text)


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

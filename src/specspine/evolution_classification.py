from __future__ import annotations

from pathlib import Path

from .evolution_git import DiffResult, _build_versioned_content
from .features import (
    FEATURE_FILE_PATHS,
    validate_feature_slug,
)
from .evolution_classification_models import (
    AC_ID_RE,
    TASK_ID_RE,
    ClassifiedChange,
    ClassificationResult,
)
from .evolution_classification_helpers import (
    _extract_metadata,
)
from .evolution_classification_file_changes import (
    _classify_added_file,
    _classify_removed_file,
)
from .evolution_classification_modified import (
    _classify_modified_file,
)

__all__ = [
    "AC_ID_RE",
    "TASK_ID_RE",
    "ClassifiedChange",
    "ClassificationResult",
    "classify_changes",
]


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
            added_changes, change_counter = _classify_added_file(
                after, rel_path, change_counter
            )
            changes.extend(added_changes)
            continue

        if before is not None and after is None:
            removed_changes, change_counter = _classify_removed_file(
                before, rel_path, change_counter
            )
            changes.extend(removed_changes)
            continue

        modified_changes, change_counter = _classify_modified_file(
            before or "", after or "", rel_path, change_counter, diff_result, kind
        )
        changes.extend(modified_changes)

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

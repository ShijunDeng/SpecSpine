from __future__ import annotations

from pathlib import Path

from ..feature_bundle import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    _first_line_h1,
    _first_scalar,
    _section_or_placeholder,
    _why_or_placeholder,
    feature_bundle_paths,
    feature_title,
    read_feature_metadata,
    validate_feature_slug,
)

__all__ = [
    "load_feature_contents",
    "extract_draft_sections",
]


def load_feature_contents(
    root: Path,
    slug: str,
) -> tuple[Path, dict[str, str], list[str], list[str]]:
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

    return resolved_root, contents, source_files, missing_files


def extract_draft_sections(
    contents: dict[str, str],
    relative_paths: dict[str, str],
    slug: str,
) -> tuple[str, str, str, str, str, str]:
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
    return title, status, why, acceptance_criteria, tasks, test_plan

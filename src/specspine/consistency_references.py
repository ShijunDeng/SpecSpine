from __future__ import annotations

from pathlib import Path

from .consistency_models import (
    ConsistencyReference,
    DOCUMENTATION_GLOBS,
    IMPLEMENTATION_GLOBS,
    LOCAL_PATH_RE,
    TEST_GLOBS,
)
from .consistency_utils import (
    _area_prefixes,
    _candidate_files,
    _dedupe_references,
    _read_text,
    _relative_path,
)
from .features import (
    build_feature_tests_report,
    get_feature_status,
)

__all__ = [
    "_changed_references",
    "_coverage_references",
    "_explicit_paths_from_feature_files",
    "_feature_missing_files",
    "_feature_source_files",
    "_references_for_area",
]


def _feature_source_files(root: Path, slug: str) -> tuple[str, ...]:
    status = get_feature_status(root, slug)
    paths: list[str] = []
    for details in status.files.values():
        if details["exists"]:
            paths.append(str(details["path"]))
    return tuple(paths)


def _feature_missing_files(root: Path, slug: str) -> tuple[str, ...]:
    return tuple(get_feature_status(root, slug).missing_files)


def _explicit_paths_from_feature_files(root: Path, source_files: tuple[str, ...]) -> set[str]:
    paths: set[str] = set()
    for relative_path in source_files:
        path = root / relative_path
        if not path.exists():
            continue
        for match in LOCAL_PATH_RE.finditer(_read_text(path)):
            paths.add(match.group("path").rstrip(".,);]`"))
    return paths


def _references_for_area(
    root: Path,
    *,
    slug: str,
    explicit_paths: set[str],
    globs: tuple[str, ...],
    area: str,
) -> tuple[ConsistencyReference, ...]:
    references: list[ConsistencyReference] = []
    seen: set[tuple[str, int | None, str, str]] = set()
    for explicit_path in sorted(explicit_paths):
        if not explicit_path.startswith(_area_prefixes(area)):
            continue
        references.append(
            ConsistencyReference(
                path=explicit_path,
                line=None,
                kind=area,
                matched="explicit feature artifact path",
                exists=(root / explicit_path).exists(),
            )
        )

    for path in _candidate_files(root, globs):
        relative_path = _relative_path(root, path)
        content = _read_text(path)
        for line_number, line in enumerate(content.splitlines(), start=1):
            if slug not in line:
                continue
            key = (relative_path, line_number, area, slug)
            if key in seen:
                continue
            references.append(
                ConsistencyReference(
                    path=relative_path,
                    line=line_number,
                    kind=area,
                    matched=slug,
                    exists=True,
                )
            )
            seen.add(key)
    return tuple(_dedupe_references(references))


def _coverage_references(report) -> tuple[ConsistencyReference, ...]:
    references: list[ConsistencyReference] = []
    for link in report.test_coverage:
        if not link.target_path.startswith("tests/"):
            continue
        references.append(
            ConsistencyReference(
                path=link.target_path,
                line=link.line,
                kind="test",
                matched=link.acceptance_criterion_id,
                exists=link.target_exists,
            )
        )
    return _dedupe_references(references)


def _changed_references(
    *,
    root: Path,
    slug: str,
    changed_files: tuple[str, ...],
    source_files: tuple[str, ...],
    implementation_references: tuple[ConsistencyReference, ...],
    test_references: tuple[ConsistencyReference, ...],
    documentation_references: tuple[ConsistencyReference, ...],
) -> tuple[ConsistencyReference, ...]:
    known_paths = set(source_files)
    known_paths.update(reference.path for reference in implementation_references)
    known_paths.update(reference.path for reference in test_references)
    known_paths.update(reference.path for reference in documentation_references)
    references: list[ConsistencyReference] = []
    for changed_file in changed_files:
        if changed_file in known_paths:
            matched = "feature evidence path"
        elif slug in changed_file:
            matched = slug
        else:
            continue
        references.append(
            ConsistencyReference(
                path=changed_file,
                line=None,
                kind="changed",
                matched=matched,
                exists=(root / changed_file).exists(),
            )
        )
    return tuple(references)

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from .helpers import _relative_path
from ._artifact_single import _artifact_record

__all__ = [
    "_workspace_artifacts",
    "_feature_artifacts",
    "_dedupe_artifacts",
]


def _workspace_artifacts(root: Path) -> tuple[dict[str, Any], ...]:
    from ..workspace import BASE_WORKSPACE_FILES

    return tuple(
        _artifact_record(
            root,
            root / relative_path,
            kind="workspace",
            display_path=relative_path,
        )
        for relative_path in sorted(BASE_WORKSPACE_FILES)
    )


def _feature_artifacts(root: Path, slug: str) -> tuple[dict[str, Any], ...]:
    from ..features import FEATURE_FILE_PATHS

    artifacts: list[dict[str, Any]] = []
    for kind in ("spec", "execution", "quality"):
        relative_path = FEATURE_FILE_PATHS[kind].format(slug=slug)
        artifacts.append(
            _artifact_record(
                root,
                root / relative_path,
                kind=f"feature-{kind}",
                display_path=relative_path,
            )
        )
    return tuple(artifacts)


def _dedupe_artifacts(
    artifact_groups: Iterable[Iterable[dict[str, Any]]],
) -> tuple[dict[str, Any], ...]:
    artifacts: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for group in artifact_groups:
        for artifact in group:
            path = str(artifact["path"])
            if path in seen_paths:
                continue
            artifacts.append(artifact)
            seen_paths.add(path)
    return tuple(artifacts)

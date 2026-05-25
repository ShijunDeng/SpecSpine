from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from ..workspace import BASE_WORKSPACE_FILES
from .helpers import _is_within_root, _relative_path, _resolve_path, _hash_file, _normalize_lexical_path

__all__ = [
    "_artifact_record",
    "_include_artifact",
    "_workspace_artifacts",
    "_feature_artifacts",
    "_dedupe_artifacts",
]


def _artifact_record(
    root: Path,
    path: Path,
    *,
    kind: str,
    display_path: str | None = None,
    requested_path: str | None = None,
) -> dict[str, Any]:
    resolved_path = _resolve_path(path)
    inside_root = _is_within_root(root, resolved_path)
    artifact_path = display_path or _relative_path(root, resolved_path)

    artifact: dict[str, Any] = {
        "exists": False,
        "inside_root": inside_root,
        "kind": kind,
        "path": artifact_path,
    }
    if requested_path is not None:
        artifact["requested_path"] = requested_path

    try:
        exists = path.exists()
    except OSError as error:
        artifact["error"] = f"exists_error:{error.__class__.__name__}"
        return artifact

    artifact["exists"] = exists
    if not inside_root:
        artifact["reason"] = "outside_root"
        return artifact
    if not exists:
        artifact["reason"] = "missing"
        return artifact

    try:
        if not path.is_file():
            artifact["reason"] = "not_file"
            return artifact
        stat = path.stat()
        artifact["bytes"] = stat.st_size
        artifact["sha256"] = _hash_file(path)
    except OSError as error:
        artifact["reason"] = "read_error"
        artifact["error"] = error.__class__.__name__

    return artifact


def _include_artifact(root: Path, include: str | Path) -> dict[str, Any]:
    include_value = str(include)
    include_path = Path(include)
    if include_path.is_absolute():
        candidate = include_path
    else:
        candidate = root / include_path

    display_candidate = _normalize_lexical_path(candidate)
    return _artifact_record(
        root,
        candidate,
        kind="include",
        display_path=_relative_path(root, display_candidate),
        requested_path=include_value,
    )


def _workspace_artifacts(root: Path) -> tuple[dict[str, Any], ...]:
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

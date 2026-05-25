from __future__ import annotations

from pathlib import Path
from typing import Any

from .helpers import _is_within_root, _relative_path, _resolve_path, _hash_file, _normalize_lexical_path

__all__ = [
    "_artifact_record",
    "_include_artifact",
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

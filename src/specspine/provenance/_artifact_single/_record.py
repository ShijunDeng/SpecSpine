from __future__ import annotations

from pathlib import Path
from typing import Any

from ..helpers import _is_within_root, _relative_path, _resolve_path, _hash_file

__all__ = [
    "_artifact_record",
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

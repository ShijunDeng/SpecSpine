from __future__ import annotations

from pathlib import Path

from ..features import list_feature_bundles
from ._task_scanner import _scan_task_downstream
from ._coverage_scanner import _scan_coverage_downstream
from ._dependency_scanner import _scan_dependency_downstream

__all__ = [
    "_find_downstream_references",
]


def _find_downstream_references(
    slug: str,
    root: Path,
) -> dict[str, list[dict[str, str]]]:
    resolved_root = root.expanduser().resolve()
    all_features = list_feature_bundles(resolved_root)
    return {
        "tasks": _scan_task_downstream(slug, resolved_root, all_features),
        "coverage": _scan_coverage_downstream(slug, resolved_root, all_features),
        "dependent_features": _scan_dependency_downstream(slug, resolved_root, all_features),
    }

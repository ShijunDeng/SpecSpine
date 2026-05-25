from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import feature_bundle_paths

__all__ = [
    "_checklist_summary",
    "_empty_evidence",
]


def _checklist_summary(items: tuple[Any, ...]) -> dict[str, int]:
    done = sum(1 for item in items if bool(item.done))
    total = len(items)
    return {
        "done": done,
        "open": total - done,
        "total": total,
    }


def _empty_evidence(root: Path, slug: str) -> dict[str, Any]:
    missing = [
        str(path.relative_to(root))
        for path in feature_bundle_paths(root, slug).values()
    ]
    return {
        "blocking_checks": [],
        "gaps": [
            {
                "id": "missing_file",
                "message": f"Missing native feature file: {relative_path}",
                "source_file": relative_path,
            }
            for relative_path in missing
        ],
        "has_native_files": False,
        "missing_files": missing,
        "quality_checks": [],
        "ready_summary": {"fail": 0, "pass": 0, "total": 0},
        "sources": {
            kind: {
                "exists": False,
                "path": str(path.relative_to(root)),
            }
            for kind, path in feature_bundle_paths(root, slug).items()
        },
        "task_summary": {"done": 0, "open": 0, "total": 0},
        "test_coverage_summary": {"done": 0, "open": 0, "total": 0},
        "test_plan": [],
    }

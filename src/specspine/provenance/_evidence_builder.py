from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import (
    build_feature_handoff_report,
    build_feature_ready_report,
)

from ._evidence_checks import _check_dicts

__all__ = [
    "_feature_evidence",
]


def _feature_evidence(root: Path, slug: str) -> dict[str, Any]:
    handoff = build_feature_handoff_report(root, slug, require_coverage=True)
    ready = build_feature_ready_report(root, slug, require_coverage=True)
    source_files = tuple(
        str(source["path"])
        for source in handoff.sources.values()
        if source.get("exists")
    )

    return {
        "blocking_checks": _check_dicts(ready.blocking_checks),
        "coverage_required": True,
        "feature_id": slug,
        "gaps": [dict(gap) for gap in ready.gaps],
        "handoff_summary": dict(handoff.summary),
        "has_native_files": handoff.has_native_files,
        "missing_files": list(ready.missing_files),
        "ready": ready.ready,
        "ready_summary": dict(ready.summary),
        "source_files": list(source_files),
        "status": ready.status,
    }

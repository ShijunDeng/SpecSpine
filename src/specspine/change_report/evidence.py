from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import (
    build_feature_handoff_report,
    build_feature_ready_report,
)

__all__ = [
    "_feature_evidence",
]


def _feature_evidence(root: Path, slug: str) -> dict[str, Any]:
    handoff = build_feature_handoff_report(root, slug, require_coverage=True)
    ready = build_feature_ready_report(root, slug, require_coverage=True)
    return {
        "blocking_checks": [check.as_dict() for check in ready.blocking_checks],
        "feature_id": slug,
        "gaps": [dict(gap) for gap in ready.gaps],
        "has_native_files": handoff.has_native_files,
        "missing_files": list(ready.missing_files),
        "ready": ready.ready,
        "source_files": [
            str(source["path"])
            for source in handoff.sources.values()
            if source.get("exists")
        ],
        "status": ready.status,
    }

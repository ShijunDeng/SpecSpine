from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from ..features import (
    FeatureReadyCheck,
    build_feature_handoff_report,
    build_feature_ready_report,
)

__all__ = [
    "_check_dicts",
    "_feature_evidence",
    "_summary",
]


def _check_dicts(checks: Iterable[FeatureReadyCheck]) -> list[dict[str, str]]:
    return [check.as_dict() for check in checks]


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


def _summary(
    artifacts: tuple[dict[str, Any], ...],
    feature_evidence: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    hashed_files = sum(1 for artifact in artifacts if "sha256" in artifact)
    existing = sum(1 for artifact in artifacts if artifact["exists"])
    missing = sum(1 for artifact in artifacts if artifact.get("reason") == "missing")
    outside_root = sum(
        1 for artifact in artifacts if artifact.get("reason") == "outside_root"
    )
    read_errors = sum(
        1 for artifact in artifacts if artifact.get("reason") == "read_error"
    )
    feature = feature_evidence[0] if feature_evidence else None

    return {
        "artifacts_total": len(artifacts),
        "artifacts_existing": existing,
        "feature_has_native_files": (
            bool(feature["has_native_files"]) if feature is not None else None
        ),
        "feature_included": feature is not None,
        "feature_ready": bool(feature["ready"]) if feature is not None else None,
        "hashed_artifacts": hashed_files,
        "missing_artifacts": missing,
        "outside_root_artifacts": outside_root,
        "read_errors": read_errors,
    }

from __future__ import annotations

from typing import Any

__all__ = [
    "_summary",
]


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

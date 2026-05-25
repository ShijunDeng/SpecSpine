from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from ..features import (
    FEATURE_FILE_PATHS,
    FeatureReadyCheck,
    build_feature_handoff_report,
    build_feature_ready_report,
    validate_feature_slug,
)
from .models import ProvenanceManifest
from .helpers import _resolve_path
from .artifacts import (
    _dedupe_artifacts,
    _feature_artifacts,
    _include_artifact,
    _workspace_artifacts,
)

__all__ = [
    "build_provenance_manifest",
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


def _recommended_commands(feature_id: str | None) -> tuple[str, ...]:
    if feature_id is None:
        return (
            "specspine provenance manifest . --json",
            "specspine validate . --fusion --features",
            "specspine review packet . --json",
            "specspine security cues . --json",
            "specspine change risk . --json",
        )

    return (
        f"specspine provenance manifest . --feature {feature_id} --json",
        f"specspine feature handoff {feature_id} . --json",
        f"specspine feature ready {feature_id} . --json --require-coverage",
        f"specspine feature trace {feature_id} . --json",
        f"specspine feature tests {feature_id} . --json",
        f"specspine tests impact . --feature {feature_id} --json",
        f"specspine review packet . --feature {feature_id} --json",
        f"specspine security cues . --feature {feature_id} --json",
        f"specspine change risk . --feature {feature_id} --json",
        "specspine validate . --fusion --features",
    )


def _safety_notes() -> tuple[str, ...]:
    return (
        "This provenance manifest is advisory only.",
        "Hashes prove only the local file bytes read at manifest build time.",
        "File contents are never included in this report.",
        "SpecSpine did not run commands, run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, read environment variables, or read tokens.",
    )


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


def build_provenance_manifest(
    root: str | Path,
    *,
    feature: str | None = None,
    includes: Iterable[str | Path] = (),
) -> ProvenanceManifest:
    resolved_root = _resolve_path(Path(root))
    feature_id = validate_feature_slug(feature) if feature is not None else None

    feature_artifacts = (
        _feature_artifacts(resolved_root, feature_id)
        if feature_id is not None
        else ()
    )
    include_artifacts = tuple(
        _include_artifact(resolved_root, include) for include in includes
    )
    artifacts = _dedupe_artifacts(
        (
            _workspace_artifacts(resolved_root),
            feature_artifacts,
            include_artifacts,
        )
    )
    evidence = (
        (_feature_evidence(resolved_root, feature_id),)
        if feature_id is not None
        else ()
    )

    return ProvenanceManifest(
        root=resolved_root,
        feature_id=feature_id,
        artifacts=artifacts,
        feature_evidence=evidence,
        summary=_summary(artifacts, evidence),
        recommended_commands=_recommended_commands(feature_id),
        safety_notes=_safety_notes(),
    )

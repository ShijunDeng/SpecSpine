from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .features import (
    FEATURE_FILE_PATHS,
    FeatureReadyCheck,
    build_feature_handoff_report,
    build_feature_ready_report,
    validate_feature_slug,
)
from .workspace import BASE_WORKSPACE_FILES


CHUNK_SIZE = 1024 * 1024
PathLike = str | Path


@dataclass(frozen=True)
class ProvenanceManifest:
    root: Path
    feature_id: str | None
    artifacts: tuple[dict[str, Any], ...]
    feature_evidence: tuple[dict[str, Any], ...]
    summary: dict[str, Any]
    recommended_commands: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "artifacts": [dict(artifact) for artifact in self.artifacts],
            "feature_evidence": [
                dict(evidence) for evidence in self.feature_evidence
            ],
            "feature_id": self.feature_id,
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "summary": dict(self.summary),
        }


def _is_within_root(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _resolve_path(path: Path) -> Path:
    try:
        return path.resolve(strict=False)
    except (OSError, RuntimeError):
        return path.absolute()


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
            return path.as_posix()


def _normalize_lexical_path(path: Path) -> Path:
    return Path(os.path.normpath(str(path)))


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


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


def _include_artifact(root: Path, include: PathLike) -> dict[str, Any]:
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
    root: PathLike,
    *,
    feature: str | None = None,
    includes: Iterable[PathLike] = (),
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


def render_provenance_manifest_json(manifest: ProvenanceManifest) -> str:
    return json.dumps(manifest.as_dict(), indent=2, sort_keys=True) + "\n"


def render_provenance_manifest_text(manifest: ProvenanceManifest) -> str:
    summary = manifest.summary
    lines = [
        f"Provenance manifest: {manifest.root}",
        f"Feature: {manifest.feature_id or 'workspace'}",
        (
            "Summary: "
            f"artifacts={summary['artifacts_total']} "
            f"existing={summary['artifacts_existing']} "
            f"hashed={summary['hashed_artifacts']} "
            f"missing={summary['missing_artifacts']} "
            f"outside_root={summary['outside_root_artifacts']}"
        ),
        "",
        "Artifacts:",
    ]
    if manifest.artifacts:
        for artifact in manifest.artifacts:
            marker = "exists" if artifact["exists"] else "missing"
            detail = ""
            if "sha256" in artifact:
                detail = f" sha256={artifact['sha256']} bytes={artifact['bytes']}"
            elif artifact.get("reason"):
                detail = f" reason={artifact['reason']}"
            lines.append(
                f"- [{marker}] {artifact['kind']}: {artifact['path']}{detail}"
            )
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Feature evidence:")
    if manifest.feature_evidence:
        for evidence in manifest.feature_evidence:
            lines.append(
                "- "
                f"{evidence['feature_id']}: "
                f"status={evidence['status']} "
                f"ready={'yes' if evidence['ready'] else 'no'} "
                f"has_native_files={'yes' if evidence['has_native_files'] else 'no'} "
                f"blocking={len(evidence['blocking_checks'])} "
                f"gaps={len(evidence['gaps'])}"
            )
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Recommended commands:")
    lines.extend(f"- {command}" for command in manifest.recommended_commands)
    lines.append("")
    lines.append("Safety notes:")
    lines.extend(f"- {note}" for note in manifest.safety_notes)
    return "\n".join(lines) + "\n"

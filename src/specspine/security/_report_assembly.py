from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import validate_feature_slug
from .models import SecurityCueReport
from .helpers import _dedupe, _feature_slug_from_path
from .builder_commands import _recommended_commands

from .detectors import _feature_evidence

__all__ = [
    "_assemble_security_report",
]


def _assemble_security_report(
    resolved_root: Path,
    feature_slug: str | None,
    normalised_changed_files: list[str],
    files: list[dict[str, Any]],
    cues: list[dict[str, Any]],
    categories: dict[str, int],
    files_existing: int,
    inferred_features: list[str],
) -> SecurityCueReport:
    feature_ids = _dedupe(
        tuple([slug for slug in inferred_features] + ([feature_slug] if feature_slug else []))
    )
    evidence = tuple(_feature_evidence(resolved_root, slug) for slug in feature_ids)
    summary = {
        "categories": dict(sorted(categories.items())),
        "changed_files": len(normalised_changed_files),
        "cues_total": len(cues),
        "feature_ids": list(feature_ids),
        "files_existing": files_existing,
        "high": _count_severity(cues, "high"),
        "low": _count_severity(cues, "low"),
        "medium": _count_severity(cues, "medium"),
    }
    severity_counts = {"high": summary["high"], "low": summary["low"], "medium": summary["medium"]}
    safety_notes = (
        "This report is advisory only and is not proof of a vulnerability.",
        "Security cues are text hints from changed paths and local files, not SAST findings.",
        "SpecSpine did not execute commands, run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, read environment variables, or read tokens.",
    )
    return SecurityCueReport(
        root=resolved_root,
        feature_id=feature_slug,
        changed_files=normalised_changed_files,
        files=tuple(files),
        cues=tuple(cues),
        feature_evidence=evidence,
        summary=summary,
        recommended_commands=_recommended_commands(normalised_changed_files, feature_ids),
        safety_notes=safety_notes,
    )


def _count_severity(cues: list[dict[str, Any]], severity: str) -> int:
    return sum(1 for cue in cues if str(cue["severity"]) == severity)


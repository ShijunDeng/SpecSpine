from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import validate_feature_slug
from .models import SecurityCueReport
from .helpers import (
    _classify_changed_file,
    _dedupe,
    _feature_slug_from_path,
    _is_within_root,
    _normalise_changed_file,
    _read_small_text,
)
from .detectors import _detect_cues, _feature_evidence
from .builder_commands import _recommended_commands

__all__ = [
    "build_security_cue_report",
]


def build_security_cue_report(
    root: Path,
    *,
    changed_files: tuple[str, ...] = (),
    feature: str | None = None,
) -> SecurityCueReport:
    resolved_root = root.resolve()
    feature_slug = validate_feature_slug(feature) if feature is not None else None
    normalised_pairs = [
        _normalise_changed_file(resolved_root, path) for path in changed_files
    ]
    normalised_changed_files = _dedupe([path for path, _resolved in normalised_pairs])
    resolved_by_path = {path: resolved for path, resolved in normalised_pairs}

    files: list[dict[str, Any]] = []
    cues: list[dict[str, Any]] = []
    inferred_features: list[str] = []
    severity_counts = {"high": 0, "low": 0, "medium": 0}
    categories: dict[str, int] = {}
    files_existing = 0

    for path in normalised_changed_files:
        resolved_path = resolved_by_path[path]
        category = _classify_changed_file(path)
        exists = resolved_path.exists()
        if exists:
            files_existing += 1
        categories[category] = categories.get(category, 0) + 1

        file_info: dict[str, Any] = {
            "category": category,
            "exists": exists,
            "path": path,
        }
        text: str | None = None
        if exists:
            if _is_within_root(resolved_root, resolved_path):
                text, skipped_reason = _read_small_text(resolved_path)
                file_info["text_read"] = text is not None
                if skipped_reason is not None:
                    file_info["read_skipped"] = skipped_reason
            else:
                file_info["text_read"] = False
                file_info["read_skipped"] = "outside_root"
        else:
            file_info["text_read"] = False
        files.append(file_info)

        if text is not None:
            found = _detect_cues(path, category, text)
            cues.extend(found)
            for cue in found:
                severity = str(cue["severity"])
                severity_counts[severity] += 1

        inferred = _feature_slug_from_path(path)
        if inferred is not None:
            inferred_features.append(inferred)

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
        "high": severity_counts["high"],
        "low": severity_counts["low"],
        "medium": severity_counts["medium"],
    }
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

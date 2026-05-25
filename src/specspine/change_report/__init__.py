from __future__ import annotations

from pathlib import Path
from typing import Any

from ..change_classifiers import (
    _classify_changed_file,
    _dedupe,
    _feature_slug_from_path,
    _normalise_changed_file,
)
from ..change_models import RISK_BY_CATEGORY, ChangeRiskReport
from ..features import (
    validate_feature_slug,
)
from .evidence import _feature_evidence
from .renderers import (
    _recommended_commands,
    render_change_risk_json,
    render_change_risk_text,
)

__all__ = [
    "build_change_risk_report",
    "render_change_risk_json",
    "render_change_risk_text",
]


def build_change_risk_report(
    root: Path,
    *,
    changed_files: tuple[str, ...] = (),
    feature: str | None = None,
) -> ChangeRiskReport:
    resolved_root = root.resolve()
    feature_slug = validate_feature_slug(feature) if feature is not None else None
    normalised_changed_files = _dedupe(
        [_normalise_changed_file(resolved_root, path) for path in changed_files]
    )

    files: list[dict[str, Any]] = []
    inferred_features: list[str] = []
    risk_counts = {"high": 0, "low": 0, "medium": 0}
    categories: dict[str, int] = {}
    for path in normalised_changed_files:
        category = _classify_changed_file(path)
        risk = RISK_BY_CATEGORY[category]
        files.append({"category": category, "path": path, "risk": risk})
        risk_counts[risk] += 1
        categories[category] = categories.get(category, 0) + 1
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
        "feature_ids": list(feature_ids),
        "high": risk_counts["high"],
        "low": risk_counts["low"],
        "medium": risk_counts["medium"],
    }
    safety_notes = (
        "This report is advisory only.",
        "Recommended commands are advisory only and are not executed.",
        "SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, or read tokens.",
    )
    return ChangeRiskReport(
        root=resolved_root,
        feature_id=feature_slug,
        changed_files=normalised_changed_files,
        files=tuple(files),
        feature_evidence=evidence,
        summary=summary,
        recommended_commands=_recommended_commands(normalised_changed_files, feature_ids),
        safety_notes=safety_notes,
    )

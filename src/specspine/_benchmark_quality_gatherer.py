from __future__ import annotations

from pathlib import Path

from .features import InvalidFeatureSlug

__all__ = [
    "_gather_quality_metrics",
]


def _gather_quality_metrics(
    slug: str,
    resolved_root: Path,
) -> dict[str, int]:
    validation_pass = 0
    validation_fail = 0
    try:
        from .validation import build_validation_report
        val_report = build_validation_report(
            resolved_root,
            include_fusion=True,
            include_features=False,
            include_adapters=False,
        )
        summary = val_report.get("summary", {})
        validation_pass = summary.get("pass", 0)
        validation_fail = summary.get("fail", 0)
    except OSError:
        pass

    consistency_fail = 0
    try:
        from .consistency import build_consistency_report
        cons_report = build_consistency_report(
            resolved_root,
            feature_filter=slug,
        )
        for fc in cons_report.features:
            if fc.feature_id == slug:
                consistency_fail = sum(
                    1 for c in fc.consistency_checks if c.status == "fail"
                )
                break
    except (OSError, InvalidFeatureSlug):
        pass

    drift_events = 0
    try:
        from .coverage import build_coverage_debt_report
        debt_report = build_coverage_debt_report(resolved_root)
        for feat in debt_report.get("features", []):
            if feat.get("feature_id") == slug:
                drift_events = feat.get("missing_acceptance_criteria", 0)
                break
    except OSError:
        pass

    return {
        "validation_pass": validation_pass,
        "validation_fail": validation_fail,
        "consistency_fail": consistency_fail,
        "drift_events": drift_events,
    }

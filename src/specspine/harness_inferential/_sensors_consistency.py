from __future__ import annotations

from pathlib import Path

from ..features import InvalidFeatureSlug
from ..harness_models import HarnessFeedbackSensor

__all__ = [
    "_build_consistency_sensor",
]


def _build_consistency_sensor(slug: str, resolved_root: Path) -> HarnessFeedbackSensor:
    from ..consistency import build_consistency_report

    try:
        consistency = build_consistency_report(resolved_root, feature_filter=slug)
        feature_consistency = None
        for feature in consistency.features:
            if feature.feature_id == slug:
                feature_consistency = feature
                break
        checks_fail = 0
        checks_pass = 0
        if feature_consistency is not None:
            checks_fail = sum(
                1 for check in feature_consistency.consistency_checks
                if check.status == "fail"
            )
            checks_pass = sum(
                1 for check in feature_consistency.consistency_checks
                if check.status == "pass"
            )
        return HarnessFeedbackSensor(
            sensor_type="inferential",
            name="consistency_scan",
            status="pass" if checks_fail == 0 else "fail",
            output={
                "checks_fail": checks_fail,
                "checks_pass": checks_pass,
            },
            ac_ids=(),
        )
    except (InvalidFeatureSlug, OSError):
        return HarnessFeedbackSensor(
            sensor_type="inferential",
            name="consistency_scan",
            status="fail",
            output={"error": "consistency_scan_unavailable"},
            ac_ids=(),
        )

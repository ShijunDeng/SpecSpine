from __future__ import annotations

from pathlib import Path

from .change import build_change_risk_report
from .consistency import build_consistency_report
from .features import (
    InvalidFeatureSlug,
)
from .harness_models import HarnessFeedbackSensor
from .hygiene import build_hygiene_scan_report
from .security import build_security_cue_report

__all__ = [
    "_run_inferential_sensors",
]


def _run_inferential_sensors(slug: str, root: Path) -> list[HarnessFeedbackSensor]:
    resolved_root = root.expanduser().resolve()
    sensors: list[HarnessFeedbackSensor] = []

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
        sensors.append(
            HarnessFeedbackSensor(
                sensor_type="inferential",
                name="consistency_scan",
                status="pass" if checks_fail == 0 else "fail",
                output={
                    "checks_fail": checks_fail,
                    "checks_pass": checks_pass,
                },
                ac_ids=(),
            )
        )
    except (InvalidFeatureSlug, OSError):
        sensors.append(
            HarnessFeedbackSensor(
                sensor_type="inferential",
                name="consistency_scan",
                status="fail",
                output={"error": "consistency_scan_unavailable"},
                ac_ids=(),
            )
        )

    try:
        hygiene = build_hygiene_scan_report(resolved_root)
        high_findings = hygiene.summary.get("high", 0)
        medium_findings = hygiene.summary.get("medium", 0)
        sensors.append(
            HarnessFeedbackSensor(
                sensor_type="inferential",
                name="hygiene_scan",
                status="pass" if high_findings == 0 else "fail",
                output={
                    "high_findings": high_findings,
                    "medium_findings": medium_findings,
                    "total_findings": hygiene.summary.get("total_findings", 0),
                },
                ac_ids=(),
            )
        )
    except OSError:
        sensors.append(
            HarnessFeedbackSensor(
                sensor_type="inferential",
                name="hygiene_scan",
                status="fail",
                output={"error": "hygiene_scan_unavailable"},
                ac_ids=(),
            )
        )

    try:
        security = build_security_cue_report(resolved_root, feature=slug)
        high_cues = security.summary.get("high", 0)
        sensors.append(
            HarnessFeedbackSensor(
                sensor_type="inferential",
                name="security_cues",
                status="pass" if high_cues == 0 else "fail",
                output={
                    "high_cues": high_cues,
                    "medium_cues": security.summary.get("medium", 0),
                    "low_cues": security.summary.get("low", 0),
                    "cues_total": security.summary.get("cues_total", 0),
                },
                ac_ids=(),
            )
        )
    except (InvalidFeatureSlug, OSError):
        sensors.append(
            HarnessFeedbackSensor(
                sensor_type="inferential",
                name="security_cues",
                status="fail",
                output={"error": "security_cues_unavailable"},
                ac_ids=(),
            )
        )

    try:
        change_risk = build_change_risk_report(resolved_root, feature=slug)
        risk_score = change_risk.summary.get("risk_score", 0)
        sensors.append(
            HarnessFeedbackSensor(
                sensor_type="inferential",
                name="change_risk",
                status="pass" if risk_score <= 3 else "fail",
                output={
                    "risk_score": risk_score,
                    "risk_level": change_risk.summary.get("risk_level", "unknown"),
                },
                ac_ids=(),
            )
        )
    except (InvalidFeatureSlug, OSError):
        sensors.append(
            HarnessFeedbackSensor(
                sensor_type="inferential",
                name="change_risk",
                status="fail",
                output={"error": "change_risk_unavailable"},
                ac_ids=(),
            )
        )

    return sensors

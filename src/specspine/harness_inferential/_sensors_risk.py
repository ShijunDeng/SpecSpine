from __future__ import annotations

from pathlib import Path

from ..features import InvalidFeatureSlug
from ..harness_models import HarnessFeedbackSensor

__all__ = [
    "_build_change_risk_sensor",
]


def _build_change_risk_sensor(slug: str, resolved_root: Path) -> HarnessFeedbackSensor:
    from ..change import build_change_risk_report

    try:
        change_risk = build_change_risk_report(resolved_root, feature=slug)
        risk_score = change_risk.summary.get("risk_score", 0)
        return HarnessFeedbackSensor(
            sensor_type="inferential",
            name="change_risk",
            status="pass" if risk_score <= 3 else "fail",
            output={
                "risk_score": risk_score,
                "risk_level": change_risk.summary.get("risk_level", "unknown"),
            },
            ac_ids=(),
        )
    except (InvalidFeatureSlug, OSError):
        return HarnessFeedbackSensor(
            sensor_type="inferential",
            name="change_risk",
            status="fail",
            output={"error": "change_risk_unavailable"},
            ac_ids=(),
        )

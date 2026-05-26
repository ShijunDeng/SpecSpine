from __future__ import annotations

from pathlib import Path

from ..features import InvalidFeatureSlug
from ..harness_models import HarnessFeedbackSensor

__all__ = [
    "_build_security_sensor",
]


def _build_security_sensor(slug: str, resolved_root: Path) -> HarnessFeedbackSensor:
    from ..security import build_security_cue_report

    try:
        security = build_security_cue_report(resolved_root, feature=slug)
        high_cues = security.summary.get("high", 0)
        return HarnessFeedbackSensor(
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
    except (InvalidFeatureSlug, OSError):
        return HarnessFeedbackSensor(
            sensor_type="inferential",
            name="security_cues",
            status="fail",
            output={"error": "security_cues_unavailable"},
            ac_ids=(),
        )

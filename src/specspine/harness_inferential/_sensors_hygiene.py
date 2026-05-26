from __future__ import annotations

from pathlib import Path

from ..harness_models import HarnessFeedbackSensor

__all__ = [
    "_build_hygiene_sensor",
]


def _build_hygiene_sensor(resolved_root: Path) -> HarnessFeedbackSensor:
    from ..hygiene import build_hygiene_scan_report

    try:
        hygiene = build_hygiene_scan_report(resolved_root)
        high_findings = hygiene.summary.get("high", 0)
        medium_findings = hygiene.summary.get("medium", 0)
        return HarnessFeedbackSensor(
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
    except OSError:
        return HarnessFeedbackSensor(
            sensor_type="inferential",
            name="hygiene_scan",
            status="fail",
            output={"error": "hygiene_scan_unavailable"},
            ac_ids=(),
        )

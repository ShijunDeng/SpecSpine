from __future__ import annotations

from pathlib import Path

from ..coverage import build_coverage_debt_report
from ..features import InvalidFeatureSlug
from ..harness_models import HarnessFeedbackSensor

__all__ = [
    "_build_coverage_debt_sensor",
]


def _build_coverage_debt_sensor(resolved_root: Path, slug: str) -> HarnessFeedbackSensor:
    try:
        debt_report = build_coverage_debt_report(resolved_root)
        feature_debt = None
        for feature in debt_report.get("features", []):
            if feature.get("feature_id") == slug:
                feature_debt = feature
                break
        if feature_debt is not None:
            return HarnessFeedbackSensor(
                sensor_type="computational",
                name="coverage_debt",
                status="pass" if int(feature_debt.get("missing_acceptance_criteria", 0)) == 0 else "fail",
                output={
                    "acceptance_criteria_total": feature_debt.get("acceptance_criteria_total", 0),
                    "covered_acceptance_criteria": feature_debt.get("covered_acceptance_criteria", 0),
                    "missing_acceptance_criteria": feature_debt.get("missing_acceptance_criteria", 0),
                },
                ac_ids=tuple(feature_debt.get("missing_acceptance_criterion_ids", [])),
            )
        else:
            return HarnessFeedbackSensor(
                sensor_type="computational",
                name="coverage_debt",
                status="warn",
                output={"error": "feature_not_in_debt_report"},
                ac_ids=(),
            )
    except (InvalidFeatureSlug, OSError):
        return HarnessFeedbackSensor(
            sensor_type="computational",
            name="coverage_debt",
            status="fail",
            output={"error": "coverage_debt_unavailable"},
            ac_ids=(),
        )

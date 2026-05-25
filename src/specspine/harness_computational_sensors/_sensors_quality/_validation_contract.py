from __future__ import annotations

from pathlib import Path

from ...features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    build_feature_trace_report,
)
from ...harness_models import HarnessFeedbackSensor

__all__ = [
    "_build_validation_contract_sensor",
]


def _build_validation_contract_sensor(resolved_root: Path, slug: str) -> HarnessFeedbackSensor:
    try:
        trace = build_feature_trace_report(resolved_root, slug)
        ac_done = sum(1 for item in trace.acceptance_criteria if item.done)
        ac_total = len(trace.acceptance_criteria)
        trace_ac_ids = tuple(
            item.id for item in trace.acceptance_criteria if not item.done
        )
        return HarnessFeedbackSensor(
            sensor_type="computational",
            name="validation_contract",
            status="pass" if ac_done == ac_total and ac_total > 0 else "fail",
            output={
                "acceptance_criteria_done": ac_done,
                "acceptance_criteria_total": ac_total,
            },
            ac_ids=trace_ac_ids,
        )
    except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
        return HarnessFeedbackSensor(
            sensor_type="computational",
            name="validation_contract",
            status="fail",
            output={"error": "validation_contract_unavailable"},
            ac_ids=(),
        )

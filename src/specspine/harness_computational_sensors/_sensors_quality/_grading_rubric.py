from __future__ import annotations

from ...executor import build_grading_rubric
from ...features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
)
from ...harness_models import HarnessFeedbackSensor

__all__ = [
    "_build_grading_rubric_sensor",
]


def _build_grading_rubric_sensor(resolved_root, slug: str) -> HarnessFeedbackSensor:
    try:
        rubric = build_grading_rubric(slug, resolved_root)
        rubric_items = rubric.get("rubric_items", [])
        rubric_pass = sum(1 for item in rubric_items if item.get("current_status") == "pass")
        rubric_total = len(rubric_items)
        rubric_ac_ids = tuple(
            item.get("ac_id", "")
            for item in rubric_items
            if item.get("current_status") != "pass"
        )
        return HarnessFeedbackSensor(
            sensor_type="computational",
            name="grading_rubric",
            status="pass" if rubric_pass == rubric_total and rubric_total > 0 else "fail",
            output={
                "pass_count": rubric_pass,
                "total_count": rubric_total,
            },
            ac_ids=rubric_ac_ids,
        )
    except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
        return HarnessFeedbackSensor(
            sensor_type="computational",
            name="grading_rubric",
            status="fail",
            output={"error": "grading_rubric_unavailable"},
            ac_ids=(),
        )

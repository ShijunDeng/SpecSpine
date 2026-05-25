from __future__ import annotations

from pathlib import Path

from .features import validate_feature_slug
from .harness_models import HarnessFeedbackReport
from .harness_repair_strategies import _classify_root_causes, _collect_gaps_from_sensors, _generate_repair_strategies
from ._harness_quality_builder import build_harness_quality
from ._harness_sensor_orchestrator import collect_harness_sensors, compute_sensor_status

__all__ = [
    "build_harness_feedback",
]


def build_harness_feedback(slug: str, root: Path) -> HarnessFeedbackReport:
    feature_id = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()

    all_sensors = collect_harness_sensors(feature_id, resolved_root)

    gaps = _collect_gaps_from_sensors(all_sensors)
    root_causes = _classify_root_causes(gaps)

    feedback_report = HarnessFeedbackReport(
        feature_id=feature_id,
        status="unknown",
        sensors=tuple(all_sensors),
        repair_strategies=(),
        root_causes=root_causes,
        steering_summary={},
        harness_quality=None,
        safety_notes=(),
    )

    repair_strategies = _generate_repair_strategies(feedback_report)

    overall_status, steering_summary = compute_sensor_status(all_sensors)

    harness_quality = build_harness_quality(resolved_root, feature_id)

    safety_notes = (
        "This harness feedback report is advisory local evidence.",
        "Recommended commands are advisory and are not executed.",
        "SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, read environment variables, or read tokens.",
    )

    return HarnessFeedbackReport(
        feature_id=feature_id,
        status=overall_status,
        sensors=tuple(all_sensors),
        repair_strategies=tuple(repair_strategies),
        root_causes=root_causes,
        steering_summary=steering_summary,
        harness_quality=harness_quality,
        safety_notes=safety_notes,
    )

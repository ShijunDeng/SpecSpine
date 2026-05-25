from __future__ import annotations

from pathlib import Path

from .features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    validate_feature_slug,
)
from .harness_computational import _run_computational_sensors
from .harness_inferential import _run_inferential_sensors
from .harness_models import HarnessFeedbackReport
from .harness_repair_strategies import _classify_root_causes, _collect_gaps_from_sensors, _generate_repair_strategies
from ._harness_quality_builder import build_harness_quality

__all__ = [
    "build_harness_feedback",
]


def build_harness_feedback(slug: str, root: Path) -> HarnessFeedbackReport:
    feature_id = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()

    computational_sensors = _run_computational_sensors(feature_id, resolved_root)
    inferential_sensors = _run_inferential_sensors(feature_id, resolved_root)
    all_sensors = computational_sensors + inferential_sensors

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

    total_sensors = len(all_sensors)
    pass_sensors = sum(1 for s in all_sensors if s.status == "pass")
    fail_sensors = sum(1 for s in all_sensors if s.status == "fail")
    warn_sensors = sum(1 for s in all_sensors if s.status == "warn")

    if fail_sensors == 0 and warn_sensors == 0:
        overall_status = "healthy"
    elif fail_sensors == 0:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    steering_summary = {
        "fail_sensors": fail_sensors,
        "pass_sensors": pass_sensors,
        "repair_strategies_count": len(repair_strategies),
        "total_sensors": total_sensors,
        "warn_sensors": warn_sensors,
    }

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

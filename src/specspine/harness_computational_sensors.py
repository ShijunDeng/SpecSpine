from __future__ import annotations

from pathlib import Path

from .coverage import build_coverage_debt_report
from .executor import build_grading_rubric
from .features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
)
from .harness_models import HarnessFeedbackSensor
from .verification import build_verification_matrix
from .harness_computational_readers import _extract_ac_ids, _read_feature_contents

__all__ = [
    "_run_computational_sensors",
]


def _run_computational_sensors(slug: str, root: Path) -> list[HarnessFeedbackSensor]:
    resolved_root = root.expanduser().resolve()
    sensors: list[HarnessFeedbackSensor] = []

    contents = _read_feature_contents(resolved_root, slug)
    ac_ids = _extract_ac_ids(contents)

    try:
        matrix = build_verification_matrix(resolved_root, slug)
        sensors.append(
            HarnessFeedbackSensor(
                sensor_type="computational",
                name="verification_matrix",
                status="pass" if matrix.ready else "fail",
                output={
                    "verified": matrix.summary.get("verified", 0),
                    "unverified": matrix.summary.get("unverified", 0),
                    "coverage_complete": matrix.summary.get("coverage_complete", 0),
                    "blocking_checks": matrix.summary.get("blocking_checks", 0),
                    "gaps": matrix.summary.get("gaps", 0),
                },
                ac_ids=ac_ids,
            )
        )
    except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
        sensors.append(
            HarnessFeedbackSensor(
                sensor_type="computational",
                name="verification_matrix",
                status="fail",
                output={"error": "verification_matrix_unavailable"},
                ac_ids=(),
            )
        )

    try:
        debt_report = build_coverage_debt_report(resolved_root)
        feature_debt = None
        for feature in debt_report.get("features", []):
            if feature.get("feature_id") == slug:
                feature_debt = feature
                break
        if feature_debt is not None:
            sensors.append(
                HarnessFeedbackSensor(
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
            )
        else:
            sensors.append(
                HarnessFeedbackSensor(
                    sensor_type="computational",
                    name="coverage_debt",
                    status="warn",
                    output={"error": "feature_not_in_debt_report"},
                    ac_ids=(),
                )
            )
    except (InvalidFeatureSlug, OSError):
        sensors.append(
            HarnessFeedbackSensor(
                sensor_type="computational",
                name="coverage_debt",
                status="fail",
                output={"error": "coverage_debt_unavailable"},
                ac_ids=(),
            )
        )

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
        sensors.append(
            HarnessFeedbackSensor(
                sensor_type="computational",
                name="grading_rubric",
                status="pass" if rubric_pass == rubric_total and rubric_total > 0 else "fail",
                output={
                    "pass_count": rubric_pass,
                    "total_count": rubric_total,
                },
                ac_ids=rubric_ac_ids,
            )
        )
    except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
        sensors.append(
            HarnessFeedbackSensor(
                sensor_type="computational",
                name="grading_rubric",
                status="fail",
                output={"error": "grading_rubric_unavailable"},
                ac_ids=(),
            )
        )

    try:
        from .features import build_feature_trace_report

        trace = build_feature_trace_report(resolved_root, slug)
        ac_done = sum(1 for item in trace.acceptance_criteria if item.done)
        ac_total = len(trace.acceptance_criteria)
        trace_ac_ids = tuple(
            item.id for item in trace.acceptance_criteria if not item.done
        )
        sensors.append(
            HarnessFeedbackSensor(
                sensor_type="computational",
                name="validation_contract",
                status="pass" if ac_done == ac_total and ac_total > 0 else "fail",
                output={
                    "acceptance_criteria_done": ac_done,
                    "acceptance_criteria_total": ac_total,
                },
                ac_ids=trace_ac_ids,
            )
        )
    except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
        sensors.append(
            HarnessFeedbackSensor(
                sensor_type="computational",
                name="validation_contract",
                status="fail",
                output={"error": "validation_contract_unavailable"},
                ac_ids=(),
            )
        )

    return sensors

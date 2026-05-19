from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .consistency import build_consistency_report
from .coverage import build_coverage_debt_report
from .executor import build_grading_rubric
from .features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    build_feature_tests_report,
    build_feature_trace_report,
    feature_bundle_paths,
    list_feature_bundles,
    parse_acceptance_criteria,
    validate_feature_slug,
)
from .hygiene import build_hygiene_scan_report
from .security import build_security_cue_report
from .change import build_change_risk_report
from .verification import build_verification_matrix


@dataclass(frozen=True)
class HarnessFeedbackSensor:
    sensor_type: str
    name: str
    status: str
    output: dict[str, Any]
    ac_ids: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "ac_ids": list(self.ac_ids),
            "name": self.name,
            "output": dict(self.output),
            "sensor_type": self.sensor_type,
            "status": self.status,
        }


@dataclass(frozen=True)
class RepairStrategy:
    ac_id: str
    target_file: str
    edit_description: str
    verification_command: str
    success_criteria: str

    def as_dict(self) -> dict[str, str]:
        return {
            "ac_id": self.ac_id,
            "edit_description": self.edit_description,
            "success_criteria": self.success_criteria,
            "target_file": self.target_file,
            "verification_command": self.verification_command,
        }


@dataclass(frozen=True)
class HarnessQualityReport:
    feature_id: str
    governed_dimensions: tuple[str, ...]
    sensor_count: int
    harness_coverage_pct: float
    dimension_scores: dict[str, float]

    def as_dict(self) -> dict[str, Any]:
        return {
            "dimension_scores": dict(self.dimension_scores),
            "feature_id": self.feature_id,
            "governed_dimensions": list(self.governed_dimensions),
            "harness_coverage_pct": round(self.harness_coverage_pct, 2),
            "sensor_count": self.sensor_count,
        }


@dataclass(frozen=True)
class HarnessFeedbackReport:
    feature_id: str
    status: str
    sensors: tuple[HarnessFeedbackSensor, ...]
    repair_strategies: tuple[RepairStrategy, ...]
    root_causes: dict[str, Any]
    steering_summary: dict[str, Any]
    harness_quality: HarnessQualityReport | None
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "feature_id": self.feature_id,
            "repair_strategies": [s.as_dict() for s in self.repair_strategies],
            "root_causes": dict(self.root_causes),
            "safety_notes": list(self.safety_notes),
            "sensors": [s.as_dict() for s in self.sensors],
            "status": self.status,
            "steering_summary": dict(self.steering_summary),
        }
        if self.harness_quality is not None:
            payload["harness_quality"] = self.harness_quality.as_dict()
        return payload


def _read_feature_contents(root: Path, slug: str) -> dict[str, str]:
    paths = feature_bundle_paths(root, slug)
    contents: dict[str, str] = {}
    for kind in ("spec", "execution", "quality"):
        path = paths.get(kind)
        if path and path.exists():
            contents[kind] = path.read_text(encoding="utf-8")
    return contents


def _extract_ac_ids(contents: dict[str, str]) -> tuple[str, ...]:
    spec_content = contents.get("spec", "")
    if not spec_content:
        return ()
    ac_items = parse_acceptance_criteria(spec_content, source_file="")
    return tuple(item.id for item in ac_items)


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


def _generate_repair_strategies(feedback_report: HarnessFeedbackReport) -> list[RepairStrategy]:
    strategies: list[RepairStrategy] = []
    seen_ac_ids: set[str] = set()

    all_failing_ac_ids: set[str] = set()
    for sensor in feedback_report.sensors:
        for ac_id in sensor.ac_ids:
            if ac_id and sensor.status == "fail":
                all_failing_ac_ids.add(ac_id)

    for ac_id in sorted(all_failing_ac_ids):
        if ac_id in seen_ac_ids:
            continue
        seen_ac_ids.add(ac_id)

        sensor_names = [
            sensor.name
            for sensor in feedback_report.sensors
            if ac_id in sensor.ac_ids and sensor.status == "fail"
        ]

        target_file = f"specs/features/{feedback_report.feature_id}.md"
        if "coverage_debt" in sensor_names or "grading_rubric" in sensor_names:
            target_file = f"quality/features/{feedback_report.feature_id}.md"

        edit_description = (
            f"Address acceptance criterion {ac_id} failures detected by: "
            f"{', '.join(sorted(sensor_names))}."
        )

        verification_command = (
            f"specspine verify matrix {feedback_report.feature_id} . --json"
        )

        success_criteria = (
            f"AC {ac_id} must pass verification matrix, coverage debt, and grading rubric checks."
        )

        strategies.append(
            RepairStrategy(
                ac_id=ac_id,
                target_file=target_file,
                edit_description=edit_description,
                verification_command=verification_command,
                success_criteria=success_criteria,
            )
        )

    if not strategies:
        computational_failures = [
            s for s in feedback_report.sensors
            if s.sensor_type == "computational" and s.status == "fail"
        ]
        for sensor in sorted(computational_failures, key=lambda s: s.name):
            if sensor.name not in [s.name for s in [r for r in []]]:
                strategies.append(
                    RepairStrategy(
                        ac_id="SENSOR_FAILURE",
                        target_file=f"specs/features/{feedback_report.feature_id}.md",
                        edit_description=f"Fix {sensor.name} sensor failure: {json.dumps(sensor.output)}",
                        verification_command=f"specspine harness feedback {feedback_report.feature_id} . --json",
                        success_criteria=f"{sensor.name} sensor must return pass status.",
                    )
                )

    return strategies


def _classify_root_causes(gaps: list[dict[str, str]]) -> dict[str, Any]:
    categories: dict[str, list[dict[str, str]]] = {
        "missing_spec": [],
        "missing_code": [],
        "missing_test": [],
        "stale_coverage": [],
        "contract_violation": [],
    }

    for gap in gaps:
        gap_id = gap.get("id", "")
        gap_message = gap.get("message", "").lower()

        if any(
            kw in gap_id.lower() or kw in gap_message
            for kw in ("missing_file", "missing_spec", "spec")
        ):
            categories["missing_spec"].append(gap)
        elif any(
            kw in gap_id.lower() or kw in gap_message
            for kw in ("missing_code", "implementation", "not_implemented")
        ):
            categories["missing_code"].append(gap)
        elif any(
            kw in gap_id.lower() or kw in gap_message
            for kw in ("missing_test", "test_coverage", "coverage", "no test")
        ):
            categories["missing_test"].append(gap)
        elif any(
            kw in gap_id.lower() or kw in gap_message
            for kw in ("stale", "outdated", "unknown_acceptance")
        ):
            categories["stale_coverage"].append(gap)
        else:
            categories["contract_violation"].append(gap)

    return {
        category: items
        for category, items in categories.items()
    }


def _collect_gaps_from_sensors(sensors: list[HarnessFeedbackSensor]) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    for sensor in sensors:
        if sensor.status == "fail":
            gaps.append(
                {
                    "id": f"sensor:{sensor.name}",
                    "message": f"Sensor {sensor.name} returned status: {sensor.status}",
                    "sensor_type": sensor.sensor_type,
                }
            )
        for ac_id in sensor.ac_ids:
            gaps.append(
                {
                    "id": ac_id,
                    "message": f"AC {ac_id} flagged by sensor {sensor.name}",
                    "sensor_type": sensor.sensor_type,
                }
            )
    return gaps


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


def build_harness_quality(root: Path, feature_id: str = "") -> HarnessQualityReport:
    resolved_root = root.expanduser().resolve()
    dimensions = (
        "verification",
        "coverage",
        "grading",
        "validation",
        "consistency",
        "hygiene",
        "security",
        "change_risk",
    )

    sensors: list[HarnessFeedbackSensor] = []
    if feature_id:
        try:
            computational = _run_computational_sensors(feature_id, resolved_root)
            inferential = _run_inferential_sensors(feature_id, resolved_root)
            sensors = computational + inferential
        except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
            sensors = []
    else:
        bundles = list_feature_bundles(resolved_root)
        for bundle in bundles:
            slug = str(bundle["slug"])
            try:
                computational = _run_computational_sensors(slug, resolved_root)
                inferential = _run_inferential_sensors(slug, resolved_root)
                sensors.extend(computational + inferential)
            except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
                continue

    sensor_count = len(sensors)
    pass_count = sum(1 for s in sensors if s.status == "pass")
    harness_coverage_pct = (pass_count / sensor_count * 100) if sensor_count > 0 else 0.0

    dimension_scores: dict[str, float] = {}
    sensor_by_dimension: dict[str, list[HarnessFeedbackSensor]] = {
        "verification": [s for s in sensors if s.name == "verification_matrix"],
        "coverage": [s for s in sensors if s.name == "coverage_debt"],
        "grading": [s for s in sensors if s.name == "grading_rubric"],
        "validation": [s for s in sensors if s.name == "validation_contract"],
        "consistency": [s for s in sensors if s.name == "consistency_scan"],
        "hygiene": [s for s in sensors if s.name == "hygiene_scan"],
        "security": [s for s in sensors if s.name == "security_cues"],
        "change_risk": [s for s in sensors if s.name == "change_risk"],
    }

    for dimension, dim_sensors in sensor_by_dimension.items():
        if not dim_sensors:
            dimension_scores[dimension] = 0.0
        else:
            dim_pass = sum(1 for s in dim_sensors if s.status == "pass")
            dimension_scores[dimension] = (dim_pass / len(dim_sensors)) * 100

    resolved_feature_id = feature_id if feature_id else "workspace"

    return HarnessQualityReport(
        feature_id=resolved_feature_id,
        governed_dimensions=dimensions,
        sensor_count=sensor_count,
        harness_coverage_pct=harness_coverage_pct,
        dimension_scores=dimension_scores,
    )


def render_harness_feedback_json(report: HarnessFeedbackReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_harness_feedback_text(report: HarnessFeedbackReport) -> str:
    lines = [
        f"Harness feedback: {report.feature_id}",
        f"Status: {report.status}",
        "",
        "Sensors:",
    ]
    for sensor in report.sensors:
        ac_info = f" ac_ids={','.join(sensor.ac_ids)}" if sensor.ac_ids else ""
        lines.append(
            f"  - [{sensor.status}] {sensor.sensor_type}/{sensor.name}{ac_info}"
        )

    lines.extend(["", "Repair strategies:"])
    if report.repair_strategies:
        for strategy in report.repair_strategies:
            lines.append(
                f"  - {strategy.ac_id}: {strategy.edit_description}"
            )
            lines.append(f"    target: {strategy.target_file}")
            lines.append(f"    verify: {strategy.verification_command}")
            lines.append(f"    success: {strategy.success_criteria}")
    else:
        lines.append("- None.")

    lines.extend(["", "Root causes:"])
    for category, items in report.root_causes.items():
        if items:
            lines.append(f"  - {category}: {len(items)} item(s)")
        else:
            lines.append(f"  - {category}: none")

    lines.extend(["", f"Steering: pass={report.steering_summary.get('pass_sensors', 0)} "
                      f"fail={report.steering_summary.get('fail_sensors', 0)} "
                      f"warn={report.steering_summary.get('warn_sensors', 0)} "
                      f"total={report.steering_summary.get('total_sensors', 0)}"])

    if report.harness_quality:
        lines.extend([
            "",
            f"Harness quality: {report.harness_quality.harness_coverage_pct}% coverage",
        ])

    lines.extend(["", "Safety notes:"])
    for note in report.safety_notes:
        lines.append(f"  - {note}")

    return "\n".join(lines) + "\n"


def render_harness_quality_json(report: HarnessQualityReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_harness_quality_text(report: HarnessQualityReport) -> str:
    lines = [
        f"Harness quality: {report.feature_id}",
        f"Coverage: {report.harness_coverage_pct}%",
        f"Sensors: {report.sensor_count}",
        "",
        "Dimensions:",
    ]
    for dimension in report.governed_dimensions:
        score = report.dimension_scores.get(dimension, 0.0)
        lines.append(f"  - {dimension}: {score}%")

    lines.extend(["", "Safety notes:"])
    lines.append("  - This harness quality report is advisory local evidence.")
    lines.append("  - SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, read environment variables, or read tokens.")

    return "\n".join(lines) + "\n"

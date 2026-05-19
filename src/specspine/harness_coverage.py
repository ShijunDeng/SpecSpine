from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    list_feature_bundles,
    validate_feature_slug,
)
from .harness import (
    HarnessFeedbackSensor,
    build_harness_quality,
)
from .policy import load_workspace_policy

GOVERNED_DIMENSIONS = (
    "verification",
    "coverage",
    "grading",
    "validation",
    "consistency",
    "hygiene",
    "security",
    "change_risk",
)

DIMENSION_SENSOR_MAP = {
    "verification": "verification_matrix",
    "coverage": "coverage_debt",
    "grading": "grading_rubric",
    "validation": "validation_contract",
    "consistency": "consistency_scan",
    "hygiene": "hygiene_scan",
    "security": "security_cues",
    "change_risk": "change_risk",
}

MATURITY_LABELS = {
    0: "none",
    1: "initial",
    2: "managed",
    3: "defined",
    4: "optimized",
    5: "mastered",
}


@dataclass(frozen=True)
class HarnessDimensionCoverage:
    dimension_name: str
    sensor_count: int
    pass_count: int
    coverage_pct: float
    missing_sensors: tuple[str, ...] = ()
    redundant_sensors: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "coverage_pct": round(self.coverage_pct, 2),
            "dimension_name": self.dimension_name,
            "missing_sensors": list(self.missing_sensors),
            "pass_count": self.pass_count,
            "redundant_sensors": list(self.redundant_sensors),
            "sensor_count": self.sensor_count,
        }


@dataclass(frozen=True)
class HarnessCoverageReport:
    feature_id: str
    dimensions: tuple[HarnessDimensionCoverage, ...]
    maturity_score: int
    blind_spots: tuple[str, ...]
    improvement_plan: tuple[str, ...]
    baseline_comparison: dict[str, Any] = field(default_factory=dict)
    safety_notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "baseline_comparison": self.baseline_comparison,
            "blind_spots": list(self.blind_spots),
            "dimensions": [d.as_dict() for d in self.dimensions],
            "feature_id": self.feature_id,
            "improvement_plan": list(self.improvement_plan),
            "maturity_score": self.maturity_score,
            "safety_notes": list(self.safety_notes),
        }


def _collect_sensors_for_feature(root: Path, slug: str) -> list[HarnessFeedbackSensor]:
    resolved_root = root.expanduser().resolve()
    try:
        quality_report = build_harness_quality(resolved_root, slug)
    except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
        return []

    sensors: list[HarnessFeedbackSensor] = []
    sensor_by_dimension: dict[str, list[HarnessFeedbackSensor]] = {
        "verification": [],
        "coverage": [],
        "grading": [],
        "validation": [],
        "consistency": [],
        "hygiene": [],
        "security": [],
        "change_risk": [],
    }

    all_sensors_by_name: dict[str, list[HarnessFeedbackSensor]] = {}

    bundles = list_feature_bundles(resolved_root)
    feature_bundles = [b for b in bundles if b.get("slug") == slug]
    if feature_bundles:
        try:
            from .harness import _run_computational_sensors, _run_inferential_sensors
            computational = _run_computational_sensors(slug, resolved_root)
            inferential = _run_inferential_sensors(slug, resolved_root)
            all_s = computational + inferential
            for s in all_s:
                all_sensors_by_name.setdefault(s.name, []).append(s)
        except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
            pass

    for dim, sensor_name in DIMENSION_SENSOR_MAP.items():
        dim_sensors = all_sensors_by_name.get(sensor_name, [])
        sensor_by_dimension[dim] = dim_sensors

    for dim, dim_sensors in sensor_by_dimension.items():
        sensors.extend(dim_sensors)

    return sensors


def _evaluate_dimensions(slug: str, root: Path) -> list[HarnessDimensionCoverage]:
    resolved_root = root.expanduser().resolve()
    dimensions: list[HarnessDimensionCoverage] = []

    all_sensors_by_name: dict[str, list[HarnessFeedbackSensor]] = {}
    try:
        from .harness import _run_computational_sensors, _run_inferential_sensors
        computational = _run_computational_sensors(slug, resolved_root)
        inferential = _run_inferential_sensors(slug, resolved_root)
        all_s = computational + inferential
        for s in all_s:
            all_sensors_by_name.setdefault(s.name, []).append(s)
    except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
        pass

    for dim in GOVERNED_DIMENSIONS:
        sensor_name = DIMENSION_SENSOR_MAP[dim]
        dim_sensors = all_sensors_by_name.get(sensor_name, [])
        sensor_count = len(dim_sensors)
        pass_count = sum(1 for s in dim_sensors if s.status == "pass")
        coverage_pct = (pass_count / sensor_count * 100) if sensor_count > 0 else 0.0

        missing_sensors: tuple[str, ...] = ()
        if sensor_count == 0:
            missing_sensors = (sensor_name,)

        redundant: list[str] = []
        if sensor_count > 1:
            ac_sets = [frozenset(s.ac_ids) for s in dim_sensors]
            for i in range(len(dim_sensors)):
                for j in range(i + 1, len(dim_sensors)):
                    if ac_sets[i] & ac_sets[j]:
                        redundant.append(dim_sensors[i].name)
                        redundant.append(dim_sensors[j].name)
            redundant_sensors = tuple(sorted(set(redundant)))
        else:
            redundant_sensors = ()

        dimensions.append(
            HarnessDimensionCoverage(
                dimension_name=dim,
                sensor_count=sensor_count,
                pass_count=pass_count,
                coverage_pct=round(coverage_pct, 2),
                missing_sensors=missing_sensors,
                redundant_sensors=redundant_sensors,
            )
        )

    return dimensions


def _detect_blind_spots(dimensions: list[HarnessDimensionCoverage]) -> list[str]:
    return [
        d.dimension_name
        for d in dimensions
        if d.sensor_count == 0
    ]


def _detect_redundancy(dimensions: list[HarnessDimensionCoverage]) -> list[dict[str, Any]]:
    redundancy_info: list[dict[str, Any]] = []
    for d in dimensions:
        if d.redundant_sensors:
            redundancy_info.append({
                "dimension": d.dimension_name,
                "redundant_sensors": list(d.redundant_sensors),
            })
    return redundancy_info


def _compute_maturity_score(dimensions: list[HarnessDimensionCoverage]) -> int:
    if not dimensions:
        return 0

    total_sensors = sum(d.sensor_count for d in dimensions)
    if total_sensors == 0:
        return 0

    pass_sensors = sum(d.pass_count for d in dimensions)
    overall_coverage = pass_sensors / total_sensors * 100

    dimensions_with_sensors = sum(1 for d in dimensions if d.sensor_count > 0)
    dimensions_fully_covered = sum(1 for d in dimensions if d.coverage_pct >= 100.0)
    dimensions_no_blind = sum(1 for d in dimensions if d.missing_sensors == ())

    if dimensions_fully_covered == len(dimensions) and dimensions_no_blind == len(dimensions):
        return 5

    if dimensions_fully_covered >= len(dimensions) * 0.75 and overall_coverage >= 90:
        return 4

    if dimensions_with_sensors >= len(dimensions) * 0.75 and overall_coverage >= 70:
        return 3

    if dimensions_with_sensors >= len(dimensions) * 0.5 and overall_coverage >= 50:
        return 2

    if total_sensors > 0:
        return 1

    return 0


def _generate_improvement_plan(
    dimensions: list[HarnessDimensionCoverage],
    blind_spots: list[str],
) -> list[str]:
    plan: list[str] = []

    for spot in blind_spots:
        sensor_name = DIMENSION_SENSOR_MAP.get(spot, spot)
        plan.append(f"Add {sensor_name} sensor to cover {spot} dimension.")

    for d in sorted(dimensions, key=lambda x: x.coverage_pct):
        if d.coverage_pct > 0 and d.coverage_pct < 100:
            plan.append(
                f"Improve {d.dimension_name} dimension coverage from "
                f"{d.coverage_pct}% to 100%."
            )
        if d.redundant_sensors:
            plan.append(
                f"Review redundant sensors in {d.dimension_name}: "
                f"{', '.join(d.redundant_sensors)}."
            )

    maturity = _compute_maturity_score(dimensions)
    if maturity < 3:
        plan.append(
            f"Current harness maturity is {maturity} ({MATURITY_LABELS[maturity]}); "
            f"target level 3 (defined) or higher."
        )

    return plan


def _load_baseline(root: Path) -> dict[str, Any] | None:
    resolved_root = root.expanduser().resolve()
    baseline_path = resolved_root / ".specspine" / "harness-baseline.json"
    if not baseline_path.exists():
        return None
    try:
        content = baseline_path.read_text(encoding="utf-8")
        return json.loads(content)
    except (OSError, json.JSONDecodeError):
        return None


def _save_baseline(root: Path, report: HarnessCoverageReport) -> None:
    resolved_root = root.expanduser().resolve()
    baseline_dir = resolved_root / ".specspine"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    baseline_path = baseline_dir / "harness-baseline.json"
    data = report.as_dict()
    baseline_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _compare_with_baseline(
    report: HarnessCoverageReport,
    baseline: dict[str, Any],
) -> dict[str, Any]:
    comparison: dict[str, Any] = {}

    baseline_maturity = baseline.get("maturity_score", 0)
    comparison["maturity_delta"] = report.maturity_score - baseline_maturity
    comparison["baseline_maturity"] = baseline_maturity
    comparison["current_maturity"] = report.maturity_score

    baseline_dimensions = {
        d["dimension_name"]: d
        for d in baseline.get("dimensions", [])
    }

    dimension_deltas: list[dict[str, Any]] = []
    for d in report.dimensions:
        baseline_d = baseline_dimensions.get(d.dimension_name, {})
        baseline_pct = baseline_d.get("coverage_pct", 0.0)
        delta = round(d.coverage_pct - baseline_pct, 2)
        dimension_deltas.append({
            "dimension": d.dimension_name,
            "baseline_coverage_pct": baseline_pct,
            "current_coverage_pct": d.coverage_pct,
            "delta": delta,
        })

    comparison["dimension_deltas"] = dimension_deltas

    baseline_blind = set(baseline.get("blind_spots", []))
    current_blind = set(report.blind_spots)
    comparison["new_blind_spots"] = sorted(current_blind - baseline_blind)
    comparison["resolved_blind_spots"] = sorted(baseline_blind - current_blind)

    if comparison["maturity_delta"] > 0:
        comparison["trend"] = "improving"
    elif comparison["maturity_delta"] < 0:
        comparison["trend"] = "regressing"
    else:
        comparison["trend"] = "stable"

    return comparison


def build_harness_coverage_report(
    root: Path,
    feature_filter: str | None = None,
) -> HarnessCoverageReport:
    resolved_root = root.expanduser().resolve()

    if feature_filter:
        slug = validate_feature_slug(feature_filter)
        dimensions = _evaluate_dimensions(slug, resolved_root)
        feature_id = slug
    else:
        all_dimensions: list[HarnessDimensionCoverage] = []
        bundles = list_feature_bundles(resolved_root)
        for bundle in bundles:
            slug = str(bundle["slug"])
            try:
                bundle_dimensions = _evaluate_dimensions(slug, resolved_root)
                all_dimensions.extend(bundle_dimensions)
            except (InvalidFeatureSlug, OSError):
                continue

        aggregated: dict[str, dict[str, Any]] = {}
        for d in all_dimensions:
            if d.dimension_name not in aggregated:
                aggregated[d.dimension_name] = {
                    "dimension_name": d.dimension_name,
                    "sensor_count": 0,
                    "pass_count": 0,
                    "missing_sensors": set(),
                    "redundant_sensors": set(),
                }
            agg = aggregated[d.dimension_name]
            agg["sensor_count"] += d.sensor_count
            agg["pass_count"] += d.pass_count
            agg["missing_sensors"].update(d.missing_sensors)
            agg["redundant_sensors"].update(d.redundant_sensors)

        dimensions = []
        for dim in GOVERNED_DIMENSIONS:
            if dim in aggregated:
                agg = aggregated[dim]
                total = agg["sensor_count"]
                passed = agg["pass_count"]
                pct = (passed / total * 100) if total > 0 else 0.0
                dimensions.append(
                    HarnessDimensionCoverage(
                        dimension_name=dim,
                        sensor_count=total,
                        pass_count=passed,
                        coverage_pct=round(pct, 2),
                        missing_sensors=tuple(sorted(agg["missing_sensors"])),
                        redundant_sensors=tuple(sorted(agg["redundant_sensors"])),
                    )
                )
            else:
                dimensions.append(
                    HarnessDimensionCoverage(
                        dimension_name=dim,
                        sensor_count=0,
                        pass_count=0,
                        coverage_pct=0.0,
                        missing_sensors=(DIMENSION_SENSOR_MAP[dim],),
                        redundant_sensors=(),
                    )
                )

        feature_id = "workspace"

    blind_spots = _detect_blind_spots(dimensions)
    improvement_plan = _generate_improvement_plan(dimensions, blind_spots)
    maturity_score = _compute_maturity_score(dimensions)

    baseline = _load_baseline(resolved_root)
    baseline_comparison: dict[str, Any] = {}
    if baseline is not None:
        baseline_comparison = _compare_with_baseline(
            HarnessCoverageReport(
                feature_id=feature_id,
                dimensions=tuple(dimensions),
                maturity_score=maturity_score,
                blind_spots=tuple(blind_spots),
                improvement_plan=tuple(improvement_plan),
            ),
            baseline,
        )

    safety_notes = (
        "This harness coverage report is advisory local evidence.",
        "SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, read environment variables, or read tokens.",
    )

    return HarnessCoverageReport(
        feature_id=feature_id,
        dimensions=tuple(dimensions),
        maturity_score=maturity_score,
        blind_spots=tuple(blind_spots),
        improvement_plan=tuple(improvement_plan),
        baseline_comparison=baseline_comparison,
        safety_notes=safety_notes,
    )


def render_harness_coverage_json(report: HarnessCoverageReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_harness_coverage_text(report: HarnessCoverageReport) -> str:
    lines = [
        f"Harness coverage: {report.feature_id}",
        f"Maturity: {report.maturity_score} ({MATURITY_LABELS.get(report.maturity_score, 'unknown')})",
        "",
        "Dimensions:",
    ]
    for d in report.dimensions:
        status = "pass" if d.coverage_pct >= 100 else "partial" if d.coverage_pct > 0 else "missing"
        lines.append(
            f"  [{status}] {d.dimension_name}: {d.coverage_pct}% "
            f"({d.pass_count}/{d.sensor_count} sensors)"
        )
        if d.missing_sensors:
            lines.append(f"    missing: {', '.join(d.missing_sensors)}")
        if d.redundant_sensors:
            lines.append(f"    redundant: {', '.join(d.redundant_sensors)}")

    if report.blind_spots:
        lines.extend(["", "Blind spots:"])
        for spot in report.blind_spots:
            lines.append(f"  - {spot}")

    if report.improvement_plan:
        lines.extend(["", "Improvement plan:"])
        for i, item in enumerate(report.improvement_plan, 1):
            lines.append(f"  {i}. {item}")

    if report.baseline_comparison:
        lines.extend(["", "Baseline comparison:"])
        trend = report.baseline_comparison.get("trend", "unknown")
        delta = report.baseline_comparison.get("maturity_delta", 0)
        lines.append(f"  Trend: {trend} (maturity delta: {delta:+d})")

    lines.extend(["", "Safety notes:"])
    for note in report.safety_notes:
        lines.append(f"  - {note}")

    return "\n".join(lines) + "\n"

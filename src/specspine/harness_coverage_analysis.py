from __future__ import annotations

from pathlib import Path
from typing import Any

from .features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    list_feature_bundles,
    validate_feature_slug,
)

from .harness_coverage_models import (
    DIMENSION_SENSOR_MAP,
    GOVERNED_DIMENSIONS,
    HarnessCoverageReport,
    HarnessDimensionCoverage,
)
from .harness_coverage_sensors import _evaluate_dimensions
from .harness_coverage_analysis_metrics import (
    _detect_blind_spots,
    _detect_redundancy,
    _generate_improvement_plan,
    _compute_maturity_score,
)
from .harness_coverage_baseline import (
    _load_baseline,
    _save_baseline,
    _compare_with_baseline,
)

__all__ = [
    "_detect_blind_spots",
    "_detect_redundancy",
    "_compute_maturity_score",
    "_generate_improvement_plan",
    "_load_baseline",
    "_save_baseline",
    "_compare_with_baseline",
    "build_harness_coverage_report",
]


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

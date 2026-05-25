from __future__ import annotations

from typing import Any

from .harness_coverage_models import HarnessCoverageReport

__all__ = [
    "_compare_with_baseline",
]


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

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .harness_coverage_models import HarnessCoverageReport

__all__ = [
    "_load_baseline",
    "_save_baseline",
    "_compare_with_baseline",
]


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

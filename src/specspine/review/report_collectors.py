from __future__ import annotations

from pathlib import Path

from ..gates import build_quality_gate_report
from ..impact import build_test_impact_report
from ..validation import build_validation_report, build_validation_summary

__all__ = [
    "collect_reports",
]


def collect_reports(
    resolved_root: Path,
    feature_slug: str | None,
    changed_files: tuple[str, ...],
) -> dict[str, object]:
    validation_report = build_validation_report(
        resolved_root,
        include_fusion=True,
        include_features=True,
    )
    validation = build_validation_summary(
        validation_report,
        included={
            "workspace": True,
            "fusion": True,
            "features": True,
            "adapters": False,
        },
    )
    gates = build_quality_gate_report(resolved_root)
    impact = build_test_impact_report(
        resolved_root,
        changed_files=changed_files,
        feature=feature_slug,
    )
    return {
        "validation": validation,
        "gates": gates,
        "impact": impact,
    }

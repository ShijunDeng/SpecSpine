from __future__ import annotations

from pathlib import Path

from .gates import build_quality_gate_report
from .health_models import QualityGates

__all__ = [
    "_build_quality_gates",
]


def _build_quality_gates(root: Path) -> QualityGates:
    try:
        report = build_quality_gate_report(root)
    except OSError:
        return QualityGates(
            required_total=0,
            required_done=0,
            required_open=0,
            definition_total=0,
        )

    summary = report.summary
    return QualityGates(
        required_total=int(summary.get("required_total", 0)),
        required_done=int(summary.get("required_done", 0)),
        required_open=int(summary.get("required_open", 0)),
        definition_total=int(summary.get("definition_total", 0)),
    )

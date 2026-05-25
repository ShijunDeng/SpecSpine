from __future__ import annotations

from pathlib import Path

from .drift_models import DriftEvent

__all__ = [
    "_classify_severity",
]


def _classify_severity(
    spec_events: list[DriftEvent],
    code_events: list[DriftEvent],
    test_events: list[DriftEvent],
    quality_events: list[DriftEvent],
) -> str:
    all_events = spec_events + code_events + test_events + quality_events
    if not all_events:
        return "none"

    severity_order = ["critical", "high", "medium", "low"]
    for sev in severity_order:
        for ev in all_events:
            if ev.severity == sev:
                return sev
    return "none"

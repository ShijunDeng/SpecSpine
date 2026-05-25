from __future__ import annotations

from pathlib import Path

from .security import build_security_cue_report
from .health_models import SecuritySummary

__all__ = [
    "_build_security_summary",
]


def _build_security_summary(root: Path) -> SecuritySummary:
    try:
        report = build_security_cue_report(root)
    except OSError:
        return SecuritySummary(
            cues_total=0,
            high=0,
            medium=0,
            low=0,
        )

    summary = report.summary
    return SecuritySummary(
        cues_total=summary.get("cues_total", 0),
        high=summary.get("high", 0),
        medium=summary.get("medium", 0),
        low=summary.get("low", 0),
    )

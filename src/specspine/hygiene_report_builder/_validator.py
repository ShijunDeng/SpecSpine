from __future__ import annotations

from ..hygiene_models import HygieneReport

__all__ = [
    "hygiene_report_has_strict_findings",
]


def hygiene_report_has_strict_findings(report: HygieneReport) -> bool:
    counts = report.summary["by_severity"]
    return bool(counts.get("critical", 0) or counts.get("high", 0))

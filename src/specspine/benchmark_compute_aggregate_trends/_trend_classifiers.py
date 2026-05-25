from __future__ import annotations

__all__ = [
    "_classify_coverage_trend",
    "_classify_drift_trend",
    "_classify_validation_trend",
]


def _classify_coverage_trend(avg_cov: float) -> str:
    if avg_cov >= 80:
        return "healthy"
    if avg_cov < 30:
        return "declining"
    return "stable"


def _classify_drift_trend(avg_drift: float) -> str:
    if avg_drift > 5:
        return "increasing"
    if avg_drift < 1:
        return "improving"
    return "stable"


def _classify_validation_trend(val_pass_rate: float) -> str:
    if val_pass_rate >= 0.9:
        return "healthy"
    if val_pass_rate < 0.5:
        return "declining"
    return "stable"

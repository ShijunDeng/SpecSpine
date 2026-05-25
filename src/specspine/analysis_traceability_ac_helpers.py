from __future__ import annotations

import re

from .features import FeatureReadyCheck
from .analysis_models import AC_REFERENCE_RE

__all__ = [
    "_normalize_ac_id",
    "_referenced_ac_ids",
    "_coverage_ac_id",
    "_ready_check_severity",
    "_ready_check_category",
]


def _normalize_ac_id(value: str) -> str:
    match = AC_REFERENCE_RE.search(value)
    if match is None:
        return "unknown"
    return f"AC{int(match.group(1)):03d}"


def _referenced_ac_ids(text: str) -> set[str]:
    return {f"AC{int(match.group(1)):03d}" for match in AC_REFERENCE_RE.finditer(text)}


def _coverage_ac_id(link) -> str:
    if link.acceptance_criterion_id != "unknown":
        return _normalize_ac_id(link.acceptance_criterion_id)
    return _normalize_ac_id(link.text)


def _ready_check_severity(check: FeatureReadyCheck) -> str:
    if check.id in {"feature.bundle_files", "feature.status_consistency"}:
        return "high"
    if check.id in {
        "feature.trace_gaps",
        "feature.acceptance_criteria",
        "feature.required_checks",
        "feature.test_plan",
        "feature.test_coverage",
    }:
        return "medium"
    return "low"


def _ready_check_category(check: FeatureReadyCheck) -> str:
    if check.id == "feature.test_coverage":
        return "coverage"
    if check.id in {"feature.bundle_files", "feature.status_consistency"}:
        return "artifact"
    return "readiness"

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "WorkspaceHealth",
    "FeaturePipeline",
    "ValidationHealth",
    "CoverageDebt",
    "ConsistencyDrift",
]


@dataclass(frozen=True)
class WorkspaceHealth:
    complete: bool
    present: tuple[str, ...]
    missing: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "complete": self.complete,
            "missing": list(self.missing),
            "present": list(self.present),
        }


@dataclass(frozen=True)
class FeaturePipeline:
    features_total: int
    by_status: dict[str, int]

    def as_dict(self) -> dict[str, Any]:
        return {
            "by_status": dict(self.by_status),
            "features_total": self.features_total,
        }


@dataclass(frozen=True)
class ValidationHealth:
    ok: bool
    pass_count: int
    fail_count: int
    warn_count: int
    skip_count: int
    total: int
    top_failing_rules: tuple[dict[str, str], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "fail_count": self.fail_count,
            "ok": self.ok,
            "pass_count": self.pass_count,
            "skip_count": self.skip_count,
            "top_failing_rules": list(self.top_failing_rules),
            "total": self.total,
            "warn_count": self.warn_count,
        }


@dataclass(frozen=True)
class CoverageDebt:
    features_with_debt: int
    missing_acceptance_criteria: int
    covered_acceptance_criteria: int
    acceptance_criteria_total: int
    top_features_with_uncovered_ac: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "acceptance_criteria_total": self.acceptance_criteria_total,
            "covered_acceptance_criteria": self.covered_acceptance_criteria,
            "features_with_debt": self.features_with_debt,
            "missing_acceptance_criteria": self.missing_acceptance_criteria,
            "top_features_with_uncovered_ac": list(self.top_features_with_uncovered_ac),
        }


@dataclass(frozen=True)
class ConsistencyDrift:
    features_scanned: int
    checks_pass: int
    checks_fail: int
    checks_warn: int
    checks_total: int
    top_failing_features: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "checks_fail": self.checks_fail,
            "checks_pass": self.checks_pass,
            "checks_total": self.checks_total,
            "checks_warn": self.checks_warn,
            "features_scanned": self.features_scanned,
            "top_failing_features": list(self.top_failing_features),
        }

from __future__ import annotations

from dataclasses import dataclass

from ._ready_check import FeatureReadyCheck

__all__ = [
    "FeatureReadyReport",
]


@dataclass(frozen=True)
class FeatureReadyReport:
    feature_id: str
    ready: bool
    status: str
    checks: tuple[FeatureReadyCheck, ...]
    missing_files: tuple[str, ...]
    gaps: tuple[dict[str, str], ...]
    coverage_required: bool = False
    policy_applied: bool = False
    coverage_required_by_policy: bool = False
    policy_source: str | None = None

    @property
    def blocking_checks(self) -> tuple[FeatureReadyCheck, ...]:
        return tuple(check for check in self.checks if check.status == "fail")

    @property
    def summary(self) -> dict[str, int]:
        passed = sum(1 for check in self.checks if check.status == "pass")
        total = len(self.checks)
        return {
            "fail": total - passed,
            "pass": passed,
            "total": total,
        }

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "blocking_checks": [
                check.as_dict() for check in self.blocking_checks
            ],
            "checks": [check.as_dict() for check in self.checks],
            "feature_id": self.feature_id,
            "gaps": [dict(gap) for gap in self.gaps],
            "missing_files": list(self.missing_files),
            "ready": self.ready,
            "status": self.status,
            "summary": self.summary,
        }
        if self.coverage_required:
            payload["coverage_required"] = True
        if self.policy_applied:
            payload["coverage_required_by_policy"] = self.coverage_required_by_policy
            payload["policy_applied"] = True
            payload["policy_source"] = self.policy_source
        return payload

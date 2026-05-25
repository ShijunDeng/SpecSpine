from __future__ import annotations

from typing import Any

from .policy import WorkspacePolicy

__all__ = [
    "_invalid_readiness_record",
]


def _invalid_readiness_record(
    feature: dict[str, object],
    *,
    reason: str,
    require_coverage: bool,
    use_policy: bool,
    policy_coverage_required: bool = False,
    policy: WorkspacePolicy | None = None,
) -> dict[str, Any]:
    slug = str(feature["slug"])
    missing_files = [str(path) for path in feature.get("missing_files", [])]
    record: dict[str, Any] = {
        "feature_id": slug,
        "status": "invalid",
        "ready": False,
        "coverage_required": require_coverage,
        "policy_coverage_required": policy_coverage_required,
        "blocking_checks": 1,
        "gaps": max(1, len(missing_files)),
        "missing_files": missing_files,
        "next_actions": [reason],
        "recommended_commands": [],
    }
    if use_policy and policy is not None:
        record["policy_applied"] = True
        record["policy_source"] = str(policy.source_file)
    return record

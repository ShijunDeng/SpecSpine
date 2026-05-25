from __future__ import annotations

import hashlib
from typing import Any

from ..drift_models import DriftAuditReport

__all__ = [
    "_build_compliance_section",
    "_severity_distribution",
]


def _build_compliance_section(report: DriftAuditReport) -> dict[str, Any]:
    evidence_parts: list[str] = [
        str(report.root),
        report.scan_metadata.get("timestamp", ""),
        report.scan_metadata.get("git_commit", ""),
    ]
    for f in report.features:
        evidence_parts.append(f.feature_id)
        evidence_parts.append(f.severity)
        for ev in f.drift_events:
            evidence_parts.append(ev.event_type)
            evidence_parts.append(ev.severity)
            evidence_parts.append(ev.description)

    evidence_str = "\n".join(sorted(evidence_parts))
    evidence_hash = hashlib.sha256(evidence_str.encode("utf-8")).hexdigest()

    pass_fail: dict[str, str] = {}
    dimensions = ["spec", "code", "test", "quality"]
    for dim in dimensions:
        has_drift = False
        for f in report.features:
            if dim == "spec" and f.spec_drift:
                has_drift = True
            elif dim == "code" and f.code_drift:
                has_drift = True
            elif dim == "test" and f.test_drift:
                has_drift = True
            elif dim == "quality" and f.quality_drift:
                has_drift = True
        pass_fail[dim] = "fail" if has_drift else "pass"

    return {
        "evidence_hash": evidence_hash,
        "pass_fail_per_dimension": pass_fail,
    }


def _severity_distribution(features: tuple) -> dict[str, int]:
    dist: dict[str, int] = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "none": 0,
    }
    for f in features:
        dist[f.severity] = dist.get(f.severity, 0) + 1
    return dist

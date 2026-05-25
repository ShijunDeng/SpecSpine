from __future__ import annotations

from pathlib import Path

from .audit_models import ComplianceReport
from .audit_report_summary import _generate_compliance_summary
from ._compliance_recommendations import _generate_recommendations

__all__ = [
    "_now_iso",
    "_finalize_compliance_report",
]


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finalize_compliance_report(
    resolved_root: Path,
    feature_filter: str | None,
    trails: list,
    evidence_hashes: list[str],
) -> ComplianceReport:
    summary = _generate_compliance_summary(trails)
    recommendations = _generate_recommendations(summary.get("gaps", []))
    feature_tuple = tuple(sorted(trails, key=lambda t: t.feature_id))

    return ComplianceReport(
        root=resolved_root,
        audit_date=_now_iso(),
        scope="feature" if feature_filter else "workspace",
        features=feature_tuple,
        compliance_summary=summary,
        evidence_hashes=tuple(evidence_hashes),
        recommendations=tuple(recommendations),
        safety_notes=(
            "This audit report reads local workspace files and git history only.",
            "SpecSpine did not run tests, invoke subprocesses (except git log/show), call network services, call GitHub APIs, invoke upstream CLIs, or read tokens.",
            "All evidence hashes are SHA-256 digests of file contents at read time.",
        ),
    )

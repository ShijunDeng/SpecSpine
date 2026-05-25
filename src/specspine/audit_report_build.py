from __future__ import annotations

from pathlib import Path

from .audit_events import (
    _build_lifecycle_transitions,
    _collect_audit_events,
    _hash_content,
)
from .audit_models import AuditTrail, ComplianceReport
from .audit_report_summary import _generate_compliance_summary
from .audit_validation import (
    _build_drift_history,
    _gather_validation_evidence,
)
from .features import (
    list_feature_bundles,
    validate_feature_slug,
)


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_compliance_report(
    root: Path,
    feature_filter: str | None = None,
    since: str | None = None,
) -> ComplianceReport:
    resolved_root = root.expanduser().resolve()

    if feature_filter is not None:
        feature_filter = validate_feature_slug(feature_filter)

    discovered = list_feature_bundles(resolved_root)
    discovered_slugs = {str(f["slug"]) for f in discovered}

    if feature_filter is not None:
        slugs = (feature_filter,)
    else:
        slugs = tuple(sorted(discovered_slugs))

    trails: list[AuditTrail] = []
    evidence_hashes: list[str] = []

    for slug in slugs:
        validate_feature_slug(slug)

        events = _collect_audit_events(slug, resolved_root, since)
        transitions = _build_lifecycle_transitions(slug, resolved_root)
        validation = _gather_validation_evidence(slug, resolved_root)
        drift = _build_drift_history(slug, resolved_root, since)

        event_tuple = tuple(events)
        transition_tuple = tuple(
            {
                "from_status": t["from_status"],
                "to_status": t["to_status"],
                "date": t["date"],
                "author": t["author"],
                "commit": t["commit"],
            }
            for t in transitions
        )
        drift_tuple = tuple(drift)

        trail = AuditTrail(
            feature_id=slug,
            events=event_tuple,
            lifecycle_transitions=transition_tuple,
            validation_evidence=validation,
            drift_history=drift_tuple,
        )
        trails.append(trail)

        hash_input = slug + "".join(e.evidence_hash for e in events)
        evidence_hashes.append(_hash_content(hash_input))

    summary = _generate_compliance_summary(trails)

    recommendations: list[str] = []
    for gap in summary.get("gaps", []):
        if "missing spec" in gap:
            recommendations.append(f"Create spec file for {gap.split(':')[0]}")
        elif "missing execution" in gap:
            recommendations.append(f"Create execution file for {gap.split(':')[0]}")
        elif "missing quality" in gap:
            recommendations.append(f"Create quality file for {gap.split(':')[0]}")
        elif "Uncovered ACs" in gap:
            slug_part = gap.split(":")[0]
            recommendations.append(f"Add test coverage links for uncovered ACs in {slug_part}")
        elif "no lifecycle transitions" in gap:
            recommendations.append(f"Record lifecycle transitions for {gap.split(':')[0]}")

    if not recommendations:
        recommendations.append("All features pass compliance checks")

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


__all__ = [
    "_now_iso",
    "build_compliance_report",
]

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .audit_events import (
    _build_lifecycle_transitions,
    _collect_audit_events,
    _hash_content,
)
from .audit_models import (
    AuditTrail,
    ComplianceReport,
)
from .audit_validation import (
    _build_drift_history,
    _gather_validation_evidence,
)
from .features import (
    FEATURE_STATUSES,
    InvalidFeatureSlug,
    list_feature_bundles,
    validate_feature_slug,
)

__all__ = [
    "_generate_compliance_summary",
    "_now_iso",
    "build_compliance_report",
    "render_compliance_json",
    "render_compliance_text",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _generate_compliance_summary(trails: list[AuditTrail]) -> dict[str, Any]:
    pass_fail: dict[str, str] = {}
    gaps: list[str] = []
    total_features = len(trails)
    compliant_features = 0

    for trail in trails:
        feature_compliant = True
        ve = trail.validation_evidence

        spec_ok = ve.get("spec", {}).get("exists", False)
        exec_ok = ve.get("execution", {}).get("exists", False)
        quality_ok = ve.get("quality", {}).get("exists", False)

        if not spec_ok:
            pass_fail[f"{trail.feature_id}_spec"] = "fail"
            feature_compliant = False
            gaps.append(f"{trail.feature_id}: missing spec file")
        else:
            pass_fail[f"{trail.feature_id}_spec"] = "pass"

        if not exec_ok:
            pass_fail[f"{trail.feature_id}_execution"] = "fail"
            feature_compliant = False
            gaps.append(f"{trail.feature_id}: missing execution file")
        else:
            pass_fail[f"{trail.feature_id}_execution"] = "pass"

        if not quality_ok:
            pass_fail[f"{trail.feature_id}_quality"] = "fail"
            feature_compliant = False
            gaps.append(f"{trail.feature_id}: missing quality file")
        else:
            pass_fail[f"{trail.feature_id}_quality"] = "pass"

        checks = ve.get("validation_checks", [])
        for check in checks:
            if check.get("status") == "fail":
                pass_fail[f"{trail.feature_id}_{check['check']}"] = "fail"
                feature_compliant = False
                gaps.append(f"{trail.feature_id}: {check.get('detail', '')}")
            else:
                pass_fail[f"{trail.feature_id}_{check['check']}"] = "pass"

        if not trail.lifecycle_transitions:
            pass_fail[f"{trail.feature_id}_lifecycle"] = "fail"
            gaps.append(f"{trail.feature_id}: no lifecycle transitions recorded")
        else:
            pass_fail[f"{trail.feature_id}_lifecycle"] = "pass"

        if feature_compliant:
            compliant_features += 1

    total_checks = len(pass_fail)
    passed_checks = sum(1 for v in pass_fail.values() if v == "pass")

    return {
        "compliant_features": compliant_features,
        "gaps": gaps,
        "pass_fail_per_dimension": pass_fail,
        "total_checks": total_checks,
        "total_features": total_features,
        "passed_checks": passed_checks,
        "compliance_rate": (
            round(compliant_features / total_features, 2) if total_features > 0 else 0.0
        ),
    }


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


def render_compliance_json(report: ComplianceReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_compliance_text(report: ComplianceReport) -> str:
    summary = report.compliance_summary
    lines = [
        f"Compliance audit report: {report.root}",
        f"Audit date: {report.audit_date}",
        f"Scope: {report.scope}",
        "",
        f"Summary: "
        f"features={summary['total_features']} "
        f"compliant={summary['compliant_features']} "
        f"checks={summary['total_checks']} "
        f"passed={summary['passed_checks']} "
        f"rate={summary['compliance_rate']:.0%}",
    ]

    pf = summary.get("pass_fail_per_dimension", {})
    if pf:
        lines.append("")
        lines.append("Compliance dimensions:")
        for key in sorted(pf):
            status = pf[key]
            marker = "PASS" if status == "pass" else "FAIL"
            lines.append(f"  [{marker}] {key}")

    lines.append("")
    lines.append("Features:")
    if not report.features:
        lines.append("- none")
    for trail in report.features:
        n_events = len(trail.events)
        n_transitions = len(trail.lifecycle_transitions)
        n_drift = len(trail.drift_history)
        lines.append(
            f"- {trail.feature_id}: "
            f"events={n_events} "
            f"transitions={n_transitions} "
            f"drift_events={n_drift}"
        )
        ve = trail.validation_evidence
        for kind in ("spec", "execution", "quality"):
            info = ve.get(kind, {})
            exists = info.get("exists", False)
            marker = "exists" if exists else "missing"
            if kind == "spec":
                detail = f"ac_count={info.get('ac_count', 0)}"
            elif kind == "execution":
                detail = f"task_count={info.get('task_count', 0)}"
            else:
                detail = f"coverage_links={info.get('coverage_links', 0)}"
            lines.append(f"    [{marker}] {kind}: {detail}")

        if trail.lifecycle_transitions:
            for t in trail.lifecycle_transitions:
                lines.append(
                    f"    transition: {t['from_status']} -> {t['to_status']} "
                    f"({t['date'][:10]} by {t['author']})"
                )

    if report.evidence_hashes:
        lines.append("")
        lines.append("Evidence hashes:")
        for i, h in enumerate(report.evidence_hashes):
            lines.append(f"  [{i}] {h[:16]}...")

    if report.recommendations:
        lines.append("")
        lines.append("Recommendations:")
        for rec in report.recommendations:
            lines.append(f"- {rec}")

    lines.append("")
    lines.append("Safety notes:")
    lines.extend(f"- {note}" for note in report.safety_notes)
    return "\n".join(lines) + "\n"

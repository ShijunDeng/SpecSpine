from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .consistency import _read_text
from .dependency import _list_feature_slugs
from .drift import _build_drift_history as _drift_build_history
from .evolution import _run_git
from .features import (
    FEATURE_FILE_PATHS,
    FEATURE_STATUSES,
    InvalidFeatureSlug,
    feature_bundle_paths,
    list_feature_bundles,
    validate_feature_slug,
)

GIT_LOG_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
LIFECYCLE_STATUS_RE = re.compile(r"Status:\s*(\S+)", re.IGNORECASE)
FEATURE_ID_RE = re.compile(r"Feature\s+ID:\s*([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE)
AC_ID_RE = re.compile(r"(AC\d{3})")
TASK_ID_RE = re.compile(r"(T\d{3})")
QUALITY_CHECK_RE = re.compile(r"(QC\d{3})")
COV_LINK_RE = re.compile(r"- \[[ xX]\]\s+(AC\d{3})\s*->\s*(\S+)")


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    timestamp: str
    feature_id: str
    description: str
    evidence_hash: str = ""
    actor: str = ""

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "actor": self.actor,
            "description": self.description,
            "evidence_hash": self.evidence_hash,
            "event_type": self.event_type,
            "feature_id": self.feature_id,
            "timestamp": self.timestamp,
        }
        return result


@dataclass(frozen=True)
class AuditTrail:
    feature_id: str
    events: tuple[AuditEvent, ...] = ()
    lifecycle_transitions: tuple[dict[str, str], ...] = ()
    validation_evidence: dict[str, Any] = field(default_factory=dict)
    drift_history: tuple[dict[str, Any], ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "drift_history": [dict(d) for d in self.drift_history],
            "events": [e.as_dict() for e in self.events],
            "feature_id": self.feature_id,
            "lifecycle_transitions": [dict(t) for t in self.lifecycle_transitions],
            "validation_evidence": dict(self.validation_evidence),
        }


@dataclass(frozen=True)
class ComplianceReport:
    root: Path
    audit_date: str
    scope: str
    features: tuple[AuditTrail, ...]
    compliance_summary: dict[str, Any]
    evidence_hashes: tuple[str, ...]
    recommendations: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "audit_date": self.audit_date,
            "compliance_summary": dict(self.compliance_summary),
            "evidence_hashes": list(self.evidence_hashes),
            "features": [f.as_dict() for f in self.features],
            "recommendations": list(self.recommendations),
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "scope": self.scope,
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _feature_peer_content(root: Path, slug: str, kind: str) -> str | None:
    rel_path = FEATURE_FILE_PATHS.get(kind)
    if rel_path is None:
        return None
    path = root / rel_path.format(slug=slug)
    if not path.exists():
        return None
    return _read_text(path)


def _collect_audit_events(slug: str, root: Path, since: str | None) -> list[AuditEvent]:
    events: list[AuditEvent] = []
    peer_files = feature_bundle_paths(root, slug)
    if not peer_files:
        return events

    rel_paths: list[str] = []
    for kind in ("spec", "execution", "quality"):
        p = peer_files.get(kind)
        if p is not None and p.exists():
            try:
                rel_paths.append(str(p.relative_to(root)))
            except ValueError:
                pass

    if not rel_paths:
        return events

    git_args = ["log", "--format=%H|%ai|%an|%s", "--"] + rel_paths
    result = _run_git(git_args, root)
    if result.returncode != 0:
        return events

    for line in result.stdout.strip().splitlines():
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        commit_hash, date_str, author, message = parts

        if since is not None:
            date_match = GIT_LOG_DATE_RE.match(date_str)
            if date_match:
                commit_date = date_match.group(0)
                if commit_date < since:
                    continue

        event_type = "file_change"
        msg_lower = message.lower()
        if any(kw in msg_lower for kw in ("status", "lifecycle", "transition")):
            event_type = "lifecycle"
        elif any(kw in msg_lower for kw in ("validat", "verif")):
            event_type = "validation"
        elif any(kw in msg_lower for kw in ("test", "coverage")):
            event_type = "test"
        elif any(kw in msg_lower for kw in ("drift", "consisten")):
            event_type = "consistency"

        content_parts: list[str] = []
        for kind in ("spec", "execution", "quality"):
            rel = FEATURE_FILE_PATHS.get(kind, "").format(slug=slug)
            show_result = _run_git(["show", f"{commit_hash}:{rel}"], root)
            if show_result.returncode == 0:
                content_parts.append(show_result.stdout)
        evidence_hash = _hash_content("\n".join(content_parts)) if content_parts else ""

        events.append(
            AuditEvent(
                event_type=event_type,
                timestamp=date_str.strip(),
                feature_id=slug,
                description=f"Commit {commit_hash[:8]}: {message}",
                evidence_hash=evidence_hash,
                actor=author.strip(),
            )
        )

    return events


def _build_lifecycle_transitions(slug: str, root: Path) -> list[dict[str, str]]:
    transitions: list[dict[str, str]] = []
    peer_files = feature_bundle_paths(root, slug)
    if not peer_files:
        return transitions

    rel_paths: list[str] = []
    for kind in ("spec", "execution", "quality"):
        p = peer_files.get(kind)
        if p is not None and p.exists():
            try:
                rel_paths.append(str(p.relative_to(root)))
            except ValueError:
                pass

    if not rel_paths:
        return transitions

    git_args = ["log", "--format=%H|%ai|%an|%s", "--diff-filter=ACDMR", "--"] + rel_paths
    result = _run_git(git_args, root)
    if result.returncode != 0:
        return transitions

    previous_status: str | None = None
    for line in result.stdout.strip().splitlines():
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        commit_hash, date_str, author, message = parts

        spec_rel = FEATURE_FILE_PATHS.get("spec", "").format(slug=slug)
        show_result = _run_git(["show", f"{commit_hash}:{spec_rel}"], root)
        if show_result.returncode != 0:
            continue

        status_match = LIFECYCLE_STATUS_RE.search(show_result.stdout)
        if status_match:
            current_status = status_match.group(1)
            if previous_status is None or current_status != previous_status:
                transitions.append({
                    "commit": commit_hash[:8],
                    "date": date_str.strip(),
                    "author": author.strip(),
                    "from_status": previous_status or "unknown",
                    "to_status": current_status,
                    "message": message,
                })
                previous_status = current_status

    return transitions


def _gather_validation_evidence(slug: str, root: Path) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "spec": {"exists": False, "ac_count": 0, "acs": []},
        "execution": {"exists": False, "task_count": 0, "tasks": []},
        "quality": {"exists": False, "qc_count": 0, "coverage_links": 0, "qcs": []},
        "validation_checks": [],
    }

    spec_content = _feature_peer_content(root, slug, "spec")
    if spec_content is not None:
        evidence["spec"]["exists"] = True
        acs = AC_ID_RE.findall(spec_content)
        evidence["spec"]["ac_count"] = len(acs)
        evidence["spec"]["acs"] = sorted(set(acs))

    exec_content = _feature_peer_content(root, slug, "execution")
    if exec_content is not None:
        evidence["execution"]["exists"] = True
        tasks = TASK_ID_RE.findall(exec_content)
        evidence["execution"]["task_count"] = len(tasks)
        evidence["execution"]["tasks"] = sorted(set(tasks))

    quality_content = _feature_peer_content(root, slug, "quality")
    if quality_content is not None:
        evidence["quality"]["exists"] = True
        qcs = QUALITY_CHECK_RE.findall(quality_content)
        cov_links = COV_LINK_RE.findall(quality_content)
        evidence["quality"]["qc_count"] = len(qcs)
        evidence["quality"]["coverage_links"] = len(cov_links)
        evidence["quality"]["qcs"] = sorted(set(qcs))

    if evidence["spec"]["exists"]:
        spec_acs = set(evidence["spec"]["acs"])
        quality_acs = set()
        if quality_content is not None:
            quality_acs = {ac for ac, _ in COV_LINK_RE.findall(quality_content)}
        uncovered = sorted(spec_acs - quality_acs)
        if uncovered:
            evidence["validation_checks"].append({
                "check": "ac_coverage",
                "status": "fail",
                "detail": f"Uncovered ACs: {', '.join(uncovered)}",
            })
        else:
            evidence["validation_checks"].append({
                "check": "ac_coverage",
                "status": "pass",
                "detail": "All ACs have coverage links",
            })

    if evidence["spec"]["exists"] and evidence["execution"]["exists"]:
        evidence["validation_checks"].append({
            "check": "execution_present",
            "status": "pass",
            "detail": "Execution file exists with tasks",
        })
    elif evidence["spec"]["exists"]:
        evidence["validation_checks"].append({
            "check": "execution_present",
            "status": "fail",
            "detail": "Missing execution file",
        })

    if evidence["spec"]["exists"] and evidence["quality"]["exists"]:
        evidence["validation_checks"].append({
            "check": "quality_present",
            "status": "pass",
            "detail": "Quality file exists",
        })
    elif evidence["spec"]["exists"]:
        evidence["validation_checks"].append({
            "check": "quality_present",
            "status": "fail",
            "detail": "Missing quality file",
        })

    return evidence


def _build_drift_history(slug: str, root: Path, since: str | None) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    peer_files = feature_bundle_paths(root, slug)
    if not peer_files:
        return events

    rel_paths = []
    for kind in ("spec", "execution", "quality"):
        p = peer_files.get(kind)
        if p is not None and p.exists():
            try:
                rel_paths.append(str(p.relative_to(root)))
            except ValueError:
                pass

    if not rel_paths:
        return events

    git_args = ["log", "--format=%H|%ai|%s", "--"] + rel_paths
    result = _run_git(git_args, root)
    if result.returncode != 0:
        return events

    for line in result.stdout.strip().splitlines():
        parts = line.split("|", 2)
        if len(parts) < 2:
            continue
        commit_hash, date_str = parts[0], parts[1]
        message = parts[2] if len(parts) > 2 else ""

        if since is not None:
            date_match = GIT_LOG_DATE_RE.match(date_str)
            if date_match:
                commit_date = date_match.group(0)
                if commit_date < since:
                    continue

        event_type = "unknown"
        for kind in ("spec", "execution", "quality"):
            rel = FEATURE_FILE_PATHS.get(kind, "").format(slug=slug)
            if rel in " ".join(rel_paths):
                event_type = kind
                break

        severity = "medium"
        if any(kw in message.lower() for kw in ("remove", "delete", "drop")):
            severity = "high"
        elif any(kw in message.lower() for kw in ("add", "new", "create")):
            severity = "low"

        events.append({
            "commit": commit_hash[:8],
            "date": date_str.strip(),
            "event_type": event_type,
            "message": message,
            "severity": severity,
        })

    return events


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

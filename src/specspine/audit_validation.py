from __future__ import annotations

from pathlib import Path

from .audit_events import _build_lifecycle_transitions, _collect_audit_events, _feature_peer_content
from .audit_models import (
    AC_ID_RE,
    AuditTrail,
    COV_LINK_RE,
    GIT_LOG_DATE_RE,
    QUALITY_CHECK_RE,
    TASK_ID_RE,
)
from .features import FEATURE_FILE_PATHS, feature_bundle_paths

__all__ = [
    "_build_drift_history",
    "_gather_validation_evidence",
]


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
    from .evolution import _run_git

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

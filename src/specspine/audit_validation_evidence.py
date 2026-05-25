from __future__ import annotations

from pathlib import Path
from typing import Any

from .audit_events import _feature_peer_content
from .audit_models import (
    AC_ID_RE,
    COV_LINK_RE,
    QUALITY_CHECK_RE,
    TASK_ID_RE,
)

__all__ = [
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

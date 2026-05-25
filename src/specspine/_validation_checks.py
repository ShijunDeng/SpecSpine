from __future__ import annotations

from typing import Any

from .audit_models import COV_LINK_RE


def _run_validation_checks(evidence: dict[str, Any], quality_content: str | None) -> list[dict[str, str]]:
    validation_checks: list[dict[str, str]] = []

    if evidence["spec"]["exists"]:
        spec_acs = set(evidence["spec"]["acs"])
        quality_acs = set()
        if quality_content is not None:
            quality_acs = {ac for ac, _ in COV_LINK_RE.findall(quality_content)}
        uncovered = sorted(spec_acs - quality_acs)
        if uncovered:
            validation_checks.append({
                "check": "ac_coverage",
                "status": "fail",
                "detail": f"Uncovered ACs: {', '.join(uncovered)}",
            })
        else:
            validation_checks.append({
                "check": "ac_coverage",
                "status": "pass",
                "detail": "All ACs have coverage links",
            })

    if evidence["spec"]["exists"] and evidence["execution"]["exists"]:
        validation_checks.append({
            "check": "execution_present",
            "status": "pass",
            "detail": "Execution file exists with tasks",
        })
    elif evidence["spec"]["exists"]:
        validation_checks.append({
            "check": "execution_present",
            "status": "fail",
            "detail": "Missing execution file",
        })

    if evidence["spec"]["exists"] and evidence["quality"]["exists"]:
        validation_checks.append({
            "check": "quality_present",
            "status": "pass",
            "detail": "Quality file exists",
        })
    elif evidence["spec"]["exists"]:
        validation_checks.append({
            "check": "quality_present",
            "status": "fail",
            "detail": "Missing quality file",
        })

    return validation_checks


__all__ = [
    "_run_validation_checks",
]

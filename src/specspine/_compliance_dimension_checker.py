from __future__ import annotations

from typing import Any

from .audit_models import AuditTrail


def _evaluate_trail_dimensions(trail: AuditTrail) -> tuple[dict[str, str], list[str], bool]:
    pass_fail: dict[str, str] = {}
    gaps: list[str] = []
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

    return pass_fail, gaps, feature_compliant


__all__ = [
    "_evaluate_trail_dimensions",
]

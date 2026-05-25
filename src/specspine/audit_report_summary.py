from __future__ import annotations

from typing import Any

from .audit_models import AuditTrail


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


__all__ = [
    "_generate_compliance_summary",
]

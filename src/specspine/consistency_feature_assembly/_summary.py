from __future__ import annotations

__all__ = [
    "_compute_feature_summary",
]


def _compute_feature_summary(
    changed_references: list,
    checks: tuple,
    documentation_references: list,
    implementation_references: list,
    source_files: list,
    test_references: list,
) -> dict:
    return {
        "changed_references": len(changed_references),
        "checks_fail": sum(1 for check in checks if check.status == "fail"),
        "checks_pass": sum(1 for check in checks if check.status == "pass"),
        "checks_warn": sum(1 for check in checks if check.status == "warn"),
        "documentation_references": len(documentation_references),
        "implementation_references": len(implementation_references),
        "source_files": len(source_files),
        "test_references": len(test_references),
    }

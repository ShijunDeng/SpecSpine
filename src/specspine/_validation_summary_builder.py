from __future__ import annotations

from typing import Any

__all__ = [
    "build_validation_summary",
]


def build_validation_summary(
    report: dict[str, Any],
    *,
    included: dict[str, bool],
    include_warning_checks: bool = False,
) -> dict[str, Any]:
    failed_checks = [
        check
        for check in report["checks"]
        if check["status"] == "fail"
    ]
    summary = {
        "ok": report["ok"],
        "summary": report["summary"],
        "failed_checks": failed_checks,
        "included": included,
    }
    if include_warning_checks:
        summary["warning_checks"] = [
            check
            for check in report["checks"]
            if check["status"] == "warn"
        ]
    return summary

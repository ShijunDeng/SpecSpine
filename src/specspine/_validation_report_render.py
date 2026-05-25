from __future__ import annotations

import json
from typing import Any

__all__ = [
    "build_validation_summary",
    "render_validation_json",
    "render_validation_text",
    "validation_exit_code",
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


def render_validation_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def render_validation_text(report: dict[str, Any]) -> str:
    result = "ok" if report["ok"] else "failed"
    lines = [
        f"SpecSpine validation at {report['root']}",
        f"Result: {result}",
        "Checks:",
    ]

    for check in report["checks"]:
        lines.append(f"  [{check['status']}] {check['id']} - {check['message']}")

    summary = report["summary"]
    lines.append(
        "Summary: "
        f"pass={summary['pass']} "
        f"fail={summary['fail']} "
        f"warn={summary['warn']} "
        f"skip={summary['skip']} "
        f"total={summary['total']}"
    )
    return "\n".join(lines) + "\n"


def validation_exit_code(report: dict[str, Any]) -> int:
    return 1 if report["summary"]["fail"] else 0

from __future__ import annotations

from typing import Any

__all__ = [
    "render_validation_text",
    "validation_exit_code",
]


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

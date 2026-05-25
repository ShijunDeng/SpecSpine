from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .validation_build_checks import _check
from .validation_build_run import _run_checks
from .validation_models import ValidationCheck, VALIDATION_STATUSES, AdapterProbe
from .adapters import probe_adapters


def _summary(checks: list[ValidationCheck]) -> dict[str, int]:
    counts = {status: 0 for status in VALIDATION_STATUSES}
    for check in checks:
        counts[check.status] += 1
    counts["total"] = len(checks)
    return counts


def build_validation_report(
    path: Path,
    *,
    include_fusion: bool = False,
    include_features: bool = False,
    include_adapters: bool = False,
    adapter_probe: AdapterProbe = probe_adapters,
) -> dict[str, Any]:
    root = path.expanduser().resolve()
    checks = _run_checks(
        root,
        include_fusion=include_fusion,
        include_features=include_features,
        include_adapters=include_adapters,
        adapter_probe=adapter_probe,
    )

    summary = _summary(checks)
    return {
        "root": str(root),
        "ok": summary["fail"] == 0,
        "checks": [check.as_dict() for check in checks],
        "summary": summary,
    }


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


__all__ = [
    "build_validation_report",
    "build_validation_summary",
    "render_validation_json",
    "render_validation_text",
    "validation_exit_code",
]

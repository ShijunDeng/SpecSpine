from __future__ import annotations

from pathlib import Path

from .validation import build_validation_report
from .health_models import (
    ValidationHealth,
)

__all__ = [
    "_build_validation_health",
]


def _build_validation_health(root: Path) -> ValidationHealth:
    try:
        report = build_validation_report(
            root,
            include_fusion=True,
            include_features=True,
            include_adapters=False,
        )
    except OSError:
        return ValidationHealth(
            ok=False,
            pass_count=0,
            fail_count=0,
            warn_count=0,
            skip_count=0,
            total=0,
            top_failing_rules=(),
        )

    summary = report["summary"]
    checks = report.get("checks", [])
    failing = [c for c in checks if c["status"] == "fail"]
    top_failing = tuple(
        {"id": c["id"], "message": c["message"]}
        for c in failing[:5]
    )

    return ValidationHealth(
        ok=report["ok"],
        pass_count=summary.get("pass", 0),
        fail_count=summary.get("fail", 0),
        warn_count=summary.get("warn", 0),
        skip_count=summary.get("skip", 0),
        total=summary.get("total", 0),
        top_failing_rules=top_failing,
    )

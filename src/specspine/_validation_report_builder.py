from __future__ import annotations

from pathlib import Path
from typing import Any

from .validation_build_checks import _check
from .validation_build_run import _run_checks
from .validation_models import ValidationCheck, VALIDATION_STATUSES, AdapterProbe
from .adapters import probe_adapters

__all__ = [
    "build_validation_report",
]


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

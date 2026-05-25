from __future__ import annotations

from typing import Any

from .hygiene_models import (
    CATEGORIES,
    SEVERITIES,
    HygieneFinding,
    _ScanState,
)
from .hygiene_scanner import _dedupe

__all__ = [
    "_summary",
    "_recommended_commands",
]


def _summary(
    findings: tuple[HygieneFinding, ...],
    *,
    changed_files: tuple[str, ...],
    state: _ScanState,
) -> dict[str, Any]:
    by_severity = {severity: 0 for severity in SEVERITIES}
    by_category: dict[str, int] = {category: 0 for category in CATEGORIES}
    for finding in findings:
        by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1
        by_category[finding.category] = by_category.get(finding.category, 0) + 1
    return {
        "by_category": dict(sorted(by_category.items())),
        "by_severity": by_severity,
        "changed_files": len(changed_files),
        "directories_scanned": state.directories_scanned,
        "directories_skipped": state.directories_skipped,
        "files_scanned": state.files_scanned,
        "files_skipped": state.files_skipped,
        "findings_total": len(findings),
        "skipped_reasons": dict(sorted((state.skipped_reasons or {}).items())),
    }


def _recommended_commands(changed_files: tuple[str, ...]) -> tuple[str, ...]:
    commands = [
        "specspine hygiene scan . --json",
        "specspine hygiene scan . --strict --json",
    ]
    for path in changed_files:
        commands.append(f"specspine hygiene scan . --changed {path} --json")
    return _dedupe(commands)

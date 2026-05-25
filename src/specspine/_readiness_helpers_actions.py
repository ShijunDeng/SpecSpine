from __future__ import annotations

from typing import Any

__all__ = [
    "_readiness_detail_command",
    "_readiness_next_actions",
]


def _readiness_next_actions(slug: str, report: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    missing_files = report.get("missing_files", [])
    gaps = report.get("gaps", [])
    blocking_checks = report.get("blocking_checks", [])

    if missing_files:
        actions.append("Add missing peer file(s): " + ", ".join(missing_files))
    if gaps:
        gap_ids = [str(gap.get("id", "unknown")) for gap in gaps if isinstance(gap, dict)]
        actions.append("Resolve trace gap(s): " + ", ".join(sorted(set(gap_ids))))
    if blocking_checks:
        check_ids = [
            str(check.get("id", "unknown"))
            for check in blocking_checks
            if isinstance(check, dict)
        ]
        actions.append(
            "Resolve blocking readiness check(s): "
            + ", ".join(sorted(set(check_ids)))
        )
    if not actions:
        actions.append("Review, merge, or archive the ready feature bundle.")
    if not report.get("ready"):
        actions.append(f"Inspect readiness details: specspine feature ready {slug} . --json")
    return actions


def _readiness_detail_command(
    slug: str,
    *,
    require_coverage: bool,
    use_policy: bool,
) -> str:
    command = f"specspine feature ready {slug} . --json"
    if require_coverage:
        command += " --require-coverage"
    elif use_policy:
        command += " --policy"
    return command

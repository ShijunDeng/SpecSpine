from __future__ import annotations

from .feature_bundle import (
    FeatureReadyCheck,
    FeatureTask,
    FeatureTraceChecklistItem,
    FeatureTraceTestPlanItem,
)

__all__ = [
    "_render_pr_checklist_items",
    "_render_pr_test_plan_items",
    "_render_pr_ready_checks",
]


def _render_pr_checklist_items(
    items: tuple[FeatureTraceChecklistItem, ...] | tuple[FeatureTask, ...],
    *,
    empty_text: str,
) -> list[str]:
    if not items:
        return [f"- [ ] {empty_text}"]

    lines: list[str] = []
    for item in items:
        marker = "x" if item.done else " "
        lines.append(
            f"- [{marker}] {item.id} {item.source_file}:{item.line} {item.text}"
        )
    return lines


def _render_pr_test_plan_items(
    items: tuple[FeatureTraceTestPlanItem, ...],
    *,
    empty_text: str,
) -> list[str]:
    if not items:
        return [f"- {empty_text}"]

    return [
        f"- {item.id} {item.source_file}:{item.line} {item.text}"
        for item in items
    ]


def _render_pr_ready_checks(
    checks: tuple[FeatureReadyCheck, ...],
) -> list[str]:
    if not checks:
        return ["- [ ] Run `specspine feature ready` before opening the PR."]

    lines: list[str] = []
    for check in checks:
        marker = "x" if check.status == "pass" else " "
        lines.append(f"- [{marker}] {check.id}: {check.message}")
    return lines

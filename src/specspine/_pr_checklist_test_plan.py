from __future__ import annotations

from .feature_bundle import FeatureTraceTestPlanItem
from .feature_drafts_pr_renderers import _render_pr_test_plan_items

__all__ = [
    "_render_pr_test_plan_section",
]


def _render_pr_test_plan_section(
    test_plan: tuple[FeatureTraceTestPlanItem, ...],
) -> list[str]:
    lines: list[str] = []
    lines.extend(["", "## Test Plan", ""])
    lines.extend(
        _render_pr_test_plan_items(
            test_plan,
            empty_text="Add a concrete test plan before review.",
        )
    )
    return lines

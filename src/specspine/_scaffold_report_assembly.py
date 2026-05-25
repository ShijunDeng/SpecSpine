from __future__ import annotations

from .scaffold_models import ScaffoldReport
from ._scaffold_report_coverage import ScaffoldCoverageContext
from ._scaffold_test_generation import build_scaffold_report as _build_scaffold_report

__all__ = [
    "assemble_scaffold_report",
]


def assemble_scaffold_report(
    ctx: ScaffoldCoverageContext,
) -> ScaffoldReport:
    return _build_scaffold_report(ctx)

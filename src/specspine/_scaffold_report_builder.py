from __future__ import annotations

from pathlib import Path

from ._scaffold_report_coverage import (
    compute_scaffold_coverage_context,
)
from ._scaffold_report_assembly import (
    assemble_scaffold_report,
)
from .scaffold_models import ScaffoldReport

__all__ = [
    "build_ac_test_scaffold",
]


def build_ac_test_scaffold(root: Path, slug: str) -> ScaffoldReport:
    ctx = compute_scaffold_coverage_context(root, slug)
    return assemble_scaffold_report(ctx)

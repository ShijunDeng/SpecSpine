from __future__ import annotations

from pathlib import Path

from .features import FEATURE_FILE_PATHS
from .benchmark_compute_metrics_patterns import (
    AC_ID_RE,
    TASK_ID_RE,
    COV_LINK_DONE_RE,
    COV_LINK_TOTAL_RE,
)
from .benchmark_metrics_utils import _read_text, _count_pattern

__all__ = [
    "AC_ID_RE",
    "TASK_ID_RE",
    "COV_LINK_DONE_RE",
    "COV_LINK_TOTAL_RE",
    "_read_text",
    "_count_pattern",
    "_count_feature_artifacts",
]


def _count_feature_artifacts(slug: str, root: Path) -> dict[str, int | float]:
    resolved_root = root.expanduser().resolve()

    ac_count = 0
    task_count = 0
    test_count = 0
    coverage_pct = 0.0

    spec_path = resolved_root / FEATURE_FILE_PATHS["spec"].format(slug=slug)
    exec_path = resolved_root / FEATURE_FILE_PATHS["execution"].format(slug=slug)
    quality_path = resolved_root / FEATURE_FILE_PATHS["quality"].format(slug=slug)

    if spec_path.exists():
        content = _read_text(spec_path)
        ac_count = _count_pattern(content, AC_ID_RE)

    if exec_path.exists():
        content = _read_text(exec_path)
        task_count = _count_pattern(content, TASK_ID_RE)

    if quality_path.exists():
        content = _read_text(quality_path)
        test_count = _count_pattern(content, COV_LINK_TOTAL_RE)
        done_count = _count_pattern(content, COV_LINK_DONE_RE)
        if test_count > 0:
            coverage_pct = round(done_count / test_count * 100, 1)

    return {
        "ac_count": ac_count,
        "task_count": task_count,
        "test_count": test_count,
        "coverage_pct": coverage_pct,
    }

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .benchmark_models import FeatureMetrics
from .consistency import (
    build_consistency_report,
)
from .coverage import build_coverage_debt_report
from .features import (
    FEATURE_FILE_PATHS,
    InvalidFeatureSlug,
    get_feature_status,
    read_feature_metadata,
    validate_feature_slug,
)
from .validation import build_validation_report

from .benchmark_compute_metrics import (
    AC_ID_RE,
    TASK_ID_RE,
    COV_LINK_DONE_RE,
    COV_LINK_TOTAL_RE,
    _read_text,
    _count_pattern,
    _compute_feature_metrics,
)
from .benchmark_compute_stats import _median, _percentile
from .benchmark_compute_aggregate import _aggregate_metrics, _compute_trends
from .benchmark_compute_scoring import (
    _primary_issue,
    _identify_top_performers,
    _identify_improvement_areas,
)


__all__ = [
    "_compute_feature_metrics",
    "_compute_trends",
    "_aggregate_metrics",
    "_median",
    "_percentile",
    "_identify_top_performers",
    "_identify_improvement_areas",
    "_primary_issue",
]

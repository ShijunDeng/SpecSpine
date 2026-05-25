from __future__ import annotations

import re
from pathlib import Path

from .features import (
    FEATURE_FILE_PATHS,
    FeatureReadyCheck,
    FeatureTask,
    FeatureTestCoverageLink,
    FeatureTraceChecklistItem,
    FeatureTraceReport,
)
from .analysis_models import (
    AC_REFERENCE_RE,
    QUALITY_REFERENCE_RE,
    TEST_TARGET_RE,
    VAGUE_TERMS,
    _PendingIssue,
)

from .analysis_traceability_ac import (
    _normalize_ac_id,
    _referenced_ac_ids,
    _coverage_ac_id,
    _ready_check_severity,
    _ready_check_category,
    _readiness_issues,
    _trace_gap_issues,
    _ac_traceability_issues,
)
from .analysis_traceability_commands import (
    _feature_trace_command,
    _feature_ready_command,
    _feature_tests_command,
)
from .analysis_traceability_quality import (
    _normalized_criterion_text,
    _criterion_quality_issues,
)
from .analysis_traceability_tasks import (
    _source_files,
    _missing_files,
    _read_test_coverage,
    _task_traceability_issues,
)


__all__ = [
    "_readiness_issues",
    "_ac_traceability_issues",
    "_task_traceability_issues",
    "_criterion_quality_issues",
    "_normalize_ac_id",
    "_referenced_ac_ids",
    "_source_files",
    "_missing_files",
    "_read_test_coverage",
    "_coverage_ac_id",
    "_ready_check_severity",
    "_ready_check_category",
    "_trace_gap_issues",
    "_normalized_criterion_text",
    "_feature_trace_command",
    "_feature_ready_command",
    "_feature_tests_command",
]

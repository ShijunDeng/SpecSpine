from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .consistency import _explicit_paths_from_feature_files, LOCAL_PATH_RE
from .consistency import _read_text
from .drift_models import DriftEvent
from .features import FEATURE_FILE_PATHS
from .drift_detection_extractors import (
    AC_ID_RE,
    TASK_ID_RE,
    QUALITY_CHECK_RE,
    COV_LINK_RE,
    _now_iso,
    _feature_peer_content,
    _extract_acs_from_spec,
    _extract_tasks_from_execution,
    _extract_acs_from_quality,
    _extract_cov_links_from_quality,
    _extract_qc_ids_from_quality,
    _baseline_peer_content,
)
from .drift_detection_detectors import (
    _detect_code_drift,
    _detect_spec_drift,
    _detect_task_drift,
    _detect_quality_drift,
    _detect_test_drift,
)

__all__ = [
    "_detect_code_drift",
    "_detect_spec_drift",
    "_detect_task_drift",
    "_detect_quality_drift",
    "_detect_test_drift",
    "_feature_peer_content",
    "_extract_acs_from_spec",
    "_extract_tasks_from_execution",
    "_extract_acs_from_quality",
    "_extract_cov_links_from_quality",
    "_extract_qc_ids_from_quality",
]

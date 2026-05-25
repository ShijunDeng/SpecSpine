from __future__ import annotations

import re
from pathlib import Path

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

AC_ID_RE = re.compile(r"AC\d{3}")
TASK_ID_RE = re.compile(r"(?:TASK|T)\d{3}")
COV_LINK_DONE_RE = re.compile(r"-\s*\[\s*[xX]\s*\]\s+AC\d{3}\s*->")
COV_LINK_TOTAL_RE = re.compile(r"-\s*\[\s*[ xX]\s*\]\s+AC\d{3}\s*->")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _count_pattern(content: str, pattern: re.Pattern[str]) -> int:
    return len(pattern.findall(content))


def _compute_feature_metrics(slug: str, root: Path) -> FeatureMetrics:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()

    status_report = get_feature_status(resolved_root, slug)
    status = status_report.status or "unknown"

    metadata = read_feature_metadata(resolved_root, slug)
    priority = metadata.priority
    effort = metadata.effort
    project = metadata.project

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

    validation_pass = 0
    validation_fail = 0
    try:
        val_report = build_validation_report(
            resolved_root,
            include_fusion=True,
            include_features=False,
            include_adapters=False,
        )
        summary = val_report.get("summary", {})
        validation_pass = summary.get("pass", 0)
        validation_fail = summary.get("fail", 0)
    except OSError:
        pass

    consistency_fail = 0
    drift_events = 0
    try:
        cons_report = build_consistency_report(
            resolved_root,
            feature_filter=slug,
        )
        for fc in cons_report.features:
            if fc.feature_id == slug:
                consistency_fail = sum(
                    1 for c in fc.consistency_checks if c.status == "fail"
                )
                break
    except (OSError, InvalidFeatureSlug):
        pass

    try:
        debt_report = build_coverage_debt_report(resolved_root)
        for feat in debt_report.get("features", []):
            if feat.get("feature_id") == slug:
                drift_events = feat.get("missing_acceptance_criteria", 0)
                break
    except OSError:
        pass

    lifecycle_duration_days = 0.0

    return FeatureMetrics(
        feature_id=slug,
        status=status,
        priority=priority,
        effort=effort,
        project=project,
        ac_count=ac_count,
        task_count=task_count,
        test_count=test_count,
        coverage_pct=coverage_pct,
        validation_pass=validation_pass,
        validation_fail=validation_fail,
        consistency_fail=consistency_fail,
        drift_events=drift_events,
        lifecycle_duration_days=lifecycle_duration_days,
    )


__all__ = [
    "AC_ID_RE",
    "TASK_ID_RE",
    "COV_LINK_DONE_RE",
    "COV_LINK_TOTAL_RE",
    "_read_text",
    "_count_pattern",
    "_compute_feature_metrics",
]

from __future__ import annotations

from pathlib import Path

from ..feature_bundle import (
    FeatureBundleNotFoundError,
    read_feature_metadata,
    validate_feature_slug,
)
from ..feature_bundle_io_status_single import get_feature_status
from ..feature_handoff_core_trace import _build_trace_with_fallback
from ..feature_ready import build_feature_ready_report
from ..feature_tasks import build_feature_tasks_report
from ._context_model import HandoffBuildContext

__all__ = ["fetch_handoff_context"]


def fetch_handoff_context(
    root: Path,
    slug: str,
    *,
    require_coverage: bool = False,
) -> HandoffBuildContext:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    status_report = get_feature_status(resolved_root, slug)
    metadata = read_feature_metadata(resolved_root, slug)
    has_native_files = any(file["exists"] for file in status_report.files.values())

    trace_report = _build_trace_with_fallback(resolved_root, slug, status_report)

    try:
        tasks_report = build_feature_tasks_report(resolved_root, slug)
        task_summary = tasks_report.summary
    except FeatureBundleNotFoundError:
        task_summary = {"done": 0, "open": 0, "total": 0}

    from ..feature_handoff_core_quality import _parse_release_readiness_from_file

    ready_report = build_feature_ready_report(
        resolved_root,
        slug,
        require_coverage=require_coverage,
    )

    release_readiness = _parse_release_readiness_from_file(resolved_root, slug)

    return HandoffBuildContext(
        slug=slug,
        resolved_root=resolved_root,
        has_native_files=has_native_files,
        trace_report=trace_report,
        task_summary=task_summary,
        ready_report=ready_report,
        release_readiness=release_readiness,
        metadata=metadata,
    )

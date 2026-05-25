from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import (
    build_feature_handoff_report,
    build_feature_ready_report,
    build_feature_tests_report,
    build_feature_trace_report,
)

__all__ = [
    "_feature_payload",
]


def _feature_payload(root: Path, slug: str) -> dict[str, Any]:
    handoff = build_feature_handoff_report(root, slug, require_coverage=True)
    ready = build_feature_ready_report(root, slug, require_coverage=True)
    tests = build_feature_tests_report(root, slug)
    trace = build_feature_trace_report(root, slug) if handoff.has_native_files else None
    return {
        "blocking_checks": [check.as_dict() for check in ready.blocking_checks],
        "gaps": list(trace.gaps if trace is not None else handoff.gaps),
        "handoff": handoff.as_dict(),
        "has_native_files": handoff.has_native_files,
        "ready": ready.as_dict(),
        "source_files": list(tests.source_files),
        "status": handoff.status,
        "tests": tests.as_dict(),
        "trace": trace.as_dict() if trace is not None else None,
    }

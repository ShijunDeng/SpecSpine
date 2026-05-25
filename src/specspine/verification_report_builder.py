from __future__ import annotations

from pathlib import Path

from .features import (
    FeatureBundleNotFoundError,
    build_feature_ready_report,
    build_feature_tests_report,
    build_feature_trace_report,
    validate_feature_slug,
)
from .verification_matrix import (
    _empty_evidence,
    _evidence,
    _matrix_rows,
    _summary,
)
from .verification_models import VerificationMatrix
from .verification_report_constants import (
    _recommended_commands,
    _safety_notes,
)

__all__ = [
    "build_verification_matrix",
]


def build_verification_matrix(root: Path, slug: str) -> VerificationMatrix:
    feature_id = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    try:
        trace = build_feature_trace_report(resolved_root, feature_id)
        tests = build_feature_tests_report(resolved_root, feature_id)
        ready = build_feature_ready_report(
            resolved_root,
            feature_id,
            require_coverage=True,
        )
        rows = _matrix_rows(trace, tests)
        evidence = _evidence(trace, tests, ready)
        status = trace.status
        is_ready = ready.ready
    except FeatureBundleNotFoundError:
        rows = ()
        evidence = _empty_evidence(resolved_root, feature_id)
        status = "unknown"
        is_ready = False

    return VerificationMatrix(
        root=resolved_root,
        feature_id=feature_id,
        status=status,
        ready=is_ready,
        matrix=rows,
        evidence=evidence,
        summary=_summary(rows, evidence),
        recommended_commands=_recommended_commands(feature_id),
        safety_notes=_safety_notes(),
    )

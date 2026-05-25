from __future__ import annotations

from typing import Any

from ._readiness_record_builder import build_readiness_record_from_context
from ._readiness_record_context import ReadinessRecordContext

__all__ = [
    "_build_record_from_phases",
]


def _build_record_from_phases(
    phases: dict[str, Any],
) -> dict[str, Any]:
    ctx = ReadinessRecordContext(
        slug=phases["slug"],
        status=phases["status"],
        metadata=phases["metadata"],
        coverage_required=phases["coverage_required"],
        policy_coverage_required=phases["policy_coverage_required"],
        report=phases["report"],
        require_coverage=phases["require_coverage"],
        use_policy=phases["use_policy"],
        policy=phases["policy"],
    )
    return build_readiness_record_from_context(ctx)

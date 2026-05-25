from __future__ import annotations

from .adapter_models import ADAPTER_HANDOFF_SAFETY_FLAGS


def _adapter_handoff_blocking_checks(
    report,
) -> list[dict[str, object]]:
    return [
        check.as_dict() if hasattr(check, "as_dict") else dict(check)
        for check in report.blocking_checks
    ]


def adapter_feature_handoff_focused_payload(
    report,
    adapter_key: str,
) -> dict[str, object]:
    return {
        "adapter": report.adapters[adapter_key].as_dict(),
        "blocking_checks": _adapter_handoff_blocking_checks(report),
        "feature_id": report.feature_id,
        "gaps": [dict(gap) for gap in report.gaps],
        "missing_files": list(report.missing_files),
        "ready": report.ready,
        "recommended_commands": list(report.recommended_commands),
        "safety_flags": dict(ADAPTER_HANDOFF_SAFETY_FLAGS),
        "source_files": list(report.source_files),
        "status": report.status,
        "summary": report.summary,
    }


__all__ = [
    "_adapter_handoff_blocking_checks",
    "adapter_feature_handoff_focused_payload",
]

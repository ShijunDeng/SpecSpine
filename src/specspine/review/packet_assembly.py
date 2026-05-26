from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import ReviewPacket
from ._packet_checks import _build_packet_review_checks
from ._packet_commands import _build_packet_commands
from ._packet_summary import _build_summary, _build_safety_notes

__all__ = [
    "assemble_review_packet",
]


def assemble_review_packet(
    resolved_root: Path,
    feature_slug: str | None,
    validation: dict[str, Any],
    gates: Any,
    impact: Any,
    feature_payload: dict[str, Any] | None,
) -> ReviewPacket:
    review_checks, failed_checks = _build_packet_review_checks(
        validation_ok=validation["ok"],
        gates_source_missing=gates.source_missing,
        has_impact_recommendations=bool(impact.recommendations),
        feature_payload=feature_payload,
    )
    recommended_commands = _build_packet_commands(
        feature_slug=feature_slug,
        impact_recommendations=impact.recommended_commands,
        gates_recommended_commands=gates.recommended_commands,
    )
    summary = _build_summary(
        impact=impact,
        failed_checks=failed_checks,
        feature_slug=feature_slug,
        review_checks=review_checks,
        recommended_commands=recommended_commands,
        validation=validation,
    )
    safety_notes = _build_safety_notes()
    return ReviewPacket(
        root=resolved_root,
        feature_id=feature_slug,
        changed_files=impact.changed_files,
        validation=validation,
        quality_gates=gates.as_dict(),
        test_impact=impact.as_dict(),
        feature=feature_payload,
        review_checks=review_checks,
        summary=summary,
        recommended_commands=recommended_commands,
        safety_notes=safety_notes,
    )

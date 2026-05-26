from __future__ import annotations

from typing import Any

from .checks_builder import _build_review_checks

__all__ = [
    "_build_packet_review_checks",
]


def _build_packet_review_checks(
    validation_ok: bool,
    gates_source_missing: bool,
    has_impact_recommendations: bool,
    feature_payload: dict[str, Any] | None,
) -> tuple[tuple[dict[str, Any], ...], tuple[str, ...]]:
    review_checks = _build_review_checks(
        validation_ok=validation_ok,
        gates_source_missing=gates_source_missing,
        has_impact_recommendations=has_impact_recommendations,
        feature_payload=feature_payload,
    )
    failed_checks = tuple(
        check["id"] for check in review_checks if check["status"] != "pass"
    )
    return review_checks, failed_checks

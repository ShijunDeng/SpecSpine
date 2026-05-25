from __future__ import annotations

from pathlib import Path

from .feature_bundle import FeatureStatusReport
from .feature_status_transition import _validate_enforced_feature_transition
from .feature_bundle import _transition_payload

__all__ = [
    "_build_transition",
]


def _build_transition(
    resolved_root: Path,
    slug: str,
    status: str,
    before: FeatureStatusReport,
    enforce_transition: bool,
) -> dict:
    if enforce_transition:
        return _validate_enforced_feature_transition(
            resolved_root,
            slug,
            status,
            before,
        )
    return _transition_payload(
        from_status=before.status,
        to_status=status,
        enforced=False,
        allowed=True,
    )

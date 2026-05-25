from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FeatureStatusReport,
)
from ._transition_status_validation import _validate_from_status
from ._transition_allowance import _validate_transition_allowed
from ._transition_archive_gate import _validate_archive_gate

__all__ = [
    "_validate_enforced_feature_transition",
]


def _validate_enforced_feature_transition(
    root: Path,
    slug: str,
    to_status: str,
    status_report: FeatureStatusReport,
) -> dict[str, object]:
    from_status = _validate_from_status(slug, status_report, to_status)
    transition = _validate_transition_allowed(
        slug, from_status, to_status, status_report.missing_files
    )
    _validate_archive_gate(root, slug, from_status, to_status, status_report.missing_files)
    return transition

from __future__ import annotations

from pathlib import Path

from .features import (
    FEATURE_FILE_PATHS,
    list_feature_bundles,
)
from .validation_models import ValidationCheck
from .validation_feature_helpers import _check, _content_scalar
from .validation_feature_peer import _feature_peer_checks

__all__ = [
    "_feature_bundle_checks",
    "_feature_status_checks",
    "_feature_peer_checks",
]


def _feature_status_checks(root: Path, slug: str) -> dict[str, str]:
    statuses_by_kind: dict[str, str] = {}
    for kind, pattern in FEATURE_FILE_PATHS.items():
        relative_path = pattern.format(slug=slug)
        target = root / relative_path
        if not target.exists():
            continue
        try:
            content = target.read_text(encoding="utf-8")
        except OSError:
            continue
        current_status = _content_scalar(content, "Status")
        if current_status:
            statuses_by_kind[kind] = current_status
    return statuses_by_kind


def _feature_bundle_checks(root: Path) -> list[ValidationCheck]:
    features = list_feature_bundles(root)
    if not features:
        return [
            _check(
                "feature.discovery",
                "skip",
                "No feature bundles were found.",
            )
        ]

    checks: list[ValidationCheck] = []
    for feature in features:
        slug = str(feature["slug"])
        checks.extend(_feature_peer_checks(root, slug))

    return checks

from __future__ import annotations

from pathlib import Path

from .features import InvalidFeatureSlug, validate_feature_slug
from .validation_feature_helpers import _check
from .validation_models import ValidationCheck

__all__ = [
    "_validate_peer_slug",
]


def _validate_peer_slug(slug: str) -> tuple[list[ValidationCheck], bool]:
    checks: list[ValidationCheck] = []
    try:
        validate_feature_slug(slug)
        checks.append(
            _check(
                f"feature.slug:{slug}",
                "pass",
                f"Feature slug is valid: {slug}",
            )
        )
        return checks, True
    except InvalidFeatureSlug as error:
        checks.append(
            _check(
                f"feature.slug:{slug}",
                "fail",
                str(error),
            )
        )
        return checks, False

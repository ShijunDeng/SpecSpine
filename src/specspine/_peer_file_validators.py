from __future__ import annotations

from .features import FEATURE_STATUSES
from .validation_feature_helpers import _check, _content_has_feature_id, _content_scalar
from .validation_models import ValidationCheck

__all__ = [
    "_validate_peer_feature_id",
    "_validate_peer_status",
]


def _validate_peer_feature_id(
    slug: str,
    kind: str,
    content: str,
) -> ValidationCheck:
    has_feature_id = _content_has_feature_id(content, slug)
    return _check(
        f"feature.id:{slug}:{kind}",
        "pass" if has_feature_id else "fail",
        f"Feature {slug} {kind} file declares its feature id."
        if has_feature_id
        else f"Feature {slug} {kind} file must declare Feature ID: {slug}.",
    )


def _validate_peer_status(
    slug: str,
    kind: str,
    content: str,
) -> tuple[ValidationCheck, str | None, bool]:
    current_status = _content_scalar(content, "Status")
    has_allowed_status = current_status in FEATURE_STATUSES
    status_value: str | None = None
    status_missing = False
    if current_status:
        status_value = current_status
    else:
        status_missing = True
    check = _check(
        f"feature.status:{slug}:{kind}",
        "pass" if has_allowed_status else "fail",
        f"Feature {slug} {kind} file declares allowed Status: {current_status}."
        if has_allowed_status
        else (
            f"Feature {slug} {kind} file must declare an allowed Status: "
            f"{', '.join(FEATURE_STATUSES)}."
        ),
    )
    return check, status_value, status_missing

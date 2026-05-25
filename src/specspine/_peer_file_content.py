from __future__ import annotations

from pathlib import Path

from .features import FEATURE_STATUSES
from .validation_feature_helpers import _check, _content_has_feature_id, _content_scalar
from .validation_models import ValidationCheck

__all__ = [
    "_check_peer_file_content",
]


def _check_peer_file_content(
    slug: str,
    kind: str,
    target: Path,
    relative_path: str,
) -> tuple[list[ValidationCheck], str | None, bool]:
    checks: list[ValidationCheck] = []
    status_value: str | None = None
    status_missing = False

    try:
        content = target.read_text(encoding="utf-8")
    except OSError:
        checks.append(
            _check(
                f"feature.readable:{slug}:{kind}",
                "fail",
                f"Feature {slug} {kind} file could not be read: {relative_path}",
            )
        )
        return checks, status_value, True

    has_feature_id = _content_has_feature_id(content, slug)
    checks.append(
        _check(
            f"feature.id:{slug}:{kind}",
            "pass" if has_feature_id else "fail",
            f"Feature {slug} {kind} file declares its feature id."
            if has_feature_id
            else f"Feature {slug} {kind} file must declare Feature ID: {slug}.",
        )
    )

    current_status = _content_scalar(content, "Status")
    has_allowed_status = current_status in FEATURE_STATUSES
    if current_status:
        status_value = current_status
    else:
        status_missing = True
    checks.append(
        _check(
            f"feature.status:{slug}:{kind}",
            "pass" if has_allowed_status else "fail",
            f"Feature {slug} {kind} file declares allowed Status: {current_status}."
            if has_allowed_status
            else (
                f"Feature {slug} {kind} file must declare an allowed Status: "
                f"{', '.join(FEATURE_STATUSES)}."
            ),
        )
    )

    return checks, status_value, status_missing

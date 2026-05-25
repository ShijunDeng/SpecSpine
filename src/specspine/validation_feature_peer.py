from __future__ import annotations

from pathlib import Path

from .features import (
    FEATURE_FILE_PATHS,
    FEATURE_STATUSES,
    InvalidFeatureSlug,
    validate_feature_slug,
)
from .validation_models import ValidationCheck
from .validation_feature_helpers import (
    _check,
    _content_has_feature_id,
    _content_scalar,
)

__all__ = [
    "_feature_peer_checks",
]


def _feature_peer_checks(root: Path, slug: str) -> list[ValidationCheck]:
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
    except InvalidFeatureSlug as error:
        checks.append(
            _check(
                f"feature.slug:{slug}",
                "fail",
                str(error),
            )
        )
        return checks

    statuses_by_kind: dict[str, str] = {}
    status_missing = False
    for kind, pattern in FEATURE_FILE_PATHS.items():
        relative_path = pattern.format(slug=slug)
        target = root / relative_path
        if target.exists():
            checks.append(
                _check(
                    f"feature.required_file:{slug}:{kind}",
                    "pass",
                    f"Feature {slug} {kind} file exists: {relative_path}",
                )
            )
        else:
            checks.append(
                _check(
                    f"feature.required_file:{slug}:{kind}",
                    "fail",
                    f"Feature {slug} {kind} file is missing: {relative_path}",
                )
            )
            continue

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
            continue

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
            statuses_by_kind[kind] = current_status
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

    unique_statuses = sorted(set(statuses_by_kind.values()))
    all_statuses_allowed = all(
        status in FEATURE_STATUSES for status in statuses_by_kind.values()
    )
    statuses_consistent = (
        not status_missing
        and len(statuses_by_kind) == len(FEATURE_FILE_PATHS)
        and len(unique_statuses) == 1
        and all_statuses_allowed
    )
    checks.append(
        _check(
            f"feature.status_consistency:{slug}",
            "pass" if statuses_consistent else "fail",
            f"Feature {slug} peer files consistently declare Status: {unique_statuses[0]}."
            if statuses_consistent
            else f"Feature {slug} peer files must declare the same allowed Status.",
        )
    )

    return checks

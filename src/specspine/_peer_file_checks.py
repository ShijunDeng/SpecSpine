from __future__ import annotations

from pathlib import Path

from .features import FEATURE_FILE_PATHS, FEATURE_STATUSES
from .validation_feature_helpers import _check, _content_has_feature_id, _content_scalar
from .validation_models import ValidationCheck

__all__ = [
    "_check_peer_files",
]


def _check_peer_files(
    root: Path,
    slug: str,
) -> tuple[list[ValidationCheck], dict[str, str], bool]:
    checks: list[ValidationCheck] = []
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

    return checks, statuses_by_kind, status_missing

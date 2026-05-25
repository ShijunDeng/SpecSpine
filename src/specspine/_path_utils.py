from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FeatureBundleNotFoundError,
    FeatureStatusReport,
    FEATURE_FILE_PATHS,
    _transition_payload,
    get_feature_status,
)

__all__ = [
    "_collect_paths",
    "_resolve_path",
    "_raise_missing_bundle_error",
]


def _collect_paths(resolved_root: Path, slug: str) -> dict:
    from .feature_bundle import feature_bundle_paths
    return feature_bundle_paths(resolved_root, slug)


def _resolve_path(slug: str, kind: str) -> Path:
    return Path(FEATURE_FILE_PATHS[kind].format(slug=slug))


def _raise_missing_bundle_error(
    slug: str,
    status: str,
    enforce_transition: bool,
    before: FeatureStatusReport,
) -> None:
    from .feature_bundle import (
        FeatureBundleNotFoundError,
        FeatureStatusTransitionError,
        _transition_payload,
    )
    if enforce_transition:
        reason = "Current peer-file statuses are missing or inconsistent."
        raise FeatureStatusTransitionError(
            feature_id=slug,
            error="current_status_inconsistent",
            transition=_transition_payload(
                from_status=before.status,
                to_status=status,
                enforced=True,
                allowed=False,
                reason=reason,
            ),
            message=(
                f"Cannot update feature {slug} status with enforced transition: "
                f"current status is unknown; {reason}"
            ),
            missing_files=before.missing_files,
        )
    paths = {kind: _resolve_path(slug, kind) for kind in FEATURE_FILE_PATHS}
    raise FeatureBundleNotFoundError(
        slug=slug,
        root=resolved_root,
        missing_paths=tuple(paths.values()),
    )

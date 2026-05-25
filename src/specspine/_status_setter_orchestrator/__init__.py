from __future__ import annotations

from pathlib import Path

from ..feature_bundle import FeatureStatusReport, get_feature_status
from ._preconditions import (
    _check_bundle_exists,
    _validate_and_resolve,
)
from ._report_builder import _build_status_report
from .._status_setter_transition import _build_transition
from .._status_setter_file_writer import _write_status_to_files

__all__ = [
    "set_feature_status",
]


def set_feature_status(
    root: Path,
    slug: str,
    status: str,
    *,
    enforce_transition: bool = False,
) -> FeatureStatusReport:
    slug, status, resolved_root, paths, relative_paths = _validate_and_resolve(
        root, slug, status,
    )

    before = get_feature_status(resolved_root, slug)
    _check_bundle_exists(slug, status, resolved_root, paths, before, enforce_transition)

    transition = _build_transition(
        resolved_root, slug, status, before, enforce_transition,
    )

    updated_files = _write_status_to_files(paths, slug, status)

    report = get_feature_status(resolved_root, slug)
    return _build_status_report(report, tuple(updated_files), transition)

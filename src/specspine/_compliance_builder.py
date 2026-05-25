from __future__ import annotations

from pathlib import Path

from .features import (
    list_feature_bundles,
    validate_feature_slug,
)
from ._compliance_audit_trail import _collect_feature_trails
from ._compliance_finalizer import _now_iso, _finalize_compliance_report

__all__ = [
    "_now_iso",
    "build_compliance_report",
]


def build_compliance_report(
    root: Path,
    feature_filter: str | None = None,
    since: str | None = None,
) -> object:
    resolved_root = root.expanduser().resolve()

    if feature_filter is not None:
        feature_filter = validate_feature_slug(feature_filter)

    discovered = list_feature_bundles(resolved_root)
    discovered_slugs = {str(f["slug"]) for f in discovered}

    if feature_filter is not None:
        slugs = (feature_filter,)
    else:
        slugs = tuple(sorted(discovered_slugs))

    trails, evidence_hashes = _collect_feature_trails(slugs, resolved_root, since)

    return _finalize_compliance_report(
        resolved_root,
        feature_filter,
        trails,
        evidence_hashes,
    )

from __future__ import annotations

from pathlib import Path

from ._feature_collection_assembly_filter import _iter_validated_features
from ._feature_collection_content import _read_bundle_content
from .release_extract import (
    _count_validation_evidence,
    _determine_status_transition,
    _extract_ac_summary,
    _extract_title,
)
from .release_models import ReleaseEntry

__all__ = [
    "_build_release_entries",
]


def _build_release_entries(
    root: Path,
    since: str | None = None,
    until: str | None = None,
) -> list[ReleaseEntry]:
    resolved_root = root.expanduser().resolve()
    entries: list[ReleaseEntry] = []
    for slug, status, metadata in _iter_validated_features(resolved_root):
        spec_content, execution_content, quality_content = _read_bundle_content(
            resolved_root, slug
        )
        title = _extract_title(spec_content)
        if not title:
            title = slug.replace("-", " ").title()
        ac_summary = _extract_ac_summary(spec_content, execution_content)
        validation_evidence_count = _count_validation_evidence(quality_content)
        status_transition = _determine_status_transition(status)
        entries.append(
            ReleaseEntry(
                slug=slug,
                title=title,
                priority=metadata.priority,
                status_transition=status_transition,
                ac_summary=ac_summary,
                validation_evidence_count=validation_evidence_count,
                project=metadata.project,
                effort=metadata.effort,
            )
        )
    entries.sort(key=lambda e: e.slug)
    return entries

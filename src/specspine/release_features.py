from __future__ import annotations

from pathlib import Path

from .features import (
    FEATURE_FILE_PATHS,
    InvalidFeatureSlug,
    list_feature_bundles,
    read_feature_metadata,
)
from .release_extract import (
    _count_validation_evidence,
    _determine_status_transition,
    _extract_ac_summary,
    _extract_title,
)
from .release_models import ReleaseEntry

__all__ = [
    "_collect_release_features",
    "_group_features",
]


def _collect_release_features(
    root: Path,
    since: str | None = None,
    until: str | None = None,
) -> list[ReleaseEntry]:
    resolved_root = root.expanduser().resolve()
    feature_bundles = list_feature_bundles(resolved_root)

    entries: list[ReleaseEntry] = []
    for feature in feature_bundles:
        slug = str(feature["slug"])
        status = feature.get("status")
        if status not in ("validated", "archived"):
            continue

        try:
            metadata = read_feature_metadata(resolved_root, slug)
        except InvalidFeatureSlug:
            continue

        bundle_paths = {
            kind: resolved_root / FEATURE_FILE_PATHS[kind].format(slug=slug)
            for kind in FEATURE_FILE_PATHS
        }

        spec_path = bundle_paths["spec"]
        execution_path = bundle_paths["execution"]
        quality_path = bundle_paths["quality"]

        spec_content = ""
        if spec_path.exists():
            try:
                spec_content = spec_path.read_text(encoding="utf-8")
            except OSError:
                pass

        execution_content = ""
        if execution_path.exists():
            try:
                execution_content = execution_path.read_text(encoding="utf-8")
            except OSError:
                pass

        quality_content = ""
        if quality_path.exists():
            try:
                quality_content = quality_path.read_text(encoding="utf-8")
            except OSError:
                pass

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


def _group_features(
    features: list[ReleaseEntry],
    group_by: str,
) -> dict[str, list[ReleaseEntry]]:
    groups: dict[str, list[ReleaseEntry]] = {}
    for feature in features:
        if group_by == "priority":
            key = feature.priority
        elif group_by == "project":
            key = feature.project
        elif group_by == "status":
            key = feature.status_transition
        elif group_by == "effort":
            key = feature.effort
        else:
            key = "all"

        groups.setdefault(key, []).append(feature)

    sorted_groups: dict[str, list[ReleaseEntry]] = {}
    for key in sorted(groups):
        sorted_groups[key] = sorted(groups[key], key=lambda e: e.slug)
    return sorted_groups

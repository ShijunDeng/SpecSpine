from __future__ import annotations

from pathlib import Path

from .feature_bundle_models import (
    FEATURE_DIRECTORIES,
    FEATURE_FILE_PATHS,
    FeatureMetadata,
    FeatureStatusReport,
    InvalidFeatureSlug,
)
from .feature_bundle_io_paths import (
    _relative_feature_paths,
    feature_bundle_paths,
)
from .feature_bundle_render import _extract_scalar
from .feature_bundle_validation import (
    normalize_feature_assignment,
    normalize_feature_effort,
    normalize_feature_owner,
    normalize_feature_priority,
    validate_feature_slug,
)

__all__ = [
    "_transition_payload",
    "_trace_gap",
    "get_feature_status",
    "list_feature_bundles",
    "read_feature_metadata",
]


def _transition_payload(
    *,
    from_status: str | None,
    to_status: str,
    enforced: bool,
    allowed: bool,
    reason: str | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "allowed": allowed,
        "enforced": enforced,
        "from": from_status,
        "to": to_status,
    }
    if reason:
        payload["reason"] = reason
    return payload


def _trace_gap(gap_id: str, source_file: str, message: str) -> dict[str, str]:
    return {
        "id": gap_id,
        "message": message,
        "source_file": source_file,
    }


def get_feature_status(root: Path, slug: str) -> FeatureStatusReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)

    files: dict[str, dict[str, object]] = {}
    missing_files: list[str] = []
    statuses: list[str] = []
    status_missing = False

    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        relative_path = relative_paths[kind]
        entry: dict[str, object] = {
            "exists": path.exists(),
            "path": relative_path,
            "status": None,
        }
        if path.exists():
            content = path.read_text(encoding="utf-8")
            status = _extract_scalar(content, "Status")
            entry["status"] = status
            if status:
                statuses.append(status)
            else:
                status_missing = True
        else:
            missing_files.append(relative_path)

        files[kind] = entry

    unique_statuses = sorted(set(statuses))
    current_status = unique_statuses[0] if len(unique_statuses) == 1 else None
    if len(unique_statuses) > 1:
        current_status = "mixed"

    existing_count = len(FEATURE_FILE_PATHS) - len(missing_files)
    consistent = existing_count > 0 and not status_missing and len(unique_statuses) == 1

    return FeatureStatusReport(
        feature_id=slug,
        status=current_status,
        consistent=consistent,
        files=files,
        missing_files=tuple(missing_files),
    )


def list_feature_bundles(root: Path) -> list[dict[str, object]]:
    resolved_root = root.expanduser().resolve()
    by_slug: dict[str, dict[str, str]] = {}

    for kind, directory_name in FEATURE_DIRECTORIES.items():
        directory = resolved_root / directory_name
        if not directory.exists():
            continue

        for path in sorted(directory.glob("*.md")):
            slug = path.stem
            relative_path = str(path.relative_to(resolved_root))
            by_slug.setdefault(slug, {})[kind] = relative_path

    features: list[dict[str, object]] = []
    required_kinds = set(FEATURE_FILE_PATHS)
    for slug in sorted(by_slug):
        files = by_slug[slug]
        try:
            status_report = get_feature_status(resolved_root, slug)
            status = status_report.status
            status_consistent = status_report.consistent
            missing_files = list(status_report.missing_files)
        except InvalidFeatureSlug:
            status = None
            status_consistent = False
            missing_files = [
                relative_path.format(slug=slug)
                for kind, relative_path in FEATURE_FILE_PATHS.items()
                if kind not in files
            ]
        features.append(
            {
                "slug": slug,
                "complete": set(files) == required_kinds,
                "files": dict(sorted(files.items())),
                "status": status,
                "status_consistent": status_consistent,
                "missing_files": missing_files,
            }
        )

    return features


def read_feature_metadata(root: Path, slug: str) -> FeatureMetadata:
    slug = validate_feature_slug(slug)
    spec_path = feature_bundle_paths(root, slug)["spec"]
    if not spec_path.exists():
        return FeatureMetadata(
            priority="unknown",
            owner="unassigned",
            milestone="unassigned",
            target_release="unassigned",
            project="unassigned",
            effort="unknown",
        )

    content = spec_path.read_text(encoding="utf-8")
    return FeatureMetadata(
        priority=normalize_feature_priority(_extract_scalar(content, "Priority")),
        owner=normalize_feature_owner(_extract_scalar(content, "Owner")),
        milestone=normalize_feature_assignment(_extract_scalar(content, "Milestone")),
        target_release=normalize_feature_assignment(
            _extract_scalar(content, "Target Release")
        ),
        project=normalize_feature_assignment(_extract_scalar(content, "Project")),
        effort=normalize_feature_effort(_extract_scalar(content, "Effort")),
    )

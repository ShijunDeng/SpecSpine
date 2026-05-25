from __future__ import annotations

import re
from pathlib import Path

from .evolution_impact_models import DEPENDENCY_PATTERNS, FEATURE_ID_RE
from .features import (
    FEATURE_FILE_PATHS,
    InvalidFeatureSlug,
    build_feature_tests_report,
    build_feature_trace_report,
    list_feature_bundles,
)


def _extract_feature_refs(text: str) -> list[str]:
    refs: list[str] = []
    for pattern in DEPENDENCY_PATTERNS:
        refs.extend(pattern.findall(text))
    refs.extend(FEATURE_ID_RE.findall(text))
    return sorted(set(refs))


def _extract_metadata(content: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    keys = {"Priority", "Owner", "Milestone", "Target Release", "Project", "Effort", "Status"}
    for line in content.splitlines():
        stripped = line.strip()
        if ":" in stripped and not stripped.startswith("#"):
            key, _, value = stripped.partition(":")
            key = key.strip()
            if key in keys:
                metadata[key] = value.strip()
    return metadata


def _find_downstream_references(
    slug: str,
    root: Path,
) -> dict[str, list[dict[str, str]]]:
    resolved_root = root.expanduser().resolve()
    all_features = list_feature_bundles(resolved_root)
    references: dict[str, list[dict[str, str]]] = {
        "tasks": [],
        "coverage": [],
        "dependent_features": [],
    }

    for feature in all_features:
        feature_slug = feature["slug"]
        if feature_slug == slug:
            continue
        try:
            trace = build_feature_trace_report(resolved_root, feature_slug)
            for ac in trace.acceptance_criteria:
                if slug.lower() in ac.text.lower():
                    references["tasks"].append({
                        "feature_id": feature_slug,
                        "item_id": ac.id,
                        "text": ac.text,
                    })
        except (InvalidFeatureSlug, OSError):
            continue

        try:
            tests_report = build_feature_tests_report(resolved_root, feature_slug)
            for coverage_link in tests_report.test_coverage:
                if slug.lower() in coverage_link.text.lower():
                    references["coverage"].append({
                        "feature_id": feature_slug,
                        "coverage_id": coverage_link.id,
                        "text": coverage_link.text,
                    })
        except (InvalidFeatureSlug, OSError):
            continue

        for file_kind in FEATURE_FILE_PATHS:
            file_path = resolved_root / FEATURE_FILE_PATHS[file_kind].format(slug=feature_slug)
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                feature_refs = _extract_feature_refs(content)
                if slug in feature_refs:
                    references["dependent_features"].append({
                        "feature_id": feature_slug,
                        "reference_type": file_kind,
                    })

    return references


__all__ = [
    "_extract_feature_refs",
    "_extract_metadata",
    "_find_downstream_references",
]

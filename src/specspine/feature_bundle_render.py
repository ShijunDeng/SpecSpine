from __future__ import annotations

from .feature_bundle_markdown import _extract_markdown_section
from .feature_bundle_models import (
    FEATURE_FILE_PATHS,
    FeatureMetadata,
    FeatureStatusReport,
)

__all__ = [
    "_extract_scalar",
    "_first_scalar",
    "_section_placeholder",
    "_section_or_placeholder",
    "_why_or_placeholder",
    "_render_metadata_lines",
    "_empty_trace_summary",
    "_feature_sources_from_status",
]


def _extract_scalar(content: str, key: str) -> str | None:
    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue

        current_key, value = stripped.split(":", 1)
        if current_key.strip().lower() != key.lower():
            continue

        value = value.strip()
        if value:
            return value

    return None


def _first_scalar(contents: dict[str, str], key: str) -> str | None:
    for kind in FEATURE_FILE_PATHS:
        content = contents.get(kind)
        if content is None:
            continue

        value = _extract_scalar(content, key)
        if value:
            return value

    return None


def _section_placeholder(kind: str, heading: str, relative_path: str) -> str:
    if kind == "missing_file":
        return f"TODO: Add `{relative_path}` with a `## {heading}` section."
    return f"TODO: Add a `## {heading}` section to `{relative_path}`."


def _section_or_placeholder(
    contents: dict[str, str],
    *,
    kind: str,
    heading: str,
    relative_path: str,
) -> str:
    content = contents.get(kind)
    if content is None:
        return _section_placeholder("missing_file", heading, relative_path)

    section = _extract_markdown_section(content, heading)
    if section:
        return section

    return _section_placeholder(kind, heading, relative_path)


def _why_or_placeholder(
    contents: dict[str, str],
    *,
    relative_path: str,
) -> str:
    spec = contents.get("spec")
    if spec is not None:
        section = _extract_markdown_section(spec, "Why")
        if section:
            return section

    scalar = _first_scalar(contents, "Why")
    if scalar:
        return scalar

    if spec is None:
        return _section_placeholder("missing_file", "Why", relative_path)

    return _section_placeholder("spec", "Why", relative_path)


def _render_metadata_lines(metadata: FeatureMetadata) -> list[str]:
    return [
        f"- Priority: {metadata.priority}",
        f"- Owner: {metadata.owner}",
        f"- Milestone: {metadata.milestone}",
        f"- Target Release: {metadata.target_release}",
        f"- Project: {metadata.project}",
        f"- Effort: {metadata.effort}",
    ]


def _empty_trace_summary() -> dict[str, object]:
    return {
        "acceptance_criteria": {"done": 0, "open": 0, "total": 0},
        "done": 0,
        "open": 0,
        "quality_checks": {"done": 0, "open": 0, "total": 0},
        "tasks": {"done": 0, "open": 0, "total": 0},
        "test_plan": {"total": 0},
        "total": 0,
    }


def _feature_sources_from_status(
    status_report: FeatureStatusReport,
) -> dict[str, dict[str, object]]:
    return {
        kind: {
            "exists": file["exists"],
            "path": file["path"],
        }
        for kind, file in status_report.files.items()
    }

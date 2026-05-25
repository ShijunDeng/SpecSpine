from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    _first_line_h1,
    _why_or_placeholder,
    feature_title,
    read_feature_metadata,
)
from .feature_handoff import build_feature_handoff_report
from .feature_ready import build_feature_ready_report

from ._pr_draft_collector import PrDraftFileCollection

__all__ = [
    "compute_draft_title",
    "compute_draft_why",
    "compute_draft_summary",
    "load_draft_context",
]


def compute_draft_title(
    spec_content: str,
    slug: str,
) -> str:
    return _first_line_h1(spec_content) or feature_title(slug)


def compute_draft_why(
    contents: dict[str, str],
    relative_paths: dict[str, str],
) -> str:
    return _why_or_placeholder(contents, relative_path=relative_paths["spec"])


def compute_draft_summary(
    handoff_summary: dict,
    collection: PrDraftFileCollection,
) -> dict:
    return {
        **handoff_summary,
        "source_files": {"total": len(collection.source_files)},
        "missing_files": {"total": len(collection.missing_files)},
    }


def load_draft_context(
    resolved_root: Path,
    slug: str,
    collection: PrDraftFileCollection,
) -> dict:
    handoff = build_feature_handoff_report(resolved_root, slug)
    ready_report = build_feature_ready_report(resolved_root, slug)
    metadata = read_feature_metadata(resolved_root, slug)
    summary = compute_draft_summary(handoff.summary, collection)
    return {
        "handoff": handoff,
        "ready_report": ready_report,
        "metadata": metadata,
        "summary": summary,
    }

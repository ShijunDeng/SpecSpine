from __future__ import annotations

from pathlib import Path

from .feature_bundle import validate_feature_slug

from ._pr_draft_assembler import (
    build_pull_request_draft as _assemble_pr_draft,
)
from ._pr_draft_collector import (
    PrDraftFileCollection,
    collect_pr_draft_files,
)

__all__ = [
    "PrDraftFileCollection",
    "build_pull_request_draft",
    "collect_pr_draft_files",
]


def build_pull_request_draft(root: Path, slug: str):
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    collection = collect_pr_draft_files(resolved_root, slug)
    return _assemble_pr_draft(resolved_root, slug, collection)

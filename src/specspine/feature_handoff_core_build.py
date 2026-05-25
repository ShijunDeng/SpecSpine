from __future__ import annotations

from pathlib import Path

from .feature_bundle import FeatureHandoffReport
from ._handoff_build_fetch import fetch_handoff_context
from ._handoff_build_assemble import assemble_handoff_report

__all__ = [
    "FeatureHandoffReport",
    "build_feature_handoff_report",
]


def build_feature_handoff_report(
    root: Path,
    slug: str,
    *,
    require_coverage: bool = False,
) -> FeatureHandoffReport:
    ctx = fetch_handoff_context(root, slug, require_coverage=require_coverage)
    return assemble_handoff_report(ctx)

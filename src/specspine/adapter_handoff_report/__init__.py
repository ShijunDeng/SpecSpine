from __future__ import annotations

from ._assembly import assemble_adapter_feature_handoff_report
from ._validation import validate_feature_bundle

__all__ = [
    "build_adapter_feature_handoff_report",
]


def build_adapter_feature_handoff_report(
    root,
    slug: str,
):
    feature_report, resolved_root = validate_feature_bundle(root, slug)
    return assemble_adapter_feature_handoff_report(
        feature_report,
        resolved_root,
        slug,
    )

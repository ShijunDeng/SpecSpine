from __future__ import annotations

from pathlib import Path

from ..features import (
    validate_feature_slug,
)
from .report_collectors import collect_reports
from .packet_assembly import assemble_review_packet
from .feature_evidence import _feature_payload

__all__ = [
    "build_review_packet",
]


def build_review_packet(
    root: Path,
    *,
    feature: str | None = None,
    changed_files: tuple[str, ...] = (),
) -> object:
    resolved_root = root.expanduser().resolve()
    feature_slug = validate_feature_slug(feature) if feature is not None else None

    reports = collect_reports(resolved_root, feature_slug, changed_files)
    validation = reports["validation"]
    gates = reports["gates"]
    impact = reports["impact"]

    feature_payload = _feature_payload(resolved_root, feature_slug) if feature_slug else None

    return assemble_review_packet(
        resolved_root,
        feature_slug,
        validation,
        gates,
        impact,
        feature_payload,
    )

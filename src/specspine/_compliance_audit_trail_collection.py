from __future__ import annotations

from pathlib import Path

from .audit_models import AuditTrail
from .features import validate_feature_slug
from ._compliance_audit_trail_build import _build_feature_audit_trail

__all__ = [
    "_collect_feature_trails",
]


def _collect_feature_trails(
    slugs: tuple[str, ...],
    resolved_root: Path,
    since: str | None,
) -> tuple[list[AuditTrail], list[str]]:
    trails: list[AuditTrail] = []
    evidence_hashes: list[str] = []

    for slug in slugs:
        validate_feature_slug(slug)
        trail, evidence_hash = _build_feature_audit_trail(slug, resolved_root, since)
        trails.append(trail)
        evidence_hashes.append(evidence_hash)

    return trails, evidence_hashes

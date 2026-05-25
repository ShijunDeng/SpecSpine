from __future__ import annotations

from pathlib import Path
from typing import Any

from .audit_events import _feature_peer_content
from ._peer_content_reader import _gather_peer_evidence
from ._validation_checks import _run_validation_checks


def _gather_validation_evidence(slug: str, root: Path) -> dict[str, Any]:
    evidence = _gather_peer_evidence(slug, root)
    evidence["validation_checks"] = []

    quality_content = _feature_peer_content(root, slug, "quality")
    evidence["validation_checks"] = _run_validation_checks(evidence, quality_content)

    return evidence


__all__ = [
    "_gather_validation_evidence",
]

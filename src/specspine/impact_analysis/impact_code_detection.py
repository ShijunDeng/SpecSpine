from __future__ import annotations

from pathlib import Path
from typing import Any

from .impact_code_source_scan import _scan_source_files
from .impact_code_artifact_scan import _scan_feature_artifacts
from .impact_models import ImpactItem

__all__ = [
    "_find_affected_code",
]


def _find_affected_code(
    slug: str,
    root: Path,
    proposed_changes: dict[str, Any] | None = None,
) -> list[ImpactItem]:
    affected, seen = _scan_source_files(slug, root, proposed_changes)
    affected.extend(_scan_feature_artifacts(slug, root, seen, proposed_changes))
    return affected

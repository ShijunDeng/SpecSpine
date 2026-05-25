from __future__ import annotations

from pathlib import Path
from typing import Any

from .impact_test_detection_slug_scan import _scan_tests_by_slug
from .impact_test_detection_ac_scan import _scan_tests_by_ac
from .impact_test_detection_quality_scan import _scan_tests_by_quality
from .impact_models import ImpactItem

__all__ = [
    "_find_affected_tests",
    "_scan_tests_by_slug",
    "_scan_tests_by_ac",
    "_scan_tests_by_quality",
]


def _find_affected_tests(
    slug: str,
    root: Path,
    proposed_changes: dict[str, Any] | None = None,
) -> list[ImpactItem]:
    resolved_root = root.expanduser().resolve()
    affected: list[ImpactItem] = []
    seen: set[str] = set()

    _scan_tests_by_slug(slug, resolved_root, affected, seen)
    _scan_tests_by_ac(slug, resolved_root, affected, seen)
    _scan_tests_by_quality(slug, resolved_root, affected, seen)

    return affected

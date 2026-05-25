from __future__ import annotations

from pathlib import Path

from .drift_models import DriftEvent
from ._drift_code_orphan_files import _detect_orphaned_code_drift
from ._drift_code_ac_references import _detect_ac_reference_drift


def _detect_code_drift(slug: str, root: Path) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    events.extend(_detect_orphaned_code_drift(slug, root))
    events.extend(_detect_ac_reference_drift(slug, root))
    return events


__all__ = [
    "_detect_code_drift",
]

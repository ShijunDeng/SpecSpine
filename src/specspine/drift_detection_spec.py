from __future__ import annotations

from pathlib import Path

from .drift_models import DriftEvent
from ._drift_spec_extract import _extract_current_spec_acs
from ._drift_spec_compare import _compare_spec_against_baseline

__all__ = [
    "_detect_spec_drift",
]


def _detect_spec_drift(slug: str, root: Path, baseline: str | None) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    current_acs = _extract_current_spec_acs(root, slug)
    if current_acs is None:
        return events

    if baseline is not None:
        events.extend(
            _compare_spec_against_baseline(slug, root, baseline, current_acs)
        )

    return events

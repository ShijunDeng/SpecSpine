from __future__ import annotations

from pathlib import Path

from ..drift_models import DriftEvent
from ._drift_spec_baseline import _extract_baseline_acs, _read_baseline_spec
from ._drift_spec_events import (
    _build_ac_added_event,
    _build_ac_removed_event,
    _build_spec_missing_event,
)
from ._ac_diff import _compute_ac_diff

__all__ = [
    "_compare_spec_against_baseline",
]


def _compare_spec_against_baseline(
    slug: str,
    root: Path,
    baseline: str,
    current_acs: list[str],
) -> list[DriftEvent]:
    events: list[DriftEvent] = []

    before = _read_baseline_spec(root, slug, baseline)
    if before is None:
        if current_acs:
            events.append(_build_spec_missing_event(baseline, current_acs))
        return events

    before_acs = _extract_baseline_acs(before)
    removed, added = _compute_ac_diff(before_acs, current_acs)

    if removed:
        events.append(_build_ac_removed_event(baseline, removed))

    if added:
        events.append(_build_ac_added_event(baseline, added))

    return events

from __future__ import annotations

from pathlib import Path

from .drift_models import DriftEvent
from .drift_detection_extractors import (
    _now_iso,
    _baseline_peer_content,
    _extract_acs_from_spec,
)

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

    before = _baseline_peer_content(root, slug, "spec", baseline)
    if before is None:
        if current_acs:
            events.append(
                DriftEvent(
                    event_type="spec",
                    severity="high",
                    timestamp=_now_iso(),
                    description=f"Spec file exists but missing at baseline '{baseline}'; all ACs are new",
                    affected_acs=tuple(sorted(set(current_acs))),
                )
            )
        return events

    before_acs = _extract_acs_from_spec(before)
    before_set = set(before_acs)
    current_set = set(current_acs)

    removed = sorted(before_set - current_set)
    added = sorted(current_set - before_set)

    if removed:
        events.append(
            DriftEvent(
                event_type="spec",
                severity="critical",
                timestamp=_now_iso(),
                description=f"ACs removed from spec compared to baseline '{baseline}'",
                affected_acs=tuple(removed),
            )
        )

    if added:
        events.append(
            DriftEvent(
                event_type="spec",
                severity="medium",
                timestamp=_now_iso(),
                description=f"ACs added to spec compared to baseline '{baseline}'",
                affected_acs=tuple(added),
            )
        )

    return events

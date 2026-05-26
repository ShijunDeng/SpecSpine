from __future__ import annotations

from ..drift_models import DriftEvent
from ..drift_detection_extractors import _now_iso

__all__ = [
    "_build_spec_missing_event",
    "_build_ac_removed_event",
    "_build_ac_added_event",
]


def _build_spec_missing_event(
    baseline: str,
    current_acs: list[str],
) -> DriftEvent:
    return DriftEvent(
        event_type="spec",
        severity="high",
        timestamp=_now_iso(),
        description=f"Spec file exists but missing at baseline '{baseline}'; all ACs are new",
        affected_acs=tuple(sorted(set(current_acs))),
    )


def _build_ac_removed_event(
    baseline: str,
    removed: list[str],
) -> DriftEvent:
    return DriftEvent(
        event_type="spec",
        severity="critical",
        timestamp=_now_iso(),
        description=f"ACs removed from spec compared to baseline '{baseline}'",
        affected_acs=tuple(removed),
    )


def _build_ac_added_event(
    baseline: str,
    added: list[str],
) -> DriftEvent:
    return DriftEvent(
        event_type="spec",
        severity="medium",
        timestamp=_now_iso(),
        description=f"ACs added to spec compared to baseline '{baseline}'",
        affected_acs=tuple(added),
    )

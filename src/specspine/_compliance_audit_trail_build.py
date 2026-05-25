from __future__ import annotations

from pathlib import Path

from .audit_events import (
    _build_lifecycle_transitions,
    _collect_audit_events,
    _hash_content,
)
from .audit_models import AuditTrail
from .audit_validation import (
    _build_drift_history,
    _gather_validation_evidence,
)

__all__ = [
    "_build_feature_audit_trail",
]


def _build_feature_audit_trail(
    slug: str,
    resolved_root: Path,
    since: str | None,
) -> tuple[AuditTrail, str]:
    events = _collect_audit_events(slug, resolved_root, since)
    transitions = _build_lifecycle_transitions(slug, resolved_root)
    validation = _gather_validation_evidence(slug, resolved_root)
    drift = _build_drift_history(slug, resolved_root, since)

    event_tuple = tuple(events)
    transition_tuple = tuple(
        {
            "from_status": t["from_status"],
            "to_status": t["to_status"],
            "date": t["date"],
            "author": t["author"],
            "commit": t["commit"],
        }
        for t in transitions
    )
    drift_tuple = tuple(drift)

    trail = AuditTrail(
        feature_id=slug,
        events=event_tuple,
        lifecycle_transitions=transition_tuple,
        validation_evidence=validation,
        drift_history=drift_tuple,
    )

    hash_input = slug + "".join(e.evidence_hash for e in events)
    evidence_hash = _hash_content(hash_input)

    return trail, evidence_hash

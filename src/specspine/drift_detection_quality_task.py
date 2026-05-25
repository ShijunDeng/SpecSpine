from __future__ import annotations

from pathlib import Path

from .drift_models import DriftEvent
from .drift_detection_extractors import (
    _now_iso,
    _feature_peer_content,
    _extract_acs_from_spec,
    _extract_tasks_from_execution,
    AC_ID_RE,
)

__all__ = [
    "_detect_task_drift",
]


def _detect_task_drift(slug: str, root: Path) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    exec_content = _feature_peer_content(root, slug, "execution")
    spec_content = _feature_peer_content(root, slug, "spec")
    if exec_content is None or spec_content is None:
        return events

    exec_tasks = _extract_tasks_from_execution(exec_content)
    spec_acs = _extract_acs_from_spec(spec_content)

    task_ac_refs: set[str] = set()
    for line in exec_content.splitlines():
        for ac_match in AC_ID_RE.finditer(line):
            task_ac_refs.add(ac_match.group(1))

    missing = sorted(set(spec_acs) - task_ac_refs)
    if missing:
        events.append(
            DriftEvent(
                event_type="task",
                severity="medium",
                timestamp=_now_iso(),
                description="Tasks in execution do not reference all spec ACs",
                affected_acs=tuple(missing),
            )
        )

    return events

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


def _extract_task_ac_refs(exec_content: str) -> set[str]:
    task_ac_refs: set[str] = set()
    for line in exec_content.splitlines():
        for ac_match in AC_ID_RE.finditer(line):
            task_ac_refs.add(ac_match.group(1))
    return task_ac_refs


def _detect_ac_reference_drift(slug: str, root: Path) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    spec_content = _feature_peer_content(root, slug, "spec")
    if spec_content is None:
        return events

    exec_content = _feature_peer_content(root, slug, "execution")
    if exec_content is not None:
        _extract_tasks_from_execution(exec_content)
        tasks_in_spec = _extract_acs_from_spec(spec_content)
        task_ac_refs = _extract_task_ac_refs(exec_content)

        missing_ac_links = sorted(set(tasks_in_spec) - task_ac_refs)
        if missing_ac_links:
            events.append(
                DriftEvent(
                    event_type="code",
                    severity="medium",
                    timestamp=_now_iso(),
                    description="Tasks in execution file do not reference all spec ACs",
                    affected_acs=tuple(missing_ac_links),
                )
            )

    return events


__all__ = [
    "_extract_task_ac_refs",
    "_detect_ac_reference_drift",
]

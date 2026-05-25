from __future__ import annotations

import re
from pathlib import Path

from .drift_models import DriftEvent
from .drift_detection_extractors import (
    _now_iso,
    _feature_peer_content,
    _extract_acs_from_spec,
)


def _detect_task_drift(slug: str, root: Path) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    exec_content = _feature_peer_content(root, slug, "execution")
    spec_content = _feature_peer_content(root, slug, "spec")
    if exec_content is None or spec_content is None:
        return events

    from .drift_detection_extractors import (
        _extract_tasks_from_execution,
        AC_ID_RE,
    )

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


def _detect_quality_drift(slug: str, root: Path) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    quality_content = _feature_peer_content(root, slug, "quality")
    spec_content = _feature_peer_content(root, slug, "spec")
    if quality_content is None:
        return events

    quality_check_re = re.compile(r"(QC\d{3})")
    cov_link_re = re.compile(r"- \[[ xX]\]\s+(AC\d{3})\s*->\s*(\S+)")

    qc_ids_in_quality = set(quality_check_re.findall(quality_content))
    cov_links = cov_link_re.findall(quality_content)
    covered_acs = {ac_id for ac_id, _ in cov_links}

    if spec_content is not None:
        spec_acs = set(_extract_acs_from_spec(spec_content))
        acs_without_qc = sorted(spec_acs - qc_ids_in_quality - covered_acs)
        if acs_without_qc:
            events.append(
                DriftEvent(
                    event_type="quality",
                    severity="low",
                    timestamp=_now_iso(),
                    description="Spec ACs missing quality check or coverage link",
                    affected_acs=tuple(acs_without_qc),
                )
            )

    for ac_id, target_path in cov_links:
        if not target_path.startswith("tests/"):
            events.append(
                DriftEvent(
                    event_type="quality",
                    severity="low",
                    timestamp=_now_iso(),
                    description=f"Coverage link for {ac_id} does not point to a tests/ path",
                    affected_acs=(ac_id,),
                )
            )

    return events


def _detect_test_drift(slug: str, root: Path) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    spec_content = _feature_peer_content(root, slug, "spec")
    quality_content = _feature_peer_content(root, slug, "quality")
    if spec_content is None or quality_content is None:
        return events

    cov_link_re = re.compile(r"- \[[ xX]\]\s+(AC\d{3})\s*->\s*(\S+)")

    spec_acs = set(_extract_acs_from_spec(spec_content))
    cov_links = cov_link_re.findall(quality_content)
    covered_acs: set[str] = set()
    for ac_id, target_path in cov_links:
        covered_acs.add(ac_id)
        if not (root / target_path).exists():
            events.append(
                DriftEvent(
                    event_type="test",
                    severity="high",
                    timestamp=_now_iso(),
                    description=f"Test coverage link references stale test file",
                    affected_acs=(ac_id,),
                )
            )

    uncovered_acs = sorted(spec_acs - covered_acs)
    if uncovered_acs:
        events.append(
            DriftEvent(
                event_type="test",
                severity="high",
                timestamp=_now_iso(),
                description="Spec ACs have no test coverage link in quality file",
                affected_acs=tuple(uncovered_acs),
            )
        )

    return events


__all__ = [
    "_detect_quality_drift",
    "_detect_task_drift",
    "_detect_test_drift",
]

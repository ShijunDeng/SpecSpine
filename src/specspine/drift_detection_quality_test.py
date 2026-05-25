from __future__ import annotations

import re
from pathlib import Path

from .drift_models import DriftEvent
from .drift_detection_extractors import (
    _now_iso,
    _feature_peer_content,
    _extract_acs_from_spec,
)

__all__ = [
    "_detect_test_drift",
]


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

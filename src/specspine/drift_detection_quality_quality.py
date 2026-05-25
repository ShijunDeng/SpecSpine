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
    "_detect_quality_drift",
]


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

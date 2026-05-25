from __future__ import annotations

from pathlib import Path

from .drift_detection import (
    _detect_code_drift,
    _detect_quality_drift,
    _detect_spec_drift,
    _detect_test_drift,
)
from .drift_history import _build_drift_history
from .drift_models import FeatureDriftRecord
from .drift_severity import _classify_severity
from .features import validate_feature_slug

__all__ = [
    "_parse_feature_drift",
]


def _parse_feature_drift(slug: str, root: Path, baseline: str | None, since: str | None) -> FeatureDriftRecord:
    validate_feature_slug(slug)

    spec_events = _detect_spec_drift(slug, root, baseline)
    code_events = _detect_code_drift(slug, root)
    test_events = _detect_test_drift(slug, root)
    quality_events = _detect_quality_drift(slug, root)

    severity = _classify_severity(spec_events, code_events, test_events, quality_events)

    all_drift = spec_events + code_events + test_events + quality_events
    history = _build_drift_history(slug, root, since)
    combined_events = tuple(all_drift + history)

    return FeatureDriftRecord(
        feature_id=slug,
        severity=severity,
        spec_drift=tuple(spec_events),
        code_drift=tuple(code_events),
        test_drift=tuple(test_events),
        quality_drift=tuple(quality_events),
        drift_events=combined_events,
        cascade_risk=False,
    )

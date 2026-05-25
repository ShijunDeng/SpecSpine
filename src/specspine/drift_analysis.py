from __future__ import annotations

from pathlib import Path

from .drift_detection import (
    _detect_code_drift,
    _detect_quality_drift,
    _detect_spec_drift,
    _detect_test_drift,
)
from .drift_history import _build_drift_history
from .drift_models import DriftEvent, FeatureDriftRecord
from .features import validate_feature_slug

__all__ = [
    "_classify_severity",
    "_correlate_cross_feature_drift",
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


def _classify_severity(
    spec_events: list[DriftEvent],
    code_events: list[DriftEvent],
    test_events: list[DriftEvent],
    quality_events: list[DriftEvent],
) -> str:
    all_events = spec_events + code_events + test_events + quality_events
    if not all_events:
        return "none"

    severity_order = ["critical", "high", "medium", "low"]
    for sev in severity_order:
        for ev in all_events:
            if ev.severity == sev:
                return sev
    return "none"


def _correlate_cross_feature_drift(
    features: list[FeatureDriftRecord],
    root: Path,
) -> None:
    from .consistency import _read_text
    from .features import FEATURE_FILE_PATHS
    from .dependency import _extract_slugs_from_text

    critical_features: dict[str, FeatureDriftRecord] = {}
    for f in features:
        if f.severity == "critical":
            critical_features[f.feature_id] = f

    if not critical_features:
        return

    all_content: dict[str, str] = {}
    for f in features:
        content_parts: list[str] = []
        for kind in ("spec", "execution", "quality"):
            rel_path = FEATURE_FILE_PATHS.get(kind)
            if rel_path is None:
                continue
            path = root / rel_path.format(slug=f.feature_id)
            if path.exists():
                content_parts.append(_read_text(path))
        all_content[f.feature_id] = "\n".join(content_parts)

    all_slugs = {f.feature_id for f in features}
    for f in features:
        if f.cascade_risk:
            continue
        content = all_content.get(f.feature_id, "")
        deps = _extract_slugs_from_text(content, f.feature_id, all_slugs)
        for dep_slug in deps:
            if dep_slug in critical_features:
                object.__setattr__(f, "cascade_risk", True)
                break

from __future__ import annotations

from pathlib import Path

from .drift_models import FeatureDriftRecord

__all__ = [
    "_correlate_cross_feature_drift",
]


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

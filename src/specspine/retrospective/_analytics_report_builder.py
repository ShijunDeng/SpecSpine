from __future__ import annotations

from pathlib import Path

from .retrospective_build import build_retrospective_report
from ._analytics_patterns import _detect_anti_patterns
from ._analytics_improvements import _generate_improvements
from ._workspace_metrics import _workspace_analytics

__all__ = [
    "build_retrospective_analytics_report",
]


def build_retrospective_analytics_report(root, *, include_improvements=False, feature_slug=None):
    """Build retrospective analytics report with anti-pattern detection."""
    resolved_root = Path(root).expanduser().resolve()
    features_data = build_retrospective_report(resolved_root, feature_slug=feature_slug)
    features = features_data.get("features", [])
    anti_patterns = _detect_anti_patterns(features)
    analytics = _workspace_analytics(features)
    improvements = _generate_improvements(anti_patterns, analytics) if include_improvements else []
    return {
        "analytics": analytics,
        "anti_patterns": anti_patterns,
        "features": features,
        "feature_filter": feature_slug,
        "improvements": improvements,
        "recommendations": features_data.get("recommendations", []),
        "root": str(resolved_root),
        "summary": features_data.get("summary", {}),
        "themes": features_data.get("themes", {})
    }

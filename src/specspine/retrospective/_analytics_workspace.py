from __future__ import annotations

import json
from pathlib import Path

from .retrospective_build import build_retrospective_report
from ._analytics_patterns import _detect_anti_patterns
from ._analytics_improvements import _generate_improvements

__all__ = [
    "_workspace_analytics",
    "build_retrospective_analytics_report",
    "render_retrospective_analytics_json",
]


def _workspace_analytics(features: list) -> dict:
    """Compute aggregate workspace analytics."""
    total = len(features)
    by_status = {}
    readiness_scores = []
    coverage_completeness = []
    for f in features:
        s = f.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
        readiness = f.get("readiness_counts", {})
        total_checks = readiness.get("total", 0)
        pass_checks = readiness.get("pass", 0)
        score = (pass_checks / total_checks * 100) if total_checks > 0 else 0
        readiness_scores.append(score)
        coverage = f.get("coverage_state", {})
        ac_total = coverage.get("total_acceptance_criteria", 0)
        links = coverage.get("total_links", 0)
        cov = (links / ac_total * 100) if ac_total > 0 else 0
        coverage_completeness.append(cov)
    avg_readiness = sum(readiness_scores) / len(readiness_scores) if readiness_scores else 0
    avg_coverage = sum(coverage_completeness) / len(coverage_completeness) if coverage_completeness else 0
    return {
        "total_features": total,
        "by_status": by_status,
        "avg_readiness_score": round(avg_readiness, 1),
        "avg_coverage_completeness": round(avg_coverage, 1)
    }


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


def render_retrospective_analytics_json(report: dict) -> str:
    """Render retrospective analytics report as JSON."""
    return json.dumps(report, indent=2, sort_keys=True) + "\n"

from __future__ import annotations

import json
from pathlib import Path

from .retrospective_build import build_retrospective_report


def _detect_anti_patterns(features: list) -> list:
    """Detect common anti-patterns across feature bundles."""
    patterns = []
    for f in features:
        fid = f.get("feature_id", "")
        coverage = f.get("coverage_state", {})
        gaps = f.get("gaps", [])
        blocking = f.get("blocking_checks", [])
        status = f.get("status", "")
        ac_count = coverage.get("total_acceptance_criteria", 0)
        links = coverage.get("total_links", 0)
        if blocking:
            for b in blocking:
                if "coverage" in b.get("id", "").lower():
                    patterns.append({
                        "anti_pattern_id": f"AP-{fid}-cov",
                        "type": "coverage_gap",
                        "severity": "high",
                        "feature_id": fid,
                        "description": f"Feature {fid} has coverage gaps",
                        "recommendation": "Add test coverage links for all ACs"
                    })
        if gaps:
            patterns.append({
                "anti_pattern_id": f"AP-{fid}-gaps",
                "type": "trace_gaps",
                "severity": "medium",
                "feature_id": fid,
                "description": f"Feature {fid} has {len(gaps)} trace gaps",
                "recommendation": "Complete traceability between ACs, tasks, and tests"
            })
        if ac_count > 0 and links == 0:
            patterns.append({
                "anti_pattern_id": f"AP-{fid}-no-tests",
                "type": "no_test_coverage",
                "severity": "high",
                "feature_id": fid,
                "description": f"Feature {fid} has {ac_count} ACs but no test coverage links",
                "recommendation": "Add test coverage links in quality file"
            })
        if status == "implemented":
            patterns.append({
                "anti_pattern_id": f"AP-{fid}-stalled",
                "type": "stalled_feature",
                "severity": "low",
                "feature_id": fid,
                "description": f"Feature {fid} stuck in implemented status",
                "recommendation": "Run feature ready and advance to validated"
            })
    return patterns


def _generate_improvements(anti_patterns: list, analytics: dict) -> list:
    """Generate improvement recommendations from anti-patterns."""
    improvements = []
    by_type = {}
    for ap in anti_patterns:
        by_type.setdefault(ap["type"], []).append(ap)
    if by_type.get("coverage_gap"):
        improvements.append({
            "id": "IMP-001",
            "priority": "high",
            "description": "Close coverage gaps across features",
            "action": "Add test coverage links for all acceptance criteria",
            "affected_features": [ap["feature_id"] for ap in by_type["coverage_gap"]]
        })
    if by_type.get("no_test_coverage"):
        improvements.append({
            "id": "IMP-002",
            "priority": "high",
            "description": "Add test coverage to features without any links",
            "action": "Map each AC to at least one test file",
            "affected_features": [ap["feature_id"] for ap in by_type["no_test_coverage"]]
        })
    if by_type.get("trace_gaps"):
        improvements.append({
            "id": "IMP-003",
            "priority": "medium",
            "description": "Complete traceability for features with gaps",
            "action": "Link ACs to tasks and tests in traceability export",
            "affected_features": [ap["feature_id"] for ap in by_type["trace_gaps"]]
        })
    if by_type.get("stalled_feature"):
        improvements.append({
            "id": "IMP-004",
            "priority": "low",
            "description": "Advance stalled features",
            "action": "Run feature ready and set status to validated",
            "affected_features": [ap["feature_id"] for ap in by_type["stalled_feature"]]
        })
    return improvements


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


__all__ = [
    "_detect_anti_patterns",
    "_generate_improvements",
    "_workspace_analytics",
    "build_retrospective_analytics_report",
    "render_retrospective_analytics_json",
]

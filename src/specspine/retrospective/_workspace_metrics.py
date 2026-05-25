from __future__ import annotations

__all__ = [
    "_workspace_analytics",
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

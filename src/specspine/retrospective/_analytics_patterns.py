from __future__ import annotations

__all__ = [
    "_detect_anti_patterns",
]


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
                "recommendation": "Add test coverage link in quality file"
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

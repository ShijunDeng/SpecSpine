from __future__ import annotations

__all__ = [
    "_generate_improvements",
]


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

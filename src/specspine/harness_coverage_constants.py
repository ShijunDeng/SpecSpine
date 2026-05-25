from __future__ import annotations

__all__ = [
    "GOVERNED_DIMENSIONS",
    "DIMENSION_SENSOR_MAP",
    "MATURITY_LABELS",
]

GOVERNED_DIMENSIONS = (
    "verification",
    "coverage",
    "grading",
    "validation",
    "consistency",
    "hygiene",
    "security",
    "change_risk",
)

DIMENSION_SENSOR_MAP = {
    "verification": "verification_matrix",
    "coverage": "coverage_debt",
    "grading": "grading_rubric",
    "validation": "validation_contract",
    "consistency": "consistency_scan",
    "hygiene": "hygiene_scan",
    "security": "security_cues",
    "change_risk": "change_risk",
}

MATURITY_LABELS = {
    0: "none",
    1: "initial",
    2: "managed",
    3: "defined",
    4: "optimized",
    5: "mastered",
}

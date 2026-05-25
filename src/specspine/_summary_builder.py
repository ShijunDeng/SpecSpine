from __future__ import annotations

from typing import Any

from .consistency_models import (
    FeatureConsistency,
)

__all__ = [
    "_summary",
]


def _summary(features: tuple[FeatureConsistency, ...], discovered_features: int) -> dict[str, Any]:
    checks = [check for feature in features for check in feature.consistency_checks]
    return {
        "changed_references": sum(len(feature.changed_references) for feature in features),
        "checks_fail": sum(1 for check in checks if check.status == "fail"),
        "checks_pass": sum(1 for check in checks if check.status == "pass"),
        "checks_total": len(checks),
        "checks_warn": sum(1 for check in checks if check.status == "warn"),
        "discovered_features": discovered_features,
        "documentation_references": sum(
            len(feature.documentation_references) for feature in features
        ),
        "features_scanned": len(features),
        "features_with_missing_files": sum(1 for feature in features if feature.missing_files),
        "implementation_references": sum(
            len(feature.implementation_references) for feature in features
        ),
        "test_references": sum(len(feature.test_references) for feature in features),
    }

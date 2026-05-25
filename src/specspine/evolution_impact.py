from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .dependency import build_dependency_graph
from .evolution_classification import ClassifiedChange
from .features import (
    FEATURE_FILE_PATHS,
    InvalidFeatureSlug,
    build_feature_tests_report,
    build_feature_trace_report,
    list_feature_bundles,
    validate_feature_slug,
)

from .evolution_impact_downstream import (
    _extract_feature_refs,
    _extract_metadata,
    _find_downstream_references,
)
from .evolution_impact_models import (
    DEPENDENCY_PATTERNS,
    FEATURE_ID_RE,
    ImpactEntry,
    ImpactResult,
    RemediationAction,
)
from .evolution_impact_remediation import (
    calculate_risk_level,
    generate_remediation_plan,
)
from .evolution_impact_resolve import resolve_impact


__all__ = [
    "DEPENDENCY_PATTERNS",
    "FEATURE_ID_RE",
    "ImpactEntry",
    "ImpactResult",
    "RemediationAction",
    "calculate_risk_level",
    "generate_remediation_plan",
    "resolve_impact",
]

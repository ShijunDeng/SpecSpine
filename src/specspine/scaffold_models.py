from __future__ import annotations

from ._scaffold_coverage_models import (
    ScaffoldCoverageLink,
    ScaffoldRemediationStep,
    ScaffoldReport,
    ScaffoldSkippedCriterion,
)
from ._scaffold_test_models import ScaffoldTestMethod

__all__ = [
    "ScaffoldCoverageLink",
    "ScaffoldRemediationStep",
    "ScaffoldReport",
    "ScaffoldSkippedCriterion",
    "ScaffoldTestMethod",
]

ScaffoldCoverageLink = ScaffoldCoverageLink
ScaffoldRemediationStep = ScaffoldRemediationStep
ScaffoldReport = ScaffoldReport
ScaffoldSkippedCriterion = ScaffoldSkippedCriterion
ScaffoldTestMethod = ScaffoldTestMethod

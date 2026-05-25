from __future__ import annotations

from ._scaffold_link_models import ScaffoldCoverageLink, ScaffoldSkippedCriterion
from ._scaffold_remediation_model import ScaffoldRemediationStep
from ._scaffold_report_model import ScaffoldReport

__all__ = [
    "ScaffoldCoverageLink",
    "ScaffoldRemediationStep",
    "ScaffoldReport",
    "ScaffoldSkippedCriterion",
]

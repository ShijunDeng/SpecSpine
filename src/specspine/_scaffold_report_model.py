from __future__ import annotations

from dataclasses import dataclass

from ._scaffold_test_models import ScaffoldTestMethod
from ._scaffold_link_models import ScaffoldCoverageLink, ScaffoldSkippedCriterion
from ._scaffold_remediation_model import ScaffoldRemediationStep


@dataclass(frozen=True)
class ScaffoldReport:
    feature_id: str
    status: str
    scaffold_file: str
    test_methods: tuple[ScaffoldTestMethod, ...]
    coverage_links: tuple[ScaffoldCoverageLink, ...]
    skipped_criteria: tuple[ScaffoldSkippedCriterion, ...]
    remediation_plan: tuple[ScaffoldRemediationStep, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "coverage_links": [link.as_dict() for link in self.coverage_links],
            "feature_id": self.feature_id,
            "remediation_plan": [step.as_dict() for step in self.remediation_plan],
            "safety_notes": list(self.safety_notes),
            "scaffold_file": self.scaffold_file,
            "skipped_criteria": [item.as_dict() for item in self.skipped_criteria],
            "status": self.status,
            "test_methods": [method.as_dict() for method in self.test_methods],
        }


__all__ = [
    "ScaffoldReport",
]

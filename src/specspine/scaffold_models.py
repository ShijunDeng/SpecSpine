from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "ScaffoldCoverageLink",
    "ScaffoldRemediationStep",
    "ScaffoldReport",
    "ScaffoldSkippedCriterion",
    "ScaffoldTestMethod",
]


@dataclass(frozen=True)
class ScaffoldTestMethod:
    method_name: str
    docstring: str
    ac_id: str
    ac_text: str
    body: str

    def as_dict(self) -> dict[str, str]:
        return {
            "ac_id": self.ac_id,
            "ac_text": self.ac_text,
            "body": self.body,
            "docstring": self.docstring,
            "method_name": self.method_name,
        }


@dataclass(frozen=True)
class ScaffoldCoverageLink:
    ac_id: str
    target_path: str
    class_name: str
    method_name: str

    def as_dict(self) -> dict[str, str]:
        return {
            "ac_id": self.ac_id,
            "class_name": self.class_name,
            "method_name": self.method_name,
            "target_path": self.target_path,
        }


@dataclass(frozen=True)
class ScaffoldSkippedCriterion:
    ac_id: str
    reason: str

    def as_dict(self) -> dict[str, str]:
        return {
            "ac_id": self.ac_id,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ScaffoldRemediationStep:
    ac_id: str
    action: str
    target_path: str
    class_name: str
    method_name: str

    def as_dict(self) -> dict[str, str]:
        return {
            "ac_id": self.ac_id,
            "action": self.action,
            "class_name": self.class_name,
            "method_name": self.method_name,
            "target_path": self.target_path,
        }


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

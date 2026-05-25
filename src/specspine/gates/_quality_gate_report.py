from __future__ import annotations

__all__ = [
    "QualityGateReport",
]

from dataclasses import dataclass
from pathlib import Path

from .constants import SUPPORTED_SEVERITIES
from ._required_gate import RequiredGate
from ._definition_of_done import DefinitionOfDoneItem


@dataclass(frozen=True)
class QualityGateReport:
    root: Path
    source_file: str
    source_missing: bool
    required_checks: tuple[RequiredGate, ...]
    definition_of_done: tuple[DefinitionOfDoneItem, ...]
    recommended_commands: tuple[str, ...]

    @property
    def summary(self) -> dict[str, object]:
        required_done = sum(1 for gate in self.required_checks if gate.done)
        required_total = len(self.required_checks)
        severity_counts = {severity: 0 for severity in SUPPORTED_SEVERITIES}
        for gate in self.required_checks:
            severity_counts[gate.severity] = severity_counts.get(gate.severity, 0) + 1
        return {
            "definition_total": len(self.definition_of_done),
            "ci_checks_total": sum(
                1 for gate in self.required_checks if gate.ci_check is not None
            ),
            "owners_total": sum(
                1 for gate in self.required_checks if gate.owner != "unassigned"
            ),
            "required_done": required_done,
            "required_open": required_total - required_done,
            "required_total": required_total,
            "severity_counts": severity_counts,
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "definition_of_done": [
                item.as_dict() for item in self.definition_of_done
            ],
            "recommended_commands": list(self.recommended_commands),
            "required_checks": [gate.as_dict() for gate in self.required_checks],
            "root": str(self.root),
            "source_file": self.source_file,
            "source_missing": self.source_missing,
            "summary": self.summary,
        }

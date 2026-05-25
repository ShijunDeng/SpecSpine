from __future__ import annotations

__all__ = [
    "RequiredGate",
]

from dataclasses import dataclass


@dataclass(frozen=True)
class RequiredGate:
    id: str
    text: str
    done: bool
    source_file: str
    line: int
    severity: str = "medium"
    owner: str = "unassigned"
    ci_check: str | None = None
    metadata: dict[str, str] | None = None
    metadata_warnings: tuple[str, ...] = ()
    raw_text: str = ""

    def as_dict(self) -> dict[str, object]:
        return {
            "ci_check": self.ci_check,
            "done": self.done,
            "id": self.id,
            "line": self.line,
            "metadata": dict(self.metadata or {}),
            "metadata_warnings": list(self.metadata_warnings),
            "owner": self.owner,
            "raw_text": self.raw_text,
            "severity": self.severity,
            "source_file": self.source_file,
            "text": self.text,
        }

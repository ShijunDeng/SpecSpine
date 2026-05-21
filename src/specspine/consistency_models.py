from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

__all__ = [
    "ConsistencyCheck",
    "ConsistencyReference",
    "ConsistencyReport",
    "FeatureConsistency",
    "DOCUMENTATION_GLOBS",
    "IMPLEMENTATION_GLOBS",
    "LOCAL_PATH_RE",
    "TEST_GLOBS",
]

LOCAL_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])"
    r"(?P<path>(?:src|tests|docs|specs|execution|quality)/[A-Za-z0-9_./-]+|README\.md|AGENTS\.md)"
)

IMPLEMENTATION_GLOBS = ("src/**/*.py",)
TEST_GLOBS = ("tests/**/*.py",)
DOCUMENTATION_GLOBS = (
    "docs/**/*.md",
    "README.md",
    "AGENTS.md",
    "specs/*.md",
    "execution/*.md",
    "quality/*.md",
)


@dataclass(frozen=True)
class ConsistencyReference:
    path: str
    line: int | None
    kind: str
    matched: str
    exists: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "exists": self.exists,
            "kind": self.kind,
            "line": self.line,
            "matched": self.matched,
            "path": self.path,
        }


@dataclass(frozen=True)
class ConsistencyCheck:
    id: str
    status: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "message": self.message,
            "status": self.status,
        }


@dataclass(frozen=True)
class FeatureConsistency:
    feature_id: str
    status: str | None
    source_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    implementation_references: tuple[ConsistencyReference, ...]
    test_references: tuple[ConsistencyReference, ...]
    documentation_references: tuple[ConsistencyReference, ...]
    changed_references: tuple[ConsistencyReference, ...]
    consistency_checks: tuple[ConsistencyCheck, ...]
    summary: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "changed_references": [
                reference.as_dict() for reference in self.changed_references
            ],
            "consistency_checks": [
                check.as_dict() for check in self.consistency_checks
            ],
            "documentation_references": [
                reference.as_dict() for reference in self.documentation_references
            ],
            "feature_id": self.feature_id,
            "implementation_references": [
                reference.as_dict() for reference in self.implementation_references
            ],
            "missing_files": list(self.missing_files),
            "source_files": list(self.source_files),
            "status": self.status,
            "summary": dict(self.summary),
            "test_references": [
                reference.as_dict() for reference in self.test_references
            ],
        }


@dataclass(frozen=True)
class ConsistencyReport:
    root: "Path"
    feature_filter: str | None
    changed_files: tuple[str, ...]
    features: tuple[FeatureConsistency, ...]
    summary: dict[str, Any]
    recommended_commands: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "changed_files": list(self.changed_files),
            "feature_filter": self.feature_filter,
            "features": [feature.as_dict() for feature in self.features],
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "summary": dict(self.summary),
        }

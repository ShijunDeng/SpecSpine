from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..policy import WorkspacePolicy

__all__ = [
    "ReadinessRecordContext",
]


@dataclass
class ReadinessRecordContext:
    slug: str
    status: str
    metadata: Any
    coverage_required: bool
    policy_coverage_required: bool
    report: Any
    require_coverage: bool
    use_policy: bool
    policy: WorkspacePolicy | None

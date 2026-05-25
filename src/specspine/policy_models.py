from __future__ import annotations

from pathlib import Path

from ._policy_readiness import ReadinessCoveragePolicy
from ._policy_workspace import WorkspacePolicy

POLICY_RELATIVE_PATH = ".specspine/policy.yaml"

__all__ = [
    "POLICY_RELATIVE_PATH",
    "ReadinessCoveragePolicy",
    "WorkspacePolicy",
]

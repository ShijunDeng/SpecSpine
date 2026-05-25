from __future__ import annotations

import json
from pathlib import Path

from .policy_models import POLICY_RELATIVE_PATH, ReadinessCoveragePolicy, WorkspacePolicy
from .policy_parser import _build_require_coverage_policy, _parse_policy_subset


def load_workspace_policy(path: Path) -> WorkspacePolicy:
    root = path.expanduser().resolve()
    source_file = root / POLICY_RELATIVE_PATH
    if not source_file.exists():
        return WorkspacePolicy(
            root=root,
            source_file=source_file,
            source_missing=True,
            require_coverage=ReadinessCoveragePolicy(),
        )

    content = source_file.read_text(encoding="utf-8")
    values = _parse_policy_subset(content)
    return WorkspacePolicy(
        root=root,
        source_file=source_file,
        source_missing=False,
        require_coverage=_build_require_coverage_policy(values),
    )


def render_policy_json(policy: WorkspacePolicy) -> str:
    return json.dumps(policy.as_dict(), indent=2, sort_keys=True) + "\n"


def render_policy_text(policy: WorkspacePolicy) -> str:
    require_coverage = policy.require_coverage
    lines = [
        f"Workspace policy: {policy.root}",
        f"Source: {policy.source_file}",
        f"Source missing: {'yes' if policy.source_missing else 'no'}",
        "Readiness coverage:",
        f"  enabled={'yes' if require_coverage.enabled else 'no'}",
        f"  default={'yes' if require_coverage.default else 'no'}",
        "  priorities=" + (", ".join(require_coverage.priorities) or "none"),
        "  statuses=" + (", ".join(require_coverage.statuses) or "none"),
        "  feature_ids=" + (", ".join(require_coverage.feature_ids) or "none"),
        f"Warnings: {len(require_coverage.warnings)}",
    ]
    for warning in require_coverage.warnings:
        lines.append(f"  - {warning}")
    return "\n".join(lines) + "\n"


__all__ = [
    "load_workspace_policy",
    "render_policy_json",
    "render_policy_text",
]

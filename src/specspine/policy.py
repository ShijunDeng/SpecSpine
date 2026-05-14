from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .features import FEATURE_PRIORITIES, FEATURE_STATUSES, FeatureMetadata


POLICY_RELATIVE_PATH = ".specspine/policy.yaml"


@dataclass(frozen=True)
class ReadinessCoveragePolicy:
    enabled: bool = False
    default: bool = False
    priorities: tuple[str, ...] = ()
    statuses: tuple[str, ...] = ()
    feature_ids: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def requires_coverage(
        self,
        *,
        feature_id: str,
        metadata: FeatureMetadata,
        status: str,
    ) -> bool:
        if not self.enabled:
            return False
        return (
            self.default
            or feature_id in self.feature_ids
            or metadata.priority in self.priorities
            or status in self.statuses
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "default": self.default,
            "enabled": self.enabled,
            "feature_ids": list(self.feature_ids),
            "priorities": list(self.priorities),
            "statuses": list(self.statuses),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class WorkspacePolicy:
    root: Path
    source_file: Path
    source_missing: bool
    require_coverage: ReadinessCoveragePolicy

    @property
    def summary(self) -> dict[str, int]:
        return {
            "coverage_rule_count": (
                len(self.require_coverage.feature_ids)
                + len(self.require_coverage.priorities)
                + len(self.require_coverage.statuses)
                + (1 if self.require_coverage.default else 0)
            ),
            "feature_ids": len(self.require_coverage.feature_ids),
            "priorities": len(self.require_coverage.priorities),
            "statuses": len(self.require_coverage.statuses),
            "warning_count": len(self.require_coverage.warnings),
            "warnings": len(self.require_coverage.warnings),
        }

    @property
    def recommended_commands(self) -> tuple[str, ...]:
        return (
            f"specspine policy {self.root} --json",
            "specspine status . --json --feature-summaries --feature-policy",
            "specspine feature ready <slug> . --json --policy",
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "readiness": {
                "require_coverage": self.require_coverage.as_dict(),
            },
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "source_file": str(self.source_file),
            "source_missing": self.source_missing,
            "summary": dict(self.summary),
        }


def _clean_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    for index, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:index]
    return line


def _parse_policy_subset(content: str) -> dict[str, object]:
    require_coverage: dict[str, object] = {}
    current_list: str | None = None
    in_readiness = False
    in_require_coverage = False

    for raw_line in content.splitlines():
        line = _strip_comment(raw_line).rstrip()
        stripped = line.strip()
        if not stripped:
            continue

        indent = len(line) - len(line.lstrip(" "))
        if indent == 0:
            in_readiness = stripped == "readiness:"
            in_require_coverage = False
            current_list = None
            continue

        if not in_readiness:
            continue

        if indent == 2:
            in_require_coverage = stripped == "require_coverage:"
            current_list = None
            continue

        if not in_require_coverage:
            continue

        if indent == 4 and stripped.endswith(":"):
            current_list = stripped[:-1].strip()
            require_coverage.setdefault(current_list, [])
            continue

        if indent == 4 and ":" in stripped:
            key, value = stripped.split(":", 1)
            current_list = None
            require_coverage[key.strip()] = _clean_scalar(value)
            continue

        if indent >= 6 and current_list and stripped.startswith("- "):
            values = require_coverage.setdefault(current_list, [])
            if isinstance(values, list):
                values.append(str(_clean_scalar(stripped[2:])))

    return require_coverage


def _dedupe_strings(values: object) -> tuple[str, ...]:
    if not isinstance(values, list):
        return ()

    deduped: list[str] = []
    for value in values:
        normalized = str(value).strip().lower()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return tuple(deduped)


def _build_require_coverage_policy(values: dict[str, object]) -> ReadinessCoveragePolicy:
    warnings: list[str] = []
    enabled = values.get("enabled", False)
    default = values.get("default", False)
    if not isinstance(enabled, bool):
        warnings.append("readiness.require_coverage.enabled must be true or false.")
        enabled = False
    if not isinstance(default, bool):
        warnings.append("readiness.require_coverage.default must be true or false.")
        default = False

    priorities = _dedupe_strings(values.get("priorities", []))
    statuses = _dedupe_strings(values.get("statuses", []))
    feature_ids = _dedupe_strings(values.get("feature_ids", []))

    for priority in priorities:
        if priority not in FEATURE_PRIORITIES:
            warnings.append(f"Unknown readiness.require_coverage priority: {priority}.")
    for status in statuses:
        if status not in FEATURE_STATUSES:
            warnings.append(f"Unknown readiness.require_coverage status: {status}.")

    return ReadinessCoveragePolicy(
        enabled=enabled,
        default=default,
        priorities=tuple(priority for priority in priorities if priority in FEATURE_PRIORITIES),
        statuses=tuple(status for status in statuses if status in FEATURE_STATUSES),
        feature_ids=feature_ids,
        warnings=tuple(warnings),
    )


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

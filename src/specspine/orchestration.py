from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .dependency import (
    _extract_slugs_from_text,
    _list_feature_slugs,
    _read_all_feature_content,
    _topological_sort,
)
from .features import FEATURE_FILE_PATHS, read_feature_metadata, validate_feature_slug

CONTRACT_PATTERN = re.compile(
    r"(?P<type>endpoint|schema|config|api|route|table|collection)\s*[=:]\s*(?P<name>[A-Za-z0-9_/.:-]+)",
    re.IGNORECASE,
)

API_ENDPOINT_PATTERNS = [
    re.compile(r"(?:GET|POST|PUT|DELETE|PATCH)\s+(/[A-Za-z0-9_/.:{}-]+)"),
    re.compile(r"(?:route|endpoint|url|path)\s*[=:]\s*['\"]?(/[A-Za-z0-9_/.:{}-]+)"),
]

SCHEMA_PATTERNS = [
    re.compile(r"(?:schema|model|table|collection)\s*[=:]\s*([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"class\s+([A-Za-z_][A-Za-z0-9_]*)(?:\(.*Model|:.*BaseModel|:.*Schema)"),
]

CONFIG_PATTERNS = [
    re.compile(r"(?:config|setting|env|variable)\s*[=:]\s*([A-Z_][A-Z0-9_]*)"),
    re.compile(r"(?:key|flag)\s*[=:]\s*['\"]?([a-z_][a-z0-9_.]*)['\"]?"),
]


@dataclass(frozen=True)
class OrchestrationConflict:
    conflict_type: str
    affected_files: tuple[str, ...]
    affected_ac_ids: tuple[str, ...]
    features_involved: tuple[str, ...]
    severity: str
    description: str

    def as_dict(self) -> dict[str, object]:
        return {
            "affected_ac_ids": list(self.affected_ac_ids),
            "affected_files": list(self.affected_files),
            "conflict_type": self.conflict_type,
            "description": self.description,
            "features_involved": list(self.features_involved),
            "severity": self.severity,
        }


@dataclass(frozen=True)
class ParallelGroup:
    group_id: int
    features: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "features": list(self.features),
            "group_id": self.group_id,
        }


@dataclass(frozen=True)
class OrchestrationPlan:
    execution_order: tuple[str, ...]
    parallel_groups: tuple[ParallelGroup, ...]
    blocked_features: tuple[str, ...]
    safe_for_parallel: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "blocked_features": list(self.blocked_features),
            "execution_order": list(self.execution_order),
            "parallel_groups": [g.as_dict() for g in self.parallel_groups],
            "safe_for_parallel": self.safe_for_parallel,
        }


@dataclass(frozen=True)
class OrchestrationReport:
    root: str
    feature_filter: str | None
    conflicts: tuple[OrchestrationConflict, ...]
    plan: OrchestrationPlan
    integration_recommendations: tuple[str, ...]
    status: str
    blocking_items: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "blocking_items": list(self.blocking_items),
            "conflicts": [c.as_dict() for c in self.conflicts],
            "feature_filter": self.feature_filter,
            "integration_recommendations": list(self.integration_recommendations),
            "plan": self.plan.as_dict(),
            "root": self.root,
            "safety_notes": list(self.safety_notes),
            "status": self.status,
        }


def _scan_feature_file_paths(root: Path, slug: str) -> set[str]:
    paths: set[str] = set()
    for kind in FEATURE_FILE_PATHS:
        file_path = root / FEATURE_FILE_PATHS[kind].format(slug=slug)
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if ":" in stripped and not stripped.startswith("src") and not stripped.startswith("tests") and not stripped.startswith("docs"):
                    continue
                if "/" not in stripped:
                    continue
                paths.add(stripped.lower())
    return paths


def _extract_ac_ids(content: str) -> list[str]:
    ac_ids: list[str] = []
    for match in re.finditer(r"(AC\d{3}|AC\d{4})", content):
        ac_ids.append(match.group(1))
    return sorted(set(ac_ids))


def _build_dependency_graph(root: Path, slugs: list[str]) -> dict[str, set[str]]:
    adj: dict[str, set[str]] = {s: set() for s in slugs}
    for slug in slugs:
        content = _read_all_feature_content(root, slug)
        referenced = _extract_slugs_from_text(content, slug, set(slugs))
        for ref in referenced:
            if ref in adj:
                adj[slug].add(ref)
    return adj


def _detect_file_conflicts(root: Path, features: list[str]) -> list[OrchestrationConflict]:
    conflicts: list[OrchestrationConflict] = []
    feature_paths: dict[str, set[str]] = {}
    for slug in features:
        feature_paths[slug] = _scan_feature_file_paths(root, slug)

    for i, slug_a in enumerate(features):
        for slug_b in features[i + 1:]:
            shared = sorted(feature_paths[slug_a] & feature_paths[slug_b])
            if shared:
                combined_content = ""
                for kind in FEATURE_FILE_PATHS:
                    for s in (slug_a, slug_b):
                        fp = root / FEATURE_FILE_PATHS[kind].format(slug=s)
                        if fp.exists():
                            combined_content += fp.read_text(encoding="utf-8")
                ac_ids = _extract_ac_ids(combined_content)
                conflicts.append(
                    OrchestrationConflict(
                        conflict_type="file",
                        affected_files=tuple(shared),
                        affected_ac_ids=tuple(ac_ids),
                        features_involved=tuple(sorted([slug_a, slug_b])),
                        severity="high" if len(shared) > 3 else "medium",
                        description=(
                            f"Features '{slug_a}' and '{slug_b}' target "
                            f"{len(shared)} overlapping file paths."
                        ),
                    )
                )
    return conflicts


def _extract_contracts(content: str) -> dict[str, list[str]]:
    contracts: dict[str, list[str]] = defaultdict(list)
    for match in CONTRACT_PATTERN.finditer(content):
        contract_type = match.group("type").lower()
        name = match.group("name")
        contracts[contract_type].append(name)
    for pattern in API_ENDPOINT_PATTERNS:
        for match in pattern.finditer(content):
            endpoint = match.group(1)
            contracts["endpoint"].append(endpoint)
    for pattern in SCHEMA_PATTERNS:
        for match in pattern.finditer(content):
            schema = match.group(1)
            contracts["schema"].append(schema)
    for pattern in CONFIG_PATTERNS:
        for match in pattern.finditer(content):
            config = match.group(1)
            contracts["config"].append(config)
    return {k: sorted(set(v)) for k, v in contracts.items()}


def _detect_contract_conflicts(root: Path, features: list[str]) -> list[OrchestrationConflict]:
    conflicts: list[OrchestrationConflict] = []
    feature_contracts: dict[str, dict[str, list[str]]] = {}
    for slug in features:
        content = _read_all_feature_content(root, slug)
        feature_contracts[slug] = _extract_contracts(content)

    for i, slug_a in enumerate(features):
        for slug_b in features[i + 1:]:
            shared_contracts: list[tuple[str, str]] = []
            for contract_type in ("endpoint", "schema", "config"):
                set_a = set(feature_contracts[slug_a].get(contract_type, []))
                set_b = set(feature_contracts[slug_b].get(contract_type, []))
                for name in sorted(set_a & set_b):
                    shared_contracts.append((contract_type, name))

            if shared_contracts:
                affected_files: list[str] = []
                for kind in FEATURE_FILE_PATHS:
                    for s in (slug_a, slug_b):
                        fp = root / FEATURE_FILE_PATHS[kind].format(slug=s)
                        if fp.exists():
                            rel = FEATURE_FILE_PATHS[kind].format(slug=s)
                            if rel not in affected_files:
                                affected_files.append(rel)

                combined_content = ""
                for kind in FEATURE_FILE_PATHS:
                    for s in (slug_a, slug_b):
                        fp = root / FEATURE_FILE_PATHS[kind].format(slug=s)
                        if fp.exists():
                            combined_content += fp.read_text(encoding="utf-8")
                ac_ids = _extract_ac_ids(combined_content)

                contract_types_involved = sorted(set(ct for ct, _ in shared_contracts))
                severity = "critical" if "endpoint" in contract_types_involved else "high"
                contract_details = ", ".join(f"{ct}: {name}" for ct, name in shared_contracts)

                conflicts.append(
                    OrchestrationConflict(
                        conflict_type="contract",
                        affected_files=tuple(affected_files),
                        affected_ac_ids=tuple(ac_ids),
                        features_involved=tuple(sorted([slug_a, slug_b])),
                        severity=severity,
                        description=(
                            f"Features '{slug_a}' and '{slug_b}' modify overlapping contracts: "
                            f"{contract_details}."
                        ),
                    )
                )
    return conflicts


def _detect_semantic_conflicts(
    features: list[str],
    root: Path,
) -> list[OrchestrationConflict]:
    """Detect semantic conflicts from mutually exclusive behaviors."""
    conflicts: list[OrchestrationConflict] = []
    feature_configs: dict[str, dict[str, str]] = {}

    for feature_id in features:
        feature_id = validate_feature_slug(feature_id)
        content = _read_all_feature_content(root, feature_id)
        configs: dict[str, str] = {}
        # Extract configuration toggles and feature flags
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("- ") and ("enable" in line or "disable" in line):
                # Look for feature flag patterns
                for keyword in ["enable", "disable", "toggle", "flag"]:
                    if keyword in line.lower():
                        # Extract the feature name
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if keyword in part.lower() and i + 1 < len(parts):
                                flag_name = parts[i + 1].strip(".,;:")
                                if flag_name and flag_name not in ("the", "a", "an"):
                                    configs[flag_name.lower()] = keyword
        feature_configs[feature_id] = configs

    # Detect conflicting configurations
    checked_pairs: set[tuple[str, str]] = set()
    for feature_a in features:
        for feature_b in features:
            if feature_a == feature_b:
                continue
            pair = tuple(sorted([feature_a, feature_b]))
            if pair in checked_pairs:
                continue
            checked_pairs.add(pair)

            configs_a = feature_configs.get(feature_a, {})
            configs_b = feature_configs.get(feature_b, {})

            for flag, action_a in configs_a.items():
                if flag in configs_b:
                    action_b = configs_b[flag]
                    if action_a != action_b:
                        conflicts.append(
                            OrchestrationConflict(
                                conflict_type="semantic",
                                severity="critical",
                                description=f"Features {feature_a} and {feature_b} have conflicting {flag} configuration ({action_a} vs {action_b})",
                                features_involved=tuple(sorted([feature_a, feature_b])),
                                affected_ac_ids=(),
                                affected_files=(),
                            )
                        )

    return conflicts


def _compute_parallel_groups(
    execution_order: list[str],
    adj: dict[str, set[str]],
) -> list[ParallelGroup]:
    if not execution_order:
        return []

    order_set = set(execution_order)
    dep_in_degree: dict[str, int] = {s: 0 for s in execution_order}
    for slug in execution_order:
        for dep in adj.get(slug, set()):
            if dep in order_set and dep in dep_in_degree:
                dep_in_degree[slug] = dep_in_degree.get(slug, 0) + 1

    groups: list[ParallelGroup] = []
    remaining = set(execution_order)
    group_id = 1

    while remaining:
        ready = sorted([s for s in remaining if dep_in_degree.get(s, 0) == 0])
        if not ready:
            remaining_sorted = sorted(remaining)
            groups.append(
                ParallelGroup(group_id=group_id, features=tuple(remaining_sorted))
            )
            break
        groups.append(
            ParallelGroup(group_id=group_id, features=tuple(ready))
        )
        for slug in ready:
            remaining.discard(slug)
            for other in remaining:
                if slug in adj.get(other, set()):
                    dep_in_degree[other] -= 1
        group_id += 1

    return groups


def _generate_integration_recommendations(
    conflicts: list[OrchestrationConflict],
    execution_order: list[str],
    adj: dict[str, set[str]],
) -> list[str]:
    recommendations: list[str] = []
    if not conflicts and not execution_order:
        recommendations.append("No integration steps required; no features or conflicts detected.")
        return recommendations

    file_conflicts = [c for c in conflicts if c.conflict_type == "file"]
    contract_conflicts = [c for c in conflicts if c.conflict_type == "contract"]

    if file_conflicts:
        affected_features: set[str] = set()
        for c in file_conflicts:
            affected_features.update(c.features_involved)
        features_str = ", ".join(sorted(affected_features))
        recommendations.append(
            f"File overlap detected for features: {features_str}. "
            "Coordinate implementation order and run consistency scan after each feature."
        )

    if contract_conflicts:
        affected_features: set[str] = set()
        for c in contract_conflicts:
            affected_features.update(c.features_involved)
        features_str = ", ".join(sorted(affected_features))
        recommendations.append(
            f"Contract overlap detected for features: {features_str}. "
            "Define shared API contracts or data schemas before implementation."
        )

    if len(execution_order) > 1:
        recommendations.append(
            f"Run integration tests after each group in execution order: {' -> '.join(execution_order)}."
        )

    deps_with_multiple = [
        slug for slug in execution_order
        if len(adj.get(slug, set())) > 1
    ]
    if deps_with_multiple:
        features_str = ", ".join(deps_with_multiple)
        recommendations.append(
            f"Features with multiple dependencies ({features_str}) need integration validation "
            "after all dependencies are implemented."
        )

    if not recommendations:
        recommendations.append("No cross-feature integration steps detected.")

    return recommendations


def build_orchestration_plan(
    root: Path,
    feature_filter: str | None = None,
) -> OrchestrationReport:
    resolved_root = root.expanduser().resolve()

    all_slugs = _list_feature_slugs(resolved_root)

    if feature_filter is not None:
        try:
            feature_filter = validate_feature_slug(feature_filter)
        except ValueError:
            raise

    if feature_filter is not None:
        slugs = [feature_filter] if feature_filter in all_slugs else []
    else:
        slugs = list(all_slugs)

    file_conflicts = _detect_file_conflicts(resolved_root, slugs)
    contract_conflicts = _detect_contract_conflicts(resolved_root, slugs)
    all_conflicts = file_conflicts + contract_conflicts

    adj = _build_dependency_graph(resolved_root, slugs)
    topo_order = _topological_sort(slugs, adj)
    if topo_order is None:
        topo_order = []
    else:
        topo_order = list(reversed(topo_order))

    parallel_groups = _compute_parallel_groups(topo_order, adj)

    has_blocking = any(c.severity in ("critical", "high") for c in all_conflicts)
    safe_for_parallel = len(parallel_groups) == 1 and not has_blocking

    blocked_features: list[str] = []
    for c in all_conflicts:
        if c.severity == "critical":
            for f in c.features_involved:
                if f not in blocked_features:
                    blocked_features.append(f)
    blocked_features.sort()

    plan = OrchestrationPlan(
        execution_order=tuple(topo_order),
        parallel_groups=tuple(parallel_groups),
        blocked_features=tuple(blocked_features),
        safe_for_parallel=safe_for_parallel,
    )

    integration_recs = _generate_integration_recommendations(all_conflicts, topo_order, adj)

    blocking_items: list[str] = []
    for c in all_conflicts:
        if c.severity in ("critical", "high"):
            blocking_items.append(
                f"[{c.severity.upper()}] {c.conflict_type} conflict: {c.description}"
            )

    if topo_order is None or (slugs and not topo_order):
        blocking_items.append("Dependency cycle detected; topological order cannot be computed.")

    status = "ok"
    if blocking_items:
        status = "blocked" if any(c.severity == "critical" for c in all_conflicts) else "warnings"

    safety_notes = (
        "This report reads local workspace files only.",
        "Recommended commands are advisory only and are not executed.",
        "SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, or read tokens.",
    )

    return OrchestrationReport(
        root=str(resolved_root),
        feature_filter=feature_filter,
        conflicts=tuple(all_conflicts),
        plan=plan,
        integration_recommendations=tuple(integration_recs),
        status=status,
        blocking_items=tuple(blocking_items),
        safety_notes=safety_notes,
    )


def render_orchestration_json(report: OrchestrationReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_orchestration_text(report: OrchestrationReport) -> str:
    lines: list[str] = []
    lines.append(f"Orchestration plan: {report.root}")
    if report.feature_filter:
        lines.append(f"Feature filter: {report.feature_filter}")
    lines.append(f"Status: {report.status}")
    lines.append("")

    lines.append(f"Conflicts ({len(report.conflicts)}):")
    if report.conflicts:
        for conflict in report.conflicts:
            lines.append(
                f"  - [{conflict.severity}] {conflict.conflict_type}: {conflict.description}"
            )
            if conflict.affected_files:
                lines.append(f"    files: {', '.join(conflict.affected_files)}")
            lines.append(f"    features: {', '.join(conflict.features_involved)}")
    else:
        lines.append("  (none)")
    lines.append("")

    plan = report.plan
    lines.append("Execution plan:")
    if plan.execution_order:
        lines.append(f"  order: {' -> '.join(plan.execution_order)}")
    else:
        lines.append("  order: (none)")

    if plan.parallel_groups:
        lines.append("  parallel groups:")
        for group in plan.parallel_groups:
            lines.append(f"    group {group.group_id}: {', '.join(group.features)}")
    else:
        lines.append("  parallel groups: (none)")

    if plan.blocked_features:
        lines.append(f"  blocked: {', '.join(plan.blocked_features)}")
    lines.append(f"  safe_for_parallel: {plan.safe_for_parallel}")
    lines.append("")

    if report.integration_recommendations:
        lines.append("Integration recommendations:")
        for rec in report.integration_recommendations:
            lines.append(f"  - {rec}")
    lines.append("")

    if report.blocking_items:
        lines.append("Blocking items:")
        for item in report.blocking_items:
            lines.append(f"  - {item}")
    else:
        lines.append("Blocking items: (none)")
    lines.append("")

    lines.append("Safety notes:")
    for note in report.safety_notes:
        lines.append(f"  - {note}")

    return "\n".join(lines) + "\n"

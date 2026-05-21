from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from ..features import FEATURE_FILE_PATHS, validate_feature_slug

from .orchestration_models import (
    CONTRACT_PATTERN,
    API_ENDPOINT_PATTERNS,
    CONFIG_PATTERNS,
    SCHEMA_PATTERNS,
    OrchestrationConflict,
)


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
        from ..dependency import _read_all_feature_content
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
        from ..dependency import _read_all_feature_content
        content = _read_all_feature_content(root, feature_id)
        configs: dict[str, str] = {}
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("- ") and ("enable" in line or "disable" in line):
                for keyword in ["enable", "disable", "toggle", "flag"]:
                    if keyword in line.lower():
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if keyword in part.lower() and i + 1 < len(parts):
                                flag_name = parts[i + 1].strip(".,;:")
                                if flag_name and flag_name not in ("the", "a", "an"):
                                    configs[flag_name.lower()] = keyword
        feature_configs[feature_id] = configs

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


__all__ = [
    "_detect_contract_conflicts",
    "_detect_file_conflicts",
    "_detect_semantic_conflicts",
    "_extract_ac_ids",
    "_extract_contracts",
    "_scan_feature_file_paths",
]

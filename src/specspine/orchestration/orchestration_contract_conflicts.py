from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from ..features import FEATURE_FILE_PATHS
from ..dependency import _read_all_feature_content
from .orchestration_models import (
    CONTRACT_PATTERN,
    API_ENDPOINT_PATTERNS,
    CONFIG_PATTERNS,
    SCHEMA_PATTERNS,
    OrchestrationConflict,
)
from .orchestration_extraction import _extract_ac_ids

__all__ = [
    "_extract_contracts",
    "_detect_contract_conflicts",
]


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

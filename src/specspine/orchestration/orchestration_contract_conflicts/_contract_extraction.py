from __future__ import annotations

from collections import defaultdict

from ..orchestration_models import (
    CONTRACT_PATTERN,
    API_ENDPOINT_PATTERNS,
    CONFIG_PATTERNS,
    SCHEMA_PATTERNS,
)


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


__all__ = [
    "_extract_contracts",
]

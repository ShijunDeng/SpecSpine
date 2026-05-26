from __future__ import annotations

from pathlib import Path

from ._contract_pair_helpers import (
    _collect_affected_files,
    _extract_ac_ids_for_pair,
    _find_shared_contracts,
)
from ._shared_contract_model import SharedContractInfo  # noqa: F401

__all__ = [
    "SharedContractInfo",
    "scan_feature_pair_contracts",
]


def scan_feature_pair_contracts(
    root: Path,
    slug_a: str,
    slug_b: str,
    feature_contracts: dict[str, dict[str, list[str]]],
) -> SharedContractInfo | None:
    """Scan a feature pair for shared contracts and return conflict info."""
    shared_contracts = _find_shared_contracts(slug_a, slug_b, feature_contracts)
    if not shared_contracts:
        return None

    affected_files = _collect_affected_files(root, slug_a, slug_b)
    ac_ids = _extract_ac_ids_for_pair(root, slug_a, slug_b)
    contract_types_involved = sorted(set(ct for ct, _ in shared_contracts))
    severity = "critical" if "endpoint" in contract_types_involved else "high"
    contract_details = ", ".join(f"{ct}: {name}" for ct, name in shared_contracts)

    return SharedContractInfo(
        slug_a=slug_a,
        slug_b=slug_b,
        shared_contracts=shared_contracts,
        affected_files=affected_files,
        ac_ids=ac_ids,
        contract_types_involved=contract_types_involved,
        severity=severity,
        contract_details=contract_details,
    )

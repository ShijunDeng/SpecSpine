from __future__ import annotations

from pathlib import Path

from ...features import FEATURE_FILE_PATHS
from ..orchestration_extraction import _extract_ac_ids

__all__ = [
    "SharedContractInfo",
    "scan_feature_pair_contracts",
]


class SharedContractInfo:
    """Holds shared contract data for a feature pair."""

    __slots__ = (
        "slug_a",
        "slug_b",
        "shared_contracts",
        "affected_files",
        "ac_ids",
        "contract_types_involved",
        "severity",
        "contract_details",
    )

    def __init__(
        self,
        slug_a: str,
        slug_b: str,
        shared_contracts: list[tuple[str, str]],
        affected_files: list[str],
        ac_ids: list[str],
        contract_types_involved: list[str],
        severity: str,
        contract_details: str,
    ) -> None:
        self.slug_a = slug_a
        self.slug_b = slug_b
        self.shared_contracts = shared_contracts
        self.affected_files = affected_files
        self.ac_ids = ac_ids
        self.contract_types_involved = contract_types_involved
        self.severity = severity
        self.contract_details = contract_details


def _find_shared_contracts(
    slug_a: str,
    slug_b: str,
    feature_contracts: dict[str, dict[str, list[str]]],
) -> list[tuple[str, str]]:
    """Find shared contracts between two features."""
    shared: list[tuple[str, str]] = []
    for contract_type in ("endpoint", "schema", "config"):
        set_a = set(feature_contracts[slug_a].get(contract_type, []))
        set_b = set(feature_contracts[slug_b].get(contract_type, []))
        for name in sorted(set_a & set_b):
            shared.append((contract_type, name))
    return shared


def _collect_affected_files(
    root: Path,
    slug_a: str,
    slug_b: str,
) -> list[str]:
    """Collect affected file paths for two features."""
    affected_files: list[str] = []
    for kind in FEATURE_FILE_PATHS:
        for s in (slug_a, slug_b):
            fp = root / FEATURE_FILE_PATHS[kind].format(slug=s)
            if fp.exists():
                rel = FEATURE_FILE_PATHS[kind].format(slug=s)
                if rel not in affected_files:
                    affected_files.append(rel)
    return affected_files


def _extract_ac_ids_for_pair(
    root: Path,
    slug_a: str,
    slug_b: str,
) -> list[str]:
    """Extract AC IDs from combined content of two features."""
    combined_content = ""
    for kind in FEATURE_FILE_PATHS:
        for s in (slug_a, slug_b):
            fp = root / FEATURE_FILE_PATHS[kind].format(slug=s)
            if fp.exists():
                combined_content += fp.read_text(encoding="utf-8")
    return _extract_ac_ids(combined_content)


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

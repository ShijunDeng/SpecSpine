from __future__ import annotations

__all__ = [
    "SharedContractInfo",
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

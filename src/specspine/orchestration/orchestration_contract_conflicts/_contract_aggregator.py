from __future__ import annotations

from pathlib import Path

from ...dependency import _read_all_feature_content
from ._contract_extraction import _extract_contracts


def _aggregate_feature_contracts(
    root: Path,
    features: list[str],
) -> dict[str, dict[str, list[str]]]:
    """Read and extract contracts for each feature."""
    feature_contracts: dict[str, dict[str, list[str]]] = {}
    for slug in features:
        content = _read_all_feature_content(root, slug)
        feature_contracts[slug] = _extract_contracts(content)
    return feature_contracts


__all__ = [
    "_aggregate_feature_contracts",
]

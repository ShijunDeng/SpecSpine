from __future__ import annotations

from pathlib import Path

from ...features import FEATURE_FILE_PATHS
from ..orchestration_extraction import _extract_ac_ids

__all__ = [
    "_find_shared_contracts",
    "_collect_affected_files",
    "_extract_ac_ids_for_pair",
]


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

from __future__ import annotations

import re
from pathlib import Path

from ..features import FEATURE_FILE_PATHS

__all__ = [
    "_scan_feature_file_paths",
    "_extract_ac_ids",
]


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

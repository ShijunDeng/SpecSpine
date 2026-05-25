from __future__ import annotations

from pathlib import Path
from typing import Any

from .impact_helpers import (
    _find_slug_symbols,
    _module_name,
    _read_text,
    _relative_path,
)
from .impact_models import (
    IMPACT_TYPE_CODE,
    SEVERITY_MEDIUM,
    ImpactItem,
    SOURCE_GLOBS,
)

__all__ = [
    "_scan_source_files",
]


def _scan_source_files(
    slug: str,
    root: Path,
    proposed_changes: dict[str, Any] | None = None,
) -> list[ImpactItem]:
    resolved_root = root.expanduser().resolve()
    affected: list[ImpactItem] = []
    seen: set[str] = set()

    for pattern in SOURCE_GLOBS:
        for source_file in sorted(resolved_root.glob(pattern)):
            if not source_file.is_file():
                continue
            content = _read_text(source_file)
            rel_path = _relative_path(resolved_root, source_file)

            if slug in content:
                module_name = _module_name(source_file, resolved_root)
                if module_name not in seen:
                    seen.add(module_name)
                    symbols = _find_slug_symbols(content, slug)
                    affected.append(
                        ImpactItem(
                            type=IMPACT_TYPE_CODE,
                            id=module_name,
                            path=rel_path,
                            severity=SEVERITY_MEDIUM,
                            reason=f"Source module references feature '{slug}'",
                            affected_acs=symbols,
                        )
                    )

    return affected, seen

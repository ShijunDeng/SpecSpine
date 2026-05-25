from __future__ import annotations

from pathlib import Path
from typing import Any

from ..consistency import LOCAL_PATH_RE
from ..features import (
    FEATURE_FILE_PATHS,
)

from .impact_helpers import (
    _find_slug_symbols,
    _module_name,
    _read_text,
    _relative_path,
)
from .impact_models import (
    IMPACT_TYPE_CODE,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    ImpactItem,
    SOURCE_GLOBS,
)

__all__ = [
    "_find_affected_code",
]


def _find_affected_code(
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

    for kind in FEATURE_FILE_PATHS:
        file_path = resolved_root / FEATURE_FILE_PATHS[kind].format(slug=slug)
        if file_path.exists():
            content = _read_text(file_path)
            for match in LOCAL_PATH_RE.finditer(content):
                ref_path = match.group("path").rstrip(".,);]`")
                if ref_path.startswith("src/"):
                    src_file = resolved_root / ref_path
                    if src_file.exists() and src_file.suffix == ".py":
                        module_name = _module_name(src_file, resolved_root)
                        if module_name not in seen:
                            seen.add(module_name)
                            affected.append(
                                ImpactItem(
                                    type=IMPACT_TYPE_CODE,
                                    id=module_name,
                                    path=ref_path,
                                    severity=SEVERITY_LOW,
                                    reason=f"Feature artifact references '{ref_path}'",
                                )
                            )

    return affected

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..consistency import LOCAL_PATH_RE
from ..features import (
    FEATURE_FILE_PATHS,
)

from .impact_helpers import (
    _module_name,
    _read_text,
)
from .impact_models import (
    IMPACT_TYPE_CODE,
    SEVERITY_LOW,
    ImpactItem,
)

__all__ = [
    "_scan_feature_artifacts",
]


def _scan_feature_artifacts(
    slug: str,
    root: Path,
    seen: set[str],
    proposed_changes: dict[str, Any] | None = None,
) -> list[ImpactItem]:
    resolved_root = root.expanduser().resolve()
    affected: list[ImpactItem] = []

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

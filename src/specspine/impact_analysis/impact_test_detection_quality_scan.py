from __future__ import annotations

import re
from pathlib import Path

from ..features import (
    FEATURE_FILE_PATHS,
)
from .impact_helpers import (
    _read_text,
)
from .impact_models import (
    IMPACT_TYPE_TEST,
    SEVERITY_LOW,
    ImpactItem,
)

__all__ = [
    "_scan_tests_by_quality",
]


def _scan_tests_by_quality(
    slug: str,
    resolved_root: Path,
    affected: list[ImpactItem],
    seen: set[str],
) -> None:
    quality_path = resolved_root / FEATURE_FILE_PATHS["quality"].format(slug=slug)
    if not quality_path.exists():
        return

    quality_content = _read_text(quality_path)
    for match in re.finditer(r"(tests/[\w./_-]+\.py)", quality_content):
        test_path = match.group(1)
        test_file = resolved_root / test_path
        if test_file.exists():
            test_id = test_file.stem
            if test_id not in seen:
                seen.add(test_id)
                affected.append(
                    ImpactItem(
                        type=IMPACT_TYPE_TEST,
                        id=test_id,
                        path=test_path,
                        severity=SEVERITY_LOW,
                        reason=f"Quality file references test '{test_path}'",
                    )
                )

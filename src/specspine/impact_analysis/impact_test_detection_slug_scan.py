from __future__ import annotations

from pathlib import Path

from ..features import (
    FEATURE_FILE_PATHS,
)
from .impact_helpers import (
    _extract_acceptance_criteria,
    _find_referenced_acs,
    _read_text,
    _relative_path,
)
from .impact_models import (
    IMPACT_TYPE_TEST,
    SEVERITY_MEDIUM,
    ImpactItem,
    TEST_GLOBS,
)

__all__ = [
    "_scan_tests_by_slug",
]


def _scan_tests_by_slug(
    slug: str,
    resolved_root: Path,
    affected: list[ImpactItem],
    seen: set[str],
) -> None:
    for pattern in TEST_GLOBS:
        for test_file in sorted(resolved_root.glob(pattern)):
            if not test_file.is_file():
                continue
            content = _read_text(test_file)
            rel_path = _relative_path(resolved_root, test_file)

            if slug in content:
                test_id = test_file.stem
                if test_id not in seen:
                    seen.add(test_id)
                    acs = _find_referenced_acs(content, slug, resolved_root)
                    affected.append(
                        ImpactItem(
                            type=IMPACT_TYPE_TEST,
                            id=test_id,
                            path=rel_path,
                            severity=SEVERITY_MEDIUM,
                            reason=f"Test file references feature '{slug}'",
                            affected_acs=acs,
                        )
                    )

from __future__ import annotations

from pathlib import Path

from ..features import (
    FEATURE_FILE_PATHS,
)
from .impact_helpers import (
    _extract_acceptance_criteria,
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
    "_scan_tests_by_ac",
]


def _scan_tests_by_ac(
    slug: str,
    resolved_root: Path,
    affected: list[ImpactItem],
    seen: set[str],
) -> None:
    spec_path = resolved_root / FEATURE_FILE_PATHS["spec"].format(slug=slug)
    if not spec_path.exists():
        return

    spec_content = _read_text(spec_path)
    acs = _extract_acceptance_criteria(spec_content)
    for ac_id, ac_text in acs:
        if ac_text:
            for pattern in TEST_GLOBS:
                for test_file in sorted(resolved_root.glob(pattern)):
                    if not test_file.is_file():
                        continue
                    content = _read_text(test_file)
                    rel_path = _relative_path(resolved_root, test_file)
                    test_id = test_file.stem
                    if ac_text[:30] in content or (ac_id and ac_id in content):
                        if test_id not in seen:
                            seen.add(test_id)
                            affected.append(
                                ImpactItem(
                                    type=IMPACT_TYPE_TEST,
                                    id=test_id,
                                    path=rel_path,
                                    severity=SEVERITY_MEDIUM,
                                    reason=f"Test covers acceptance criterion of feature '{slug}'",
                                    affected_acs=(ac_id,) if ac_id else (),
                                )
                            )

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..consistency import LOCAL_PATH_RE
from ..features import (
    FEATURE_FILE_PATHS,
)

from .impact_helpers import (
    _extract_acceptance_criteria,
    _find_referenced_acs,
    _find_slug_symbols,
    _module_name,
    _read_text,
    _relative_path,
)
from .impact_models import (
    IMPACT_TYPE_CODE,
    IMPACT_TYPE_TEST,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    ImpactItem,
    SOURCE_GLOBS,
    TEST_GLOBS,
)

__all__ = [
    "_find_affected_code",
    "_find_affected_tests",
]


def _find_affected_tests(
    slug: str,
    root: Path,
    proposed_changes: dict[str, Any] | None = None,
) -> list[ImpactItem]:
    resolved_root = root.expanduser().resolve()
    affected: list[ImpactItem] = []
    seen: set[str] = set()

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

    spec_path = resolved_root / FEATURE_FILE_PATHS["spec"].format(slug=slug)
    if spec_path.exists():
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

    quality_path = resolved_root / FEATURE_FILE_PATHS["quality"].format(slug=slug)
    if quality_path.exists():
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

    return affected


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

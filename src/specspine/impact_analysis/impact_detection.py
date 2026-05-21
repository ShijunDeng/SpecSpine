from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..consistency import LOCAL_PATH_RE
from ..dependency import (
    EXPLICIT_DEP_PATTERNS,
    _list_feature_slugs,
    _read_all_feature_content,
)
from ..features import (
    FEATURE_FILE_PATHS,
    FEATURE_DIRECTORIES,
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    read_feature_metadata,
    validate_feature_slug,
)

from .impact_models import (
    IMPACT_TYPE_CODE,
    IMPACT_TYPE_FEATURE,
    IMPACT_TYPE_TEST,
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    ImpactItem,
    SOURCE_GLOBS,
    TEST_GLOBS,
)


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _extract_acceptance_criteria(content: str) -> list[tuple[str, str]]:
    criteria: list[tuple[str, str]] = []
    in_section = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("## acceptance criteria"):
            in_section = True
            continue
        if in_section:
            if stripped.startswith("## "):
                break
            match = re.match(r"- \[[ xX]\]\s+(.+)", stripped)
            if match:
                criteria.append(("", match.group(1)))
            match_ac = re.match(r"- \[[ xX]\]\s*(AC\d+)\s*[-:]\s*(.*)", stripped)
            if match_ac:
                criteria[-1] = (match_ac.group(1), match_ac.group(2)) if criteria else (match_ac.group(1), match_ac.group(2))
    return criteria


def _extract_slugs_from_text(
    text: str,
    current_slug: str,
    valid_slugs: set[str] | None = None,
) -> list[str]:
    slugs: list[str] = []
    for pattern in EXPLICIT_DEP_PATTERNS:
        for match in pattern.finditer(text):
            found = match.group(1)
            if found != current_slug and found not in slugs:
                if valid_slugs is None or found in valid_slugs:
                    slugs.append(found)
    return slugs


def _find_referenced_acs(
    content: str,
    slug: str,
    root: Path,
) -> tuple[str, ...]:
    acs: list[str] = []
    for match in re.finditer(r"(AC\d+)", content):
        ac_id = match.group(1)
        if ac_id not in acs:
            acs.append(ac_id)
    return tuple(acs)


def _module_name(source_file: Path, root: Path) -> str:
    rel = _relative_path(root, source_file)
    if rel.endswith(".py"):
        rel = rel[:-3]
    return rel.replace("/", ".")


def _find_slug_symbols(content: str, slug: str) -> tuple[str, ...]:
    symbols: list[str] = []
    for line in content.splitlines():
        if slug in line:
            for match in re.finditer(r"(?:def|class)\s+(\w+)", line):
                sym = match.group(1)
                if sym not in symbols:
                    symbols.append(sym)
    return tuple(sorted(symbols))


def _find_affected_features(
    slug: str,
    root: Path,
    proposed_changes: dict[str, Any] | None = None,
) -> list[ImpactItem]:
    resolved_root = root.expanduser().resolve()
    all_slugs = _list_feature_slugs(resolved_root)
    if slug not in all_slugs:
        return []

    downstream: dict[str, list[str]] = {s: [] for s in all_slugs}
    for s in all_slugs:
        if s == slug:
            continue
        content = _read_all_feature_content(resolved_root, s)
        referenced = _extract_slugs_from_text(content, s, set(all_slugs))
        if slug in referenced:
            downstream[s].append(slug)

    affected: list[ImpactItem] = []
    seen: set[str] = set()
    for s in sorted(downstream):
        if slug in downstream[s] and s not in seen:
            seen.add(s)
            metadata = read_feature_metadata(resolved_root, s)
            severity = SEVERITY_HIGH if metadata.priority == "high" else (
                SEVERITY_MEDIUM if metadata.priority == "medium" else SEVERITY_LOW
            )
            affected.append(
                ImpactItem(
                    type=IMPACT_TYPE_FEATURE,
                    id=s,
                    path=FEATURE_FILE_PATHS["spec"].format(slug=s),
                    severity=severity,
                    reason=f"Feature '{s}' depends on '{slug}'",
                )
            )

    if proposed_changes and "shared_paths" in proposed_changes:
        shared_paths = proposed_changes["shared_paths"]
        for s in sorted(all_slugs):
            if s == slug or s in seen:
                continue
            for kind in FEATURE_FILE_PATHS:
                file_path = resolved_root / FEATURE_FILE_PATHS[kind].format(slug=s)
                if file_path.exists():
                    content = file_path.read_text(encoding="utf-8")
                    for line in content.splitlines():
                        stripped = line.strip().lower()
                        for sp in shared_paths:
                            if sp.lower() in stripped and len(sp) > 3:
                                seen.add(s)
                                affected.append(
                                    ImpactItem(
                                        type=IMPACT_TYPE_FEATURE,
                                        id=s,
                                        path=FEATURE_FILE_PATHS[kind].format(slug=s),
                                        severity=SEVERITY_MEDIUM,
                                        reason=f"Feature '{s}' shares file path reference '{sp}' with '{slug}'",
                                    )
                                )
                                break
                        if s in seen:
                            break
                if s in seen:
                    break

    return affected


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


__all__ = [
    "_extract_acceptance_criteria",
    "_extract_slugs_from_text",
    "_find_affected_code",
    "_find_affected_features",
    "_find_affected_tests",
    "_find_referenced_acs",
    "_find_slug_symbols",
    "_module_name",
    "_read_text",
    "_relative_path",
]

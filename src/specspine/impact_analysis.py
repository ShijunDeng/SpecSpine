from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .consistency import LOCAL_PATH_RE
from .dependency import (
    EXPLICIT_DEP_PATTERNS,
    _list_feature_slugs,
    _read_all_feature_content,
)
from .features import (
    FEATURE_FILE_PATHS,
    FEATURE_DIRECTORIES,
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    read_feature_metadata,
    validate_feature_slug,
)

SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"

IMPACT_TYPE_FEATURE = "feature"
IMPACT_TYPE_TEST = "test"
IMPACT_TYPE_CODE = "code"

SOURCE_GLOBS = ("src/**/*.py",)
TEST_GLOBS = ("tests/**/*.py",)


@dataclass(frozen=True)
class ImpactItem:
    type: str
    id: str
    path: str
    severity: str
    reason: str
    affected_acs: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "affected_acs": list(self.affected_acs),
            "id": self.id,
            "path": self.path,
            "reason": self.reason,
            "severity": self.severity,
            "type": self.type,
        }
        return result


@dataclass(frozen=True)
class ImpactAnalysis:
    feature_id: str
    total_affected: int
    impacted_features: tuple[ImpactItem, ...]
    impacted_tests: tuple[ImpactItem, ...]
    impacted_code: tuple[ImpactItem, ...]
    risk_score: int
    mitigation_steps: tuple[str, ...]
    safety_notes: tuple[str, ...]
    recommended_commands: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "impacted_code": [item.as_dict() for item in self.impacted_code],
            "impacted_features": [
                item.as_dict() for item in self.impacted_features
            ],
            "impacted_tests": [item.as_dict() for item in self.impacted_tests],
            "mitigation_steps": list(self.mitigation_steps),
            "recommended_commands": list(self.recommended_commands),
            "risk_score": self.risk_score,
            "safety_notes": list(self.safety_notes),
            "total_affected": self.total_affected,
        }


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


def _compute_risk_score(
    impacted_features: tuple[ImpactItem, ...],
    impacted_tests: tuple[ImpactItem, ...],
    impacted_code: tuple[ImpactItem, ...],
) -> int:
    score = 0

    high_count = sum(
        1 for item in impacted_features + impacted_tests + impacted_code
        if item.severity == SEVERITY_HIGH
    )
    medium_count = sum(
        1 for item in impacted_features + impacted_tests + impacted_code
        if item.severity == SEVERITY_MEDIUM
    )
    low_count = sum(
        1 for item in impacted_features + impacted_tests + impacted_code
        if item.severity == SEVERITY_LOW
    )

    score += high_count * 15
    score += medium_count * 8
    score += low_count * 3

    feature_count = len(impacted_features)
    test_count = len(impacted_tests)
    code_count = len(impacted_code)

    if feature_count > 3:
        score += 20
    elif feature_count > 1:
        score += 10

    if test_count > 5:
        score += 15
    elif test_count > 2:
        score += 8

    if code_count > 5:
        score += 10
    elif code_count > 2:
        score += 5

    return min(score, 100)


def _generate_mitigation_steps(analysis: ImpactAnalysis) -> list[str]:
    steps: list[str] = []

    if analysis.impacted_features:
        slugs = ", ".join(item.id for item in analysis.impacted_features[:5])
        steps.append(
            f"Review dependent features before merging changes: {slugs}"
        )
        steps.append(
            "Update dependent feature specs if API contracts or behaviors change"
        )

    if analysis.impacted_tests:
        test_paths = ", ".join(item.path for item in analysis.impacted_tests[:5])
        steps.append(
            f"Update impacted tests to reflect new behavior: {test_paths}"
        )
        steps.append(
            "Run full test suite after changes to catch regressions"
        )

    if analysis.impacted_code:
        code_paths = ", ".join(item.path for item in analysis.impacted_code[:5])
        steps.append(
            f"Review code changes in impacted modules: {code_paths}"
        )

    if analysis.risk_score >= 50:
        steps.append(
            "High risk score detected: consider breaking changes into smaller PRs"
        )

    if analysis.risk_score >= 75:
        steps.append(
            "Critical risk score: require additional peer review before merging"
        )

    steps.append(
        f"Run 'specspine impact analyze {analysis.feature_id} . --json' after changes to re-assess"
    )
    steps.append(
        "Run 'specspine validate . --fusion --features' before handoff or release"
    )

    return steps


def _generate_recommended_commands(slug: str) -> tuple[str, ...]:
    commands = [
        f"specspine impact analyze {slug} . --json",
        f"specspine consistency scan . --feature {slug} --json",
        f"specspine tests impact . --feature {slug} --json",
        f"specspine verify matrix {slug} . --json",
        f"specspine feature handoff {slug} . --json",
        "specspine validate . --fusion --features",
    ]
    return tuple(commands)


def analyze_feature_impact(
    root: Path,
    slug: str,
    proposed_changes: dict[str, Any] | None = None,
) -> ImpactAnalysis:
    resolved_root = root.expanduser().resolve()
    slug = validate_feature_slug(slug)

    spec_path = resolved_root / FEATURE_FILE_PATHS["spec"].format(slug=slug)
    if not spec_path.exists():
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(
                resolved_root / FEATURE_FILE_PATHS[kind].format(slug=slug)
                for kind in FEATURE_FILE_PATHS
            ),
        )

    impacted_features = _find_affected_features(slug, resolved_root, proposed_changes)
    impacted_tests = _find_affected_tests(slug, resolved_root, proposed_changes)
    impacted_code = _find_affected_code(slug, resolved_root, proposed_changes)

    risk_score = _compute_risk_score(
        tuple(impacted_features),
        tuple(impacted_tests),
        tuple(impacted_code),
    )

    feature_items = tuple(impacted_features)
    test_items = tuple(impacted_tests)
    code_items = tuple(impacted_code)
    total_affected = len(feature_items) + len(test_items) + len(code_items)

    preliminary = ImpactAnalysis(
        feature_id=slug,
        total_affected=total_affected,
        impacted_features=feature_items,
        impacted_tests=test_items,
        impacted_code=code_items,
        risk_score=risk_score,
        mitigation_steps=(),
        safety_notes=(
            "This command reads local workspace files only.",
            "It does not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, or read tokens.",
            "Impact predictions are static analysis only and do not prove actual runtime behavior.",
        ),
        recommended_commands=(),
    )

    mitigation_steps = _generate_mitigation_steps(preliminary)
    recommended_commands = _generate_recommended_commands(slug)

    return ImpactAnalysis(
        feature_id=slug,
        total_affected=total_affected,
        impacted_features=feature_items,
        impacted_tests=test_items,
        impacted_code=code_items,
        risk_score=risk_score,
        mitigation_steps=tuple(mitigation_steps),
        safety_notes=preliminary.safety_notes,
        recommended_commands=recommended_commands,
    )


def render_impact_json(analysis: ImpactAnalysis) -> str:
    return json.dumps(analysis.as_dict(), indent=2, sort_keys=True) + "\n"


def render_impact_text(analysis: ImpactAnalysis) -> str:
    lines: list[str] = []
    lines.append(f"Feature impact analysis: {analysis.feature_id}")
    lines.append(f"Risk score: {analysis.risk_score}/100")
    lines.append(f"Total affected items: {analysis.total_affected}")
    lines.append("")

    lines.append(f"Impacted features ({len(analysis.impacted_features)}):")
    if analysis.impacted_features:
        for item in analysis.impacted_features:
            lines.append(f"  - [{item.severity}] {item.id}: {item.reason}")
    else:
        lines.append("  (none)")
    lines.append("")

    lines.append(f"Impacted tests ({len(analysis.impacted_tests)}):")
    if analysis.impacted_tests:
        for item in analysis.impacted_tests:
            ac_info = ""
            if item.affected_acs:
                ac_info = f" (ACs: {', '.join(item.affected_acs)})"
            lines.append(f"  - [{item.severity}] {item.path}: {item.reason}{ac_info}")
    else:
        lines.append("  (none)")
    lines.append("")

    lines.append(f"Impacted code ({len(analysis.impacted_code)}):")
    if analysis.impacted_code:
        for item in analysis.impacted_code:
            lines.append(f"  - [{item.severity}] {item.path}: {item.reason}")
    else:
        lines.append("  (none)")
    lines.append("")

    lines.append("Mitigation steps:")
    for step in analysis.mitigation_steps:
        lines.append(f"  - {step}")
    lines.append("")

    lines.append("Recommended commands:")
    for cmd in analysis.recommended_commands:
        lines.append(f"  - {cmd}")
    lines.append("")

    lines.append("Safety notes:")
    for note in analysis.safety_notes:
        lines.append(f"  - {note}")

    return "\n".join(lines) + "\n"

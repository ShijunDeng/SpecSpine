from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .dependency import build_dependency_graph
from .evolution_classification import ClassifiedChange
from .features import (
    FEATURE_FILE_PATHS,
    InvalidFeatureSlug,
    build_feature_tests_report,
    build_feature_trace_report,
    list_feature_bundles,
    validate_feature_slug,
)

FEATURE_ID_RE = re.compile(r"Feature\s+ID:\s*([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE)
DEPENDENCY_PATTERNS = [
    re.compile(r"depends\s+on\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"after\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"blocked\s+by\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"requires\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
]

__all__ = [
    "DEPENDENCY_PATTERNS",
    "FEATURE_ID_RE",
    "ImpactEntry",
    "ImpactResult",
    "RemediationAction",
    "calculate_risk_level",
    "generate_remediation_plan",
    "resolve_impact",
]


@dataclass(frozen=True)
class ImpactEntry:
    change_id: str
    affected_type: str
    affected_id: str
    severity: str

    def as_dict(self) -> dict[str, str]:
        return {
            "affected_id": self.affected_id,
            "affected_type": self.affected_type,
            "change_id": self.change_id,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class ImpactResult:
    slug: str
    impacts: list[ImpactEntry]

    @property
    def summary(self) -> dict[str, int]:
        return {
            "breaking": sum(1 for i in self.impacts if i.severity == "breaking"),
            "info": sum(1 for i in self.impacts if i.severity == "info"),
            "total": len(self.impacts),
            "warning": sum(1 for i in self.impacts if i.severity == "warning"),
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "impacts": [i.as_dict() for i in self.impacts],
            "slug": self.slug,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class RemediationAction:
    action_id: str
    description: str
    priority: int
    target_file: str

    def as_dict(self) -> dict[str, object]:
        return {
            "action_id": self.action_id,
            "description": self.description,
            "priority": self.priority,
            "target_file": self.target_file,
        }


def _extract_feature_refs(text: str) -> list[str]:
    refs: list[str] = []
    for pattern in DEPENDENCY_PATTERNS:
        refs.extend(pattern.findall(text))
    refs.extend(FEATURE_ID_RE.findall(text))
    return sorted(set(refs))


def _extract_metadata(content: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    keys = {"Priority", "Owner", "Milestone", "Target Release", "Project", "Effort", "Status"}
    for line in content.splitlines():
        stripped = line.strip()
        if ":" in stripped and not stripped.startswith("#"):
            key, _, value = stripped.partition(":")
            key = key.strip()
            if key in keys:
                metadata[key] = value.strip()
    return metadata


def _find_downstream_references(
    slug: str,
    root: Path,
) -> dict[str, list[dict[str, str]]]:
    resolved_root = root.expanduser().resolve()
    all_features = list_feature_bundles(resolved_root)
    references: dict[str, list[dict[str, str]]] = {
        "tasks": [],
        "coverage": [],
        "dependent_features": [],
    }

    for feature in all_features:
        feature_slug = feature["slug"]
        if feature_slug == slug:
            continue
        try:
            trace = build_feature_trace_report(resolved_root, feature_slug)
            for ac in trace.acceptance_criteria:
                if slug.lower() in ac.text.lower():
                    references["tasks"].append({
                        "feature_id": feature_slug,
                        "item_id": ac.id,
                        "text": ac.text,
                    })
        except (InvalidFeatureSlug, OSError):
            continue

        try:
            tests_report = build_feature_tests_report(resolved_root, feature_slug)
            for coverage_link in tests_report.test_coverage:
                if slug.lower() in coverage_link.text.lower():
                    references["coverage"].append({
                        "feature_id": feature_slug,
                        "coverage_id": coverage_link.id,
                        "text": coverage_link.text,
                    })
        except (InvalidFeatureSlug, OSError):
            continue

        for file_kind in FEATURE_FILE_PATHS:
            file_path = resolved_root / FEATURE_FILE_PATHS[file_kind].format(slug=feature_slug)
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                feature_refs = _extract_feature_refs(content)
                if slug in feature_refs:
                    references["dependent_features"].append({
                        "feature_id": feature_slug,
                        "reference_type": file_kind,
                    })

    return references


def resolve_impact(
    changes: list[ClassifiedChange],
    slug: str,
    root: Path,
) -> ImpactResult:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()

    downstream = _find_downstream_references(slug, resolved_root)
    impacts: list[ImpactEntry] = []
    impact_counter = 0

    change_has_refs: dict[str, list[str]] = {}
    for ref_type, refs in downstream.items():
        for ref in refs:
            feature_id = ref.get("feature_id", "")
            for change in changes:
                if change.change_type in ("removed", "modified"):
                    if feature_id not in change_has_refs:
                        change_has_refs[change.change_id] = []
                    if feature_id not in change_has_refs[change.change_id]:
                        change_has_refs[change.change_id].append(feature_id)

    for change in changes:
        if change.change_type == "removed" and change.category == "ac":
            refs = change_has_refs.get(change.change_id, [])
            for ref_feature in refs:
                impact_counter += 1
                impacts.append(
                    ImpactEntry(
                        change_id=change.change_id,
                        affected_type="feature",
                        affected_id=ref_feature,
                        severity="breaking",
                    )
                )
            coverage_refs = downstream.get("coverage", [])
            for cov_ref in coverage_refs:
                if cov_ref.get("feature_id") in [r.get("feature_id") for r in refs]:
                    impact_counter += 1
                    impacts.append(
                        ImpactEntry(
                            change_id=change.change_id,
                            affected_type="coverage",
                            affected_id=cov_ref.get("coverage_id", "unknown"),
                            severity="breaking",
                        )
                    )

            impact_counter += 1
            impacts.append(
                ImpactEntry(
                    change_id=change.change_id,
                    affected_type="ac",
                    affected_id=change.after or change.before or "unknown",
                    severity="warning",
                )
            )

        elif change.change_type == "modified" and change.category == "ac":
            refs = change_has_refs.get(change.change_id, [])
            for ref_feature in refs:
                impact_counter += 1
                impacts.append(
                    ImpactEntry(
                        change_id=change.change_id,
                        affected_type="feature",
                        affected_id=ref_feature,
                        severity="warning",
                    )
                )
            if not refs:
                impact_counter += 1
                impacts.append(
                    ImpactEntry(
                        change_id=change.change_id,
                        affected_type="ac",
                        affected_id=change.after or change.before or "unknown",
                        severity="info",
                    )
                )

        elif change.change_type == "removed" and change.category == "task":
            refs = change_has_refs.get(change.change_id, [])
            for ref_feature in refs:
                impact_counter += 1
                impacts.append(
                    ImpactEntry(
                        change_id=change.change_id,
                        affected_type="feature",
                        affected_id=ref_feature,
                        severity="breaking",
                    )
                )
            impact_counter += 1
            impacts.append(
                ImpactEntry(
                    change_id=change.change_id,
                    affected_type="task",
                    affected_id=change.before or "unknown",
                    severity="warning",
                )
            )

        elif change.change_type == "added":
            impact_counter += 1
            impacts.append(
                ImpactEntry(
                    change_id=change.change_id,
                    affected_type=change.category,
                    affected_id=change.after or "unknown",
                    severity="info",
                )
            )

        elif change.change_type == "modified" and change.category == "metadata":
            impact_counter += 1
            impacts.append(
                ImpactEntry(
                    change_id=change.change_id,
                    affected_type="metadata",
                    affected_id=slug,
                    severity="info",
                )
            )

        elif change.change_type == "modified" and change.category in ("spec", "execution", "quality"):
            refs = change_has_refs.get(change.change_id, [])
            if refs:
                for ref_feature in refs:
                    impact_counter += 1
                    impacts.append(
                        ImpactEntry(
                            change_id=change.change_id,
                            affected_type="feature",
                            affected_id=ref_feature,
                            severity="warning",
                        )
                    )
            else:
                impact_counter += 1
                impacts.append(
                    ImpactEntry(
                        change_id=change.change_id,
                        affected_type=change.category,
                        affected_id=slug,
                        severity="info",
                    )
                )

    return ImpactResult(slug=slug, impacts=impacts)


def calculate_risk_level(change: ClassifiedChange, impact: ImpactEntry) -> str:
    if change.change_type == "removed" and change.category == "ac":
        if impact.severity in ("breaking", "warning"):
            return "breaking"
    if change.change_type == "modified" and change.category == "ac":
        if impact.severity == "warning":
            return "warning"
    if change.change_type == "removed" and change.category == "task":
        if impact.severity == "breaking":
            return "breaking"
        return "warning"
    if change.change_type == "modified" and impact.severity == "warning":
        return "warning"
    return "info"


def generate_remediation_plan(
    changes: list[ClassifiedChange],
    impacts: list[ImpactEntry],
) -> list[RemediationAction]:
    actions: list[RemediationAction] = []
    action_counter = 0

    impact_by_change: dict[str, list[ImpactEntry]] = {}
    for impact in impacts:
        if impact.severity == "info":
            continue
        if impact.change_id not in impact_by_change:
            impact_by_change[impact.change_id] = []
        impact_by_change[impact.change_id].append(impact)

    for change in changes:
        relevant_impacts = impact_by_change.get(change.change_id, [])
        if not relevant_impacts:
            continue

        if change.change_type == "removed" and change.category == "ac":
            ac_id = change.before or "unknown"
            action_counter += 1
            actions.append(
                RemediationAction(
                    action_id=f"ACT{action_counter:03d}",
                    description=f"Update downstream features referencing removed AC {ac_id}",
                    priority=1,
                    target_file=change.file,
                )
            )
            for impact in relevant_impacts:
                if impact.affected_type == "coverage":
                    action_counter += 1
                    actions.append(
                        RemediationAction(
                            action_id=f"ACT{action_counter:03d}",
                            description=f"Remove coverage link {impact.affected_id} from quality file",
                            priority=2,
                            target_file=FEATURE_FILE_PATHS["quality"].format(slug=change.file.split("/")[-1].replace(".md", "")),
                        )
                    )
                elif impact.affected_type == "feature":
                    action_counter += 1
                    actions.append(
                        RemediationAction(
                            action_id=f"ACT{action_counter:03d}",
                            description=f"Re-validate feature {impact.affected_id} that depends on removed AC",
                            priority=1,
                            target_file=FEATURE_FILE_PATHS["spec"].format(slug=impact.affected_id),
                        )
                    )

        elif change.change_type == "modified" and change.category == "ac":
            ac_id = change.after or change.before or "unknown"
            for impact in relevant_impacts:
                if impact.affected_type == "feature":
                    action_counter += 1
                    actions.append(
                        RemediationAction(
                            action_id=f"ACT{action_counter:03d}",
                            description=f"Re-validate feature {impact.affected_id} for modified AC {ac_id}",
                            priority=2,
                            target_file=FEATURE_FILE_PATHS["quality"].format(slug=impact.affected_id),
                        )
                    )

        elif change.change_type == "removed" and change.category == "task":
            task_id = change.before or "unknown"
            action_counter += 1
            actions.append(
                RemediationAction(
                    action_id=f"ACT{action_counter:03d}",
                    description=f"Update execution file for removed task {task_id}",
                    priority=1,
                    target_file=FEATURE_FILE_PATHS["execution"].format(
                        slug=change.file.split("/")[-1].replace(".md", "")
                    ),
                )
            )

        elif change.change_type == "added" and change.category == "task":
            task_id = change.after or "unknown"
            action_counter += 1
            actions.append(
                RemediationAction(
                    action_id=f"ACT{action_counter:03d}",
                    description=f"Add test coverage for new task {task_id}",
                    priority=3,
                    target_file=FEATURE_FILE_PATHS["quality"].format(
                        slug=change.file.split("/")[-1].replace(".md", "")
                    ),
                )
            )

    actions.sort(key=lambda a: a.priority)
    return actions

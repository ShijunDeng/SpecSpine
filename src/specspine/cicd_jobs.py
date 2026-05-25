from __future__ import annotations

from pathlib import Path

from .cicd_models import MergeCondition, PipelineJob
from .gates import QUALITY_GATE_SOURCE_FILE, build_quality_gate_report
from .validation import build_validation_report
from .workspace import BASE_WORKSPACE_FILES, check_workspace

__all__ = [
    "_validate_workspace",
    "_build_core_jobs",
    "_build_merge_conditions",
]


def _validate_workspace(root: Path) -> tuple[bool, list[str]]:
    present, missing = check_workspace(root, required_files=BASE_WORKSPACE_FILES)
    if not present:
        return False, [str(m.relative_to(root)) for m in missing]
    return True, []


def _build_core_jobs(feature_slug: str | None = None) -> list[PipelineJob]:
    jobs: list[PipelineJob] = [
        PipelineJob(
            name="validate",
            steps=(
                "specspine validate --fusion --features",
            ),
            description="Validate SpecSpine workspace contracts",
        ),
        PipelineJob(
            name="test",
            steps=(
                "python3 -m unittest discover -s tests",
            ),
            description="Run the full test suite",
        ),
        PipelineJob(
            name="coverage",
            steps=(
                "specspine coverage debt . --json --policy",
            ),
            description="Check acceptance-criteria coverage debt",
        ),
        PipelineJob(
            name="quality-gates",
            steps=(
                "specspine gates . --json",
            ),
            description="Export repository quality gate definitions",
        ),
        PipelineJob(
            name="consistency",
            steps=(
                "specspine consistency scan . --json",
            ),
            description="Scan for spec-code-test-doc drift",
        ),
        PipelineJob(
            name="hygiene",
            steps=(
                "specspine hygiene scan . --strict --json",
            ),
            description="Check repository hygiene",
        ),
        PipelineJob(
            name="security",
            steps=(
                "specspine security cues . --json",
            ),
            description="Surface security-sensitive review cues",
        ),
    ]

    if feature_slug:
        jobs.append(
            PipelineJob(
                name="feature-readiness",
                steps=(
                    f"specspine feature ready {feature_slug} . --json --require-coverage",
                ),
                description=f"Check readiness gate for feature: {feature_slug}",
            ),
        )

    return jobs


def _build_merge_conditions(
    feature_slug: str | None = None,
) -> list[MergeCondition]:
    conditions: list[MergeCondition] = [
        MergeCondition(
            id="merge-001",
            text="specspine validate --fusion --features passes with no failures",
        ),
        MergeCondition(
            id="merge-002",
            text="python3 -m unittest discover -s tests passes",
        ),
        MergeCondition(
            id="merge-003",
            text="specspine coverage debt . --json --policy shows no policy-selected debt",
        ),
        MergeCondition(
            id="merge-004",
            text="specspine gates . --json shows all required checks done",
        ),
        MergeCondition(
            id="merge-005",
            text="specspine consistency scan . --json shows no critical drift",
        ),
        MergeCondition(
            id="merge-006",
            text="specspine hygiene scan . --strict --json shows no strict findings",
        ),
        MergeCondition(
            id="merge-007",
            text="specspine security cues . --json reviewed with no unresolved cues",
        ),
    ]

    if feature_slug:
        conditions.append(
            MergeCondition(
                id="merge-008",
                text=f"specspine feature ready {feature_slug} . --json --require-coverage passes",
            ),
        )

    return conditions

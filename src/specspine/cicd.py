from __future__ import annotations

import json
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .gates import QUALITY_GATE_SOURCE_FILE, build_quality_gate_report
from .validation import build_validation_report
from .workspace import BASE_WORKSPACE_FILES, check_workspace

SUPPORTED_FORMATS = ("github-actions", "gitlab-ci", "generic")


@dataclass(frozen=True)
class PipelineJob:
    name: str
    steps: tuple[str, ...]
    description: str = ""
    condition: str = ""

    def as_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "name": self.name,
            "steps": list(self.steps),
        }
        if self.description:
            result["description"] = self.description
        if self.condition:
            result["condition"] = self.condition
        return result


@dataclass(frozen=True)
class MergeCondition:
    id: str
    text: str
    required: bool = True

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "required": self.required,
            "text": self.text,
        }


@dataclass(frozen=True)
class PipelineResult:
    pipeline_type: str
    jobs: tuple[PipelineJob, ...]
    merge_conditions: tuple[MergeCondition, ...]
    safety_notes: tuple[str, ...]
    feature_slug: str | None = None
    raw_content: str = ""

    def as_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "jobs": [job.as_dict() for job in self.jobs],
            "merge_conditions": [
                mc.as_dict() for mc in self.merge_conditions
            ],
            "pipeline_type": self.pipeline_type,
            "safety_notes": list(self.safety_notes),
        }
        if self.feature_slug:
            result["feature_slug"] = self.feature_slug
        return result


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


SAFETY_NOTES = (
    "This pipeline is generated read-only: no network calls, no subprocess execution, no token reads.",
    "Acceptance criteria from spec bundles become test gates in the pipeline.",
    "Quality metrics from quality/checklist.md become merge requirements.",
    "Feature readiness gates become deployment conditions when --feature is specified.",
    "Review generated pipeline before committing to CI system.",
)


def _generate_github_actions_yaml(
    jobs: list[PipelineJob],
    feature_slug: str | None = None,
) -> str:
    job_parts: list[str] = []
    for job in jobs:
        run_lines = []
        for step_cmd in job.steps:
            run_lines.append(f"        run: {step_cmd}")
        run_block = "\n".join(run_lines)

        job_yaml = (
            f"  {job.name}:\n"
            f"    runs-on: ubuntu-latest\n"
            f"    steps:\n"
            f"      - uses: actions/checkout@v4\n"
            f"      - uses: actions/setup-python@v5\n"
            f"        with:\n"
            f'          python-version: "3.12"\n'
            f"      - name: {job.description or job.name}\n"
            f"{run_block}\n"
        )
        job_parts.append(job_yaml)

    jobs_block = "\n".join(job_parts)

    feature_label = f" (feature: {feature_slug})" if feature_slug else ""

    return (
        f"# SpecSpine CI/CD pipeline{feature_label}\n"
        f"# Generated by specspine cicd generate\n"
        f"# Review before committing\n"
        f"\n"
        f"name: SpecSpine Pipeline\n"
        f"\n"
        f"on:\n"
        f"  push:\n"
        f"    branches: [main]\n"
        f"  pull_request:\n"
        f"    branches: [main]\n"
        f"\n"
        f"permissions:\n"
        f"  contents: read\n"
        f"\n"
        f"jobs:\n"
        f"{jobs_block}"
    )


def _generate_gitlab_ci_yaml(
    jobs: list[PipelineJob],
    feature_slug: str | None = None,
) -> str:
    stage_names = [job.name for job in jobs]
    stages_block = "\n".join(f"  - {name}" for name in stage_names)

    job_parts: list[str] = []
    for job in jobs:
        steps_block = "\n".join(f"    - {step_cmd}" for step_cmd in job.steps)

        job_yaml = (
            f"{job.name}:\n"
            f"  stage: {job.name}\n"
            f"  image: python:3.12\n"
            f"  script:\n"
            f"{steps_block}"
        )
        job_parts.append(job_yaml)

    jobs_block = "\n\n".join(job_parts)

    feature_label = f" (feature: {feature_slug})" if feature_slug else ""

    return (
        f"# SpecSpine CI/CD pipeline{feature_label}\n"
        f"# Generated by specspine cicd generate\n"
        f"# Review before committing\n"
        f"\n"
        f"stages:\n"
        f"{stages_block}\n"
        f"\n"
        f"{jobs_block}\n"
    )


def _generate_generic_shell(
    jobs: list[PipelineJob],
    feature_slug: str | None = None,
) -> str:
    feature_label = f" (feature: {feature_slug})" if feature_slug else ""

    lines = [
        "#!/usr/bin/env bash",
        "# SpecSpine CI/CD pipeline" + feature_label,
        "# Generated by specspine cicd generate",
        "# Review before committing",
        "",
        "set -euo pipefail",
        "",
        'echo "=== SpecSpine CI/CD Pipeline ==="',
        'echo "Started at $(date -u +%Y-%m-%dT%H:%M:%SZ)"',
        "",
    ]

    for idx, job in enumerate(jobs, 1):
        lines.append(f"# Stage {idx}: {job.name}")
        lines.append(f'echo "--- {job.name}: {job.description or job.name} ---"')
        for step_cmd in job.steps:
            lines.append(f'echo "Running: {step_cmd}"')
            lines.append(f"{step_cmd}")
        lines.append(f'echo "--- {job.name}: passed ---"')
        lines.append("")

    lines.extend([
        'echo "=== All pipeline stages passed ==="',
        'echo "Completed at $(date -u +%Y-%m-%dT%H:%M:%SZ)"',
        "",
    ])

    return "\n".join(lines)


def generate_github_actions(
    root: Path,
    feature_slug: str | None = None,
) -> str:
    jobs = _build_core_jobs(feature_slug)
    return _generate_github_actions_yaml(jobs, feature_slug)


def generate_gitlab_ci(
    root: Path,
    feature_slug: str | None = None,
) -> str:
    jobs = _build_core_jobs(feature_slug)
    return _generate_gitlab_ci_yaml(jobs, feature_slug)


def generate_generic(
    root: Path,
    feature_slug: str | None = None,
) -> str:
    jobs = _build_core_jobs(feature_slug)
    return _generate_generic_shell(jobs, feature_slug)


_GENERATORS = {
    "github-actions": generate_github_actions,
    "gitlab-ci": generate_gitlab_ci,
    "generic": generate_generic,
}


def generate_pipeline(
    root: Path,
    format: str = "github-actions",
    feature_slug: str | None = None,
) -> dict[str, Any]:
    if format not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported pipeline format: {format}. "
            f"Supported formats: {', '.join(SUPPORTED_FORMATS)}."
        )

    resolved_root = root.expanduser().resolve()
    valid, missing = _validate_workspace(resolved_root)
    if not valid:
        raise FileNotFoundError(
            f"No SpecSpine workspace found at {resolved_root}. "
            f"Missing: {', '.join(missing)}"
        )

    generator = _GENERATORS[format]
    raw_content = generator(resolved_root, feature_slug)

    jobs = _build_core_jobs(feature_slug)
    merge_conditions = _build_merge_conditions(feature_slug)

    return {
        "pipeline_type": format,
        "jobs": tuple(jobs),
        "merge_conditions": tuple(merge_conditions),
        "safety_notes": SAFETY_NOTES,
        "feature_slug": feature_slug,
        "raw_content": raw_content,
    }


def render_pipeline_json(result: dict[str, Any]) -> str:
    serializable: dict[str, object] = {
        "feature_slug": result.get("feature_slug"),
        "jobs": [
            {
                "description": job["description"] if isinstance(job, dict) else job.description,
                "name": job["name"] if isinstance(job, dict) else job.name,
                "steps": list(job["steps"] if isinstance(job, dict) else job.steps),
            }
            for job in result["jobs"]
        ],
        "merge_conditions": [
            {
                "id": mc["id"] if isinstance(mc, dict) else mc.id,
                "required": mc["required"] if isinstance(mc, dict) else mc.required,
                "text": mc["text"] if isinstance(mc, dict) else mc.text,
            }
            for mc in result["merge_conditions"]
        ],
        "pipeline_type": result["pipeline_type"],
        "raw_content": result["raw_content"],
        "safety_notes": list(result["safety_notes"]),
    }
    return json.dumps(serializable, indent=2, sort_keys=True) + "\n"


def render_pipeline_yaml(result: dict[str, Any]) -> str:
    raw = result.get("raw_content", "")
    if raw:
        return raw
    return "# No raw content available; use render_pipeline_json instead.\n"


def render_pipeline_text(result: dict[str, Any]) -> str:
    lines = [
        f"SpecSpine CI/CD Pipeline ({result['pipeline_type']})",
        "",
    ]

    if result.get("feature_slug"):
        lines.append(f"Feature: {result['feature_slug']}")
        lines.append("")

    lines.append("Jobs:")
    for job in result["jobs"]:
        name = job["name"] if isinstance(job, dict) else job.name
        steps = job["steps"] if isinstance(job, dict) else job.steps
        desc = (
            job["description"]
            if isinstance(job, dict) and job.get("description")
            else (job.description if not isinstance(job, dict) else "")
        )
        lines.append(f"  {name}")
        if desc:
            lines.append(f"    Description: {desc}")
        for step in steps:
            lines.append(f"    - {step}")
        lines.append("")

    lines.append("Merge Conditions:")
    for mc in result["merge_conditions"]:
        req = mc["required"] if isinstance(mc, dict) else mc.required
        text = mc["text"] if isinstance(mc, dict) else mc.text
        marker = "[REQUIRED]" if req else "[OPTIONAL]"
        lines.append(f"  {marker} {text}")
    lines.append("")

    lines.append("Safety Notes:")
    for note in result["safety_notes"]:
        lines.append(f"  - {note}")
    lines.append("")

    return "\n".join(lines)

from __future__ import annotations

from pathlib import Path
from textwrap import dedent


BASE_WORKSPACE_FILES: dict[str, str] = {
    ".specspine/spine.yaml": """
        name: SpecSpine Workspace
        version: 0.1
        backbone:
          intent: specs/intent.md
          product: specs/product.md
          architecture: specs/architecture.md
          execution_plan: execution/plan.md
          task_board: execution/tasks.md
          quality_checklist: quality/checklist.md
          review_notes: quality/review.md
        adapters:
          openspec:
            enabled: false
            config: .specspine/adapters/openspec.md
          speckit:
            enabled: false
            config: .specspine/adapters/speckit.md
          superpowers:
            enabled: false
            config: .specspine/adapters/superpowers.md
    """,
    "specs/intent.md": """
        # Intent

        ## Why

        What problem are we solving, and why does it matter now?

        ## Users

        Who benefits from this work?

        ## Outcomes

        What measurable signals show that the work succeeded?

        ## Constraints

        What business, technical, legal, operational, or timing constraints shape the solution?
    """,
    "specs/product.md": """
        # Product Spec

        ## Scope

        What should be built?

        ## Non-Goals

        What is explicitly out of scope?

        ## User Workflows

        What should users be able to do from start to finish?

        ## Acceptance Criteria

        What must be true before this work is considered complete?
    """,
    "specs/architecture.md": """
        # Architecture

        ## System Shape

        What are the major components and boundaries?

        ## Data And Interfaces

        What data structures, APIs, files, commands, or events matter?

        ## Decisions

        What decisions have been made, and why?

        ## Risks

        What can break the plan, and how will it be handled?
    """,
    "specs/features/.gitkeep": "",
    "execution/plan.md": """
        # Execution Plan

        ## Milestones

        What are the meaningful checkpoints?

        ## Work Breakdown

        What tasks need to be completed?

        ## Dependencies

        What needs to happen first?

        ## Open Questions

        What must be resolved before implementation can proceed safely?
    """,
    "execution/tasks.md": """
        # Tasks

        - [ ] Define intent
        - [ ] Draft product spec
        - [ ] Document architecture decisions
        - [ ] Break work into implementation tasks
        - [ ] Define quality gates
    """,
    "quality/checklist.md": """
        # Quality Checklist

        ## Required Checks

        - [ ] Acceptance criteria are complete.
        - [ ] Tests cover the changed behavior.
        - [ ] Documentation reflects the final behavior.
        - [ ] Risks and tradeoffs are recorded.
        - [ ] Release readiness is reviewed.

        ## Definition Of Done

        What must be true before this work ships?
    """,
    "quality/review.md": """
        # Review Notes

        ## Findings

        What issues, regressions, or risks were found?

        ## Decisions

        What changed after review?

        ## Release Notes

        What should users or operators know?
    """,
}


def normalize_template(content: str) -> str:
    if not content:
        return content
    return dedent(content).strip() + "\n"


def write_workspace_files(
    root: Path,
    files: dict[str, str],
    *,
    force: bool = False,
) -> list[Path]:
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for relative_path, template in files.items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists() and not force:
            continue

        target.write_text(normalize_template(template), encoding="utf-8")
        written.append(target)

    return written


def init_workspace(path: Path, *, force: bool = False) -> list[Path]:
    return write_workspace_files(path, BASE_WORKSPACE_FILES, force=force)


def check_workspace(
    path: Path,
    *,
    required_files: dict[str, str] | None = None,
) -> tuple[list[Path], list[Path]]:
    root = path.expanduser().resolve()
    files = required_files or BASE_WORKSPACE_FILES
    present: list[Path] = []
    missing: list[Path] = []

    for relative_path in files:
        target = root / relative_path
        if target.exists():
            present.append(target)
        else:
            missing.append(target)

    return present, missing

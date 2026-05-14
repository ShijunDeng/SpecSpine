from __future__ import annotations

import argparse
from pathlib import Path
from textwrap import dedent

from . import __version__


WORKSPACE_FILES: dict[str, str] = {
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
          openspec: null
          speckit: null
          superpower: null
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


def init_workspace(path: Path, *, force: bool = False) -> list[Path]:
    root = path.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for relative_path, template in WORKSPACE_FILES.items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists() and not force:
            continue

        target.write_text(normalize_template(template), encoding="utf-8")
        written.append(target)

    return written


def check_workspace(path: Path) -> tuple[list[Path], list[Path]]:
    root = path.expanduser().resolve()
    present: list[Path] = []
    missing: list[Path] = []

    for relative_path in WORKSPACE_FILES:
        target = root / relative_path
        if target.exists():
            present.append(target)
        else:
            missing.append(target)

    return present, missing


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="specspine",
        description="SpecSpine: the backbone for spec-driven AI execution.",
    )
    parser.add_argument("--version", action="version", version=f"specspine {__version__}")

    subcommands = parser.add_subparsers(dest="command", required=True)

    init_parser = subcommands.add_parser("init", help="initialize a SpecSpine workspace")
    init_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    init_parser.add_argument("--force", action="store_true", help="overwrite existing SpecSpine files")

    doctor_parser = subcommands.add_parser("doctor", help="check SpecSpine workspace files")
    doctor_parser.add_argument("path", nargs="?", default=".", help="workspace path")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        written = init_workspace(Path(args.path), force=args.force)
        if written:
            print(f"Initialized SpecSpine workspace at {Path(args.path).resolve()}")
            for path in written:
                print(f"  created {path.relative_to(Path(args.path).resolve())}")
        else:
            print(f"SpecSpine workspace already exists at {Path(args.path).resolve()}")
        return 0

    if args.command == "doctor":
        _present, missing = check_workspace(Path(args.path))
        if missing:
            print("SpecSpine workspace is incomplete.")
            for path in missing:
                print(f"  missing {path.relative_to(Path(args.path).resolve())}")
            return 1

        print(f"SpecSpine workspace is ready at {Path(args.path).resolve()}")
        return 0

    parser.print_help()
    return 1

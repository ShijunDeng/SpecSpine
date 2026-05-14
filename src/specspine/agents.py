from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .workspace import normalize_template


AGENTS_FILE_NAME = "AGENTS.md"

AGENTS_TEMPLATE = """
    # AGENTS.md

    SpecSpine is the spec-driven AI development hub for this workspace. It connects why / what / how into one backbone: intent, product specs, execution, and quality.

    Coding agents including Codex, Claude, and Gemini should treat these files as the local context boundary.

    ## Project Structure

    - `specs/`: intent, product, architecture, and feature specs.
    - `execution/`: plans, task breakdowns, dependencies, and open questions.
    - `quality/`: checks, test plans, reviews, and release readiness.
    - `integrations/`: local notes for external tool integration when present.
    - `docs/`: project documentation and architecture notes.

    ## Common Commands

    ```bash
    specspine status . --json --validate
    specspine status . --json --validate --validation-warnings
    specspine status . --json --validate --feature-summaries
    specspine status . --json --validate --feature-summaries --feature-status validated --feature-ready yes --feature-sort slug
    specspine gates . --json
    specspine validate .
    specspine validate . --features
    specspine validate . --fusion --features
    specspine feature new <slug> . --title "..." --why "..."
    specspine feature status <slug> . --json
    specspine feature status <slug> . --set planned --enforce-transition --json
    specspine feature handoff <slug> . --json
    specspine feature tasks <slug> . --json
    specspine feature task-issues <slug> . --json
    specspine feature trace <slug> . --json
    specspine feature ready <slug> . --json
    specspine feature tests <slug> . --json
    specspine feature issue <slug> . --json
    specspine feature pr <slug> . --json
    PYTHONPATH=src python3 -m unittest discover -s tests
    ```

    ## Working Rules

    - Read `specspine status . --json --validate` before planning or editing; add `--validation-warnings` only when scaffold warning check ids are needed.
    - Use `specspine status . --json --validate --feature-summaries` when choosing or comparing multiple native features; add local filters such as `--feature-status validated --feature-ready yes --feature-sort slug` for triage.
    - Use `specspine gates . --json` when an agent or reviewer needs repository-level quality gate definitions; it exports definitions and does not execute checks.
    - For new requirements, create a feature bundle with `specspine feature new`; the generated peer files include focused handoff, task issue drafts, tests, PR, readiness, and validation guidance.
    - Keep feature peer files on a consistent lifecycle status with `specspine feature status`; prefer `--enforce-transition` when advancing lifecycle state.
    - Before archiving, run `specspine feature ready <slug> . --json`, then archive with `specspine feature status <slug> . --set archived --enforce-transition`.
    - Start feature implementation, review, and acceptance handoffs with `specspine feature handoff <slug> . --json`.
    - Use `specspine feature tasks`, `specspine feature task-issues`, `specspine feature trace`, `specspine feature ready`, and `specspine feature tests` for focused task, task issue draft, trace, gate, and acceptance-test views.
    - For QA context, add local `## Test Coverage` checklist links such as `- [ ] AC001 -> tests/test_features.py` in `quality/features/<slug>.md`.
    - Use `specspine feature pr <slug> . --json` to prepare an offline Pull Request draft from local evidence without reading tokens or calling GitHub.
    - Run `specspine validate .` before and after edits; use `specspine validate . --fusion --features` when feature bundles or fusion artifacts are involved.
    - Keep OpenSpec, Spec Kit, and Superpowers as external adapters. Do not vendor upstream code.
    - By default, do not read or write GitHub tokens and do not call the GitHub API.
    - Use `--run-upstream` only when the user explicitly asks to invoke upstream tools.
"""


@dataclass(frozen=True)
class AgentsFileExistsError(FileExistsError):
    path: Path

    def __str__(self) -> str:
        return f"{AGENTS_FILE_NAME} already exists at {self.path}. Use --force to overwrite it."


def build_agents_file() -> str:
    return normalize_template(AGENTS_TEMPLATE)


def init_agents_file(root: Path, *, force: bool = False) -> Path:
    resolved_root = root.expanduser().resolve()
    target = resolved_root / AGENTS_FILE_NAME

    if target.exists() and not force:
        raise AgentsFileExistsError(path=target)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_agents_file(), encoding="utf-8")
    return target

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
    specspine status . --json --validate --feature-summaries
    specspine validate .
    specspine validate . --features
    specspine feature new <slug> . --title "..." --why "..."
    specspine feature status <slug> . --json
    specspine feature handoff <slug> . --json
    specspine feature tasks <slug> . --json
    specspine feature trace <slug> . --json
    specspine feature ready <slug> . --json
    specspine feature issue <slug> . --json
    PYTHONPATH=src python3 -m unittest discover -s tests
    ```

    ## Working Rules

    - Read `specspine status . --json --validate` before planning or editing.
    - Use `specspine status . --json --validate --feature-summaries` when choosing or comparing multiple native features.
    - For new requirements, create a feature bundle with `specspine feature new`.
    - Keep feature peer files on a consistent lifecycle status with `specspine feature status`.
    - Start feature implementation, review, and acceptance handoffs with `specspine feature handoff <slug> . --json`.
    - Use `specspine feature tasks`, `specspine feature trace`, and `specspine feature ready` for focused task, trace, and gate views.
    - Run `specspine validate .` before and after edits; add `--features` when feature bundles are involved.
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

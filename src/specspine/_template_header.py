from __future__ import annotations

__all__ = [
    "_TEMPLATE_HEADER",
]

_TEMPLATE_HEADER = """
    # AGENTS.md

    SpecSpine is the spec-driven AI development hub for this workspace. It connects why / what / how into one backbone: intent, product specs, execution, and quality.

    Coding agents including Codex, Claude, and Gemini should treat these files as the local context boundary.

    ## Project Structure

    - `specs/`: intent, product, architecture, and feature specs.
    - `execution/`: plans, task breakdowns, dependencies, and open questions.
    - `quality/`: checks, test plans, reviews, and release readiness.
    - `integrations/`: local notes for external tool integration when present.
    - `docs/`: project documentation and architecture notes.
"""

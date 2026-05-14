# Superpowers Quality Policy

Superpowers is the optional agent-side discipline layer for SpecSpine work. SpecSpine does not copy Superpowers skill files; this document records the local policy bridge.

## Before Implementation

- Use brainstorming when intent, users, acceptance criteria, or boundaries are unclear.
- Use writing-plans for multi-step changes and keep the plan tied to SpecSpine artifacts.
- For new requirements, create a native feature bundle before editing implementation code.

## During Implementation

- Prefer test-driven-development for behavior changes in CLI, validation, status, feature, adapter, or fusion logic.
- Keep task progress reflected in `execution/tasks.md` or the relevant `execution/features/<slug>.md`.
- Use subagent-driven-development or executing-plans only when the task size justifies coordination overhead.

## Before Completion

- Run verification-before-completion with:
  - `PYTHONPATH=src python3 -m unittest discover -s tests`
  - `PYTHONPATH=src python3 -m specspine status . --json`
  - `PYTHONPATH=src python3 -m specspine validate . --fusion --features`
  - the repository token-prefix scan requested by maintainers
- Review changes against `specs/intent.md`, `specs/product.md`, and `specs/architecture.md`.
- Record unresolved findings or release notes in `quality/review.md`.

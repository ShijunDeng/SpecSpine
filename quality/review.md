# Review Notes

## Current Review Focus

This repository is now being used as a SpecSpine workspace. Reviews should check both code behavior and the project-level artifacts that guide agents.

## Findings

- No current blocking defects recorded in project-level artifacts.
- The generated workspace templates were too generic for dogfooding and have been replaced with repository-specific intent, product, architecture, execution, and quality content.
- Native feature lifecycle status can now be queried, updated, listed in status JSON, and validated across peer files.
- `specspine status --validate` now reports workspace, fusion, and feature validation summaries without becoming a failing gate command.
- No upstream code should be copied into this repository as part of fusion work.

## Decisions

- Treat `specspine status . --json` as the first context packet for future agents.
- Use `specspine status . --json --validate` when agents need context and failed quality checks together.
- Treat `specspine validate . --fusion --features` plus the unit test suite as the local completion gate.
- Keep GitHub issue generation offline and token-free by default.
- Keep native feature peer files on a consistent allowed lifecycle status.
- Use `--run-upstream` only after explicit user instruction.

## Release Notes

- The repository itself now contains a complete SpecSpine fusion workspace.
- Future feature work should start with native feature bundles under `specs/features/`, `execution/features/`, and `quality/features/`.
- Feature bundles support `proposed`, `planned`, `in-progress`, `implemented`, `validated`, and `archived` statuses.
- Status packets can now include compact validation summaries with failed checks only.
